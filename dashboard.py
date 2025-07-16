import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# ✅ Required first
st.set_page_config(page_title="MJ Estates Prompt Editor", layout="centered")

# 🔐 Load env + connect Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ✅ Logout function
def logout():
    st.session_state.clear()
    st.rerun()


# 🔐 Show login form if not authenticated
if "user" not in st.session_state:
    st.title("🔐 MJ Estates Admin Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth_response.session:
                st.session_state["user"] = auth_response.user
                st.success(f"✅ Welcome {auth_response.user.email}!")
                st.rerun()  # Hide login after success
            else:
                st.error("❌ Login failed. Please check your credentials.")
        except Exception as e:
            st.error(f"Login error: {e}")

    st.stop()  # Prevent rest of app from loading

# ✅ Show logout button once logged in
if "user" in st.session_state:
    st.sidebar.markdown(f"👤 {st.session_state['user'].email}")
    st.sidebar.button("Logout", on_click=logout)

# ✅ Main Dashboard UI
st.title("MJ Estates AI Prompt Dashboard")

# 🚀 Load English prompt
try:
    result_en = supabase.table("prompts").select("*").eq("language", "english").single().execute()
    english_prompt = result_en.data["prompt"]
except Exception as e:
    st.error(f"Could not load English prompt: {e}")
    st.stop()

# ✏️ Edit English Prompt
st.header("English Prompt")
new_prompt_en = st.text_area("Edit English Prompt", value=english_prompt, height=200)

# 🌍 Auto-translate to Spanish
try:
    translated_prompt = GoogleTranslator(source='en', target='es').translate(new_prompt_en)
except Exception as e:
    translated_prompt = ""
    st.warning(f"Translation failed: {e}")

# 🪞 Show auto-translated Spanish version
st.header("🌐 Translated Spanish Prompt (Auto)")
st.text_area("Auto-translated", value=translated_prompt, height=200, disabled=True)

# 💾 Save both prompts
if st.button("💾 Save Prompts"):
    try:
        supabase.table("prompts").update({"prompt": new_prompt_en}).eq("language", "english").execute()
        supabase.table("prompts").update({"prompt": translated_prompt}).eq("language", "spanish").execute()
        st.success("✅ Prompts saved successfully!")
    except Exception as e:
        st.error(f"❌ Failed to save prompts: {e}")