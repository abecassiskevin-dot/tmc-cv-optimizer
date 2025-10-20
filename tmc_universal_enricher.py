#!/usr/bin/env python3
"""
TMC Universal CV Enricher
Lit n'importe quel CV → Enrichit avec IA → Génère CV TMC professionnel
"""

import os
import sys
import json
from docxtpl import DocxTemplate, RichText
from docx import Document
import jinja2
from typing import Dict, List, Any
import PyPDF2
import re
from zipfile import ZipFile
from xml.etree import ElementTree as ET

print(">>> tmc_universal_enricher module loading", flush=True)


class TMCUniversalEnricher:
    """Enrichisseur universel de CV au format TMC"""
    
    def __init__(self, api_key: str = None):
        """Initialiser avec clé API Claude"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("❌ Clé API Claude manquante! Définissez ANTHROPIC_API_KEY dans les secrets Streamlit ou en variable d'environnement.")
        
        # Debug clé API
        print(f">>> ANTHROPIC_KEY_PRESENT: {bool(self.api_key)}, len: {len(self.api_key) if self.api_key else 0}", flush=True)
        
        # Ne crée PAS le client ici (lazy loading)
        self._anthropic_client = None
    
    def _get_anthropic_client(self):
        """Lazy loading du client Anthropic"""
        if self._anthropic_client is None:
            try:
                print(">>> Creating anthropic client", flush=True)
                import anthropic
                # Création SIMPLE du client, sans arguments supplémentaires
                self._anthropic_client = anthropic.Client(api_key=self.api_key)
                print(">>> Anthropic client created OK", flush=True)
            except Exception as e:
                print(f">>> ERROR creating anthropic client: {repr(e)}", flush=True)
                raise
        return self._anthropic_client
    
    # ========================================
    # MODULE 1 : EXTRACTION UNIVERSELLE
    # ========================================
    
    def detect_file_type(self, file_path: str) -> str:
        """Détecter le type de fichier"""
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            return 'pdf'
        elif ext in ['docx', 'doc']:
            return 'docx'
        elif ext in ['txt', 'text']:
            return 'txt'
        else:
            return 'unknown'
    
    def extract_from_pdf(self, file_path: str) -> str:
        """Extraire texte d'un PDF"""
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n".join(text)
        except Exception as e:
            print(f"⚠️ Erreur extraction PDF: {e}")
            return ""
    
     
    def extract_from_docx(self, file_path: str) -> str:
        """Extraire texte d'un Word + zones textes"""
        try:
            doc = Document(file_path)
            text = []
            
            # Paragraphes normaux
            for para in doc.paragraphs:
                if para.text.strip():
                    text.append(para.text.strip())
            
            # Tableaux
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                    if row_text:
                        text.append(row_text)
            
            # NOUVEAU : Extraire les zones textes du XML
            textbox_content = self.extract_textboxes(file_path)
            if textbox_content:
                text.append("\n=== ZONES TEXTES ===")
                text.extend(textbox_content)
            
            return "\n".join(text)
        except Exception as e:
            print(f"⚠️ Erreur extraction Word: {e}")
            return ""
    def extract_from_txt(self, file_path: str) -> str:
        """Extraire texte d'un fichier texte"""
        try:
            # Essayer plusieurs encodages
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            # Si tout échoue, ignorer les erreurs
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Erreur extraction TXT: {e}")
            return ""
    
    def extract_textboxes(self, docx_path: str) -> list:
        """Extraire le contenu des zones textes (text boxes) du XML"""
        textboxes = []
        
        try:
            with ZipFile(docx_path, 'r') as docx:
                # Lire le document.xml
                xml_content = docx.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                
                # Namespaces Word
                namespaces = {
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                    'v': 'urn:schemas-microsoft-com:vml',
                    'w10': 'urn:schemas-microsoft-com:office:word'
                }
                
                # Chercher tous les éléments de texte dans les zones textes
                # Les zones textes sont dans w:txbxContent
                for txbx in tree.findall('.//w:txbxContent', namespaces):
                    texts = []
                    for t in txbx.findall('.//w:t', namespaces):
                        if t.text:
                            texts.append(t.text.strip())
                    if texts:
                        textboxes.append(' '.join(texts))
                
                # Aussi chercher dans v:textbox (ancien format)
                for vtxbx in tree.findall('.//v:textbox', namespaces):
                    texts = []
                    for t in vtxbx.findall('.//w:t', namespaces):
                        if t.text:
                            texts.append(t.text.strip())
                    if texts:
                        textboxes.append(' '.join(texts))
                        
        except Exception as e:
            print(f"⚠️ Erreur extraction zones textes: {e}")
        
        return textboxes
    
    def extract_cv_text(self, cv_path: str) -> str:
        """Extraction universelle - détecte et extrait selon le type"""
        print(f"📄 Extraction du CV: {cv_path}")
        
        file_type = self.detect_file_type(cv_path)
        
        if file_type == 'pdf':
            print("   Format détecté: PDF")
            return self.extract_from_pdf(cv_path)
        elif file_type == 'docx':
            print("   Format détecté: Word")
            return self.extract_from_docx(cv_path)
        elif file_type == 'txt':
            print("   Format détecté: Texte")
            return self.extract_from_txt(cv_path)
        else:
            raise ValueError(f"❌ Format non supporté: {file_type}")

    # ========================================
    # MODULE 2 : PARSING INTELLIGENT
    # ========================================
    
    def parse_cv_with_claude(self, cv_text: str) -> Dict[str, Any]:
        """Parser le CV avec Claude pour extraire les infos structurées"""
        print("🤖 Parsing du CV avec Claude AI...", flush=True)
        
        try:
            client = self._get_anthropic_client()
            
            prompt = f"""Tu es un expert en analyse de CV. Extrait TOUTES les informations de ce CV et structure-les en JSON.

CV À ANALYSER:
{cv_text}

IMPORTANT CRITIQUE:
- Le NOM peut être caché dans un tableau HTML ou être stylisé. Cherche PARTOUT.
- Le LIEU DE RÉSIDENCE est OBLIGATOIRE : cherche "Montréal", "Montreal", villes + pays (ex: "Montreal CA", "Montréal, Canada", "Toronto ON", etc.). Si introuvable, mets "Location not specified".
- Les LANGUES sont OBLIGATOIRES : cherche "Français", "French", "English", "Anglais", "Bilingual", "Bilingue", etc. Si introuvable, mets ["Not specified"].

Extrait et structure en JSON STRICT (sans markdown):
{{
  "nom_complet": "Nom Prénom du candidat (cherche PARTOUT, même dans tableaux/HTML)",
  "titre_professionnel": "Titre/poste actuel",
  "profil_resume": "Résumé du profil si présent (sinon vide)",
  "lieu_residence": "OBLIGATOIRE - Ville, Pays (ex: Montréal, Canada) ou Montreal CA. Cherche codes pays (CA, US, FR). Si vraiment introuvable: 'Location not specified'",
  "langues": ["OBLIGATOIRE - Français", "Anglais", ... Cherche 'bilingual', 'French', 'English', etc. Si introuvable: ['Not specified']],
  "competences": ["compétence1", "compétence2", "compétence3", ...],
  "experiences": [
    {{
      "periode": "2020-2023",
      "entreprise": "Nom entreprise",
      "poste": "Titre du poste",
      "responsabilites": ["tâche 1", "tâche 2", "tâche 3"]
    }}
  ],
  "formation": [
    {{
      "diplome": "Nom COMPLET du diplôme",
      "institution": "Nom école/université",
      "annee": "2020 (ou période exacte)",
      "pays": "Canada"
    }}
  ],
  "certifications": [
    {{
      "nom": "Nom certification",
      "organisme": "Organisme",
      "annee": "2023"
    }}
  ],
  "projets": [
    {{
      "nom": "Nom projet",
      "description": "Description courte"
    }}
  ]
}}

RÈGLES CRITIQUES:
- Le NOM est PRIORITAIRE - cherche dans tout le texte (tableaux, début, fin)
- LIEU DE RÉSIDENCE : cherche formats "Ville, Pays", "Montreal CA", "Montréal QC", codes postaux (H2X, etc.)
- LANGUES : cherche "Languages", "Langues", "French", "English", "Bilingual", même dans sections compétences
- Pour les diplômes: nom COMPLET + année EXACTE
- Extrait TOUT (ne rate rien)
- Si une section est vide, mets une liste vide []
- Format JSON strict uniquement"""

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )
            
        except Exception as e:
            print(f">>> ERROR calling anthropic for parsing: {repr(e)}", flush=True)
            return {}
        
        response_text = response.content[0].text.strip()
        
        # Nettoyer JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            parsed_data = json.loads(response_text)
            print(f"✅ Parsing réussi!")
            print(f"   Nom: [ANONYMIZED]")
            print(f"   Langues: {', '.join(parsed_data.get('langues', []))}")
            print(f"   Lieu: [ANONYMIZED]")
            print(f"   Compétences: {len(parsed_data.get('competences', []))}")
            print(f"   Expériences: {len(parsed_data.get('experiences', []))}")
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur JSON: {e}")
            print(f"Réponse brute: {response_text[:500]}")
            return {}

    # ========================================
    # MODULE 3 : ENRICHISSEMENT (TON PROMPT)
    # ========================================
    
    def read_job_description(self, jd_path: str) -> str:
        """Lire la job description"""
        file_type = self.detect_file_type(jd_path)
        
        if file_type == 'docx':
            return self.extract_from_docx(jd_path)
        else:
            return self.extract_from_txt(jd_path)
    
    def enrich_cv_with_prompt(self, parsed_cv: Dict[str, Any], jd_text: str, language: str = "French") -> Dict[str, Any]:
        """Enrichir le CV avec ton prompt exact"""
        print(f"✨ Enrichissement du CV avec l'IA...", flush=True)
        print(f"   Langue cible: {language}", flush=True)
        
        try:
            client = self._get_anthropic_client()
            
            # Reconstruire le CV en texte pour le prompt
            cv_text = f"""
PROFIL: {parsed_cv.get('profil_resume', '')}

TITRE: {parsed_cv.get('titre_professionnel', '')}

COMPÉTENCES:
{chr(10).join(['- ' + comp for comp in parsed_cv.get('competences', [])])}

EXPÉRIENCES:
"""
            for exp in parsed_cv.get('experiences', []):
                cv_text += f"\n{exp.get('periode', '')} | {exp.get('entreprise', '')} | {exp.get('poste', '')}\n"
                for resp in exp.get('responsabilites', []):
                    cv_text += f"  - {resp}\n"
            
            cv_text += "\nFORMATION:\n"
            for form in parsed_cv.get('formation', []):
                cv_text += f"- {form.get('diplome', '')} | {form.get('institution', '')} | {form.get('annee', '')}\n"
        
            # PROMPT OPTIMISÉ STYLE CHATGPT
            language_instruction = f"""\n\n⚠️ IMPORTANT - LANGUE:\nTu DOIS générer TOUT le contenu en {language}.\n- Tous les titres, descriptions, compétences, responsabilités doivent être en {language}.\n- Respecte les conventions professionnelles de la langue {language}.\n- Si la langue cible est English, utilise un ton professionnel américain/canadien.\n"""
            
            prompt = f"""Voici la job description et le CV actuel ci-dessous.

🔹 Améliore le CV pour qu'il soit parfaitement aligné avec la job description tout en gardant le format d'origine (titres, mise en page, structure, ton professionnel).
{language_instruction}

Fais :

1. Une analyse des écarts entre la job description et le CV actuel.
2. Une version réécrite et enrichie du CV, en conservant le style et le format de mise en page (ex. sections : Profil, Compétences, Expériences, Formation, etc.).

2b. PROFIL exceptionnel : écris un paragraphe NARRATIF fluide (pas de liste), 5-6 lignes avec progression logique. Commence par "Titre/rôle + expérience", enchaîne avec expertise technique, puis soft skills et valeur. Style : Administrateur de plateformes Atlassian fort de 10 ans d'expérience...

2c. GRAS ULTRA-SÉLECTIF : identifie UNIQUEMENT 3-5 technologies CRITIQUES (noms de plateformes/outils demandés explicitement dans la JD). Évite les mots génériques comme "gestion", "configuration", "documentation". Exemples: Jira, SharePoint, Azure, Confluence.

3. Intègre naturellement les mots-clés techniques, fonctionnels et comportementaux issus de la job description (sans sur-optimisation artificielle).
4. Ajuste les intitulés et formulations pour que le profil paraisse livrable immédiatement pour le poste visé.
5. N'invente rien — reformule, réorganise et valorise uniquement les éléments déjà présents ou implicitement cohérents avec le parcours.
6. EXPÉRIENCES : bullets courts et percutants (1 ligne max par bullet), maximum 5-6 bullets par expérience.

Le rendu final doit être :
✅ clair, professionnel, fluide, et client-ready (format TMC/Desjardins).
✅ prêt à être copié dans Word sans modification.

Réponds en JSON STRICT (sans markdown) avec cette structure:
{{
  "profil_enrichi": "Profil NARRATIF en 5-6 lignes (style paragraphe fluide, sans liste à puces). Structure: [Titre/rôle + années] → [Expertise technique clé] → [Soft skills] → [Valeur ajoutée]. Ton professionnel et concis. IMPORTANT: Mettre en **gras** 3-5 MOTS-CLÉS TECHNIQUES UNIQUEMENT (technologies/outils de la JD comme **SharePoint**, **Confluence**, **Teams**, etc.). Exemple: 'Analyste en **configuration** et **gestion documentaire** fort de 25 ans d'expérience...'",
  
  "mots_cles_a_mettre_en_gras": ["LISTE DE 15-20 TECHNOLOGIES CRITIQUES mentionnées dans la Job Description. Inclure TOUTES les plateformes, outils, langages et technologies clés (ex: Jira, SharePoint, Azure, Confluence, PowerShell, Windows Server, Active Directory, SCCM, Intune, Teams, ServiceNow, SQL, Python, etc.). PAS de verbes, PAS de mots génériques comme 'gestion' ou 'administration'"],
  
  "competences_enrichies": {{
    "Nom Catégorie 1 (3-6 mots max)": [
      "**Technologie principale** : description en 2-3 lignes (MAXIMUM 100-150 caractères) incluant contexte, outils associés (**outil1**, **outil2**) et résultats. Style concis et percutant.",
      "**Autre technologie** : description COURTE avec contexte + outils (**tech1**, **tech2**) + impact. 2-3 technologies en **gras** par compétence."
    ],
    "Nom Catégorie 2": [
      "Compétence concise..."
    ]
  }},
  
  RÈGLES ULTRA-CRITIQUES pour les compétences (NON-NÉGOCIABLE):
  - Noms de catégories COURTS (3-6 mots max)
  - 5-6 catégories ADAPTÉES à la JD
  - Chaque catégorie: 3-5 compétences MAXIMUM
  - CHAQUE compétence : 2-3 LIGNES MAXIMUM (100-150 caractères) - NE PAS DÉPASSER
  - Format: "**Technologie** : description concise avec outils (**outil1**, **outil2**) + résultats"
  - 2-3 technologies en **gras** par compétence (PAS PLUS)
  - Descriptions CONCISES, CLAIRES et PROFESSIONNELLES
  - Privilégier CLARTÉ et CONCISION sur la longueur
  
  "experiences_enrichies": [
    {{
      "periode": "2020-2023",
      "entreprise": "Nom entreprise",
      "poste": "Titre reformulé selon JD",
      "responsabilites": [
        "Configuration **Open edX** incluant structuration et intégration avec **SharePoint** pour gestion contenus",
        "Automatisation processus documentaires via **Power Automate** et **Teams** pour améliorer efficacité"
      ],
      "environment": "**Open edX**, **SharePoint**, **Microsoft 365**, Teams, Power Automate, OneDrive, SQL"
    }}
  ],
  
  FORMAT OBLIGATOIRE (COPIER format compétences):
  - Responsabilités: Technologies **isolées** dans texte normal (ex: "Configuration **Tech1** incluant **Tech2** pour résultats")
  - Environnement: Liste virgules avec 3-5 technologies **critiques** en gras, autres sans
  - JAMAIS phrases entières en gras
  - Maximum 2-3 mots entre **astérisques**
  
  "score_matching": 85,
  "points_forts": ["force 1", "force 2", "force 3"]
}}

---

JOB DESCRIPTION:
{jd_text}

---

CV ACTUEL:
{cv_text}

---

IMPORTANT: JSON strict uniquement, sans commentaire ni balise."""

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )
            
        except Exception as e:
            print(f">>> ERROR calling anthropic for enrichment: {repr(e)}", flush=True)
            return {}
        
        response_text = response.content[0].text.strip()
        
        # Nettoyer JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            enriched = json.loads(response_text)
            print(f"✅ Enrichissement réussi!")
            print(f"   Score matching: {enriched.get('score_matching', 0)}/100")
            print(f"   Mots-clés en gras: {len(enriched.get('mots_cles_a_mettre_en_gras', []))}")
            
            # DEBUG: Afficher une responsabilité pour voir le format
            if enriched.get('experiences_enrichies'):
                first_exp = enriched['experiences_enrichies'][0]
                if first_exp.get('responsabilites'):
                    print(f"\n🔍 DEBUG - Première responsabilité :")
                    print(f"   {first_exp['responsabilites'][0]}")
                if first_exp.get('environment'):
                    print(f"\n🔍 DEBUG - Environnement :")
                    print(f"   {first_exp['environment']}")
            
            return enriched
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur JSON: {e}")
            return {}

    # ========================================
    # MODULE 4 : MAPPING TMC + RICHTEXT
    # ========================================
    
    def mdbold_to_richtext(self, s: str) -> RichText:
        """Convertit les **bold** markdown en RichText propre sans cascade de gras."""
        import re
        rt = RichText()
        pattern = re.compile(r'\*\*(.*?)\*\*')
        last_end = 0

        # Ajouter le texte avant chaque bloc en gras
        for match in pattern.finditer(s):
            if match.start() > last_end:
                rt.add(s[last_end:match.start()], bold=False, font='Arial')
            # Le texte entre **...** est en gras
            rt.add(match.group(1), bold=True, font='Arial')
            last_end = match.end()

        # Ajouter le texte après le dernier bloc
        if last_end < len(s):
            rt.add(s[last_end:], bold=False, font='Arial')

        return rt

    def map_to_tmc_structure(self, parsed_cv: Dict[str, Any], enriched_cv: Dict[str, Any]) -> Dict[str, Any]:
        """Mapper les données enrichies vers la structure TMC"""
        print("🗺️  Mapping vers structure TMC...")
        
        # HELPER: Échapper les caractères XML
        def escape_xml(text):
            """\u00c9chappe les caract\u00e8res sp\u00e9ciaux XML"""
            if not isinstance(text, str):
                return text
            return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))
        
        # 1. PROFIL - Convertir en RichText pour supporter le gras
        profil_brut = enriched_cv.get('profil_enrichi', parsed_cv.get('profil_resume', ''))
        profil_brut = escape_xml(profil_brut)  # Échapper XML
        profil = self.mdbold_to_richtext(profil_brut) if profil_brut else ''
        
        # 2. COMPÉTENCES - FORMAT CATÉGORISÉ DÉTAILLÉ
        competences_enrichies = enriched_cv.get('competences_enrichies', {})
        
        # Si competences_enrichies est un dict (nouveau format), l'utiliser directement
        if isinstance(competences_enrichies, dict):
            # Supprimer la clé "NOTE" si présente
            skills_categorized = {k: v for k, v in competences_enrichies.items() if k != 'NOTE' and isinstance(v, list)}
        else:
            # Fallback ancien format (liste simple)
            competences = competences_enrichies if isinstance(competences_enrichies, list) else parsed_cv.get('competences', [])
            skills_categorized = {
                'Compétences techniques': competences[:8] if len(competences) >= 8 else competences,
                'Compétences transversales': competences[8:12] if len(competences) > 8 else []
            }
            # Supprimer les catégories vides
            skills_categorized = {k: v for k, v in skills_categorized.items() if v}
        
        # 🔥 Transformation en RichText pour le formatage
        skills_categorized_doc = []
        for cat, skills in skills_categorized.items():
            rt_cat = RichText()
            rt_cat.add(escape_xml(cat), bold=True)  # Échapper catégorie
            rt_skills = [self.mdbold_to_richtext(escape_xml(s)) for s in skills]  # Échapper compétences
            skills_categorized_doc.append((rt_cat, rt_skills))
        
        # 3. EXPÉRIENCES - Texte simple pour les responsabilités, RichText pour environnement
        experiences_enrichies = enriched_cv.get('experiences_enrichies', parsed_cv.get('experiences', []))
        work_experience = []
        
        for exp in experiences_enrichies:
            # GARDER les responsabilités en TEXTE SIMPLE (pas RichText)
            responsabilites_text = [escape_xml(r) for r in exp.get('responsabilites', [])]  # Échapper
            
            # Convertir l'environnement en RichText pour le gras
            environment_brut = exp.get('environment', '')
            environment_brut = escape_xml(environment_brut)  # Échapper
            environment_rt = self.mdbold_to_richtext(environment_brut) if environment_brut else ''
            
            work_exp = {
                'period': escape_xml(exp.get('periode', '')),
                'company': escape_xml(exp.get('entreprise', '')),
                'position': escape_xml(exp.get('poste', '')),
                'general_responsibilities': responsabilites_text,  # Texte simple
                'environment': environment_rt
            }
            work_experience.append(work_exp)
        
        # 4. FORMATION (avec détails complets)
        formation = parsed_cv.get('formation', [])
        education = []
        for form in formation:
            education.append({
                'institution': form.get('institution', ''),
                'degree': form.get('diplome', ''),
                'graduation_year': form.get('annee', 'Date inconnue'),
                'country': form.get('pays', 'Canada'),
                'level': '',
                'title': form.get('diplome', '')
            })
        
        # 5. CERTIFICATIONS (avec mapping vers format template)
        certifications_raw = parsed_cv.get('certifications', [])
        certifications = []
        for cert in certifications_raw:
            certifications.append({
                'name': escape_xml(cert.get('nom', cert.get('name', ''))),
                'institution': escape_xml(cert.get('organisme', cert.get('institution', ''))),
                'year': escape_xml(str(cert.get('annee', cert.get('year', '')))),
                'country': escape_xml(cert.get('pays', cert.get('country', '')))
            })
        
        # 6. PROJETS
        projects = parsed_cv.get('projets', [])
        
        # 6. INFORMATIONS PERSONNELLES
        nom_complet = parsed_cv.get('nom_complet', '')
        
        # Séparer prénom et nom
        parts = nom_complet.split() if nom_complet else []
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = ' '.join(parts[1:])
        elif len(parts) == 1:
            first_name = parts[0]
            last_name = ''
        else:
            first_name = 'Prénom'
            last_name = 'Nom'
        
        titre_professionnel = parsed_cv.get('titre_professionnel', '')
        lieu_residence = parsed_cv.get('lieu_residence', 'Montréal, Canada')
        langues_list = parsed_cv.get('langues', ['Français', 'Anglais'])
        langues = ', '.join(langues_list)
        
        context = {
            # Pour le header (minuscules) - AVEC ÉCHAPPEMENT
            'first_name': escape_xml(first_name),
            'last_name': escape_xml(last_name),
            'title': escape_xml(titre_professionnel),
            
            # Pour la page 1 (MAJUSCULES) - AVEC ÉCHAPPEMENT
            'FIRST_NAME': escape_xml(first_name.upper()),
            'LAST_NAME': escape_xml(last_name.upper()),
            'TITLE': escape_xml(titre_professionnel),
            'RESIDENCY': escape_xml(lieu_residence),
            'LANGUAGES': escape_xml(langues),
            
            # AUSSI en minuscules pour compatibilité template
            'residency': escape_xml(lieu_residence),
            'languages': escape_xml(langues),
            
            # Reste du CV
            'summary': profil,
            'skills_categorized': skills_categorized,
            'skills_categorized_doc': skills_categorized_doc,  # 🔥 Version RichText pour le template
            'work_experience': work_experience,
            'education': education,
            'projects': projects,
            'certifications': certifications
        }
        
        print(f"✅ Mapping terminé!")
        print(f"   Nom: [ANONYMIZED]")
        print(f"   Titre: {titre_professionnel}")
        print(f"   Langues: {langues}")
        print(f"   Profil: RichText généré")
        total_competences = sum(len(v) for v in skills_categorized.values() if isinstance(v, list))
        print(f"   Catégories: {len(skills_categorized)}")
        print(f"   Compétences: {total_competences}")
        print(f"   Expériences: {len(work_experience)}")
        
        return context

    # ========================================
    # MODULE 5 : GÉNÉRATION DOCX TMC
    # ========================================
    
    def generate_tmc_docx(self, context: Dict[str, Any], output_path: str, template_path: str = "TMC_NA_template_FR.docx"):
        """Générer le CV TMC final avec docxtpl"""
        print(f"📝 Génération du CV TMC: {output_path}")
        print(f"   Template utilisé: {template_path}")
        
        # Créer environnement Jinja2 avec filtre pairwise
        jinja_env = jinja2.Environment()
        
        def pairwise(iterable):
            items = list(iterable)
            result = []
            for i in range(0, len(items), 2):
                if i + 1 < len(items):
                    result.append((items[i], items[i + 1]))
                else:
                    result.append((items[i], ''))
            return result
        
        jinja_env.filters['pairwise'] = pairwise
        
        # 🔥 Ajouter la fonction r pour RichText dans le contexte
        context['r'] = lambda x: x
        
        # Charger le template TMC
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"❌ Template TMC introuvable: {template_path}")
        
        doc = DocxTemplate(template_path)
        
        # Rendre le document
        doc.render(context, jinja_env)
        
        # Sauvegarder
        doc.save(output_path)
        print(f"✅ CV TMC généré avec succès!")

    def apply_bold_post_processing(self, docx_path: str, keywords: list):
        """Post-traiter le document pour mettre en gras les technologies dans les tableaux"""
        print(f"🎨 Application du gras sur les technologies...")
        
        from docx import Document as DocxDocument
        from docx.shared import RGBColor
        import re
        
        doc = DocxDocument(docx_path)
        modifications = 0
        
        print(f"   Recherche des **mot** dans le document...")
        
        def apply_bold_to_runs(paragraph):
            """Trouve **mot** et met en gras UNIQUEMENT ce mot"""
            text = paragraph.text
            if '**' not in text:
                return 0
            
            changes = 0
            # Pattern pour trouver **mot**
            pattern = re.compile(r'\*\*([^*]+)\*\*')
            
            # Reconstituer le paragraphe avec le bon formatage
            matches = list(pattern.finditer(text))
            if not matches:
                return 0
            
            # Supprimer tous les runs existants
            for run in paragraph.runs:
                run._element.getparent().remove(run._element)
            
            # Reconstruire avec le bon formatage
            last_end = 0
            for match in matches:
                # Texte normal avant
                if match.start() > last_end:
                    run = paragraph.add_run(text[last_end:match.start()])
                    run.bold = False
                    run.font.name = 'Arial'
                
                # Texte en gras
                run = paragraph.add_run(match.group(1))
                run.bold = True
                run.font.name = 'Arial'
                changes += 1
                
                last_end = match.end()
            
            # Texte normal après
            if last_end < len(text):
                run = paragraph.add_run(text[last_end:])
                run.bold = False
                run.font.name = 'Arial'
            
            return changes
        
        # Parcourir TOUS les tableaux (où sont les expériences)
        print("   📋 Traitement des tableaux...")
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        modifications += apply_bold_to_runs(paragraph)
        
        # Parcourir aussi les paragraphes normaux
        print("   📝 Traitement des paragraphes...")
        for paragraph in doc.paragraphs:
            modifications += apply_bold_to_runs(paragraph)
        
        # Sauvegarder
        doc.save(docx_path)
        if modifications > 0:
            print(f"✅ {modifications} mots mis en gras")
        else:
            print(f"⚠️ Aucun **mot** trouvé")
        
        return modifications
        
def main():
    """Point d'entrée CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TMC Universal CV Enricher')
    parser.add_argument('cv_path', help='Chemin du CV (PDF, Word, etc.)')
    parser.add_argument('jd_path', help='Chemin de la Job Description')
    parser.add_argument('--output', '-o', default='cv_enriched_tmc.docx', help='Fichier de sortie')
    
    args = parser.parse_args()
    
    try:
        enricher = TMCUniversalEnricher()
        
        print("\n🚀 TMC UNIVERSAL CV ENRICHER")
        print("=" * 60)
        
        # MODULE 1: Extraction
        print("\n[1/5] Extraction du CV...")
        cv_text = enricher.extract_cv_text(args.cv_path)
        print(f"      ✅ {len(cv_text)} caractères extraits")
        
        # MODULE 2: Parsing
        print("\n[2/5] Parsing intelligent...")
        parsed_cv = enricher.parse_cv_with_claude(cv_text)
        
        # MODULE 3: Enrichissement
        print("\n[3/5] Enrichissement avec IA...")
        jd_text = enricher.read_job_description(args.jd_path)
        enriched_cv = enricher.enrich_cv_with_prompt(parsed_cv, jd_text)
        
        # MODULE 4: Mapping TMC
        print("\n[4/5] Mapping structure TMC...")
        tmc_context = enricher.map_to_tmc_structure(parsed_cv, enriched_cv)
        
        # MODULE 5: Génération
        print("\n[5/5] Génération CV final...")
        enricher.generate_tmc_docx(tmc_context, args.output)
        
        # POST-PROCESSING: Application du gras
        print("\n[POST] Application du gras sur mots-clés...")
        keywords = enriched_cv.get('mots_cles_a_mettre_en_gras', [])
        print(f"   Mots-clés à mettre en gras: {keywords}")
        
        if keywords:
            result = enricher.apply_bold_post_processing(args.output, keywords)
            if result == 0:
                print("   ⚠️ AUCUN mot-clé n'a été mis en gras!")
                print("   Vérifiez que les mots-clés sont bien dans le CV")
        else:
            print("   ⚠️ Aucun mot-clé retourné par l'IA")
        
        # RÉSUMÉ FINAL
        print("\n" + "=" * 60)
        print("🎉 ENRICHISSEMENT TERMINÉ!")
        print("=" * 60)
        print(f"📊 Score matching: {enriched_cv.get('score_matching', 0)}/100")
        print(f"💪 Points forts:")
        for pf in enriched_cv.get('points_forts', [])[:3]:
            print(f"   • {pf}")
        print(f"\n📄 Fichier généré: {args.output}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
