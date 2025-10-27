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
                st.session_state.authenticated = True
                st.session_state.login_time = datetime.now()
                st.session_state.last_activity = datetime.now()
                st.session_state.user_location = user_location
                st.session_state.user_name = user_name
                
                # Sauvegarder dans un cookie
                save_session_to_cookie(user_name, user_location)
                
                st.rerun()
            else:
                st.error("❌ Invalid password")
        
        st.markdown('<p style="text-align: center; color: #9CA3AF; font-size: 0.85rem; margin-top: 30px;">TMC Internal Tool - Authorized Access Only</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #9CA3AF; font-size: 0.75rem; margin-top: 10px;">🔒 Session: 12h max | Auto-logout after 1h inactivity</p>', unsafe_allow_html=True)
    
    st.stop()  # Stop execution if not authenticated

# ==========================================
# 🧠 IMPORT LOURD — Lazy Loading
# ==========================================
@st.cache_resource(show_spinner="🚀 Initializing CV Optimizer...")
def load_backend():
    from tmc_universal_enricher import TMCUniversalEnricher
    return TMCUniversalEnricher()

# =====================================================
# 🔧 HELPER FUNCTIONS
# =====================================================

# ===== SESSION STATE INITIALIZATION =====
if 'results' not in st.session_state:
    st.session_state.results = None

def get_user_info():
    """
    Récupère l'IP, la localisation et le User Agent de l'utilisateur
    Avec système de fallback sur plusieurs APIs
    """
    import requests
    
    # Liste d'APIs de géolocalisation (par ordre de priorité)
    apis = [
        {
            'url': 'https://ipapi.co/json/',
            'timeout': 5,
            'parser': lambda d: {
                'ip': d.get('ip', 'Unknown'),
                'city': d.get('city', 'Unknown'),
                'country': d.get('country_name', 'Unknown'),
                'user_agent': 'Streamlit App'
            }
        },
        {
            'url': 'https://ipwhois.app/json/',
            'timeout': 5,
            'parser': lambda d: {
                'ip': d.get('ip', 'Unknown'),
                'city': d.get('city', 'Unknown'),
                'country': d.get('country', 'Unknown'),
                'user_agent': 'Streamlit App'
            }
        },
        {
            'url': 'http://ip-api.com/json/',
            'timeout': 5,
            'parser': lambda d: {
                'ip': d.get('query', 'Unknown'),
                'city': d.get('city', 'Unknown'),
                'country': d.get('country', 'Unknown'),
                'user_agent': 'Streamlit App'
            }
        }
    ]
    
    # Essayer chaque API dans l'ordre
    for api in apis:
        try:
            print(f"🔍 Tentative géolocalisation avec {api['url']}...")
            response = requests.get(api['url'], timeout=api['timeout'])
            
            if response.status_code == 200:
                data = response.json()
                result = api['parser'](data)
                
                # Vérifier que les données sont valides
                if result['ip'] != 'Unknown' and result['country'] != 'Unknown':
                    print(f"✅ Géolocalisation réussie: {result['city']}, {result['country']}")
                    return result
                else:
                    print(f"⚠️ API {api['url']} a retourné des données incomplètes")
            else:
                print(f"⚠️ API {api['url']} a retourné le code {response.status_code}")
                
        except requests.Timeout:
            print(f"⏱️ Timeout pour {api['url']}")
            continue
        except Exception as e:
            print(f"⚠️ Erreur avec {api['url']}: {str(e)}")
            continue
    
    # Si toutes les APIs ont échoué
    print("❌ Toutes les APIs de géolocalisation ont échoué")
    return {
        'ip': 'Unknown',
        'city': 'Unknown',
        'country': 'Unknown',
        'user_agent': 'Streamlit App'
    }

def get_base64_image(image_path: Path) -> str:
    """Convertit une image en base64 pour l'afficher en HTML."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def horizontal_progress_timeline(current_step: int = 1) -> str:
    """
    Génère une timeline horizontale avec 6 étapes (Two-Step).
    current_step: 1-6 (étape en cours)
    """
    steps = [
        {"num": 1, "icon": "🔍", "label": "Extraction"},
        {"num": 2, "icon": "🤖", "label": "Analysis"},
        {"num": 3, "icon": "🎯", "label": "Matching"},  # NOUVELLE ÉTAPE
        {"num": 4, "icon": "✨", "label": "Enrichment"},
        {"num": 5, "icon": "🗺️", "label": "Structuring"},
        {"num": 6, "icon": "📝", "label": "Generation"},
    ]
    
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
                max-width: 1200px;
                min-width: 700px;
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
                width: 55px;
                height: 55px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
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
                margin-top: 10px;
                font-size: 12px;
                font-weight: 600;
                color: #9CA3AF;
                transition: color 0.3s ease;
                text-align: center;
            }
            .step.active .step-label {
                color: #193E92;
                font-size: 13px;
            }
            .step.completed .step-label {
                color: #193E92;
            }
            .connector {
                position: absolute;
                top: 27px;
                left: 0;
                right: 0;
                height: 4px;
                background: #E5E7EB;
                z-index: 1;
                margin: 0 27px;
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
                <div class="connector-progress" style="width: """ + str((current_step - 1) * 20) + """%;"></div>
            </div>"""
    
    for step in steps:
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

# =====================================================
# 🎨 BRANDING TMC — Constantes
# =====================================================
TMC_BLUE = "#193E92"
TMC_ORANGE = "#D97104"
BG_LIGHT = "#F9FAFB"
TEXT_MAIN = "#111827"
TEXT_MUTED = "#6B7280"

# =====================================================
# 🎨 CSS CUSTOM — Design Premium
# =====================================================
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
    color: {TMC_BLUE};
    font-weight: 800;
    font-size: 2.8rem;
    letter-spacing: 0.3px;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }}
  .tmc-subtitle {{
    color: {TEXT_MUTED};
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
    background: linear-gradient(90deg, {TMC_BLUE} 0%, {TMC_ORANGE} 100%) !important;
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
    border: 2px dashed {TMC_BLUE}40;
    border-radius: 14px;
    background: white;
    padding: 1.5rem;
    transition: all 0.3s ease;
  }}
  [data-testid="stFileUploader"]:hover {{
    border-color: {TMC_ORANGE};
    background: #FEF3E2;
  }}

  /* ===== PROGRESS BAR ===== */
  .stProgress > div > div {{
    background: linear-gradient(90deg, {TMC_BLUE} 0%, {TMC_ORANGE} 100%);
    height: 8px;
    border-radius: 10px;
  }}

  /* ===== STEPS ===== */
  .tmc-step {{
    color: {TEXT_MUTED};
    font-size: 1rem;
    margin: 0.3rem 0;
    padding: 0.5rem;
    border-left: 3px solid {TMC_BLUE}30;
    padding-left: 1rem;
    background: {BG_LIGHT};
    border-radius: 6px;
  }}
  .tmc-step.active {{
    border-left-color: {TMC_ORANGE};
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
    color: {TMC_BLUE};
    font-size: 2rem;
    font-weight: 800;
  }}
  [data-testid="stMetricLabel"] {{
    color: {TEXT_MUTED};
    font-weight: 600;
    font-size: 0.95rem;
  }}

  /* ===== FOOTER ===== */
  .tmc-footer {{
    text-align: center;
    color: {TEXT_MUTED};
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
# 🎬 BOUTON GÉNÉRATION
# =====================================================
can_run = cv_file is not None and jd_file is not None

col_btn1, col_btn2, col_btn3 = st.columns([2, 3, 2])
with col_btn2:
    submit = st.button(
        "✨ Generate my TMC CV",
        disabled=not can_run,
        use_container_width=True
    )

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
# ⚙️ PIPELINE PRINCIPALE AVEC TWO-STEP MATCHING
# =====================================================
if submit:
    # Réinitialiser les résultats précédents dès qu'on clique sur Generate
    st.session_state.results = None
    
    if not can_run:
        st.error("❌ Please upload **the resume** and **the job description**.")
        st.stop()

    # Temporary save
    with st.spinner("📁 Preparing files..."):
        cv_path = save_uploaded(cv_file)
        jd_path = save_uploaded(jd_file)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = cv_path.parent / f"CV_TMC_{ts}.docx"

    # Processing container
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### 🔄 Processing...")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Timeline horizontale centrée avec 6 étapes
        col_tl1, col_tl2, col_tl3 = st.columns([0.5, 4, 0.5])
        with col_tl2:
            timeline_placeholder = st.empty()
        
        try:
            # Chargement optimisé du backend (lazy loading)
            enricher = load_backend()
            
            # Étape 1: Extraction
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(1), unsafe_allow_html=True)
            cv_text = enricher.extract_cv_text(str(cv_path))
            
            # Étape 2: Parsing
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(2), unsafe_allow_html=True)
            parsed_cv = enricher.parse_cv_with_claude(cv_text)
            
            # Étape 3: TWO-STEP - Matching Analysis (NOUVELLE ÉTAPE)
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(3), unsafe_allow_html=True)
            jd_text = enricher.read_job_description(str(jd_path))
            
            # Appeler analyze_cv_matching (Step 1 du two-step)
            matching_analysis = enricher.analyze_cv_matching(parsed_cv, jd_text)
            
            # Étape 4: Enrichissement avec contexte du matching
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(4), unsafe_allow_html=True)
            
            # Passer la langue choisie ET le matching_analysis à l'enrichissement
            target_language = "English" if template_lang == "EN" else "French"
            enriched_cv = enricher.enrich_cv_with_prompt(
                parsed_cv, 
                jd_text, 
                language=target_language,
                matching_analysis=matching_analysis  # ✅ NOUVELLE LIGNE
            )
            
            # Étape 5: Mapping
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(5), unsafe_allow_html=True)
            tmc_context = enricher.map_to_tmc_structure(parsed_cv, enriched_cv, template_lang=template_lang)
            
            # Étape 6: Génération
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(6), unsafe_allow_html=True)
            
            # Utiliser le template sélectionné (déjà défini en fonction du mode anonymisé)
            enricher.generate_tmc_docx(tmc_context, str(out_path), template_path=template_file)
            
            # Post-processing
            keywords = enriched_cv.get('mots_cles_a_mettre_en_gras', [])
            if keywords:
                enricher.apply_bold_post_processing(str(out_path), keywords)
            
            # Terminé - Timeline complète
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(6), unsafe_allow_html=True)
            
            # ===== STOCKER LES RÉSULTATS DANS SESSION STATE =====
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
            
            # NOUVEAU: Choisir le préfixe et le nom selon le mode anonymisé
            if mode_anonymise:
                # CV anonymisé: toujours "CV - Candidate - Titre"
                nom_fichier = f"CV - Candidate - {titre_court}.docx"
            else:
                # CV standard: "TMC - Prénom NOM - Titre"
                if nom:
                    nom_fichier = f"TMC - {prenom} {nom} - {titre_court}.docx"
                else:
                    nom_fichier = f"TMC - {prenom} - {titre_court}.docx"
            
            # Stocker dans session_state
            st.session_state.results = {
                'score': enriched_cv.get('score_matching', 0),
                'nom': parsed_cv.get('nom_complet', 'N/A'),
                'nb_exp': len(enriched_cv.get('experiences_enrichies', [])),
                'experiences_raw': parsed_cv.get('experiences', []),  # Pour calculer les années
                'points_forts': enriched_cv.get('points_forts', []),
                'domaines_analyses': enriched_cv.get('domaines_analyses', []),
                'synthese_matching': enriched_cv.get('synthese_matching', ''),
                'cv_bytes': cv_bytes,
                'nom_fichier': nom_fichier
            }
            
            # ===== 📊 TRACKING AIRTABLE - ANALYTICS =====
            try:
                import os
                import requests
                from datetime import datetime
                import json
                
                # Configuration Airtable
                AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
                BASE_ID = 'apptzRcN1NnoNLCJ7'
                TABLE_ID = 'tblYjn3wCdMBU6Gcq'
                
                if AIRTABLE_API_KEY:
                    print("🔑 AIRTABLE_API_KEY found, preparing data...")
                    
                    # Préparer les données à enregistrer
                    now = datetime.now()
                    timestamp_iso = now.strftime('%Y-%m-%dT%H:%M:%S')
                    
                    # Langue choisie
                    language = "French" if template_lang == "FR" else "English"
                    
                    # Récupérer les métadonnées d'enrichissement (tokens, temps, coût)
                    metadata = enriched_cv.get('_metadata', {})
                    processing_time = metadata.get('processing_time_seconds', 0)
                    total_tokens = metadata.get('total_tokens', 0)
                    estimated_cost = metadata.get('estimated_cost_usd', 0)
                    
                    # Récupérer les infos utilisateur depuis session_state
                    user_full_name = st.session_state.get('user_name', 'Unknown User')
                    user_location = st.session_state.get('user_location', 'Unknown')
                    
                    # Séparer First Name et Last Name
                    name_parts = user_full_name.split(' ', 1)  # Split en 2 parties max
                    first_name_user = name_parts[0] if len(name_parts) > 0 else 'Unknown'
                    last_name_user = name_parts[1] if len(name_parts) > 1 else ''
                    
                    # Données du log - SEULEMENT les champs qui existent dans Airtable
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
                    
                    print(f"📤 Sending to Airtable:")
                    print(json.dumps(record_data, indent=2))
                    
                    # Envoyer à Airtable
                    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}'
                    headers = {
                        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
                        'Content-Type': 'application/json'
                    }
                    
                    response = requests.post(url, json=record_data, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        print("✅ Analytics logged to Airtable successfully")
                    else:
                        print(f"⚠️ Airtable logging failed: {response.status_code}")
                        print(f"📋 Response body: {response.text}")
                else:
                    print("⚠️ AIRTABLE_API_KEY not found - analytics not logged")
                    
            except Exception as e:
                # Ne pas bloquer l'app si Airtable échoue
                print(f"⚠️ Airtable logging error (non-blocking): {e}")
                import traceback
                print(f"📋 Full traceback: {traceback.format_exc()}")
            
            # Nettoyage des fichiers temporaires
            try:
                cv_path.unlink()
                jd_path.unlink()
                out_path.unlink()
            except:
                pass
            
            # ✅ IMPORTANT: Forcer un rerun pour afficher proprement les résultats
            st.rerun()
                
        except FileNotFoundError as e:
            st.error(f"❌ **Missing file:** {str(e)}")
            st.info("💡 Check that the template `TMC_NA_template_FR.docx` is present in the folder.")
            
        except ModuleNotFoundError:
            st.error("❌ **Backend module not found**")
            st.info("💡 Make sure `tmc_universal_enricher.py` is in the same folder as this app.")
            
        except Exception as e:
            st.error(f"❌ **Processing error:** {str(e)}")
            
            # Debug mode
            with st.expander("🔍 Technical details (for debug)"):
                import traceback
                st.code(traceback.format_exc())

# =====================================================
# 📊 AFFICHAGE DES RÉSULTATS (en dehors du bloc submit)
# =====================================================
if st.session_state.results:
    results = st.session_state.results
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== SUCCÈS ! Badge discret =====
    col_s1, col_s2, col_s3 = st.columns([2, 1, 2])
    with col_s2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #22c55e 0%, #047857 100%);
            border-radius: 50px;
            padding: 8px 20px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(34, 197, 94, 0.3);
            margin: 12px 0;
            display: inline-block;
            width: 100%;
        ">
            <span style="color: white; font-size: 0.95rem; font-weight: 600;">
                ✅ Success!
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== RESULTS =====
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.metric("📊 Matching Score", f"{results['score']}/100")
    
    with col_res2:
        nom_display = results['nom'] if len(results['nom']) < 20 else results['nom'][:17] + "..."
        st.metric("👤 Candidate", nom_display)
    
    with col_res3:
        # Calculer les années d'expérience totales avec méthode robuste
        experiences = results.get('experiences_raw', [])
        total_years = 0
        
        import re
        from datetime import datetime
        current_year = datetime.now().year
        
        for exp in experiences:
            periode = exp.get('periode', '')
            
            # Remplacer Present/Présent par l'année actuelle
            periode_clean = periode.replace('Present', str(current_year)).replace('Présent', str(current_year)).replace('present', str(current_year))
            
            # Extraire TOUTES les années (4 chiffres consécutifs)
            years_found = re.findall(r'\b(\d{4})\b', periode_clean)
            
            if len(years_found) >= 2:
                try:
                    start = int(years_found[0])
                    end = int(years_found[-1])  # Prendre la dernière année trouvée
                    if end >= start:  # Vérification cohérence
                        total_years += (end - start)
                except:
                    pass
            elif len(years_found) == 1:
                # Si une seule année, considérer jusqu'à maintenant
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
    
    # ===== DOWNLOAD =====
    st.markdown("""
    <style>
    .download-button-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col_dl1, col_dl2, col_dl3 = st.columns([1.5, 2, 1.5])
    with col_dl2:
        st.download_button(
            label="📥 Download TMC CV",
            data=results['cv_bytes'],
            file_name=results['nom_fichier'],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

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
