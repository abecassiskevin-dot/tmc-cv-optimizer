#!/usr/bin/env python3
"""
TMC CV Optimizer — VERSION 2.0 PRO (Streamlit Cloud Safe) + TWO-STEP MATCHING
Interface Streamlit premium pour générer des CVs TMC optimisés
"""

import streamlit as st
from pathlib import Path
import base64
import tempfile
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import extra_streamlit_components as stx

# Charger les variables d'environnement depuis .env
load_dotenv()

# ==========================================
# ⚙️ CONFIG PAGE
# ==========================================
st.set_page_config(
    page_title="CV Optimizer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🎨 TIMELINE FUNCTION
# ==========================================
def horizontal_progress_timeline(current_step: int = 1, total_steps: int = 5, step_labels: list = None) -> str:
    """
    Génère une timeline horizontale avec des étapes dynamiques.
    current_step: étape en cours (1-N)
    total_steps: nombre total d'étapes
    step_labels: liste des étapes avec icon et label
    """
    if step_labels is None:
        # Default: 5 steps comme V1
        step_labels = [
            {"num": 1, "icon": "🔍", "label": "Extraction"},
            {"num": 2, "icon": "🤖", "label": "Analysis"},
            {"num": 3, "icon": "✨", "label": "Enrichment"},
            {"num": 4, "icon": "🗺️", "label": "Structuring"},
            {"num": 5, "icon": "📝", "label": "Generation"},
        ]
    
    # Calculate progress percentage
    if total_steps > 1:
        progress_percent = ((current_step - 1) / (total_steps - 1)) * 100
    else:
        progress_percent = 100 if current_step >= total_steps else 0
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Arial', sans-serif;
                background: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .timeline {
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 90%;
                max-width: 1000px;
                min-width: 600px;
                margin: 0 auto;
                position: relative;
            }
            .step {
                display: flex;
                flex-direction: column;
                align-items: center;
                position: relative;
                z-index: 2;
                flex: 1;
            }
            .step-circle {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                background: #E5E7EB;
                border: 4px solid #E5E7EB;
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .step.active .step-circle {
                background: linear-gradient(135deg, #193E92 0%, #D97104 100%);
                border-color: #193E92;
                transform: scale(1.1);
                box-shadow: 0 4px 20px rgba(25, 62, 146, 0.4);
                animation: pulse 1.5s ease-in-out infinite;
            }
            .step.completed .step-circle {
                background: #193E92;
                border-color: #193E92;
                transform: scale(1);
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1.1); }
                50% { transform: scale(1.15); }
            }
            .step-label {
                margin-top: 12px;
                font-size: 13px;
                font-weight: 600;
                color: #9CA3AF;
                transition: color 0.3s ease;
                text-align: center;
            }
            .step.active .step-label {
                color: #193E92;
                font-size: 14px;
            }
            .step.completed .step-label {
                color: #193E92;
            }
            .connector {
                position: absolute;
                top: 30px;
                left: 0;
                right: 0;
                height: 4px;
                background: #E5E7EB;
                z-index: 1;
                margin: 0 30px;
            }
            .connector-progress {
                height: 100%;
                background: linear-gradient(90deg, #193E92 0%, #D97104 100%);
                transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                border-radius: 2px;
            }
        </style>
    </head>
    <body>
        <div class="timeline">
            <div class="connector">
                <div class="connector-progress" style="width: """ + str(progress_percent) + """%;"></div>
            </div>"""
    
    for step in step_labels:
        status = "completed" if step["num"] < current_step else ("active" if step["num"] == current_step else "")
        html_content += f"""
            <div class="step {status}">
                <div class="step-circle">{step["icon"]}</div>
                <div class="step-label">{step["label"]}</div>
            </div>"""
    
    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

def generation_progress_timeline(current_step: int = 1) -> str:
    """Timeline pour la génération de CV (3 étapes)"""
    step_labels = [
        {"num": 1, "icon": "✨", "label": "Enrichment"},
        {"num": 2, "icon": "🗂️", "label": "Structuring"},
        {"num": 3, "icon": "📝", "label": "Generation"},
    ]
    return horizontal_progress_timeline(current_step, 3, step_labels)

# ==========================================
# 🍪 COOKIE MANAGER
# ==========================================
cookie_manager = stx.CookieManager()

# ==========================================
# 🔐 AUTHENTICATION WITH COOKIES
# ==========================================

# Liste des utilisateurs autorisés
AUTHORIZED_USERS = [
    "Kevin Abecassis",
    "Aurélien Bertrand",
    "Julia Delpon",
    "Lucas Maurer",
    "Roberta Santiago"
]

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'login_time' not in st.session_state:
    st.session_state.login_time = None
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = None
if 'user_location' not in st.session_state:
    st.session_state.user_location = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'matching_done' not in st.session_state:
    st.session_state.matching_done = False
if 'matching_data' not in st.session_state:
    st.session_state.matching_data = None    

# Fonction pour vérifier et restaurer la session depuis les cookies
def restore_session_from_cookies():
    """Restaure la session depuis les cookies si valide"""
    try:
        cookies = cookie_manager.get_all()
        
        if cookies and 'tmc_session' in cookies:
            session_data = cookies['tmc_session']
            
            # Parser les données du cookie (format: "user_name|location|timestamp")
            parts = session_data.split('|')
            if len(parts) == 3:
                user_name, location, timestamp_str = parts
                login_timestamp = datetime.fromisoformat(timestamp_str)
                
                # Vérifier si la session est encore valide (4 heures)
                now = datetime.now()
                if (now - login_timestamp).total_seconds() < 4 * 3600:
                    # Session valide, restaurer
                    st.session_state.authenticated = True
                    st.session_state.user_name = user_name
                    st.session_state.user_location = location
                    st.session_state.login_time = login_timestamp
                    st.session_state.last_activity = now
                    print(f"✅ Session restaurée depuis cookie pour {user_name}")
                    return True
                else:
                    # Session expirée, supprimer le cookie
                    cookie_manager.delete('tmc_session')
                    print("⏰ Session cookie expirée")
    except Exception as e:
        print(f"⚠️ Erreur restauration cookie: {e}")
    
    return False

# Fonction pour sauvegarder la session dans un cookie
def save_session_to_cookie(user_name: str, location: str):
    """Sauvegarde la session dans un cookie (4 heures)"""
    try:
        now = datetime.now()
        # Format: "user_name|location|timestamp"
        session_data = f"{user_name}|{location}|{now.isoformat()}"
        
        # Cookie expire dans 4 heures
        expires_at = now + timedelta(hours=4)
        
        cookie_manager.set(
            'tmc_session',
            session_data,
            expires_at=expires_at,
            key='session_cookie'
        )
        print(f"✅ Session sauvegardée dans cookie pour {user_name}")
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde cookie: {e}")

# Vérifier si la session a expiré
def check_session_validity():
    """
    Vérifie si la session est toujours valide selon les règles :
    - Max 12 heures depuis le login
    - Expire à minuit
    - Max 4 heures d'inactivité
    """
    from datetime import datetime, timedelta
    
    if not st.session_state.authenticated:
        return False
    
    if st.session_state.login_time is None:
        return False
    
    now = datetime.now()
    login_time = st.session_state.login_time
    last_activity = st.session_state.last_activity or login_time
    
    # Règle 1 : Session max 12 heures
    if (now - login_time).total_seconds() > 12 * 3600:  # 12 heures
        print("⏰ Session expirée : plus de 12h")
        cookie_manager.delete('tmc_session')
        return False
    
    # Règle 2 : Session expire à minuit
    if now.date() > login_time.date():
        print("🌙 Session expirée : nouvelle journée")
        cookie_manager.delete('tmc_session')
        return False
    
    # Règle 3 : Max 1 heure d'inactivité
    if (now - last_activity).total_seconds() > 1 * 3600:  # 1 heure
        print("💤 Session expirée : 1h d'inactivité")
        cookie_manager.delete('tmc_session')
        return False
    
    # Session valide - mettre à jour l'activité
    st.session_state.last_activity = now
    return True

# Essayer de restaurer la session depuis les cookies
if not st.session_state.authenticated:
    restore_session_from_cookies()

# Vérifier la validité de la session
if st.session_state.authenticated and not check_session_validity():
    st.session_state.authenticated = False
    st.session_state.login_time = None
    st.session_state.last_activity = None
    st.rerun()

if not st.session_state.authenticated:
    from datetime import datetime
    
    # Show login screen
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    .login-title {
        color: #193E92;
        font-size: 2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-title">🔐 CV Optimizer</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #6B7280; margin-bottom: 30px;">Enter password to access</p>', unsafe_allow_html=True)
        
        password = st.text_input("Password", type="password", key="password_input")
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        # Location selector
        st.markdown('<p style="color: #193E92; font-weight: 600; margin-bottom: 5px;">📍 Your Location</p>', unsafe_allow_html=True)
        user_location = st.selectbox(
            "Select your location",
            ["Montreal", "Miami", "Mexico"],
            key="location_input",
            label_visibility="collapsed"
        )
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        # User Name (dropdown list)
        st.markdown('<p style="color: #193E92; font-weight: 600; margin-bottom: 5px;">👤 Your Name *</p>', unsafe_allow_html=True)
        user_name = st.selectbox(
            "Select your name",
            AUTHORIZED_USERS,
            key="user_name_input",
            label_visibility="collapsed"
        )
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        if st.button("Login", use_container_width=True):
            # Get password from environment variable
            correct_password = os.getenv('APP_PASSWORD', 'TMC2025')  # Default: TMC2025
            
            if password == correct_password:
                # Set session state
                st.session_state.authenticated = True
                st.session_state.login_time = datetime.now()
                st.session_state.last_activity = datetime.now()
                st.session_state.user_location = user_location
                st.session_state.user_name = user_name
                
                # Save to cookie
                save_session_to_cookie(user_name, user_location)
                
                # Track login in Airtable
                try:
                    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
                    if AIRTABLE_API_KEY:
                        import requests
                        import json
                        
                        BASE_ID = 'apptzRcN1NnoNLCJ7'
                        TABLE_ID = 'tbluQqI2WCCZFMg9W'
                        
                        name_parts = user_name.split(' ', 1)
                        first_name = name_parts[0] if len(name_parts) > 0 else 'Unknown'
                        last_name = name_parts[1] if len(name_parts) > 1 else ''
                        
                        record_data = {
                            "fields": {
                                "Timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                                "Event Type": "Login",
                                "First Name": first_name,
                                "Last Name": last_name,
                                "Location": user_location
                            }
                        }
                        
                        url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}'
                        headers = {
                            'Authorization': f'Bearer {AIRTABLE_API_KEY}',
                            'Content-Type': 'application/json'
                        }
                        
                        requests.post(url, headers=headers, data=json.dumps(record_data))
                except Exception as e:
                    print(f"Airtable error: {e}")
                
                st.success(f"✅ Welcome, {user_name}!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    
    st.stop()

# =====================================================
# 📦 IMPORTS & SETUP
# =====================================================
from tmc_cv_enricher import TMCUniversalEnricher as TMCCVEnricher

# =====================================================
# 🎨 STYLES & THEMING
# =====================================================

# TMC Brand Colors
PRIMARY_BLUE = "#193E92"  # Bleu TMC principal
SECONDARY_ORANGE = "#D97104"  # Orange TMC
BG_LIGHT = "#F9FAFB"
SUCCESS_GREEN = "#10B981"

def get_base64_image(path: Path) -> str:
    """Convertir image en base64 pour affichage inline"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_resource(show_spinner=False)
def load_backend():
    """Charge le backend enricher (cached)"""
    return TMCCVEnricher()

CUSTOM_CSS = f"""
<style>
  /* ===== GLOBAL ===== */
  .stApp {{ 
    background: linear-gradient(180deg, {BG_LIGHT} 0%, #ECEFF3 100%);
  }}
  * {{ 
    font-family: 'Arial', 'Open Sans', sans-serif;
  }}

  /* ===== CACHER HEADER STREAMLIT ===== */
  header {{
    visibility: hidden;
  }}
  #MainMenu {{
    visibility: hidden;
  }}
  footer {{
    visibility: hidden;
  }}

  /* ===== HERO SECTION ===== */
  .tmc-hero {{
    text-align: center;
    padding: 2rem 0;
  }}
  .tmc-hero h1 {{
    color: {PRIMARY_BLUE};
    font-weight: 800;
    font-size: 2.8rem;
    letter-spacing: 0.3px;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }}
  .tmc-subtitle {{
    color: #6B7280;
    font-size: 1.1rem;
    margin-top: 0.3rem;
    line-height: 1.6;
  }}

  /* ===== CARDS ===== */
  .tmc-card {{
    background: white;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 8px 24px rgba(17, 24, 39, 0.08);
    transition: all 0.3s ease;
  }}
  .tmc-card:hover {{
    box-shadow: 0 12px 32px rgba(17, 24, 39, 0.12);
  }}

  /* ===== BOUTONS ===== */
  .stButton>button {{
    background: linear-gradient(90deg, {PRIMARY_BLUE} 0%, {SECONDARY_ORANGE} 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.9rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px rgba(25, 62, 146, 0.25) !important;
  }}
  .stButton>button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(25, 62, 146, 0.35) !important;
  }}
  .stButton>button:disabled {{
    background: #D1D5DB !important;
    color: #9CA3AF !important;
    cursor: not-allowed !important;
    transform: none !important;
  }}
  
  /* ===== GENERATE BUTTON (inverted gradient: Orange → Blue) ===== */
  .generate-button-wrapper .stButton>button {{
    background: linear-gradient(90deg, {SECONDARY_ORANGE} 0%, {PRIMARY_BLUE} 100%) !important;
    box-shadow: 0 4px 14px rgba(217, 113, 4, 0.25) !important;
  }}
  .generate-button-wrapper .stButton>button:hover {{
    box-shadow: 0 8px 24px rgba(217, 113, 4, 0.35) !important;
  }}

  /* ===== DOWNLOAD BUTTON ===== */
  .stDownloadButton>button {{
    background: linear-gradient(90deg, #22c55e 0%, #047857 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.9rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    box-shadow: 0 4px 14px rgba(34, 197, 94, 0.3) !important;
    transition: all 0.3s ease !important;
    text-transform: none !important;
  }}
  .stDownloadButton>button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(34, 197, 94, 0.4) !important;
  }}

  /* ===== FILE UPLOADER ===== */
  [data-testid="stFileUploader"] {{
    border: 2px dashed {PRIMARY_BLUE}40;
    border-radius: 14px;
    background: white;
    padding: 1.5rem;
    transition: all 0.3s ease;
  }}
  [data-testid="stFileUploader"]:hover {{
    border-color: {SECONDARY_ORANGE};
    background: #FEF3E2;
  }}

  /* ===== PROGRESS BAR ===== */
  .stProgress > div > div {{
    background: linear-gradient(90deg, {PRIMARY_BLUE} 0%, {SECONDARY_ORANGE} 100%);
    height: 8px;
    border-radius: 10px;
  }}

  /* ===== STEPS ===== */
  .tmc-step {{
    color: #6B7280;
    font-size: 1rem;
    margin: 0.3rem 0;
    padding: 0.5rem;
    border-left: 3px solid {PRIMARY_BLUE}30;
    padding-left: 1rem;
    background: {BG_LIGHT};
    border-radius: 6px;
  }}
  .tmc-step.active {{
    border-left-color: {SECONDARY_ORANGE};
    background: #FEF3E2;
    font-weight: 600;
  }}
  
  /* Animation des points */
  .tmc-step.active::after {{
    content: '';
    animation: dots 1.5s steps(4, end) infinite;
  }}
  
  @keyframes dots {{
    0%, 20% {{ content: '.'; }}
    40% {{ content: '..'; }}
    60% {{ content: '...'; }}
    80%, 100% {{ content: ''; }}
  }}

  /* ===== SUCCESS BOX ===== */
  .success-box {{
    background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
    border-left: 5px solid #10b981;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1.5rem 0;
  }}
  .success-box h3 {{
    color: #065F46 !important;
    margin: 0 !important;
    font-size: 1.5rem !important;
  }}

  /* ===== METRICS ===== */
  [data-testid="stMetricValue"] {{
    color: {PRIMARY_BLUE};
    font-size: 2rem;
    font-weight: 800;
  }}
  [data-testid="stMetricLabel"] {{
    color: #6B7280;
    font-weight: 600;
    font-size: 0.95rem;
  }}

  /* ===== FOOTER ===== */
  .tmc-footer {{
    text-align: center;
    color: #6B7280;
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 2px solid #E5E7EB;
    font-size: 0.95rem;
  }}

  /* ===== RADIO BUTTONS CENTRÉS ===== */
  div[data-testid="stHorizontalBlock"] {{
    justify-content: center !important;
  }}
  
  .stRadio > div {{
    justify-content: center !important;
  }}
  
  .stRadio > label {{
    justify-content: center !important;
  }}

  /* ===== EXPANDER ===== */
  .streamlit-expanderHeader {{
    background: {BG_LIGHT};
    border-radius: 8px;
    font-weight: 600;
  }}

  /* ===== LOGO - Enlever fond blanc ===== */
  img {{
    background: transparent !important;
  }}
  [data-testid="stImage"] {{
    background: transparent !important;
  }}

  /* ===== ANIMATIONS ===== */
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}
  .processing {{
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =====================================================
# 🏠 HERO SECTION — Logo + Titre
# =====================================================
logo_big_path = Path("TMC big logo.png")
logo_mini_path = Path("TMC mini logo.png")

# Vérifier si le logo existe
if logo_big_path.exists():
    # Logo seul, centré au-dessus du titre avec filtre pour enlever le blanc
    col_center1, col_logo, col_center2 = st.columns([2, 2, 2])
    with col_logo:
        st.markdown(
            f"<div style='mix-blend-mode: multiply;'>"
            f"<img src='data:image/png;base64,{get_base64_image(logo_big_path)}' style='width: 100%; mix-blend-mode: multiply;' />"
            f"</div>",
            unsafe_allow_html=True
        )

# Hero section - Title (always displayed)
st.markdown(
    "<div class='tmc-hero'>"
    "<h1>CV Optimizer</h1>"
    "<div class='tmc-subtitle'>Generate a professional TMC CV perfectly aligned with your Job Description.<br>"
    "Designed for Business Managers and Recruiters</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# 📤 UPLOAD SECTION
# =====================================================
left, right = st.columns(2, gap="large")

with left:
    st.markdown("### 📄 Your Resume")
    st.caption("Accepted formats: PDF, DOCX, DOC, TXT")
    cv_file = st.file_uploader(
        "Drop your resume here or click to browse",
        type=["pdf", "docx", "doc", "txt"],
        key="cv_upload"
    )

with right:
    st.markdown("### 📋 Job Description")
    st.caption("Accepted formats: TXT, DOCX, DOC, PDF")
    jd_file = st.file_uploader(
        "Drop the job description here",
        type=["txt", "docx", "doc", "pdf"],
        key="jd_upload"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Instructions
if not cv_file or not jd_file:
    st.info("📌 **Instructions:** Upload your resume and job description to start the optimization.")

# =====================================================
# 🌍 SÉLECTEUR DE LANGUE
# =====================================================
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 15px;">
    <strong style="color: #193E92; font-size: 1.15rem;">🌍 Generated CV Language</strong>
</div>
""", unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([3, 2, 3])
with col_center:
    language_choice = st.radio(
        "Select language",
        options=["🇫🇷 French", "🇬🇧 English"],
        horizontal=True,
        label_visibility="collapsed",
        key="language_selector"
    )

# =====================================================
# 🔒 MODE ANONYMISÉ
# =====================================================
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 15px;">
    <strong style="color: #193E92; font-size: 1.15rem;">🔒 Anonymous Mode</strong>
</div>
""", unsafe_allow_html=True)

col_anon_left, col_anon_center, col_anon_right = st.columns([3, 2, 3])
with col_anon_center:
    mode_anonymise_choice = st.radio(
        "Select anonymous mode",
        options=["Disabled", "Enabled"],
        horizontal=True,
        label_visibility="collapsed",
        key="anonymous_mode_selector"
    )

# Determine template to use based on language AND anonymous mode
template_lang = "FR" if "🇫🇷" in language_choice else "EN"
mode_anonymise = (mode_anonymise_choice == "Enabled")

if mode_anonymise:
    template_file = f"TMC_NA_template_{template_lang}_Anonymise.docx"
else:
    template_file = f"TMC_NA_template_{template_lang}.docx"

# =====================================================
# 🎬 DYNAMIC BUTTON LOGIC
# =====================================================
can_run = cv_file is not None and jd_file is not None

st.markdown("<br>", unsafe_allow_html=True)

# Initialize button visibility states
if 'show_generate_button' not in st.session_state:
    st.session_state.show_generate_button = False

# Initialize button variables
analyze_button = False
generate_button = False

# Create a single placeholder for the button
button_placeholder = st.empty()

with button_placeholder.container():
    col_btn1, col_btn2, col_btn3 = st.columns([2, 3, 2])
    with col_btn2:
        # Show either Analyze or Generate button (or Download if results exist)
        if st.session_state.get('results'):
            # Show Download button (green) if CV is generated
            st.markdown('<div id="download-btn-wrapper">', unsafe_allow_html=True)
            st.markdown("""
            <style>
            #download-btn-wrapper button {
                background: linear-gradient(90deg, #22c55e 0%, #047857 100%) !important;
                color: white !important;
                border: none !important;
                box-shadow: 0 4px 14px rgba(34, 197, 94, 0.35) !important;
            }
            #download-btn-wrapper button:hover {
                box-shadow: 0 8px 24px rgba(34, 197, 94, 0.45) !important;
                transform: translateY(-1px);
            }
            </style>
            """, unsafe_allow_html=True)
            st.download_button(
                label="📥 Download TMC CV",
                data=st.session_state.results['cv_bytes'],
                file_name=st.session_state.results['nom_fichier'],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="download_tmc_cv_button"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        elif st.session_state.show_generate_button:
            # Show Generate button after analysis is done (with inverted gradient)
            st.markdown('<div id="generate-btn-wrapper">', unsafe_allow_html=True)
            st.markdown("""
            <style>
            #generate-btn-wrapper button {
                background: linear-gradient(90deg, #D97104 0%, #193E92 100%) !important;
                box-shadow: 0 4px 14px rgba(217, 113, 4, 0.25) !important;
            }
            #generate-btn-wrapper button:hover {
                box-shadow: 0 8px 24px rgba(217, 113, 4, 0.35) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            generate_button = st.button(
                "✨ Generate TMC CV",
                disabled=not can_run,
                use_container_width=True,
                key="generate_cv_button"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Show Analyze button initially
            analyze_button = st.button(
                "📊 Analyze Matching",
                disabled=not can_run,
                use_container_width=True,
                key="analyze_matching_button"
            )

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# 📍 GENERATION STEPPER PLACEHOLDER (BEFORE RESULTS)
# =====================================================
generation_stepper_container = st.empty()

# =====================================================
# 📊 DISPLAY ANALYSIS RESULTS (if matching done)
# =====================================================
# Only show Step 1 results if CV not yet generated (to avoid duplicates with final results section)
if st.session_state.matching_done and st.session_state.matching_data and not st.session_state.get('results'):
    matching_analysis = st.session_state.matching_data['matching_analysis']
    parsed_cv = st.session_state.matching_data['parsed_cv']
    
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display score metrics
    score = matching_analysis.get('score_matching', 0)
    nom = parsed_cv.get('nom_complet', 'Candidate')
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("📊 Matching Score", f"{score}/100")
    
    with col_m2:
        nom_display = nom if len(nom) < 20 else nom[:17] + "..."
        st.metric("👤 Candidate", nom_display)
    
    with col_m3:
        # Calculate years of experience
        experiences = parsed_cv.get('experiences', [])
        total_years = 0
        
        import re
        from datetime import datetime
        current_year = datetime.now().year
        
        for exp in experiences:
            periode = exp.get('periode', '')
            periode_clean = periode.replace('Present', str(current_year)).replace('Présent', str(current_year)).replace('present', str(current_year))
            years_found = re.findall(r'\b(\d{4})\b', periode_clean)
            
            if len(years_found) >= 2:
                try:
                    start = int(years_found[0])
                    end = int(years_found[-1])
                    if end >= start:
                        total_years += (end - start)
                except:
                    pass
            elif len(years_found) == 1:
                try:
                    start = int(years_found[0])
                    total_years += (current_year - start)
                except:
                    pass
        
        years_display = f"{total_years} years" if total_years > 0 else "N/A"
        st.metric("📅 Experience", years_display)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display domain analysis table
    if matching_analysis.get('domaines_analyses'):
        import pandas as pd
        
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; color: #111827; font-size: 1.4rem; font-weight: 700;">
                ⚙️ Detailed Weighting Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        df_domaines = pd.DataFrame(matching_analysis['domaines_analyses'])
        
        def format_domain(row):
            match = row['match']
            if match == 'incompatible':
                icon = "❌"
            elif match == 'partiel':
                icon = "⚠️"
            else:
                icon = "✅"
            return f"{icon} {row['domaine']}"
        
        df_domaines['Domain'] = df_domaines.apply(format_domain, axis=1)
        df_domaines['Weight'] = df_domaines['poids'].astype(str) + '%'
        df_domaines['Score'] = df_domaines.apply(
            lambda row: f"{row['score']}/{row['score_max']}", axis=1
        )
        
        def truncate(text, max_len=150):
            if len(text) <= max_len:
                return text
            text = text[:max_len]
            last_space = text.rfind(' ')
            if last_space > 0:
                text = text[:last_space]
            if text and text[-1] not in '.!?':
                text += '.'
            return text
        
        df_domaines['Comment'] = df_domaines['commentaire'].apply(truncate)
        df_display = df_domaines[['Domain', 'Weight', 'Score', 'Comment']]
        
        def style_rows(row):
            idx = row.name
            match = df_domaines.loc[idx, 'match']
            
            if match == 'incompatible':
                bg = '#fef2f2'
            elif match == 'partiel':
                bg = '#fffbeb'
            else:
                bg = '#f0fdf4'
            
            return [f'background-color: {bg}'] * len(row)
        
        styled_df = df_display.style.apply(style_rows, axis=1)
        
        st.markdown("""
        <style>
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(25, 62, 146, 0.12);
            border: 2px solid #193E92;
        }
        [data-testid="stDataFrame"] thead {
            background: linear-gradient(135deg, #193E92 0%, #2563eb 100%);
        }
        [data-testid="stDataFrame"] thead th {
            color: white !important;
            font-weight: 700 !important;
            padding: 18px 16px !important;
        }
        [data-testid="stDataFrame"] tbody td {
            padding: 16px !important;
            line-height: 1.6 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Domain": st.column_config.TextColumn("Domain", width=400),
                "Weight": st.column_config.TextColumn("Weight", width=70),
                "Score": st.column_config.TextColumn("Score", width=70),
                "Comment": st.column_config.TextColumn("Comment", width=None),
            }
        )
        
        # Analysis summary
        st.markdown("<br>", unsafe_allow_html=True)
        if matching_analysis.get('synthese_matching'):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border-left: 4px solid #3b82f6;
                border-radius: 12px;
                padding: 20px 24px;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
            ">
                <div style="display: flex; align-items: start;">
                    <div style="font-size: 1.5rem; margin-right: 12px;">📊</div>
                    <div>
                        <div style="font-weight: 700; color: #1e40af; font-size: 1.1rem; margin-bottom: 8px;">Analysis Summary</div>
                        <div style="color: #1e3a8a; line-height: 1.6;">{matching_analysis['synthese_matching']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# 🔧 FONCTIONS HELPER
# =====================================================
def save_uploaded(file, suffix=None) -> Path:
    """Enregistre un fichier uploadé dans un temp file."""
    suffix = suffix or Path(file.name).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(file.read())
    tmp.flush()
    tmp.close()
    return Path(tmp.name)

@st.cache_data(show_spinner=False)
def read_bytes(path: Path) -> bytes:
    """Cache la lecture du fichier final."""
    return Path(path).read_bytes()

# =====================================================
# ⚙️ STEP 1: MATCHING ANALYSIS PIPELINE
# =====================================================
if analyze_button:
    # Reset previous results
    st.session_state.results = None
    st.session_state.matching_done = False
    st.session_state.matching_data = None
    
    if not can_run:
        st.error("❌ Please upload **the resume** and **the job description**.")
        st.stop()

    # Temporary save
    with st.spinner("📁 Preparing files..."):
        cv_path = save_uploaded(cv_file)
        jd_path = save_uploaded(jd_file)

    # Processing container
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### 🔍 Analyzing Matching...")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Timeline with ICONS (like V1)
        timeline_placeholder = st.empty()
        
        try:
            enricher = load_backend()
            
            # Define step labels for matching analysis (3 steps)
            matching_steps = [
                {"num": 1, "icon": "🔍", "label": "Extraction"},
                {"num": 2, "icon": "🤖", "label": "Analysis"},
                {"num": 3, "icon": "📊", "label": "Matching"},
            ]
            
            # Step 1: Extraction
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(1, 3, matching_steps), unsafe_allow_html=True)
            cv_text = enricher.extract_cv_text(str(cv_path))
            
            # Step 2: Parsing (Analysis)
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(2, 3, matching_steps), unsafe_allow_html=True)
            parsed_cv = enricher.parse_cv_with_claude(cv_text)
            
            # Step 3: Matching Analysis
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(3, 3, matching_steps), unsafe_allow_html=True)
                
            
            # Step 3: Matching Analysis
            jd_text = enricher.read_job_description(str(jd_path))
            matching_analysis = enricher.analyze_cv_matching(parsed_cv, jd_text)
            
            # Clear timeline
            timeline_placeholder.empty()
            
            # Store data for Step 2
            st.session_state.matching_data = {
                'parsed_cv': parsed_cv,
                'jd_text': jd_text,
                'matching_analysis': matching_analysis,
                'cv_path': cv_path,
                'jd_path': jd_path,
                'template_lang': template_lang,
                'mode_anonymise': mode_anonymise,
                'template_file': template_file
            }
            st.session_state.matching_done = True
            
            # Show temporary success badge
            import time
            success_placeholder = st.empty()
            
            with success_placeholder.container():
                col_s1, col_s2, col_s3 = st.columns([3, 2, 3])
                with col_s2:
                    st.markdown("""
                    <div style="
                        background: linear-gradient(90deg, #22c55e 0%, #047857 100%);
                        border-radius: 30px;
                        padding: 8px 16px;
                        text-align: center;
                        box-shadow: 0 2px 8px rgba(34, 197, 94, 0.25);
                        animation: fadeIn 0.3s ease-in;
                    ">
                        <span style="color: white; font-size: 0.85rem; font-weight: 600;">
                            ✅ Analysis Complete!
                        </span>
                    </div>
                    <style>
                        @keyframes fadeIn {
                            from { opacity: 0; transform: translateY(-10px); }
                            to { opacity: 1; transform: translateY(0); }
                        }
                    </style>
                    """, unsafe_allow_html=True)
            
            # Auto-disappear after 2 seconds (réduit pour meilleure réactivité)
            time.sleep(2)
            success_placeholder.empty()
            
            # Switch to Generate button and rerun to show results
            st.session_state.show_generate_button = True
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ **Analysis error:** {str(e)}")
            with st.expander("🔍 Technical details"):
                import traceback
                st.code(traceback.format_exc())
            st.session_state.matching_done = False
            st.session_state.matching_data = None


# =====================================================
# ⚙️ STEP 2: CV GENERATION PIPELINE
# =====================================================
if generate_button:
    # Allow generation even without prior matching
    if not can_run:
        st.error("❌ Please upload **the resume** and **the job description**.")
        st.stop()
    
    # Reset previous full results
    st.session_state.results = None
    
    # If matching was done, retrieve Step 1 data; otherwise process from scratch
    if st.session_state.matching_done and st.session_state.matching_data:
        # Reuse existing matching data
        data = st.session_state.matching_data
        parsed_cv = data['parsed_cv']
        jd_text = data['jd_text']
        matching_analysis = data['matching_analysis']
        cv_path = data['cv_path']
        jd_path = data['jd_path']
        template_lang = data['template_lang']
        mode_anonymise = data['mode_anonymise']
        template_file = data['template_file']
    else:
        # Process from scratch without matching
        with st.spinner("📁 Preparing files..."):
            cv_path = save_uploaded(cv_file)
            jd_path = save_uploaded(jd_file)
        
        # Quick extraction and parsing
        enricher = load_backend()
        cv_text = enricher.extract_cv_text(str(cv_path))
        parsed_cv = enricher.parse_cv_with_claude(cv_text)
        jd_text = enricher.read_job_description(str(jd_path))
        matching_analysis = enricher.analyze_cv_matching(parsed_cv, jd_text)

    # Use the placeholder created ABOVE (appears right after button, before results)
    with generation_stepper_container.container():
        st.markdown("### ✨ Generating CV...")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Timeline - will be updated as we progress
        stepper_timeline = st.empty()
        stepper_timeline.markdown(generation_progress_timeline(1), unsafe_allow_html=True)
    
    try:
        enricher = load_backend()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = cv_path.parent / f"CV_TMC_{ts}.docx"
        
        # Step 4: Enrichment
        target_language = "English" if template_lang == "EN" else "French"
        enriched_cv = enricher.enrich_cv_with_prompt(
            parsed_cv, 
            jd_text, 
            language=target_language,
            matching_analysis=matching_analysis  # ✅ FIX: Réutilise le score du Step 1!
        )
        
        # Update timeline - step 2 active
        stepper_timeline.markdown(generation_progress_timeline(2), unsafe_allow_html=True)
        
        # Step 5: Structuring
        tmc_context = enricher.map_to_tmc_structure(parsed_cv, enriched_cv, template_lang=template_lang)
        
        # Update timeline - step 3 active
        stepper_timeline.markdown(generation_progress_timeline(3), unsafe_allow_html=True)
        
        # Step 6: Generation
        enricher.generate_tmc_docx(tmc_context, str(out_path), template_path=template_file)
        
        # Post-processing
        keywords = enriched_cv.get('mots_cles_a_mettre_en_gras', [])
        if keywords:
            enricher.apply_bold_post_processing(str(out_path), keywords)
        
        # Clear the generation stepper
        generation_stepper_container.empty()
        
        # Store results
        cv_bytes = read_bytes(out_path)
        
        # Format: TMC - Prénom NOM - Titre Court.docx
        nom_complet = parsed_cv.get('nom_complet', 'Candidate Name')
        nom_parts = nom_complet.split()

        if len(nom_parts) >= 2:
            prenom = nom_parts[0]
            nom = ' '.join(nom_parts[1:]).upper()
        else:
            prenom = nom_parts[0] if nom_parts else 'Candidate'
            nom = ''

        titre_brut = enriched_cv.get('titre_professionnel_enrichi', parsed_cv.get('titre_professionnel', 'Professional'))
        titre_words = titre_brut.split()
        titre_court = ' '.join(titre_words[:5]) if len(titre_words) > 5 else titre_brut

        # NOUVEAU: Choisir le préfixe selon le mode anonymisé
        if mode_anonymise:
            # Mode anonymisé: remplacer "TMC" par "CV" pour cacher l'entreprise
            if nom:
                nom_fichier = f"CV - {prenom} {nom} - {titre_court}.docx"
            else:
                nom_fichier = f"CV - {prenom} - {titre_court}.docx"
        else:
            # Mode standard: garder "TMC"
            if nom:
                nom_fichier = f"TMC - {prenom} {nom} - {titre_court}.docx"
            else:
                nom_fichier = f"TMC - {prenom} - {titre_court}.docx"
        
        st.session_state.results = {
            'score': enriched_cv.get('score_matching', 0),
            'nom': parsed_cv.get('nom_complet', 'N/A'),
            'nb_exp': len(enriched_cv.get('experiences_enrichies', [])),
            'experiences_raw': parsed_cv.get('experiences', []),
            'points_forts': enriched_cv.get('points_forts', []),
            'domaines_analyses': enriched_cv.get('domaines_analyses', []),
            'synthese_matching': enriched_cv.get('synthese_matching', ''),
            'cv_bytes': cv_bytes,
            'nom_fichier': nom_fichier
        }
        
        # Airtable tracking
        try:
            import os
            import requests
            import json
            
            AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
            BASE_ID = 'apptzRcN1NnoNLCJ7'
            TABLE_ID = 'tblYjn3wCdMBU6Gcq'
            
            if AIRTABLE_API_KEY:
                now = datetime.now()
                timestamp_iso = now.strftime('%Y-%m-%dT%H:%M:%S')
                language = "French" if template_lang == "FR" else "English"
                
                metadata = enriched_cv.get('_metadata', {})
                processing_time = metadata.get('processing_time_seconds', 0)
                total_tokens = metadata.get('total_tokens', 0)
                estimated_cost = metadata.get('estimated_cost_usd', 0)
                
                user_full_name = st.session_state.get('user_name', 'Unknown User')
                user_location = st.session_state.get('user_location', 'Unknown')
                
                name_parts = user_full_name.split(' ', 1)
                first_name_user = name_parts[0] if len(name_parts) > 0 else 'Unknown'
                last_name_user = name_parts[1] if len(name_parts) > 1 else ''
                
                record_data = {
                    "fields": {
                        "Timestamp": timestamp_iso,
                        "Candidate Name": nom_complet[:100] if nom_complet else "Unknown",
                        "Matching Score": int(enriched_cv.get('score_matching', 0)),
                        "Language": language,
                        "First Name": first_name_user,
                        "Last Name": last_name_user,
                        "User Location": user_location,
                        "Processing Time": round(processing_time, 2),
                        "Total Tokens": int(total_tokens),
                        "Estimated Cost ($)": round(estimated_cost, 4)
                    }
                }
                
                url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}'
                headers = {
                    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(record_data), timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ Airtable tracking success: {nom_complet}")
                else:
                    print(f"⚠️ Airtable error: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Airtable tracking failed: {e}")
        
        # Show temporary success badge
        import time
        gen_success_placeholder = st.empty()
        
        with gen_success_placeholder.container():
            col_g1, col_g2, col_g3 = st.columns([3, 2, 3])
            with col_g2:
                st.markdown("""
                <div style="
                    background: linear-gradient(90deg, #22c55e 0%, #047857 100%);
                    border-radius: 30px;
                    padding: 8px 16px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.25);
                    animation: fadeIn 0.3s ease-in;
                ">
                    <span style="color: white; font-size: 0.85rem; font-weight: 600;">
                        ✅ Generation Complete!
                    </span>
                </div>
                <style>
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(-10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                </style>
                """, unsafe_allow_html=True)
        
        # Auto-disappear after 2 seconds (réduit pour meilleure réactivité)
        time.sleep(2)
        gen_success_placeholder.empty()
        
        # ✅ FIX: Pas de st.rerun() - le tableau du Step 1 reste visible!
        
    except Exception as e:
        st.error(f"❌ **Generation error:** {str(e)}")
        with st.expander("🔍 Technical details"):
            import traceback
            st.code(traceback.format_exc())

# =====================================================
# 📊 AFFICHAGE FINAL (si results présent)
# =====================================================
if st.session_state.get('results'):
    results = st.session_state.results
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## 🎉 Result")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== MÉTRIQUES CLÉS =====
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # AMÉLIORATION #4: Score simple avec st.metric
        st.metric("📊 Matching Score", f"{results['score']}/100")
    
    with col2:
        st.metric("👤 Candidate", results['nom'])
    
    with col3:
        # Calculate years
        experiences = results.get('experiences_raw', [])
        total_years = 0
        
        import re
        from datetime import datetime
        current_year = datetime.now().year
        
        for exp in experiences:
            periode = exp.get('periode', '')
            periode_clean = periode.replace('Present', str(current_year)).replace('Présent', str(current_year)).replace('present', str(current_year))
            years_found = re.findall(r'\b(\d{4})\b', periode_clean)
            
            if len(years_found) >= 2:
                try:
                    start = int(years_found[0])
                    end = int(years_found[-1])
                    if end >= start:
                        total_years += (end - start)
                except:
                    pass
            elif len(years_found) == 1:
                try:
                    start = int(years_found[0])
                    total_years += (current_year - start)
                except:
                    pass
        
        years_display = f"{total_years} years" if total_years > 0 else "N/A"
        st.metric("📅 Years of Experience", years_display)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== TABLEAU DE PONDÉRATION PROFESSIONNEL (st.dataframe) =====
    if results.get('domaines_analyses'):
        import pandas as pd
        
        # ===== TITRE =====
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; color: #111827; font-size: 1.4rem; font-weight: 700;">
                ⚙️ Detailed Weighting Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Créer le DataFrame
        df_domaines = pd.DataFrame(results['domaines_analyses'])
        
        # Ajouter colonne avec icône + domaine
        def format_domain(row):
            match = row['match']
            if match == 'incompatible':
                icon = "❌"
            elif match == 'partiel':
                icon = "⚠️"
            else:
                icon = "✅"
            return f"{icon} {row['domaine']}"
        
        df_domaines['Domain'] = df_domaines.apply(format_domain, axis=1)
        df_domaines['Weight'] = df_domaines['poids'].astype(str) + '%'
        df_domaines['Score'] = df_domaines.apply(
            lambda row: f"{row['score']}/{row['score_max']}", axis=1
        )
        
        # Tronquer commentaires
        def truncate(text, max_len=150):
            if len(text) <= max_len:
                return text
            text = text[:max_len]
            last_space = text.rfind(' ')
            if last_space > 0:
                text = text[:last_space]
            if text and text[-1] not in '.!?':
                text += '.'
            return text
        
        df_domaines['Comment'] = df_domaines['commentaire'].apply(truncate)
        
        # Sélectionner colonnes finales
        df_display = df_domaines[['Domain', 'Weight', 'Score', 'Comment']]
        
        # Fonction de style pour les lignes
        def style_rows(row):
            idx = row.name
            match = df_domaines.loc[idx, 'match']
            
            if match == 'incompatible':
                bg = '#fef2f2'
            elif match == 'partiel':
                bg = '#fffbeb'
            else:
                bg = '#f0fdf4'
            
            return [f'background-color: {bg}'] * len(row)
        
        # Appliquer style
        styled_df = df_display.style.apply(style_rows, axis=1)
        
        # CSS pour le dataframe avec couleurs TMC
        st.markdown("""
        <style>
        /* Dataframe professionnel avec couleurs TMC */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(25, 62, 146, 0.12);
            border: 2px solid #193E92;
        }
        [data-testid="stDataFrame"] table {
            border-collapse: collapse;
        }
        [data-testid="stDataFrame"] thead {
            background: linear-gradient(135deg, #193E92 0%, #2563eb 100%);
        }
        [data-testid="stDataFrame"] thead th {
            color: white !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            padding: 18px 16px !important;
            text-align: left !important;
            border: none !important;
        }
        [data-testid="stDataFrame"] tbody td {
            padding: 16px !important;
            font-size: 0.9rem !important;
            border-bottom: 1px solid #e5e7eb !important;
            vertical-align: middle !important;
            line-height: 1.6 !important;
        }
        [data-testid="stDataFrame"] tbody tr:last-child td {
            border-bottom: none !important;
        }
        /* Accent orange TMC sur hover */
        [data-testid="stDataFrame"] tbody tr:hover {
            box-shadow: inset 4px 0 0 #D97104;
            transition: all 0.2s ease;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Afficher le dataframe sans lignes vides
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Domain": st.column_config.TextColumn(
                    "Domain",
                    width=400,
                    help="Technical/functional domain"
                ),
                "Weight": st.column_config.TextColumn(
                    "Weight",
                    width=70,
                    help="Importance weight (%)"
                ),
                "Score": st.column_config.TextColumn(
                    "Score",
                    width=70,
                    help="Candidate score"
                ),
                "Comment": st.column_config.TextColumn(
                    "Comment",
                    width=None,  # Prend l'espace restant
                    help="Detailed assessment"
                ),
            }
        )
        
        # ===== BLOC RÉSUMÉ TEXTUEL =====
        st.markdown("<br>", unsafe_allow_html=True)
        if results.get('synthese_matching'):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border-left: 4px solid #3b82f6;
                border-radius: 12px;
                padding: 20px 24px;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
            ">
                <div style="display: flex; align-items: start;">
                    <div style="font-size: 1.5rem; margin-right: 12px;">📊</div>
                    <div>
                        <div style="font-weight: 700; color: #1e40af; font-size: 1.1rem; margin-bottom: 8px;">Analysis Summary</div>
                        <div style="color: #1e3a8a; line-height: 1.6;">{results['synthese_matching']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== KEY STRENGTHS =====
    if results['points_forts']:
        st.markdown("### 💪 Key Strengths Identified")
        for i, pf in enumerate(results['points_forts'][:5], 1):
            st.markdown(f"**{i}.** {pf}")
    
    st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# 🔚 FOOTER
# =====================================================
st.markdown("<br><br>", unsafe_allow_html=True)

# Privacy notice
st.markdown("""
<div style="
    background: linear-gradient(135deg, #EBF4FF 0%, #E0E7FF 100%);
    border-left: 4px solid #193E92;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    text-align: center;
">
    <strong style="color: #193E92;">🔒 Privacy & Data Protection</strong><br>
    <span style="color: #6B7280; font-size: 0.9rem;">
        Your data is processed securely and <strong>never stored</strong>. All files are automatically deleted after processing.
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class='tmc-footer'>
        <strong>TMC CV Optimizer</strong> — Designed for TMC Business Managers & Recruiters<br>
        Made by <strong>Kevin Abecassis</strong> | Powered by Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)

if logo_mini_path.exists():
    st.image(str(logo_mini_path), width=100)
