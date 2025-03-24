import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

_import_('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


def send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, sender_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            st.success(f"✅ Email sent successfully to {receiver_email}")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")

    url_input = st.text_input("Enter a URL:")
    sender_email = st.text_input("Your Email", value="sanhulk73@gmail.com")
    receiver_email = st.text_input("Receiver's Email", value="sanjayshankar91@gmail.com")
    sender_password = st.text_input("Your Email Password", type="password")
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email_body = llm.write_mail(job, links)

                subject = "Expert Solutions for Your Job Requirement"
                send_email(sender_email, receiver_email, subject, email_body, smtp_server, smtp_port, sender_password)

        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
