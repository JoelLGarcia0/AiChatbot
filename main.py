import streamlit as st
from openai import OpenAI
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def send_email(name, email, phone):
    broker_email = os.getenv("BROKER_EMAIL")
    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg['Subject'] = "New MJ Estates Lead from AI Chatbot"
    msg['From'] = email_sender
    msg['To'] = broker_email

    msg.set_content(
            f"New lead submitted:\n\nName: {name}\nEmail: {email}\nPhone: {phone if phone else 'N/A'}"
    
    )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)
        return True 
    except Exception as e:
        print("Email failed:", e)
        return False
    
st.set_page_config(page_title="MJ Estates AI Assistant", layout="centered")
st.title("Welcome to MJ Estates AI Assistant")
st.markdown("""
Since 2007, MJ Estates has proudly served the Miami-Dade real estate market — from luxury homes to income-producing investments.

Ask me anything about:
- Buying or selling a home
- Local neighborhoods (like Brickell, Homestead, or Kendall)
- Financing and investment options
- Scheduling a tour or speaking with an agent
""")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask me a question:")

if user_input:
    with st.spinner("Thinking..."):
        messages = [
                       {
                "role": "system",
                "content": """You are MJ Estates' virtual real estate assistant. MJ Estates is a full-service real estate firm based in Miami-Dade, founded in 2007, with expertise in both luxury and income-generating properties.

You help users with questions about:
- Buying or selling property in Miami-Dade
- Renting, leasing, or investment property strategy
- The home buying process, financing options, and valuation
- Neighborhood guidance (e.g. Brickell, Homestead, Kendall)
- Scheduling tours or speaking to an agent

Answer in a helpful, professional, and friendly tone. Be brief and clear. If someone has a more personal or complex need, recommend they submit their info to speak directly with an MJ Estates agent."""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
        reply = response.choices[0].message.content
        st.session_state.chat_history.append((user_input,reply))
        st.success(reply)
if st.session_state.chat_history:
    st.subheader("Chat History")
    for question, answer in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {question}")
        st.markdown(f"**MJ Estates AI:** {answer}")
        st.markdown("---")

if len(st.session_state.chat_history) >= 10:
    st.warning("You've reached the maximum number of questions for this session.")
    st.stop()

st.subheader("Want to speak to an MJ Estates Agent?")
with st.form("lead_capture"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    phone = st.text_input("Phone Number (optional)")
    submitted = st.form_submit_button("Send")


if submitted:
    success = send_email(name, email, phone)
    if success:
        st.success("Thanks! An agent will contact you soon.")
    else:
        st.error("There was an issue sending your message.")