import streamlit as st
import httpx
import time

st.set_page_config(page_title="DeenAI", page_icon="🌙", layout="centered")

st.title("🕌 DeenAI")
st.markdown("**Quran aur Sahih Hadith** ke mutabiq sawal poochho")

# ===================== NEW GROQ API KEY =====================
GROQ_API_KEY = "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"

# ===================== SESSION STATE =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "free_chats_used" not in st.session_state:
    st.session_state.free_chats_used = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===================== LOGIN / SIGNUP =====================
if not st.session_state.logged_in:
    st.subheader("Login / Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()

    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Create Account"):
            st.session_state.logged_in = True
            st.success("Account created successfully!")
            st.rerun()

    st.info("Free users can ask **3 questions** only. Login for unlimited access.")

# ===================== IMPROVED GROQ API FUNCTION =====================
def get_deenai_response(user_message):
    SYSTEM_PROMPT = """You are DeenAI, a humble Islamic assistant.
Answer strictly from Quran and Sahih Hadith.
Give clear point-wise answers with emojis.
Include references when possible.
Use simple Roman Urdu / Hinglish.
End with: Wallahu A'lam"""

    for attempt in range(3):  # 3 attempts
        try:
            with httpx.Client(timeout=60) as client:
                r = client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.6,
                        "max_tokens": 1200
                    }
                )
                
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                elif r.status_code == 429:
                    time.sleep(2)  # Rate limit hit, wait
                else:
                    time.sleep(1)
        except:
            time.sleep(1)
    
    return "Maaf kijiye, abhi thodi technical problem aa rahi hai. Thodi der baad try kijiye.\n\nWallahu A'lam"

# ===================== MAIN CHAT =====================
if st.session_state.logged_in or st.session_state.free_chats_used < 3:

    user_input = st.text_input("Apna sawal yahan likho:")

    if user_input:
        if not st.session_state.logged_in:
            st.session_state.free_chats_used += 1

        with st.spinner("Jawab taiyar ho raha hai..."):
            response = get_deenai_response(user_input)

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("DeenAI", response))

    for role, msg in st.session_state.chat_history:
        if role == "You":
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)
else:
    st.warning("Aapke free 3 chats khatam ho gaye hain. Please Login/Signup for unlimited access.")
    if st.button("Login / Signup"):
        st.session_state.logged_in = False
        st.rerun()