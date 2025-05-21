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
            padding-top: 0rem;  /* This class often wraps st.title */
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
¡Bienvenido al equipo de IA de MJ Estates!

Desde 2007, MJ Estates ha servido con orgullo al mercado inmobiliario de Miami-Dade, desde casas de lujo hasta propiedades de inversión.

Pregúntame sobre:
- Comprar o vender una propiedad
- Barrios locales (como Brickell, Homestead o Kendall)
- Opciones de financiamiento e inversión
- Programar un recorrido o hablar con un agente
"""
    system_prompt = """Eres el asistente virtual de bienes raíces de MJ Estates. MJ Estates es una empresa de bienes raíces en Miami-Dade. Si el usuario escribe en español, responde completamente en español. Sé profesional, claro y útil.
    Evita hacer promesas como contactar a un prestamista o programar citas, a menos que el usuario envíe el formulario de contacto. Deja claro que eres un asistente y que cualquier acción requiere el seguimiento de un agente.

Puedes ayudar con:
- Compra o venta de propiedades
- Estrategias de inversión o alquiler
- Proceso de compra, opciones de financiamiento y valoración
- Información de barrios como Brickell, Homestead, Kendall
- Programar recorridos o hablar con un agente
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
    disclaimer = "⚠️ Este asistente de IA proporciona información general sobre bienes raíces y no reemplaza el asesoramiento profesional. Para orientación personalizada, comunícate con un agente de MJ Estates."
    back_link = "← Volver al sitio web de MJ Estates"
else:
    title = "MJ Estates AI Assistant"
    intro = """
Welcome to MJ's AI Team!

Since 2007, MJ Estates has proudly served the Miami-Dade real estate market — from luxury homes to income-producing investments.

Ask me anything about:
- Buying or selling a home
- Local neighborhoods (like Brickell, Homestead, or Kendall)
- Financing and investment options
- Scheduling a tour or speaking with an agent
"""
    system_prompt = """You are MJ Estates' virtual real estate assistant. MJ Estates is a full-service real estate firm based in Miami-Dade. If the user writes in Spanish, respond in Spanish. Otherwise, reply in English. Be helpful, brief, and professional.
    Avoid making promises such as contacting a lender or scheduling appointments unless the user submits the contact form. Make clear that you're an assistant and actions require agent follow-up.


You help users with:
- Buying or selling property in Miami-Dade
- Renting, leasing, or investment strategies
- Home buying process, financing, and valuation
- Neighborhood info (Brickell, Homestead, Kendall)
- Scheduling tours or speaking to an agent
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
    disclaimer = "⚠️ This AI assistant provides general real estate information and is not a substitute for professional advice. For personalized guidance, please speak directly with an MJ Estates agent."
    back_link = "← Back to MJ Estates Website"

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

    st.session_state.chat_history.append((user_input, reply))

if len(st.session_state.chat_history) >= 10:
    st.warning(limit_warning)
    st.stop()

st.subheader(lead_title)
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

st.markdown(f"""
---  
<small>{disclaimer}</small>
""", unsafe_allow_html=True)

st.markdown(f"""
<small><a href="https://mjestates.com" target="_blank">{back_link}</a></small>
""", unsafe_allow_html=True)

