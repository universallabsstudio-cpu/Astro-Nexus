import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import uuid
import time
import random
import datetime
import pickle
import os

# --- 1. API SETUP & CONSTANTS ---
API_KEY = "AIzaSyA4c-et3rzJLdQrHmKeJbRps-ZTeRGTje0" # Tumhari key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-3-flash-preview')

SAVE_PATH = "nexus_memory.pkl"
COST_PER_ACTION = 5  # Har sawal ya scan ke 5 coins
AD_REWARD = 50       # Ad dekhne par 50 coins

# --- 2. DATA SAVING WITH WALLET ---
def save_data():
    """Saves chat sessions AND wallet to F: drive."""
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "wb") as f:
        pickle.dump({
            "sessions": st.session_state.chat_sessions,
            "current": st.session_state.current_session,
            "wallet": st.session_state.wallet
        }, f)

def load_data():
    """Loads chat sessions AND wallet from F: drive."""
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "rb") as f:
                data = pickle.load(f)
                return data.get("sessions"), data.get("current"), data.get("wallet", 50)
        except:
            return None, None, 50
    return None, None, 50

# --- 3. MOBILE-FIRST UI CONFIG ---
st.set_page_config(page_title="Astro-Nexus", page_icon="🌌", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { max-width: 500px; padding-top: 2rem; }
    .stChatInputContainer { padding-bottom: 20px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stExpander { border: 1px solid #30363d !important; border-radius: 10px !important; background-color: #161b22 !important; }
    .stButton>button { border-radius: 8px; text-align: left; }
    </style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE (SMART CHAT & WALLET) ---
if "wallet" not in st.session_state or "chat_sessions" not in st.session_state:
    loaded_sessions, loaded_current, loaded_wallet = load_data()
    
    st.session_state.wallet = loaded_wallet if loaded_wallet is not None else 50
    
    if loaded_sessions:
        st.session_state.chat_sessions = loaded_sessions
        st.session_state.current_session = loaded_current
    else:
        default_id = str(uuid.uuid4())
        st.session_state.chat_sessions = {
            default_id: {
                "title": "New Chat",
                "messages": [{"role": "assistant", "content": "Namaste! Main Astro-Nexus hoon. 🌌"}],
                "reading_data": "",
                "updated_at": time.time()
            }
        }
        st.session_state.current_session = default_id

def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {
        "title": "New Chat",
        "messages": [{"role": "assistant", "content": "Namaste! Main Astro-Nexus hoon. 🌌"}],
        "reading_data": "",
        "updated_at": time.time()
    }
    st.session_state.current_session = new_id
    save_data()

def switch_session(session_id):
    st.session_state.current_session = session_id
    st.session_state.chat_sessions[session_id]["updated_at"] = time.time()
    save_data()

active_chat = st.session_state.chat_sessions[st.session_state.current_session]

# --- 5. SIDEBAR (WALLET & ADS) ---
with st.sidebar:
    st.title("⚙️ Astro-Nexus")
    
    # 💰 WALLET & AD BUTTON
    st.metric(label="💰 Nexus Coins", value=st.session_state.wallet)
    if st.button("📺 Watch Ad (+50 Coins)", type="primary", use_container_width=True):
        with st.spinner("Ad chal raha hai... (Simulating 30s)"):
            time.sleep(2) # Fake ad delay
            st.session_state.wallet += AD_REWARD
            save_data()
            st.success(f"🎉 50 Coins Added! Balance: {st.session_state.wallet}")
            time.sleep(1)
            st.rerun()
            
    st.divider()
    user_language = st.selectbox("Bhasha", ["Hinglish", "Hindi", "English"])
    st.divider()
    
    if st.button("➕ New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()
        
    st.subheader("📜 Chat History")
    sorted_sessions = sorted(st.session_state.chat_sessions.items(), key=lambda x: x[1]['updated_at'], reverse=True)
    
    for sid, s_data in sorted_sessions:
        icon = "🟢" if sid == st.session_state.current_session else "💬"
        if st.button(f"{icon} {s_data['title']}", key=f"btn_{sid}", use_container_width=True):
            switch_session(sid)
            st.rerun()
            
    st.divider()
    if st.button("🗑️ Clear All History", use_container_width=True):
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
        st.session_state.chat_sessions = {}
        st.session_state.wallet = 50 # Reset wallet on clear history too
        create_new_chat()
        st.rerun()

# --- 6. LOGIC FUNCTION ---
def get_ai_response(prompt_content):
    response = model.generate_content(prompt_content)
    return response.text.replace('```json', '').replace('```', '').strip()

# --- 7. MAIN SCREEN DISPLAY ---
st.title("🌌 Astro-Nexus")

if len(active_chat["messages"]) == 1:
    daily_tips = ["Aaj kuch naya seekhne ka din hai!", "Apne health par dhyan dein.", "Patience rakhein, sitare aapke haq mein hain."]
    st.success(f"🌟 **Aaj Ka Tip:** {random.choice(daily_tips)}")

    tab_palm, tab_kundli = st.tabs(["✋ Palmistry", "📜 Kundli Form"])

    with tab_palm:
        st.info("Niche chat bar mein **'+'** se photo upload karein.")

    with tab_kundli:
        with st.form("kundli_form"):
            col1, col2 = st.columns(2)
            with col1: dob = st.date_input("Date of Birth")
            with col2: tob = st.time_input("Time of Birth")
            pob = st.text_input("Birth Place")
            
            if st.form_submit_button("Generate Kundli 🚀"):
                if st.session_state.wallet >= COST_PER_ACTION:
                    with st.spinner("Analysis ho raha hai..."):
                        k_prompt = f"Analyze DOB {dob}, Time {tob}, Place {pob}. Lang: {user_language}. JSON ONLY. Format: {{ 'Career': {{'Short': '..', 'Detailed': '..'}}, 'Health': {{'Short': '..', 'Detailed': '..'}}, 'Relationships': {{'Short': '..', 'Detailed': '..'}}, 'SpecialYoga': {{'Short': '..', 'Detailed': '..'}} }}"
                        res = get_ai_response(k_prompt)
                        
                        st.session_state.wallet -= COST_PER_ACTION # Deduct Coins
                        active_chat["reading_data"] = res
                        active_chat["title"] = f"📜 Kundli: {pob}"
                        active_chat["updated_at"] = time.time()
                        active_chat["messages"].append({"role": "assistant", "content": f"Kundli generated for {pob}. (Cost: 5 Coins)"})
                        save_data() 
                        st.rerun()
                else:
                    st.error("⚠️ Balance low! Sidebar se ek ad dekh kar coins badhayein.")

if active_chat["reading_data"]:
    st.markdown("### 🔮 Aapki Reading")
    try:
        data = json.loads(active_chat["reading_data"])
        for key, val in data.items():
            with st.expander(f"✨ {key.upper()} (Free View)"):
                st.info(f"🟢 {val['Short']}")
                st.success(f"🔓 Premium: {val['Detailed']}")
    except:
        pass

for msg in active_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- 8. UNIFIED INPUT (Bottom Fixed) ---
user_input = st.chat_input("Upay puchein ya Photo attach karein...", accept_file=True, file_type=["jpg", "png", "jpeg"])

if user_input:
    if st.session_state.wallet >= COST_PER_ACTION:
        # A. Image Uploaded
        if user_input.files:
            img = Image.open(user_input.files[0])
            with st.chat_message("user"): st.image(img, width=150)
            with st.spinner("AI scan kar raha hai..."):
                p_prompt = [img, f"Analyze palm strictly. Lang: {user_language}. JSON ONLY. Format: {{ 'Career': {{'Short': '..', 'Detailed': '..'}}, 'Health': {{'Short': '..', 'Detailed': '..'}}, 'Relationships': {{'Short': '..', 'Detailed': '..'}}, 'Special': {{'Short': '..', 'Detailed': '..'}} }}"]
                res = get_ai_response(p_prompt)
                
                st.session_state.wallet -= COST_PER_ACTION # Deduct Coins
                active_chat["reading_data"] = res
                if active_chat["title"] == "New Chat":
                    active_chat["title"] = "✋ Palm Reading"
                active_chat["updated_at"] = time.time()
                active_chat["messages"].append({"role": "user", "content": "[Palm Image Uploaded]"})
                active_chat["messages"].append({"role": "assistant", "content": f"Palm scan complete. Cards niche dekhein. (Cost: 5 Coins)"})
                save_data()
                st.rerun()

        # B. Text Sent
        if user_input.text:
            active_chat["messages"].append({"role": "user", "content": user_input.text})
            if active_chat["title"] == "New Chat":
                active_chat["title"] = user_input.text[:15] + "..."
                
            active_chat["updated_at"] = time.time()
            
            with st.chat_message("user"): st.write(user_input.text)
            
            with st.chat_message("assistant"):
                with st.spinner("Sitaron ki chaal aur waqt ki ganana kar raha hoon... ✨"):
                    # Aaj ki date fetch karo
                    aaj_ka_din = datetime.datetime.now().strftime("%A, %d %B %Y")
                    
                    # NAYA ADVANCED ASTROTALK PROMPT
                    chat_prompt = f"""
                    You are Astro-Nexus, a highly premium, expert astrologer similar to the top astrologers on AstroTalk.
                    Your tone should be empathetic, mystical, yet highly logical and practical.
                    
                    CURRENT REAL-TIME BASELINE DATE: {aaj_ka_din}.
                    
                    CRITICAL TIME RULE: The baseline date is today. IF the user asks about "tomorrow", "yesterday", or a specific future/past day, calculate the correct day logically based on the baseline date before answering. Do NOT force today's answer if they ask for tomorrow.
                    
                    User's Language: {user_language}. 
                    User's Astrological Data (if any): {active_chat['reading_data']}. 
                    User's Question: {user_input.text}. 
                    
                    Give a detailed, professional astrological prediction and remedy based on Vedic astrology principles.
                    """
                    
                    response = model.generate_content(chat_prompt)
                    ans = response.text
                    st.write(ans)
                    
                    st.session_state.wallet -= COST_PER_ACTION # Deduct Coins
                    active_chat["messages"].append({"role": "assistant", "content": ans})
                    save_data() 
                    st.rerun()
    else:
        st.error("⚠️ Balance low! Sidebar se ek ad dekh kar coins badhayein.")