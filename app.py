#!/usr/bin/env python3
"""
TMC CV Optimizer — VERSION 1.3.9 - FIXES COMPLETS
✅ Système de scoring réaliste (plus de 100/100 faciles)
✅ Vraie synthèse détaillée de Claude (4-6 paragraphes)
✅ Bouton Download pleine largeur (= bouton Generate)
✅ Signature Ekinext sur page de connexion
✅ Emojis sans fusées

Date: 30 octobre 2025
"""

import streamlit as st
from pathlib import Path
import base64
import tempfile
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import extra_streamlit_components as stx
import PyPDF2
from docx import Document
import json
import requests

# Charger les variables d'environnement depuis .env
load_dotenv()

# ==========================================
# 🎨 CONSTANTES COULEURS TMC
# ==========================================
PRIMARY_BLUE = "#193E92"    # Bleu TMC principal
SECONDARY_ORANGE = "#D97104"  # Orange TMC
BG_LIGHT = "#F9FAFB"
SUCCESS_GREEN = "#10B981"

# ==========================================
# ⚙️ CONFIG PAGE
# ==========================================
st.set_page_config(
    page_title="CV Optimizer",
    page_icon="📊",  # ✅ Changé: enlevé fusée
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 CSS CENTRALISÉ (V1.3.9 Style)
# ==========================================
def local_css():
    """Styles CSS modernes et centralisés"""
    st.markdown(f"""
    <style>
        /* ========== GLOBAL STYLES ========== */
        .stApp {{
            background: linear-gradient(180deg, {BG_LIGHT} 0%, #ECEFF3 100%);
        }}
        
        * {{
            font-family: 'Arial', 'Open Sans', sans-serif;
        }}
        
        /* Remove default Streamlit padding */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1100px !important;
            width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }}
        
        /* Hide Streamlit default elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* ========== HIDE SECRETS ERROR MESSAGE ========== */
        .element-container:has(> .stException) {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }}
        
        [data-testid="stException"] {{
            display: none !important;
            visibility: hidden !important;
        }}
        
        .stException {{
            display: none !important;
            visibility: hidden !important;
        }}
        
        div.stException {{
            display: none !important;
            visibility: hidden !important;
        }}
        
        /* ========== HEADER ========== */
        .tmc-hero {{
            text-align: center;
            padding: 3rem 1rem 2rem 1rem;
            margin-bottom: 2rem;
        }}
        
        .tmc-subtitle {{
            color: #6B7280;
            font-size: 1.15rem;
            margin-top: 0.75rem;
            font-weight: 400;
        }}
        
        /* ========== DIVIDER ========== */
        .divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, #CBD5E1, transparent);
            margin: 2rem 0;
        }}
        
        /* ========== CLIENT CARDS ========== */
        .client-card {{
            border-radius: 16px;
            padding: 24px;
            margin: 10px 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}
        
        .client-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .client-card:hover {{
            transform: translateX(8px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
        }}
        
        .client-card:hover::before {{
            width: 100%;
            opacity: 0.05;
        }}
        
        /* Desjardins style */
        .client-card-desj {{
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 2px solid #86efac;
            box-shadow: 0 4px 12px rgba(134, 239, 172, 0.2);
        }}
        
        .client-card-desj::before {{
            background: #16a34a;
        }}
        
        /* Morgan Stanley style */
        .client-card-ms {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 2px solid #93c5fd;
            box-shadow: 0 4px 12px rgba(147, 197, 253, 0.2);
        }}
        
        .client-card-ms::before {{
            background: #2563eb;
        }}
        
        /* CAE style */
        .client-card-cae {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 2px solid #fbbf24;
            box-shadow: 0 4px 12px rgba(251, 191, 36, 0.2);
        }}
        
        .client-card-cae::before {{
            background: #d97706;
        }}
        
        /* ========== BUTTONS ========== */
        .stButton > button {{
            width: 100%;
            background: linear-gradient(90deg, {PRIMARY_BLUE} 0%, {SECONDARY_ORANGE} 100%);
            color: white;
            border: none;
            padding: 0.9rem 2rem;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px rgba(25, 62, 146, 0.3);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(25, 62, 146, 0.4);
        }}
        
        .stButton > button:active {{
            transform: translateY(0);
        }}
        
        /* ✅ NEW: Style global pour TOUS les download buttons */
        div[data-testid="stDownloadButton"] > button {{
            background: linear-gradient(90deg, #22c55e 0%, #047857 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.9rem 2rem !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 14px rgba(34, 197, 94, 0.35) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }}
        
        div[data-testid="stDownloadButton"] > button:hover {{
            box-shadow: 0 8px 24px rgba(34, 197, 94, 0.45) !important;
            transform: translateY(-2px) !important;
        }}
        
        div[data-testid="stDownloadButton"] > button:active {{
            transform: translateY(0) !important;
        }}
        
        /* ========== FILE UPLOADER ========== */
        [data-testid="stFileUploader"] {{
            border: 2px dashed #CBD5E1;
            border-radius: 12px;
            padding: 1.5rem;
            background: white;
            transition: all 0.3s ease;
        }}
        
        [data-testid="stFileUploader"]:hover {{
            border-color: {PRIMARY_BLUE};
            background: #F9FAFB;
        }}
        
        /* ========== METRICS ========== */
        [data-testid="stMetricValue"] {{
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, {PRIMARY_BLUE}, {SECONDARY_ORANGE});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        /* ========== DATAFRAME ========== */
        [data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}
        
        /* ========== FOOTER SIGNATURE ========== */
        .footer-signature {{
            text-align: center;
            padding: 2rem 0 1rem 0;
            color: #9CA3AF;
            font-size: 0.9rem;
            margin-top: 3rem;
            border-top: 1px solid #E5E7EB;
        }}
        
        .footer-signature a {{
            color: {PRIMARY_BLUE};
            text-decoration: none;
            font-weight: 600;
        }}
        
        .footer-signature a:hover {{
            color: {SECONDARY_ORANGE};
        }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔐 AUTHORIZED USERS
# ==========================================
AUTHORIZED_USERS = [
    "Kevin Abecassis",
    "Morgan Richer", 
    "Amelie Blais",
    "Lauralie Martin",
    "Admin Test"
]

# ==========================================
# 🏢 CLIENT DATA (Updated with improved configs)
# ==========================================
CLIENT_DATA = {
    "Morgan Stanley": {
        "rules": [
            "📄 3-page format with Skills Matrix",
            "🎯 No TMC branding",
            "⚙️ Technical depth required"
        ],
        "card_class": "client-card-ms",
        "show_language": False,  # Pas de choix de langue
        "anonymize": False,      # Jamais anonymisé
        "language": "English",   # Toujours anglais
        "use_skizmatrix": True   # ✅ Utilise Skills Matrix
    },
    "CAE": {
        "rules": [
            "🌐 <strong>Choose language: 🇫🇷 French or 🇬🇧 English</strong>",
            "📄 Format: Clean 2-page CV",
            "🎯 No TMC branding (anonymized)"
        ],
        "card_class": "client-card-cae",
        "show_language": True,   # ✅ Choix FR/EN
        "anonymize": True,       # ✅ Mode anonymisé (pas de logo TMC)
        "language": None,        # Sera défini par l'utilisateur
        "use_skizmatrix": False  # Pas de Skills Matrix
    },
    "Desjardins": {
        "rules": [
            "🌐 <strong>French only</strong>",
            "📄 Format: TMC Branded with logo",
            "🎯 Quebec experience valued"
        ],
        "card_class": "client-card-desj",
        "show_language": False,  # Pas de choix (toujours français)
        "anonymize": False,      # Jamais anonymisé
        "language": "French",    # Toujours français
        "use_skizmatrix": False  # Pas de Skills Matrix
    }
}

# ==========================================
# 🎨 HORIZONTAL TIMELINE
# ==========================================
def horizontal_progress_timeline(current_step: int = 1, total_steps: int = 5, step_labels: list = None) -> str:
    """
    Génère une timeline horizontale avec des étapes dynamiques.
    current_step: étape en cours (1-N)
    total_steps: nombre total d'étapes
    step_labels: liste des étapes avec icon et label
    """
    if step_labels is None:
        # Default: 5 steps
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

# ==========================================
# 🍪 COOKIE MANAGER
# ==========================================
cookie_manager = stx.CookieManager()

# ==========================================
# 🔐 SESSION STATE INITIALIZATION
# ==========================================
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
if 'selected_client' not in st.session_state:
    st.session_state.selected_client = "Desjardins"
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "French"
if 'cv_file' not in st.session_state:
    st.session_state.cv_file = None
if 'jd_file' not in st.session_state:
    st.session_state.jd_file = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'skills_matrix_file' not in st.session_state:
    st.session_state.skills_matrix_file = None
if 'show_generate_button' not in st.session_state:
    st.session_state.show_generate_button = False

# ==========================================
# 🔐 AUTHENTICATION FUNCTIONS
# ==========================================

def check_session():
    """Check if session is still valid (5 hours)"""
    if st.session_state.authenticated and st.session_state.login_time:
        elapsed = datetime.now() - st.session_state.login_time
        if elapsed > timedelta(hours=5):
            st.session_state.authenticated = False
            return False
    return st.session_state.authenticated

def load_session_from_cookies():
    """Load session from cookies if available"""
    try:
        session_data = cookie_manager.get('tmc_session')
        if session_data:
            data = json.loads(session_data)
            login_time = datetime.fromisoformat(data['login_time'])
            elapsed = datetime.now() - login_time
            
            if elapsed <= timedelta(hours=5):
                st.session_state.authenticated = True
                st.session_state.user_name = data['user_name']
                st.session_state.user_location = data['user_location']
                st.session_state.login_time = login_time
                st.session_state.last_activity = datetime.now()
                return True
    except:
        pass
    return False

def save_session_to_cookies():
    """Save session to cookies"""
    try:
        session_data = {
            'user_name': st.session_state.user_name,
            'user_location': st.session_state.user_location,
            'login_time': st.session_state.login_time.isoformat()
        }
        cookie_manager.set('tmc_session', json.dumps(session_data))
    except:
        pass

def logout():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    st.session_state.user_name = None
    st.session_state.user_location = None
    st.session_state.login_time = None
    st.session_state.matching_done = False
    st.session_state.matching_data = None
    st.session_state.cv_file = None
    st.session_state.jd_file = None
    st.session_state.processing = False
    st.session_state.skills_matrix_file = None
    st.session_state.show_generate_button = False
    try:
        cookie_manager.delete('tmc_session')
    except:
        pass

# ==========================================
# 📊 AIRTABLE LOGGING
# ==========================================

def log_to_airtable(user_name, event_type, metadata=None):
    """Log events to Airtable"""
    try:
        AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN') or st.secrets.get("AIRTABLE_TOKEN")
        AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID') or st.secrets.get("AIRTABLE_BASE_ID")
        AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME') or st.secrets.get("AIRTABLE_TABLE_NAME")
        
        if not all([AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME]):
            return
        
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_TOKEN}",
            "Content-Type": "application/json"
        }
        
        fields = {
            "User": user_name,
            "Event_Type": event_type,
            "Timestamp": datetime.now().isoformat(),
        }
        
        if metadata:
            fields["Metadata"] = json.dumps(metadata)
        
        data = {"fields": fields}
        requests.post(url, headers=headers, json=data)
    except:
        pass

# ==========================================
# 🔓 LOGIN SCREEN
# ==========================================

def show_login_screen():
    """Display login screen"""
    local_css()
    
    # ✅ Header SANS fusée
    st.markdown(f"""
    <div class="tmc-hero">
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 0.5rem;">
            <svg width="600" height="80" viewBox="0 0 600 80" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="titleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:{PRIMARY_BLUE};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{SECONDARY_ORANGE};stop-opacity:1" />
                    </linearGradient>
                </defs>
                <text x="50%" y="60" font-family="Arial, sans-serif" font-size="48" font-weight="800" fill="url(#titleGradient)" text-anchor="middle">
                    CV Optimizer
                </text>
            </svg>
        </div>
        <p class="tmc-subtitle">Generate optimized TMC CVs with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Authentication")
        
        name = st.selectbox(
            "Select your name",
            options=AUTHORIZED_USERS,
            key="name_select"
        )
        
        location = st.selectbox(
            "Select your location",
            options=["Montréal, QC", "Toronto, ON", "Vancouver, BC", "Other"],
            key="location_select"
        )
        
        if st.button("📊 Access CV Optimizer", use_container_width=True):  # ✅ Emoji changé
            st.session_state.authenticated = True
            st.session_state.user_name = name
            st.session_state.user_location = location
            st.session_state.login_time = datetime.now()
            st.session_state.last_activity = datetime.now()
            
            # Save to cookies
            save_session_to_cookies()
            
            # Log to Airtable
            log_to_airtable(name, "login", {"location": location})
            
            st.rerun()
    
    # ✅ Signature Ekinext en bas
    st.markdown("""
    <div class="footer-signature">
        © 2025 <a href="https://ekinext.com" target="_blank">Ekinext</a> - Automation Consulting
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 🏠 MAIN APPLICATION
# ==========================================

def main_app():
    """Application principale"""
    
    # Initialize reset counter for file uploaders (if not exists)
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
    
    # Apply custom CSS
    local_css()
    
    # ========== SIDEBAR ==========
    with st.sidebar:
        # User info
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.markdown(f"📍 {st.session_state.user_location}")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Client selector
        st.markdown("#### 🏢 Select Client")
        
        clients_list = list(CLIENT_DATA.keys())
        client = st.selectbox(
            "Client",
            options=clients_list,
            index=clients_list.index(st.session_state.selected_client),
            label_visibility="collapsed",
            key="client_select"
        )
        
        # Update session state if changed
        if client != st.session_state.selected_client:
            st.session_state.selected_client = client
            # Reset matching when client changes
            st.session_state.matching_done = False
            st.session_state.matching_data = None
            st.session_state.skills_matrix_file = None
            st.session_state.show_generate_button = False
            # Reset file uploaders by incrementing counter
            st.session_state.reset_counter += 1
            st.rerun()
        
        # Show client rules
        client_config = CLIENT_DATA[st.session_state.selected_client]
        st.markdown(f"""
        <div class="client-card {client_config['card_class']}" style="margin-top: 1rem;">
            <h4 style="margin: 0 0 12px 0; color: #111827; font-weight: 700;">{client}</h4>
            <div style="line-height: 1.8;">
                {"<br>".join(client_config['rules'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ✅ CAE Language Selector (si applicable)
        if client_config.get("show_language", False):
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("#### 🌐 Select Language")
            
            language = st.radio(
                "Language for CV",
                options=["French 🇫🇷", "English 🇬🇧"],
                index=0 if st.session_state.selected_language == "French" else 1,
                label_visibility="collapsed",
                key="language_select"
            )
            
            # Extract language name
            new_language = "French" if "French" in language else "English"
            
            # Update session state if changed
            if new_language != st.session_state.selected_language:
                st.session_state.selected_language = new_language
                # ✅ DEBUG log
                print(f"🌐 CAE Language selected: {st.session_state.selected_language}", flush=True)
                st.rerun()
        else:
            # Auto-set language for non-CAE clients
            st.session_state.selected_language = client_config.get("language", "French")
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # ========== MAIN CONTENT ==========
    
    # ✅ Header SANS fusée
    st.markdown(f"""
    <div class="tmc-hero">
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 0.5rem;">
            <svg width="600" height="80" viewBox="0 0 600 80" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="titleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:{PRIMARY_BLUE};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{SECONDARY_ORANGE};stop-opacity:1" />
                    </linearGradient>
                </defs>
                <text x="50%" y="60" font-family="Arial, sans-serif" font-size="48" font-weight="800" fill="url(#titleGradient)" text-anchor="middle">
                    CV Optimizer
                </text>
            </svg>
        </div>
        <p class="tmc-subtitle">Generate optimized TMC CVs with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### 📁 Upload Files")
    
    col_upload1, col_upload2 = st.columns(2)
    
    with col_upload1:
        cv_file = st.file_uploader(
            "**Upload CV** (PDF or DOCX)",
            type=['pdf', 'docx'],
            key=f"cv_uploader_{st.session_state.reset_counter}",
            help="Upload the candidate's resume"
        )
        if cv_file:
            st.session_state.cv_file = cv_file
            st.success(f"✅ CV Uploaded: **{cv_file.name}**")
    
    with col_upload2:
        jd_file = st.file_uploader(
            "**Upload Job Description** (PDF, DOCX, or TXT)",
            type=['pdf', 'docx', 'txt'],
            key=f"jd_uploader_{st.session_state.reset_counter}",
            help="Upload the job description"
        )
        if jd_file:
            st.session_state.jd_file = jd_file
            st.success(f"✅ JD Uploaded: **{jd_file.name}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analyze button
    if st.session_state.cv_file and st.session_state.jd_file and not st.session_state.processing:
        if not st.session_state.matching_done:
            if st.button("🔍 Analyze Matching", use_container_width=True, key="analyze_button"):
                st.session_state.processing = True
                st.rerun()
    elif not (st.session_state.cv_file and st.session_state.jd_file):
        st.info("📤 Please upload both CV and Job Description to start analysis")
    
    # Process matching if triggered
    if st.session_state.processing and not st.session_state.matching_done:
        process_cv_matching()
    
    # Display results if matching is done
    if st.session_state.matching_done and st.session_state.matching_data:
        display_matching_results(st.session_state.matching_data)

# ==========================================
# 🔍 CV MATCHING ANALYSIS
# ==========================================

def save_uploaded(uploaded_file) -> Path:
    """Save uploaded file temporarily"""
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        return Path(tmp.name)

def process_cv_matching():
    """Process CV matching analysis with 3-step timeline"""
    st.markdown("---")
    st.markdown("## 🔍 Analyzing Matching...")
    st.markdown("<br>", unsafe_allow_html=True)
    
    timeline_placeholder = st.empty()
    
    # Define 3-step matching timeline
    matching_steps = [
        {"num": 1, "icon": "🔍", "label": "Extraction"},
        {"num": 2, "icon": "🤖", "label": "Analysis"},
        {"num": 3, "icon": "📊", "label": "Matching"},
    ]
    
    try:
        # Import enricher
        from tmc_cv_enricher import TMCUniversalEnricher
        
        # Initialize enricher
        api_key = os.getenv('ANTHROPIC_API_KEY') or st.secrets.get("ANTHROPIC_API_KEY")
        enricher = TMCUniversalEnricher(api_key=api_key)
        
        # Save uploaded files temporarily
        cv_path = save_uploaded(st.session_state.cv_file)
        jd_path = save_uploaded(st.session_state.jd_file)
        
        # Step 1: Extraction
        timeline_placeholder.markdown(horizontal_progress_timeline(1, 3, matching_steps), unsafe_allow_html=True)
        cv_text = enricher.extract_cv_text(str(cv_path))
        
        # Step 2: Parsing
        timeline_placeholder.markdown(horizontal_progress_timeline(2, 3, matching_steps), unsafe_allow_html=True)
        parsed_cv = enricher.parse_cv_with_claude(cv_text)
        
        # Step 3: Matching Analysis
        timeline_placeholder.markdown(horizontal_progress_timeline(3, 3, matching_steps), unsafe_allow_html=True)
        jd_text = enricher.read_job_description(str(jd_path))
        matching_analysis = enricher.analyze_cv_matching(parsed_cv, jd_text)
        
        # Clear timeline
        timeline_placeholder.empty()
        
        # Store results
        st.session_state.matching_data = {
            'parsed_cv': parsed_cv,
            'jd_text': jd_text,
            'matching_analysis': matching_analysis,
            'cv_path': cv_path,
            'jd_path': jd_path
        }
        st.session_state.matching_done = True
        st.session_state.show_generate_button = True
        st.session_state.processing = False
        
        # Log to Airtable
        log_to_airtable(
            st.session_state.user_name,
            "analysis_completed",
            {
                "client": st.session_state.selected_client,
                "score": matching_analysis.get('score_matching', 0)
            }
        )
        
        st.success("✅ Analysis Complete!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error during processing: {str(e)}")
        st.session_state.processing = False
        import traceback
        st.code(traceback.format_exc())

# ==========================================
# 📊 DISPLAY RESULTS
# ==========================================

def display_matching_results(data):
    """Display matching results with professional styling"""
    results = data['matching_analysis']
    parsed_cv = data.get('parsed_cv', {})
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Score section
    col1, col2, col3 = st.columns(3)
    
    # Get parsed_cv and experiences for col2 and col3
    experiences = parsed_cv.get('experiences', [])
    
    with col1:
        score = results.get('score_matching', 0)
        st.metric(
            "🎯 Matching Score",
            f"{score}/100",
            help="Overall compatibility score"
        )
    
    with col2:
        nom = parsed_cv.get('nom_complet', 'Candidate')
        nom_display = nom if len(nom) < 20 else nom[:17] + "..."
        st.metric("👤 Candidate", nom_display)
    
    with col3:
        # Calculate years of experience
        import re
        total_years = 0
        current_year = datetime.now().year
        
        for exp in experiences:
            periode = exp.get('periode', '')
            periode_clean = periode.replace('Present', str(current_year)).replace('Présent', str(current_year))
            years_found = re.findall(r'\b(\d{4})\b', periode_clean)
            
            if len(years_found) >= 2:
                try:
                    start = int(years_found[0])
                    end = int(years_found[-1])
                    if end >= start:
                        total_years += (end - start)
                except:
                    pass
        
        years_display = f"{total_years} years" if total_years > 0 else "N/A"
        st.metric("📅 Years of Experience", years_display)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed weighting table
    if results.get('domaines_analyses'):
        import pandas as pd
        
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; color: #111827; font-size: 1.4rem; font-weight: 700;">
                ⚙️ Detailed Weighting Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create DataFrame
        df_domaines = pd.DataFrame(results['domaines_analyses'])
        
        # Format columns
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
        
        # Truncate comments
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
        
        # Select final columns
        df_display = df_domaines[['Domain', 'Weight', 'Score', 'Comment']]
        
        # Style rows
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
        
        # Apply style
        styled_df = df_display.style.apply(style_rows, axis=1)
        
        # Display dataframe
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
                    width=None,
                    help="Detailed assessment"
                ),
            }
        )
        
        # ✅ UTILISER LA VRAIE SYNTHÈSE DE CLAUDE (détaillée, 4-6 paragraphes)
        st.markdown("<br>", unsafe_allow_html=True)
        
        synthese_claude = results.get('synthese_matching', '')
        
        if synthese_claude:
            # Format la synthèse avec des paragraphes
            # La synthèse vient de Claude et contient déjà des paragraphes naturels
            synthese_formatted = synthese_claude.replace('\n\n', '<br><br>').replace('\n', '<br>')
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                border-left: 4px solid #3b82f6;
                border-radius: 12px;
                padding: 24px 28px;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
            ">
                <div style="display: flex; align-items: start;">
                    <div style="font-size: 1.8rem; margin-right: 14px;">📊</div>
                    <div>
                        <div style="font-weight: 700; color: #1e40af; font-size: 1.25rem; margin-bottom: 10px;">Analysis Summary</div>
                        <div style="color: #1e3a8a; line-height: 1.7; font-size: 1.05rem;">{synthese_formatted}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback si pas de synthèse (ne devrait pas arriver avec le nouveau système)
            st.warning("⚠️ Detailed analysis not available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key strengths
    if results.get('points_forts'):
        st.markdown("### 💪 Key Strengths Identified")
        for i, pf in enumerate(results['points_forts'][:5], 1):
            st.markdown(f"**{i}.** {pf}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ✨ Skills Matrix Upload Section (ONLY for Morgan Stanley)
    if st.session_state.selected_client == "Morgan Stanley":
        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 15px;">
            <strong style="color: #193E92; font-size: 1.15rem;">📊 Skills Matrix Upload (Required)</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader for Skills Matrix
        col_sm_left, col_sm_center, col_sm_right = st.columns([1, 2, 1])
        with col_sm_center:
            skills_matrix_file = st.file_uploader(
                "Upload Skills Matrix (.docx only)",
                type=['docx'],
                key=f"skills_matrix_uploader_{st.session_state.reset_counter}",
                help="Morgan Stanley requires a Skills Matrix as page 2 of the CV"
            )
            
            # Store in session state and show feedback
            if skills_matrix_file:
                st.session_state.skills_matrix_file = skills_matrix_file
                st.success(f"✅ Skills Matrix Uploaded: **{skills_matrix_file.name}**")
            else:
                if st.session_state.skills_matrix_file:
                    # Show previously uploaded file
                    st.info(f"✅ Skills Matrix Ready: **{st.session_state.skills_matrix_file.name}**")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate CV button
    if st.button("📝 Generate Optimized CV", use_container_width=True, key="generate_cv_button"):
        generate_cv(data)

# ==========================================
# 📝 CV GENERATION
# ==========================================

def generate_cv(data):
    """Generate the optimized CV with 3-step timeline"""
    
    # ✨ Validation pour Morgan Stanley
    if st.session_state.selected_client == "Morgan Stanley":
        if not st.session_state.skills_matrix_file:
            st.error("❌ **Skills Matrix is required for Morgan Stanley clients**")
            st.error("📊 Please upload the Skills Matrix document before generating the CV.")
            st.stop()
    
    st.markdown("---")
    st.markdown("## 📝 Generating Optimized CV")
    
    timeline_placeholder = st.empty()
    
    # Define 3-step generation timeline
    generation_steps = [
        {"num": 1, "icon": "✨", "label": "Enrichment"},
        {"num": 2, "icon": "🗂️", "label": "Structuring"},
        {"num": 3, "icon": "📝", "label": "Generation"},
    ]
    
    try:
        from tmc_cv_enricher import TMCUniversalEnricher
        
        api_key = os.getenv('ANTHROPIC_API_KEY') or st.secrets.get("ANTHROPIC_API_KEY")
        enricher = TMCUniversalEnricher(api_key=api_key)
        
        # Get client config
        client_config = CLIENT_DATA[st.session_state.selected_client]
        
        # Step 1: Enrichment
        timeline_placeholder.markdown(horizontal_progress_timeline(1, 3, generation_steps), unsafe_allow_html=True)
        
        # ✅ DEBUG: Log selected language
        print(f"🌐 LANGUAGE SELECTED: {st.session_state.selected_language}", flush=True)
        print(f"📋 CLIENT: {st.session_state.selected_client}", flush=True)
        
        parsed_cv = data.get('parsed_cv')
        jd_text = data.get('jd_text')
        matching_analysis = data.get('matching_analysis')
        
        # Enrichir le CV
        enriched_cv = enricher.enrich_cv_with_claude(
            parsed_cv, 
            jd_text, 
            matching_analysis,
            language=st.session_state.selected_language
        )
        
        # Step 2: Structuring
        timeline_placeholder.markdown(horizontal_progress_timeline(2, 3, generation_steps), unsafe_allow_html=True)
        
        # Préparer le contexte TMC
        tmc_context = enricher.prepare_tmc_context(enriched_cv, parsed_cv)
        
        # Step 3: Generation
        timeline_placeholder.markdown(horizontal_progress_timeline(3, 3, generation_steps), unsafe_allow_html=True)
        
        success = False
        
        # Generate based on client
        if st.session_state.selected_client == "Morgan Stanley":
            # ✨ Generate 3-part CV with Skills Matrix
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as output_tmp:
                output_path = output_tmp.name
            
            # Save Skills Matrix temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as sm_tmp:
                sm_tmp.write(st.session_state.skills_matrix_file.read())
                skills_matrix_path = sm_tmp.name
            
            # ✅ Use correct MS generation method
            result = enricher.generate_ms_cv_3parts(
                tmc_context,
                output_path,
                skills_matrix_path=skills_matrix_path
            )
            
            if result == "SUCCESS":
                success = True
            else:
                st.error(f"❌ Error generating Morgan Stanley CV: {result}")
        
        elif st.session_state.selected_client == "CAE":
            # Generate anonymized 2-page CV (no logo)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as output_tmp:
                output_path = output_tmp.name
            
            # Use template without logo (anonymized)
            template_file = "tmc_cv_template_anonymized.docx"
            if not Path(template_file).exists():
                st.error(f"❌ Template not found: {template_file}")
                st.stop()
            
            enricher.generate_tmc_docx(
                tmc_context,
                output_path,
                template_path=template_file
            )
            
            # Post-processing: Bold keywords
            keywords = enriched_cv.get('mots_cles_a_mettre_en_gras', [])
            if keywords:
                enricher.apply_bold_post_processing(output_path, keywords)
            
            success = True
        
        else:
            # Desjardins: Standard TMC CV with logo
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as output_tmp:
                output_path = output_tmp.name
            
            template_file = "tmc_cv_template.docx"
            if not Path(template_file).exists():
                st.error(f"❌ Template not found: {template_file}")
                st.stop()
            
            enricher.generate_tmc_docx(
                tmc_context,
                output_path,
                template_path=template_file
            )
            
            # Post-processing: Bold keywords
            keywords = enriched_cv.get('mots_cles_a_mettre_en_gras', [])
            if keywords:
                enricher.apply_bold_post_processing(output_path, keywords)
            
            success = True
        
        # Clear timeline
        timeline_placeholder.empty()
        
        if success:
            # Read the generated file
            with open(output_path, 'rb') as f:
                cv_bytes = f.read()
            
            # Clean up
            os.unlink(output_path)
            
            st.success("🎉 **CV Generated Successfully!**")
            
            # Generate filename with correct format per client
            parsed_cv = data.get('parsed_cv', {})
            nom_complet = parsed_cv.get('nom_complet', 'Candidate')
            
            # ✅ Use ENRICHED title (in correct language) instead of original
            titre = enriched_cv.get('titre_professionnel_enrichi', parsed_cv.get('titre_professionnel', 'Profile'))
            
            # Format name as "Prenom NOM" (last name in uppercase)
            import re
            nom_parts = nom_complet.strip().split()
            if len(nom_parts) >= 2:
                # Assume last part is surname
                prenom = ' '.join(nom_parts[:-1])  # Everything except last part
                nom = nom_parts[-1].upper()  # Last part in uppercase
                nom_formatted = f"{prenom} {nom}"
            else:
                # Single name - just use as is
                nom_formatted = nom_complet
            
            # Clean special characters from title
            titre_clean = re.sub(r'[^\w\s-]', '', titre).strip()
            
            # Build filename according to client
            client = st.session_state.selected_client
            language = st.session_state.selected_language
            
            if client == "Desjardins":
                filename = f"TMC - {nom_formatted} - {titre_clean}.docx"
            elif client == "Morgan Stanley":
                filename = f"CV - {nom_formatted} - {titre_clean}.docx"
            elif client == "CAE":
                # Add language suffix for CAE
                lang_suffix = "(EN)" if language == "English" else "(FR)"
                filename = f"CV - {nom_formatted} - {titre_clean} {lang_suffix}.docx"
            else:
                # Fallback to old format
                filename = f"TMC - {nom_formatted} - {titre_clean}.docx"
            
            # ✅ Download button - Utiliser directement sans wrapper pour être full-width
            st.download_button(
                label="📥 Download Optimized CV",
                data=cv_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="download_cv_button"
            )
            
            # Log to Airtable
            log_to_airtable(
                st.session_state.user_name,
                "cv_generated",
                {
                    "client": st.session_state.selected_client,
                    "language": st.session_state.selected_language,
                    "anonymized": client_config["anonymize"],
                    "skills_matrix_used": bool(st.session_state.skills_matrix_file and client_config["use_skizmatrix"])
                }
            )
        else:
            st.error(f"❌ Error generating CV: {result}")
            
    except Exception as e:
        st.error(f"❌ Error during generation: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

def create_download_link(file_bytes, filename):
    """Create a download link for file"""
    b64 = base64.b64encode(file_bytes).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" class="download-link">📥 Download {filename}</a>'

# ==========================================
# 🚀 MAIN ENTRY POINT
# ==========================================

if __name__ == "__main__":
    # Try to restore session from cookies
    if not st.session_state.authenticated:
        load_session_from_cookies()
    
    # Check session validity
    if not check_session():
        show_login_screen()
    else:
        # Update last activity
        st.session_state.last_activity = datetime.now()
        main_app()
