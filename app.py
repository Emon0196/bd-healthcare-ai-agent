import streamlit as st
import os
from config import APP_TITLE, APP_ICON
from modules.symptom_analyzer import analyze_symptoms
from modules.care_referral import get_referral

# Page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered"
)

# Visual design styling for the Streamlit application (Clinical Dark/Slate UI)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Reset & Body styling */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

.stApp {
    background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #070a13 100%) !important;
}

/* Scrollbar Customization */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.01);
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 198, 255, 0.3);
}

/* Styled Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    background-color: rgba(255, 255, 255, 0.02);
    border-bottom: 2px solid rgba(255, 255, 255, 0.05);
    padding: 6px 12px 0 12px;
    border-radius: 12px 12px 0 0;
}

.stTabs [data-baseweb="tab"] {
    height: 45px;
    white-space: pre-wrap;
    background-color: transparent;
    border: none;
    color: #94a3b8;
    font-weight: 600;
    font-size: 14.5px;
    transition: all 0.2s ease;
    padding: 0 16px;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #00c6ff;
}

.stTabs [aria-selected="true"] {
    color: #00c6ff !important;
    border-bottom: 2.5px solid #00c6ff !important;
}

/* Custom Header Typography */
.gradient-title-container {
    text-align: center;
    margin-top: -30px;
    padding-bottom: 20px;
}

.title-logo {
    font-size: 3.5rem;
    margin-bottom: 5px;
    filter: drop-shadow(0 0 15px rgba(0, 198, 255, 0.3));
    display: inline-block;
    animation: float-logo 3s ease-in-out infinite;
}

@keyframes float-logo {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}

.gradient-title {
    font-family: 'Outfit', sans-serif !important;
    background: linear-gradient(135deg, #58a6ff 0%, #00c6ff 50%, #0072ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.5px;
    text-shadow: 0 10px 30px rgba(0, 198, 255, 0.05);
}

.sub-title {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 5px;
    font-weight: 400;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}

/* Styled Alert Bar */
.stAlert {
    border-radius: 14px !important;
    border: 1px solid rgba(0, 198, 255, 0.15) !important;
    background: rgba(0, 198, 255, 0.04) !important;
    color: #94a3b8 !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
    padding: 16px !important;
}

/* Glassmorphism General Card */
.glass-card {
    background: rgba(22, 27, 34, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 22px;
    margin: 15px 0;
    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    border-color: rgba(0, 198, 255, 0.25);
    box-shadow: 0 15px 45px 0 rgba(0, 198, 255, 0.08);
}

/* Example Option Card Buttons & Form Buttons */
div.stButton > button {
    background: rgba(22, 27, 34, 0.8) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    width: 100% !important;
    text-align: left !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, rgba(0, 198, 255, 0.08) 0%, rgba(0, 114, 255, 0.08) 100%) !important;
    border-color: rgba(0, 198, 255, 0.4) !important;
    color: #00c6ff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 198, 255, 0.15) !important;
}

/* Form Action Buttons style override (center aligned and bold) */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    text-align: center !important;
    letter-spacing: 0.5px !important;
}

[data-testid="stFormSubmitButton"] button:hover {
    box-shadow: 0 8px 25px rgba(0, 198, 255, 0.45) !important;
    transform: translateY(-2px) !important;
}

/* Native Chat Messages styles override */
[data-testid="stChatMessage"] {
    background-color: rgba(22, 27, 34, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15) !important;
    padding: 20px !important;
    margin-bottom: 18px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatMessage"]:hover {
    border-color: rgba(0, 198, 255, 0.15) !important;
    background-color: rgba(22, 27, 34, 0.65) !important;
}

[data-testid="chatAvatarIcon-user"] {
    background-color: #0072ff !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background-color: #00c6ff !important;
}

/* Chat Input custom styles */
div[data-testid="stChatInput"] {
    background-color: rgba(13, 17, 23, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 24px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    transition: border-color 0.25s ease !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0, 198, 255, 0.5) !important;
}

/* Urgency Status Tags */
.urgency-badge {
    padding: 6px 14px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin: 8px 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.badge-low {
    background: rgba(46, 204, 113, 0.1);
    color: #2ecc71;
    border: 1px solid rgba(46, 204, 113, 0.25);
}
.badge-medium {
    background: rgba(241, 196, 15, 0.1);
    color: #f1c40f;
    border: 1px solid rgba(241, 196, 15, 0.25);
}
.badge-high {
    background: rgba(230, 126, 34, 0.1);
    color: #e67e22;
    border: 1px solid rgba(230, 126, 34, 0.25);
}
.badge-emergency {
    background: rgba(231, 76, 60, 0.15);
    color: #e74c3c;
    border: 1px solid rgba(231, 76, 60, 0.35);
    animation: glow-pulse 1.8s infinite alternate;
}

@keyframes glow-pulse {
    0% {
        box-shadow: 0 0 4px rgba(231, 76, 60, 0.2);
        border-color: rgba(231, 76, 60, 0.4);
    }
    100% {
        box-shadow: 0 0 16px rgba(231, 76, 60, 0.6);
        border-color: rgba(231, 76, 60, 0.8);
    }
}

/* Custom referral display cards */
.referral-box {
    background: rgba(0, 198, 255, 0.02) !important;
    border: 1px solid rgba(0, 198, 255, 0.12) !important;
    border-radius: 14px !important;
    padding: 18px !important;
    margin-top: 10px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

.ref-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    color: #00c6ff;
    font-size: 15px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(0, 198, 255, 0.08);
    padding-bottom: 8px;
    font-family: 'Outfit', sans-serif !important;
}

.ref-row {
    font-size: 13.5px;
    margin-bottom: 8px;
    color: #cbd5e1;
    line-height: 1.5;
}

.ref-row strong {
    color: #58a6ff;
}

/* Clinical Report Layout */
.report-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 10px;
    margin-bottom: 15px;
}

/* Sidebar Styling Override */
[data-testid="stSidebar"] {
    background-image: linear-gradient(180deg, #0a0e17 0%, #111827 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}

.sidebar-title {
    font-family: 'Outfit', sans-serif !important;
    color: white;
    font-weight: 700;
    margin-top: 5px;
    font-size: 1.4rem;
    letter-spacing: -0.3px;
}

/* Styled Hotline boxes */
.hotline-card {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}

.hotline-card:hover {
    background: rgba(0, 198, 255, 0.04);
    border-color: rgba(0, 198, 255, 0.2);
    transform: translateX(2px);
}

.hotline-icon {
    font-size: 20px;
    filter: drop-shadow(0 0 4px rgba(0, 198, 255, 0.2));
}

.hotline-details {
    display: flex;
    flex-direction: column;
}

.hotline-title {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.hotline-number {
    font-size: 15px;
    font-weight: 700;
    color: #e2e8f0;
}
</style>
"""

# Inject CSS overrides
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Urgency icons
URGENCY_COLORS = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🟠",
    "emergency": "🔴"
}

# Render Header Banner
st.markdown(
    f'<div class="gradient-title-container">'
    f'  <span class="title-logo">{APP_ICON}</span>'
    f'  <div class="gradient-title">{APP_TITLE}</div>'
    f'  <div class="sub-title">'
    f'    Empathetic, RAG-grounded health information assistant for Bangladesh'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True
)

st.info(
    "ℹ️ **Disclaimer:** This tool provides general educational health information only. "
    "It is NOT a medical diagnosis and does NOT replace consultation with a registered MBBS doctor. "
    "In emergencies, go directly to the nearest hospital or call 999.",
    icon="ℹ️"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "guided_report" not in st.session_state:
    st.session_state.guided_report = None

# Render a beautifully formatted custom HTML Care Referral box
def render_referral_box(urgency: str, lang: str):
    ref = get_referral(urgency, lang=lang)
    if urgency == "emergency":
        action = ref["action_bn"] if lang == "bn" else ref["action"]
        message = ref["message_bn"] if lang == "bn" else ref["message_en"]
        return f"""
        <div class="referral-box" style="border-color: rgba(231, 76, 60, 0.4) !important; background: rgba(231, 76, 60, 0.03) !important;">
            <div class="ref-header" style="color: #e74c3c !important; border-color: rgba(231, 76, 60, 0.15) !important;">
                <span>🚨</span> EMERGENCY ACTION REFERRAL / জরুরি নির্দেশাবলী
            </div>
            <div class="ref-row" style="font-weight: 700; color: #f85149;">{action}</div>
            <div class="ref-row" style="color: #cbd5e1;">{message}</div>
        </div>
        """
        
    title = "RECOMMENDED FACILITY REFERRAL" if lang == "en" else "সুপারিশকৃত স্বাস্থ্য কেন্দ্র রেফারেল"
    lbl_facility = "Facility" if lang == "en" else "স্বাস্থ্য কেন্দ্র"
    lbl_when = "When to use" if lang == "en" else "কখন যাবেন"
    lbl_cost = "Expected Cost" if lang == "en" else "আনুমানিক খরচ"
    lbl_hotline = "Health Helpline" if lang == "en" else "হেলথ হেল্পলাইন"
    
    return f"""
    <div class="referral-box">
        <div class="ref-header">
            <span>🏥</span> {title}
        </div>
        <div class="ref-row"><strong>{lbl_facility}:</strong> {ref['action']}</div>
        <div class="ref-row"><strong>{lbl_when}:</strong> {ref.get('when_to_go', 'N/A')}</div>
        <div class="ref-row"><strong>{lbl_cost}:</strong> {ref.get('cost', 'N/A')}</div>
        <div class="ref-row"><strong>{lbl_hotline}:</strong> {ref.get('dghs_hotline', '16401')}</div>
    </div>
    """

# Create Tabs for Conversational Chat and Guided Wizard
tab_chat, tab_wizard = st.tabs(["💬 Conversational Chat Assistant", "📋 Guided Symptom Checker Wizard"])

# =========================================================================
# TAB 1: CONVERSATIONAL CHAT
# =========================================================================
with tab_chat:
    # Display welcome message and example buttons when starting
    if not st.session_state.messages:
        st.markdown(
            '<div class="glass-card" style="margin-top: 15px;">'
            '  <h3 style="margin-top:0; color:#00c6ff; font-family:\'Outfit\', sans-serif;">AI Health Chat / কথোপকথন</h3>'
            '  <p style="color:#94a3b8; font-size:14px; line-height:1.6;">'
            '    Describe symptoms in your own words below. You can write in English or বাংলা. The AI will cross-reference regional manuals and answer you with guidance.'
            '  </p>'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown("<p style='font-size:13.5px; font-weight:600; color:#94a3b8; margin-bottom:12px;'>👉 Click one of these examples to start immediately / উদাহরণ:</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🌡️ I have fever and headache for 2 days", key="ex1"):
                st.session_state.temp_input = "I have fever and headache for 2 days"
                st.rerun()
            if st.button(" আমার প্রচন্ড জ্বর ও শরীর ব্যথা", key="ex2"):
                st.session_state.temp_input = "আমার প্রচন্ড জ্বর ও শরীর ব্যথা"
                st.rerun()
                
        with col2:
            if st.button("🫁 Cough and breathing difficulty", key="ex3"):
                st.session_state.temp_input = "Cough and breathing difficulty"
                st.rerun()
            if st.button("💊 Which medicine for stomach pain?", key="ex4"):
                st.session_state.temp_input = "Which medicine for stomach pain?"
                st.rerun()

    # Pre-fill chat prompt from examples if clicked
    prompt_val = ""
    if "temp_input" in st.session_state:
        prompt_val = st.session_state.temp_input
        del st.session_state.temp_input

    # Display existing chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("urgency"):
                urgency = msg["urgency"]
                lang = msg.get("language", "en")
                badge_class = f"badge-{urgency}"
                urgency_text = f"Urgency: {urgency.upper()}" if lang == "en" else f"জরুরি অবস্থা: {urgency.upper()}"
                st.markdown(
                    f'<span class="urgency-badge {badge_class}">'
                    f'  {URGENCY_COLORS.get(urgency, "⚪")} {urgency_text}'
                    f'</span>',
                    unsafe_allow_html=True
                )
                # Render premium referral HTML box
                st.markdown(render_referral_box(urgency, lang), unsafe_allow_html=True)

    # Chat input handle
    if prompt := st.chat_input("Describe your symptoms... / আপনার উপসর্গ বলুন...") or prompt_val:
        actual_prompt = prompt if prompt else prompt_val

        # Display user message
        st.session_state.messages.append({"role": "user", "content": actual_prompt})
        with st.chat_message("user"):
            st.markdown(actual_prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing symptoms and consulting health manuals..."):
                result = analyze_symptoms(
                    symptoms=actual_prompt,
                    chat_history=st.session_state.chat_history
                )

            st.markdown(result["response"])
            urgency = result["urgency"]
            lang = result["language"]
            
            badge_class = f"badge-{urgency}"
            urgency_text = f"Urgency: {urgency.upper()}" if lang == "en" else f"জরুরি অবস্থা: {urgency.upper()}"
            st.markdown(
                f'<span class="urgency-badge {badge_class}">'
                f'  {URGENCY_COLORS.get(urgency, "⚪")} {urgency_text}'
                f'</span>',
                unsafe_allow_html=True
            )

            # Render premium referral HTML box
            st.markdown(render_referral_box(urgency, lang), unsafe_allow_html=True)

        # Save to session
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "urgency": urgency,
            "language": lang
        })

        # Update LangChain chat history (last 5 exchanges)
        from langchain_core.messages import HumanMessage, AIMessage
        st.session_state.chat_history.append(HumanMessage(content=actual_prompt))
        st.session_state.chat_history.append(AIMessage(content=result["response"]))
        if len(st.session_state.chat_history) > 10:
            st.session_state.chat_history = st.session_state.chat_history[-10:]

# =========================================================================
# TAB 2: GUIDED SYMPTOM CHECKER WIZARD
# =========================================================================
with tab_wizard:
    st.markdown(
        '<div style="margin-bottom:15px;">'
        '  <h3 style="color:#00c6ff; font-family:\'Outfit\', sans-serif; margin-top:0;">Triage Wizard / লক্ষণ নির্ণয় নির্দেশিকা</h3>'
        '  <p style="color:#94a3b8; font-size:14px;">Select symptoms and parameters to generate a structured medical advice report.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # Symptom checker Form
    with st.form(key="symptom_checker_form"):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            ui_lang = st.radio("Output Language / আউটপুট ভাষা", ["English", "বাংলা"], horizontal=True)
            
            # Diagnostic lists
            symptoms_list_en = [
                "Fever (জ্বর)", "Headache (মাথাব্যথা)", "Body/Joint Ache (শরীর/পেশী ব্যথা)", 
                "Cough (কাশি)", "Sore Throat (গলা ব্যথা)", "Diarrhea (পাতলা পায়খানা)", 
                "Vomiting/Nausea (বমি বমি ভাব)", "Skin Rash (চামড়ায় লাল দাগ)", 
                "Yellow skin/eyes (চোখ/ত্বক হলুদ হওয়া)", "Extreme fatigue (চরম দুর্বলতা)", 
                "Runny nose (সর্দি)"
            ]
            
            selected_sympts = st.multiselect(
                "Select Symptoms / লক্ষণসমূহ সিলেক্ট করুন",
                options=symptoms_list_en,
                help="Choose all symptoms currently felt / অনুভব করছেন এমন লক্ষণগুলো সিলেক্ট করুন"
            )

        with col_form2:
            duration = st.selectbox(
                "Duration of Symptoms / লক্ষণের সময়সীমা",
                ["Less than 24 hours (২৪ ঘণ্টার কম)", "1-2 Days (১-২ দিন)", "3-5 Days (৩-৫ দিন)", "6-10 Days (৬-১০ দিন)", "More than 10 days (১০ দিনের বেশি)"]
            )
            
            division = st.selectbox(
                "Your Division / বর্তমান বিভাগ (Bangladesh)",
                ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barisal", "Rangpur", "Mymensingh"]
            )
            
        # Warning signs checklist
        st.markdown("<p style='font-size:13.5px; font-weight:600; color:#e74c3c; margin-top:10px; margin-bottom:5px;'>🚨 Severe Warning Signs / গুরুতর বিপদের লক্ষণসমূহ (Check all that apply):</p>", unsafe_allow_html=True)
        
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            w_chest = st.checkbox("Chest Pain or Tightness / বুকে ব্যথা বা চাপ অনুভব")
            w_breath = st.checkbox("Severe Shortness of breath / তীব্র শ্বাসকষ্ট")
            w_bleed = st.checkbox("Bleeding from nose/gums/stool / নাক, মুখ বা মলদ্বারে রক্তক্ষরণ")
        with col_w2:
            w_unconscious = st.checkbox("Loss of consciousness or confusion / অজ্ঞান হওয়া বা বিভ্রান্তি")
            w_convulsion = st.checkbox("High fever with convulsions / তীব্র জ্বরের সাথে খিঁচুনি বা কাঁপুনি")
            w_dehydrate = st.checkbox("Severe dehydration (sunken eyes, no urine) / চরম পানিশূন্যতা")

        extra_details = st.text_area(
            "Additional context or notes / অতিরিক্ত তথ্য (Optional)",
            placeholder="Type any other details (e.g., travel history, pre-existing diseases)..."
        )
        
        submit_report = st.form_submit_button("Generate Care Report / রিপোর্ট তৈরি করুন")

    if submit_report:
        if not selected_sympts and not (w_chest or w_breath or w_bleed or w_unconscious or w_convulsion or w_dehydrate):
            st.warning("⚠️ Please select at least one symptom or warning sign / অনুগ্রহ করে অন্তত একটি লক্ষণ সিলেক্ট করুন।")
        else:
            with st.spinner("Analyzing parameters and generating clinical report..."):
                lang_code = "bn" if ui_lang == "বাংলা" else "en"
                
                # Synthesizing clinical text query
                warning_items = []
                if w_chest: warning_items.append("Chest Pain" if lang_code == "en" else "বুকে ব্যথা")
                if w_breath: warning_items.append("Shortness of breath" if lang_code == "en" else "শ্বাসকষ্ট")
                if w_bleed: warning_items.append("Bleeding" if lang_code == "en" else "রক্তপাত")
                if w_unconscious: warning_items.append("Confusion/Unconsciousness" if lang_code == "en" else "অজ্ঞান হওয়া")
                if w_convulsion: warning_items.append("Convulsions" if lang_code == "en" else "খিঁচুনি")
                if w_dehydrate: warning_items.append("Severe Dehydration" if lang_code == "en" else "তীব্র পানিশূন্যতা")
                
                clean_sympts = [s.split(" (")[0] for s in selected_sympts]
                
                query_text = f"Patient has symptoms: {', '.join(clean_sympts)}."
                query_text += f" Symptom duration is: {duration.split(' (')[0]}."
                query_text += f" Patient lives in {division} division."
                
                if warning_items:
                    query_text += f" Critical warning signs present: {', '.join(warning_items)}."
                if extra_details:
                    query_text += f" Additional context: {extra_details}."
                
                # Call analyzer
                st.session_state.guided_report = analyze_symptoms(
                    symptoms=query_text,
                    chat_history=[],
                    use_rag=True
                )
                st.session_state.guided_report["lang_code"] = lang_code

    # Render generated report card
    if st.session_state.guided_report:
        report = st.session_state.guided_report
        r_lang = report["lang_code"]
        r_urgency = report["urgency"]
        
        st.markdown('<div class="glass-card" style="border-left: 5px solid #00c6ff;">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="report-title">'
            f'  🏥 Clinical Assessment Report / স্বাস্থ্য মূল্যায়ন রিপোর্ট'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Display Urgency Level
        badge_class = f"badge-{r_urgency}"
        urgency_lbl = f"Urgency Classification: {r_urgency.upper()}" if r_lang == "en" else f"জরুরি অবস্থা: {r_urgency.upper()}"
        st.markdown(
            f'<span class="urgency-badge {badge_class}" style="font-size:12.5px; padding: 8px 18px; margin-bottom: 20px;">'
            f'  {URGENCY_COLORS.get(r_urgency, "⚪")} {urgency_lbl}'
            f'</span>',
            unsafe_allow_html=True
        )
        
        # Care recommendation box
        st.markdown(render_referral_box(r_urgency, r_lang), unsafe_allow_html=True)
        st.write("")
        
        # Educational Guidance section
        sec_title = "📚 Educational Information & Grounded Context" if r_lang == "en" else "📚 সাধারণ স্বাস্থ্য শিক্ষা ও তথ্য"
        st.markdown(f"<h4 style='color:#58a6ff; font-family:\'Outfit\', sans-serif;'>{sec_title}</h4>", unsafe_allow_html=True)
        st.markdown(report["response"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Reset Wizard / রিপোর্ট পরিষ্কার করুন"):
            st.session_state.guided_report = None
            st.rerun()

# =========================================================================
# SIDEBAR INTERACTIVE HOTLINES
# =========================================================================
with st.sidebar:
    st.markdown(
        f'<div style="text-align: center; margin-bottom: 20px; margin-top: 15px;">'
        f'  <span style="font-size: 3rem; filter: drop-shadow(0 0 10px rgba(0, 198, 255, 0.25));">🏥</span>'
        f'  <div class="sidebar-title">BD Health Agent</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.subheader("About")
    st.write(
        "This agent analyzes user-described symptoms, cross-references regional "
        "medical databases, and provides care tier guidance. It supports both Bengali and "
        "English query inputs."
    )
    
    st.divider()
    
    st.subheader("Emergency Hotlines 🇧🇩")
    
    # Styled custom hotlines cards
    st.markdown(
        '<div class="hotline-card">'
        '  <span class="hotline-icon">🚨</span>'
        '  <div class="hotline-details">'
        '    <span class="hotline-title">National Emergency</span>'
        '    <span class="hotline-number">999</span>'
        '  </div>'
        '</div>'
        '<div class="hotline-card">'
        '  <span class="hotline-icon">🏥</span>'
        '  <div class="hotline-details">'
        '    <span class="hotline-title">DGHS Health Line</span>'
        '    <span class="hotline-number">16401</span>'
        '  </div>'
        '</div>'
        '<div class="hotline-card">'
        '  <span class="hotline-icon">🦠</span>'
        '  <div class="hotline-details">'
        '    <span class="hotline-title">IEDCR Outbreak info</span>'
        '    <span class="hotline-number">10655</span>'
        '  </div>'
        '</div>'
        '<div class="hotline-card">'
        '  <span class="hotline-icon">🚑</span>'
        '  <div class="hotline-details">'
        '    <span class="hotline-title">Ambulance Line</span>'
        '    <span class="hotline-number">199</span>'
        '  </div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.divider()
    
    if st.button("Clear Conversation / চ্যাট পরিষ্কার করুন"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.guided_report = None
        st.rerun()
