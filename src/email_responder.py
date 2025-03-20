from relevanceai import RelevanceAI
import yaml
from fastapi import FastAPI, BackgroundTasks
import imaplib
import smtplib
import email
import sqlite3
import os
from email.message import EmailMessage
from email.header import decode_header

app = FastAPI()

# Load configuration
def load_config():
    with open("credentials.yml", "r") as f:
        return yaml.safe_load(f)

RAI_CLIENT = RelevanceAI(
    api_key=load_config().get("API_KEY"), 
    region=load_config().get("REGION"), 
    project=load_config().get("PROJECT")
)

# Database setup
DB_FILE = "responses.db"
if not os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE responses (id INTEGER PRIMARY KEY, sender TEXT, subject TEXT, response TEXT)""")
    conn.commit()
    conn.close()

# Fetch unread emails
def fetch_unread_emails():
    print("Fetching unread emails...")

    config = load_config()
    mail = imaplib.IMAP4_SSL(config.get("IMAP_SERVER"))
    mail.login(config.get("EMAIL"), config.get("PASSWORD"))
    mail.select("inbox")
    
    # Search for unread emails from the specific sender
    search_criteria = f'(UNSEEN FROM "mailmeluckysharma6618@rediffmail.com")'
    _, data = mail.search(None, search_criteria)
    email_ids = data[0].split()
    
    print(email_ids)

    emails = []
    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        sender = msg["From"]
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and part.get("Content-Disposition") is None:
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        
        emails.append({"sender": sender, "subject": subject, "body": body})
    
    mail.logout()
    return emails

# Classify email intent and generate response using AI agent
def classify_and_generate_response(text):
    print("----------- incomming text --------------------")
    print(text)
    agent_id = "8923a2ca-93eb-42a6-b499-5a76266682ef"
    my_agent = RAI_CLIENT.agents.retrieve_agent(agent_id=agent_id)
    task = my_agent.trigger_task(message=f"{text}")
    steps = my_agent.view_task_steps(conversation_id=task.conversation_id)

    print(steps)

    return steps[-1]["output"] if steps else "Thank you for your email. We will get back to you soon."

# Send response email
def send_email(to_email, subject, body):
    config = load_config()
    msg = EmailMessage()
    msg["From"] = load_config().get("EMAIL")
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    
    with smtplib.SMTP_SSL(config.get("SMTP_SERVER"), 465) as server:
        server.login(config.get("EMAIL"), config.get("PASSWORD"))
        server.send_message(msg)

# Log response
def log_response(sender, subject, response):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO responses (sender, subject, response) VALUES (?, ?, ?)", (sender, subject, response))
    conn.commit()
    conn.close()

# Process unread emails immediately after startup
def process_and_print_emails():
    emails = fetch_unread_emails()
    
    print("----------- emails --------------------")
    print(emails)

    for email_data in emails:
        response = classify_and_generate_response(email_data["body"])
        send_email(email_data["sender"], "Re: " + email_data["subject"], response)
        log_response(email_data["sender"], email_data["subject"], response)
        print(f"Processed Email: {email_data}\nGenerated Response: {response}")

# Background task to process emails
@app.post("/process_emails")
def process_emails(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_and_print_emails)
    return {"message": "Processing emails in the background..."}

# Get logged responses
@app.get("/responses")
def get_responses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM responses")
    data = c.fetchall()
    conn.close()
    return {"responses": data}

# Run email processing when the application starts
process_and_print_emails()
