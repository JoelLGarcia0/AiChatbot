import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from supabase import create_client, Client

# Config
st.set_page_config(page_title="MJ Estates AI Assistant", page_icon="mjestatesicon.png", layout="centered")
load_dotenv()
client = OpenAI()

# Load Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load logo
logo = Image.open("mjestatesicon.png")

# Email handling
def send_email(name, email, phone):
    broker_email = os.getenv("BROKER_EMAIL")
    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg['Subject'] = "New MJ Estates Lead from AI Chatbot"
    msg['From'] = email_sender
    msg['To'] = broker_email
    msg.set_content(f"New lead submitted:\n\nName: {name}\nEmail: {email}\nPhone: {phone or 'N/A'}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email failed:", e)
        return False

# Get dynamic system prompt from Supabase
def get_prompt(lang):
    result = supabase.table("prompts").select("*").eq("language", lang).single().execute()
    return result.data["prompt"]

# Language toggle
language_is_spanish = st.toggle("Language: English / Español")
language_code = "spanish" if language_is_spanish else "english"
system_prompt = get_prompt(language_code)

# UI labels per language
if language_is_spanish:
    title = "Asistente de IA de MJ Estates"
    intro = """
¡Bienvenido al equipo de IA de MJ Estates! Pregúntame sobre:
- Comprar o vender una propiedad
- Barrios locales (como Brickell, Homestead o Kendall)
- Opciones de financiamiento e inversión
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

# Render
st.markdown(f"""<small><a href="https://mjestates.com" target="_blank">{back_link}</a></small>""", unsafe_allow_html=True)
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

    st.markdown("""
<input id="blur-hack" style="position:absolute; top:-1000px; left:-1000px;" />
<script>
  setTimeout(() => {
    document.getElementById("blur-hack")?.focus();
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
  }, 300);
</script>
""", unsafe_allow_html=True)

if len(st.session_state.chat_history) >= 10:
    st.warning(limit_warning)
    st.stop()

st.markdown("---")
st.markdown(f"<small>{disclaimer}</small>", unsafe_allow_html=True)

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
