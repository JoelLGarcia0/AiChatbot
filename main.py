import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="MJ Estates AI Assistant", page_icon="mjestatesicon.png", layout="centered")

# Load .env and OpenAI
load_dotenv()
client = OpenAI()

# Load and display logo
logo = Image.open("mjestatesicon.png")

# Custom style
st.markdown("""
    <style>
        .block-container {
            padding-top: 2.5rem;
        }
              .st-emotion-cache-1v0mbdj {
            padding-top: 0rem; 
        }
        h1 {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

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
    
    

# Language toggle
language_is_spanish = st.toggle("Language: English / Español")
language = "Español" if language_is_spanish else "English"

# Set prompts based on language
if language == "Español":
    title = "Asistente de IA de MJ Estates"
    intro = """
¡Bienvenido al equipo de IA de MJ Estates! Pregúntame sobre:
- Comprar o vender una propiedad
- Barrios locales (como Brickell, Homestead o Kendall)
- Opciones de financiamiento e inversión
- Programar un recorrido o hablar con un agente
"""
    system_prompt = """Eres el asistente virtual de bienes raíces de MJ Estates. MJ Estates es una empresa de bienes raíces en Miami-Dade. Si el usuario escribe en español, responde completamente en español. Sé profesional, claro y útil.
    Si el usuario desea hablar con un agente, no le pidas directamente su información de contacto. En su lugar, dile: "Por favor, desplázate hacia abajo y completa el formulario de contacto para que un agente de MJ Estates pueda comunicarse contigo.


Puedes ayudar con:
- Compra o venta de propiedades
- Estrategias de inversión o alquiler
- Proceso de compra, opciones de financiamiento y valoración
- Información de barrios como Brickell, Homestead, Kendall
"""
    chat_placeholder = "Hazme una pregunta:"
    chat_history_title = "Historial de conversación"
    lead_title = "¿Quieres hablar con un agente de MJ Estates?"
    name_label = "Tu nombre"
    email_label = "Tu correo electrónico"
    phone_label = "Número de teléfono (opcional)"
    submit_button = "Enviar"
    success_msg = "¡Gracias! Un agente se pondrá en contacto contigo pronto."
    error_msg = "Hubo un problema al enviar tu mensaje."
    limit_warning = "Has alcanzado el número máximo de preguntas para esta sesión."
    disclaimer = "⚠️ Este asistente ofrece información general. Contacta a un agente de MJ Estates para asesoría."
    back_link = "← Volver al sitio web de MJ Estates"
else:
    title = "MJ Estates AI Assistant"
    intro = """
Welcome to MJ's AI Team! Ask me anything about:
- Buying or selling a home
- Local neighborhoods (like Brickell, Homestead, or Kendall)
- Financing and investment options
- Scheduling a tour or speaking with an agent
"""
    system_prompt = """You are MJ Estates' virtual real estate assistant. MJ Estates is a full-service real estate firm based in Miami-Dade. If the user writes in Spanish, respond in Spanish. Otherwise, reply in English. Be helpful and professional.
    If a user wants to speak with an agent, do not ask them for their contact info directly. Instead, say something like: "Please scroll down and use the contact form to submit your information, and an MJ Estates agent will reach out to you.


You help users with:
- Buying or selling property in Miami-Dade
- Renting, leasing, or investment strategies
- Home buying process, financing, and valuation
- Neighborhood info (Brickell, Homestead, Kendall)
"""
    chat_placeholder = "Ask me a question:"
    chat_history_title = "Chat History"
    lead_title = "Want to speak to an MJ Estates Agent?"
    name_label = "Your Name"
    email_label = "Your Email"
    phone_label = "Phone Number (optional)"
    submit_button = "Send"
    success_msg = "Thanks! An agent will contact you soon."
    error_msg = "There was an issue sending your message."
    limit_warning = "You've reached the maximum number of questions for this session."
    disclaimer = "⚠️ This AI assistant provides general real estate information only. For professional advice, contact an MJ Estates agent."
    back_link = "← Back to MJ Estates Website"
st.markdown(f"""
<small><a href="https://mjestates.com" target="_blank">{back_link}</a></small>
""", unsafe_allow_html=True)
st.title(title)

st.markdown(intro)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for question, answer in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant", avatar="mjestatesicon.png"):
        st.markdown(answer)

user_input = st.chat_input(chat_placeholder)

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.spinner("Thinking..."):
       
        messages = [{"role": "system", "content": system_prompt}]
        for question, answer in st.session_state.chat_history:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = response.choices[0].message.content

    with st.chat_message("assistant", avatar="mjestatesicon.png"):
        st.markdown(reply)
   

    st.markdown("""
    <script>
    setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }, 200);

    setTimeout(() => {
        if (document.activeElement) {
            document.activeElement.blur();
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)

    st.session_state.chat_history.append((user_input, reply))
    

if len(st.session_state.chat_history) >= 10:
    st.warning(limit_warning)
    st.stop()
st.markdown(f"""
---  
<small>{disclaimer}</small>
""", unsafe_allow_html=True)

with st.expander(lead_title):
    with st.form("lead_capture"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(name_label)
            email = st.text_input(email_label)
        with col2:
            phone = st.text_input(phone_label)

        submitted = st.form_submit_button(submit_button)

    if submitted:
        success = send_email(name, email, phone)
        if success:
            st.success(success_msg)
        else:
            st.error(error_msg)



