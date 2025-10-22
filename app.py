#!/usr/bin/env python3
"""
TMC CV Optimizer — VERSION 2.0 PRO (Streamlit Cloud Safe)
Interface Streamlit premium pour générer des CVs TMC optimisés
"""

import streamlit as st
from pathlib import Path
import base64
import tempfile
from datetime import datetime

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

def get_base64_image(image_path: Path) -> str:
    """Convertit une image en base64 pour l'afficher en HTML."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def horizontal_progress_timeline(current_step: int = 1) -> str:
    """
    Génère une timeline horizontale avec 5 étapes.
    current_step: 1-5 (étape en cours)
    """
    steps = [
        {"num": 1, "icon": "🔍", "label": "Extraction"},
        {"num": 2, "icon": "🤖", "label": "Analysis"},
        {"num": 3, "icon": "✨", "label": "Enrichment"},
        {"num": 4, "icon": "🗺️", "label": "Structuring"},
        {"num": 5, "icon": "📝", "label": "Generation"},
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
                <div class="connector-progress" style="width: """ + str((current_step - 1) * 25) + """%;"></div>
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

# Centrer avec des colonnes (version originale qui marchait)
col_left, col_center, col_right = st.columns([3, 2, 3])
with col_center:
    language_choice = st.radio(
        "Select language",
        options=["🇫🇷 French", "🇬🇧 English"],
        horizontal=True,
        label_visibility="collapsed",
        key="language_selector"
    )

# Determine template to use
template_lang = "FR" if "🇫🇷" in language_choice else "EN"
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
# ⚙️ PIPELINE PRINCIPALE
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
        
        # Timeline horizontale centrée
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
            
            # Étape 3: Enrichissement
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(3), unsafe_allow_html=True)
            jd_text = enricher.read_job_description(str(jd_path))
            
            # Passer la langue choisie à l'enrichissement
            target_language = "English" if template_lang == "EN" else "French"
            enriched_cv = enricher.enrich_cv_with_prompt(parsed_cv, jd_text, language=target_language)
            
            # Étape 4: Mapping
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(4), unsafe_allow_html=True)
            tmc_context = enricher.map_to_tmc_structure(parsed_cv, enriched_cv, template_lang=template_lang)
            
            # Étape 5: Génération
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(5), unsafe_allow_html=True)
            
            # Utiliser le template sélectionné
            enricher.generate_tmc_docx(tmc_context, str(out_path), template_path=template_file)
            
            # Post-processing
            keywords = enriched_cv.get('mots_cles_a_mettre_en_gras', [])
            if keywords:
                enricher.apply_bold_post_processing(str(out_path), keywords)
            
            # Terminé - Timeline complète
            with timeline_placeholder.container():
                st.markdown(horizontal_progress_timeline(5), unsafe_allow_html=True)
            
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
            
            if nom:
                nom_fichier = f"TMC - {prenom} {nom} - {titre_court}.docx"
            else:
                nom_fichier = f"TMC - {prenom} - {titre_court}.docx"
            
            # Stocker dans session_state
            st.session_state.results = {
                'score': enriched_cv.get('score_matching', 0),
                'nom': parsed_cv.get('nom_complet', 'N/A'),
                'nb_exp': len(enriched_cv.get('experiences_enrichies', [])),
                'points_forts': enriched_cv.get('points_forts', []),
                'domaines_analyses': enriched_cv.get('domaines_analyses', []),
                'synthese_matching': enriched_cv.get('synthese_matching', ''),
                'cv_bytes': cv_bytes,
                'nom_fichier': nom_fichier
            }
            
            # Nettoyage des fichiers temporaires
            try:
                cv_path.unlink()
                jd_path.unlink()
                out_path.unlink()
            except:
                pass
                
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
        st.metric("💼 Experiences", results['nb_exp'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== TABLEAU DE PONDÉRATION PREMIUM =====
    if results.get('domaines_analyses'):
        import pandas as pd
        
        # Nom du candidat
        nom_parts = results['nom'].split()
        nom_display = f"{nom_parts[0]} {nom_parts[-1]}" if len(nom_parts) >= 2 else results['nom']
        score_global = results['score']
        
        # Déterminer le niveau de match
        if score_global >= 75:
            fit_level = "Excellent Match"
            fit_color = "#10b981"
        elif score_global >= 50:
            fit_level = "Good Match"
            fit_color = "#f59e0b"
        else:
            fit_level = "Moderate Mismatch"
            fit_color = "#ef4444"
        
        # ===== TITRE SIMPLE (sans header) =====
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; color: #111827; font-size: 1.4rem; font-weight: 700;">
                ⚙️ Detailed Weighting Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Créer le DataFrame
        df_domaines = pd.DataFrame(results['domaines_analyses'])
        
        # ===== TABLEAU HTML RESPONSIVE =====
        st.markdown("""
        <style>
        .domain-table-container {
            max-width: 1200px;
            margin: 0 auto;
            overflow-x: auto;
        }
        .domain-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
        }
        .domain-table thead {
            background: linear-gradient(135deg, #193E92 0%, #2563eb 100%);
        }
        .domain-table th {
            color: white;
            font-weight: 700;
            font-size: 0.9rem;
            padding: 14px 18px;
            text-align: left;
        }
        .domain-table td {
            padding: 14px 18px;
            font-size: 0.875rem;
            border-bottom: 1px solid #f3f4f6;
            vertical-align: top;
            word-wrap: break-word;
            overflow-wrap: break-word;
            line-height: 1.5;
            white-space: normal;
        }
        .domain-table tr:hover {
            background: transparent !important;
        }
        .domain-table tr:last-child td {
            border-bottom: none;
        }
        .domain-table th:nth-child(1),
        .domain-table td:nth-child(1) {
            width: 280px;
            min-width: 280px;
            max-width: 280px;
        }
        .domain-table th:nth-child(2),
        .domain-table td:nth-child(2) {
            width: 80px;
            min-width: 80px;
            max-width: 80px;
            text-align: center;
        }
        .domain-table th:nth-child(3),
        .domain-table td:nth-child(3) {
            width: 120px;
            min-width: 120px;
            max-width: 120px;
        }
        .domain-table th:nth-child(4),
        .domain-table td:nth-child(4) {
            width: auto;
            overflow-wrap: break-word;
            word-break: break-word;
        }
        .icon-badge {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            margin-right: 6px;
            vertical-align: middle;
            flex-shrink: 0;
        }
        .progress-bar-container {
            width: 100%;
            max-width: 140px;
            height: 8px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 4px;
        }
        .progress-bar {
            height: 100%;
            border-radius: 10px;
            animation: fillBar 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        @keyframes fillBar {
            from { width: 0; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Démarrer le tableau HTML
        st.markdown("""
        <div class="domain-table-container">
        <table class="domain-table">
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>Weight</th>
                    <th>Score</th>
                    <th>Comment</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)
        
        # Lignes du tableau
        for idx, row in df_domaines.iterrows():
            match = row['match']
            score = row['score']
            score_max = row['score_max']
            poids = row['poids']
            
            # Couleurs selon le match
            if match == 'incompatible':
                bg_color = "#fef2f2"
                icon_bg = "#fca5a5"
                icon = "✕"
                bar_color = "#ef4444"
            elif match == 'partiel':
                bg_color = "#fffbeb"
                icon_bg = "#fcd34d"
                icon = "⚠"
                bar_color = "#f59e0b"
            else:
                bg_color = "#f0fdf4"
                icon_bg = "#86efac"
                icon = "✓"
                bar_color = "#10b981"
            
            # Calculer le pourcentage pour la barre
            percentage = (score / score_max * 100) if score_max > 0 else 0
            
            # Commentaire tronqué intelligemment (sans "...")
            commentaire = row['commentaire']
            max_length = 120
            
            if len(commentaire) > max_length:
                # Tronquer au dernier mot complet avant max_length
                commentaire_court = commentaire[:max_length]
                derniere_espace = commentaire_court.rfind(' ')
                if derniere_espace > 0:
                    commentaire_court = commentaire_court[:derniere_espace]
                # Ajouter un point si la phrase n'en a pas
                if commentaire_court and commentaire_court[-1] not in '.!?':
                    commentaire_court += '.'
            else:
                commentaire_court = commentaire
            
            st.markdown(f"""
            <tr style="background: {bg_color};">
                <td>
                    <span class="icon-badge" style="background: {icon_bg};">{icon}</span>
                    <strong>{row['domaine']}</strong>
                </td>
                <td><strong>{poids}%</strong></td>
                <td>
                    <div><strong>{score}/{score_max}</strong></div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: {percentage}%; background: {bar_color};"></div>
                    </div>
                </td>
                <td style="color: #6b7280; line-height: 1.5;">{commentaire_court}</td>
            </tr>
            """, unsafe_allow_html=True)
        
        # Fermer le tableau
        st.markdown("""
            </tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)
        
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
