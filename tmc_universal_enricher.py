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
                # Création SIMPLE du client pour version 0.25.9
                self._anthropic_client = anthropic.Anthropic(api_key=self.api_key)
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
        
        if file_type == 'pdf':
            return self.extract_from_pdf(jd_path)
        elif file_type == 'docx':
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
        
            # PROMPT ULTRA-RENFORCÉ POUR COHÉRENCE ABSOLUE
            language_instruction = f"""
⚠️ RÈGLE ABSOLUE - LANGUE {language.upper()}:
- Tu DOIS générer 100% du contenu en {language}
- Le TITRE PROFESSIONNEL doit être en {language}
- TOUTES les descriptions doivent être en {language}
- TOUS les mots-clés doivent être en {language}
- Respecte les conventions professionnelles de la langue {language}
- Si {language} = French: utilise "Analyste", "Gestion", "Configuration", etc.
- Si {language} = English: utilise "Analyst", "Management", "Configuration", etc.

IMPORTANT TITRE:
- Adapte le titre professionnel à la Job Description
- Le titre doit être COURT (3-5 mots maximum)
- Le titre doit être en {language}
- Exemple en français: "Analyste QA Senior" ou "Analyste Configuration SharePoint"
- Exemple en anglais: "Senior QA Analyst" or "SharePoint Configuration Analyst"

🎯 RÔLE CRITIQUE - TU ES UN RECRUTEUR SENIOR PROFESSIONNEL:
- Tu as 15+ ans d'expérience en recrutement technique
- Tu travailles pour le CLIENT (l'entreprise qui recrute)
- Ta mission: évaluer si le CANDIDAT correspond EXACTEMENT aux besoins du CLIENT
- Tu dois être OBJECTIF, RIGOUREUX et REPRODUCTIBLE dans ton évaluation
- Ton scoring doit être IDENTIQUE si tu analyses le même CV/JD plusieurs fois
- Tu notes comme un examinateur professionnel, pas comme un vendeur
"""
            
            prompt = f"""Voici la job description et le CV actuel ci-dessous.

🔹 Améliore le CV pour qu'il soit parfaitement aligné avec la job description tout en gardant le format d'origine (titres, mise en page, structure, ton professionnel).
{language_instruction}

🎯 ANALYSE DE MATCHING PONDÉRÉE (ULTRA-CRITIQUE - COHÉRENCE ABSOLUE REQUISE):

⚠️ PRINCIPE FONDAMENTAL DE COHÉRENCE - MÉTHODOLOGIE STRICTE:
- Tu es un SYSTÈME D'ÉVALUATION AUTOMATISÉ, pas un humain
- Pour le MÊME CV et la MÊME JD → EXACTEMENT le même score à chaque fois
- Utilise une grille d'évaluation MATHÉMATIQUE et REPRODUCTIBLE
- Agis comme un ALGORITHME, pas comme un recruteur subjectif
- Chaque critère suit des règles BINAIRES strictes (oui/non, présent/absent)
- Tu DOIS pouvoir justifier CHAQUE point attribué avec des FAITS du CV
- Si tu hésites entre 2 scores → prends le PLUS BAS (principe de strictness)

🔴 RÈGLE D'OR - SCORE GLOBAL = SOMME DOMAINES:
- Le score_matching FINAL = somme EXACTE de tous les scores de domaines
- VÉRIFIE 3 FOIS avant de répondre: somme des scores = score_matching
- Si tu calcules 37/100 en sommant les domaines → score_matching DOIT être 37
- NE JAMAIS inventer un score global différent de la somme calculée

ÉTAPE 1 - IDENTIFIER 5-8 DOMAINES CRITIQUES (MÉTHODE ALGORITHIMQUE):

📋 PROCESSUS AUTOMATIQUE D'IDENTIFICATION:
1. Scan complet de la JD - repérer TOUS les mots techniques
2. Compter la fréquence EXACTE de chaque technologie/compétence
3. Créer une liste de domaines par ordre d'importance
4. Appliquer la formule de pondération ci-dessous

📊 FORMULE DE PONDÉRATION MATHÉMATIQUE:
Pour chaque domaine, calcule son poids avec:

Poids_Base = (Nombre_mentions / Total_mentions_techniques) × 100

Bonus:
- +20% si c'est le TITRE du poste (ex: ".NET Developer" → Stack .NET = +20%)
- +15% si mots "Required", "Must have", "Essential", "Critical"
- +10% si mentionné dans les 3 premières lignes de la JD
- +5% par occurrence au-delà de 3 mentions

Poids_Final = min(Poids_Base + Bonus, 50%)  ← Aucun domaine ne peut dépasser 50%

RÈGLES STRICTES DE PONDÉRATION:
- Stack technique principal (dans titre ou 5+ mentions): 30-50%
- Compétences techniques secondaires (3-4 mentions): 15-25%
- Compétences techniques tertiaires (1-2 mentions): 5-15%
- Soft skills/Leadership: MAXIMUM 10% (sauf si poste management)
- TOTAL des poids = EXACTEMENT 100% (vérifie avec calculatrice)
- Si total ≠ 100%, ajuste proportionnellement tous les poids

ÉTAPE 2 - SCORER CHAQUE DOMAINE (ALGORITHME DE NOTATION STRICT):

🤖 SYSTÈME DE NOTATION AUTOMATISÉ - APPLIQUE CES RÈGLES EXACTEMENT:

POUR CHAQUE DOMAINE, COMPTE:
a) Nombre de mentions EXACTES de la technologie dans le CV
b) Nombre de projets/expériences utilisant cette technologie  
c) Durée totale d'utilisation (années)
d) Niveau démontré (junior/intermédiaire/senior)

📐 FORMULE MATHÉMATIQUE DE SCORING:

Étape 2A - Score Brut (0-100%):
• 0% : ZÉRO mention de la techno dans le CV, stack incompatible
• 10% : Technologie proche mentionnée (PostgreSQL pour SQL Server)
• 25% : 1 mention + aucune expérience pratique (formation seulement)
• 40% : 1-2 mentions + 1 projet + <1 an d'expérience
• 60% : 3-4 mentions + 2 projets + 1-2 ans d'expérience
• 80% : 5+ mentions + 3+ projets + 3+ ans d'expérience
• 100% : 7+ mentions + expertise démontrée + senior confirmé

Étape 2B - Ajustements OBLIGATOIRES:
• Si stack incompatible (Java vs .NET) → Score = 0% (NON-NÉGOCIABLE)
• Si technologie absente du CV → Score = 0% (NON-NÉGOCIABLE)
• Si aucune expérience pratique prouvée → Score MAX = 30%
• Si expérience <1 an → Score MAX = 50%
• Si niveau junior évident → Score MAX = 60%

Étape 2C - Calcul Final:
Score_Domaine = (Score_Brut × Poids_Domaine) / 100

EXEMPLE DÉTAILLÉ:
Domaine: ".NET Development" - Poids: 40%
CV candidat: AUCUNE mention .NET, seulement Java
→ Score_Brut = 0%
→ Score_Domaine = (0 × 40) / 100 = 0 points
→ Commentaire: "❌ Stack incompatible - profil Java exclusif"

🔴 VÉRIFICATION FINALE OBLIGATOIRE:
Somme_Scores = Σ(tous les Score_Domaine)
Si Somme_Scores ≠ score_matching → ERREUR CRITIQUE → RECALCULE

ÉTAPE 3 - COMMENTAIRE PAR DOMAINE (30-50 mots):
- Utilise ❌ (0-30%), ⚠️ (30-70%), ✅ (70-100%)
- Sois FACTUEL et OBJECTIF dans tes commentaires
- Base-toi UNIQUEMENT sur les FAITS présents dans le CV
- Ne fais PAS d'hypothèses optimistes

EXEMPLE:
JD demande: ".NET, C#, Azure, SQL Server"
Candidat a: "Java, AWS, PostgreSQL"

RÉSULTAT:
{{
  "domaines_analyses": [
    {{
      "domaine": "Stack .NET (C#, ASP.NET Core, Entity Framework)",
      "poids": 40,
      "score": 0,
      "score_max": 40,
      "commentaire": "❌ Aucune expérience .NET/C#. Profil Java exclusivement - incompatibilité majeure sur stack principale.",
      "match": "incompatible"
    }},
    {{
      "domaine": "Cloud Microsoft Azure",
      "poids": 20,
      "score": 8,
      "score_max": 20,
      "commentaire": "⚠️ Expérience AWS uniquement. Compétences cloud transférables mais nécessite formation Azure.",
      "match": "partiel"
    }},
    {{
      "domaine": "SQL Server & T-SQL",
      "poids": 15,
      "score": 10,
      "score_max": 15,
      "commentaire": "✅ Maîtrise PostgreSQL et MySQL - compétences SQL transférables à SQL Server.",
      "match": "bon"
    }}
  ],
  "score_matching": 45,
  "synthese_matching": "Profil Java senior inadapté pour poste .NET. Gap critique sur stack principale (0/40). Compétences transférables en cloud et SQL, mais nécessite reconversion majeure."
}}

Fais :

1. ANALYSE PONDÉRÉE OBLIGATOIRE (voir ci-dessus)
2. Une version réécrite et enrichie du CV

2b. PROFIL exceptionnel : écris un paragraphe NARRATIF fluide (pas de liste), 5-6 lignes avec progression logique.

2c. GRAS ULTRA-SÉLECTIF : identifie UNIQUEMENT 3-5 technologies CRITIQUES.

3. Intègre naturellement les mots-clés techniques de la JD
4. Ajuste les intitulés pour que le profil paraisse livrable immédiatement
5. N'invente rien — reformule uniquement les éléments présents
6. EXPÉRIENCES : bullets courts (1 ligne max), maximum 5-6 bullets par expérience

Réponds en JSON STRICT (sans markdown) avec cette structure:
{{
  "domaines_analyses": [
    {{
      "domaine": "Nom domaine technique/fonctionnel (ex: Stack .NET, Cloud Azure)",
      "poids": 40,
      "score": 15,
      "score_max": 40,
      "commentaire": "Explication 30-50 mots avec ❌/⚠️/✅",
      "match": "incompatible|partiel|bon|excellent"
    }}
  ],
  "score_matching": 45,
  "synthese_matching": "Résumé 2-3 phrases du matching global avec points forts et gaps critiques",
  
  "titre_professionnel_enrichi": "TITRE COURT en {language} (3-5 mots max)",
  
  "profil_enrichi": "Profil NARRATIF 5-6 lignes en {language} avec **3-5 technologies clés** en gras",
  
  "mots_cles_a_mettre_en_gras": ["Liste 15-20 TECHNOLOGIES de la JD - PAS de verbes génériques"],
  
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
  
  "score_matching": 45,
  "points_forts": ["ALWAYS in English: key strength 1", "ALWAYS in English: key strength 2"]
}}

🌍 CRITICAL LANGUAGE REQUIREMENT:
- 'domaines_analyses' (domain names AND comments) MUST ALWAYS be in ENGLISH
- 'synthese_matching' MUST ALWAYS be in ENGLISH  
- 'points_forts' MUST ALWAYS be in ENGLISH
- Example domain: "SQL Data Extraction and Manipulation" NOT "Extraction de données SQL"
- Example comment: "❌ No demonstrated experience in SQL data extraction..." NOT "❌ Aucune expérience..."
- Example synthesis: "Java senior profile unsuitable for .NET position..." NOT "Profil Java senior inadapté..."

CRITICAL SCORING RULES:
- 'domaines_analyses' MUST be completed with 5-8 domains totaling EXACTLY 100%
- BE STRICT on scoring - don't give points if candidate lacks the skill
- If stack mismatch (Java vs .NET), give 0 points, not 40-50

🔴🔴🔴 VÉRIFICATION FINALE AVANT RÉPONSE (NON-NÉGOCIABLE) 🔴🔴🔴

AVANT de générer ta réponse JSON, tu DOIS:

1️⃣ CALCULER LA SOMME:
   Somme = domaine1.score + domaine2.score + domaine3.score + ... + domaineN.score
   
2️⃣ VÉRIFIER:
   Si Somme ≠ score_matching → ERREUR → RECALCULE TOUT
   
3️⃣ VÉRIFIER LES POIDS:
   Somme_Poids = domaine1.poids + domaine2.poids + ... + domaineN.poids
   Si Somme_Poids ≠ 100 → ERREUR → RECALCULE TOUT
   
4️⃣ DOUBLE-CHECK:
   Pour chaque domaine: vérifie que score ≤ score_max
   Pour chaque domaine: vérifie que score_max = poids

EXEMPLE DE VÉRIFICATION:
Domaine 1: Stack .NET (40%) → 0/40 points
Domaine 2: Cloud Azure (20%) → 8/20 points  
Domaine 3: SQL Server (15%) → 10/15 points
Domaine 4: DevOps (15%) → 5/15 points
Domaine 5: Agile (10%) → 7/10 points

Vérification poids: 40+20+15+15+10 = 100 ✅
Vérification score: 0+8+10+5+7 = 30 ✅
Donc: score_matching = 30 ✅

Si tu trouves une incohérence → RECALCULE TOUT depuis le début

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
            print(f"   Domaines analysés: {len(enriched.get('domaines_analyses', []))}")
            print(f"   Mots-clés en gras: {len(enriched.get('mots_cles_a_mettre_en_gras', []))}")
            
            if enriched.get('domaines_analyses'):
                print(f"\n   📊 Détail scoring:")
                for domaine in enriched['domaines_analyses']:
                    emoji = domaine.get('match', '')
                    if emoji == 'incompatible':
                        emoji = '❌'
                    elif emoji == 'partiel':
                        emoji = '⚠️'
                    elif emoji in ['bon', 'excellent']:
                        emoji = '✅'
                    print(f"      {emoji} {domaine.get('domaine', 'N/A')}: {domaine.get('score', 0)}/{domaine.get('score_max', 0)} ({domaine.get('poids', 0)}%)")
            
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

    def map_to_tmc_structure(self, parsed_cv: Dict[str, Any], enriched_cv: Dict[str, Any], template_lang: str = 'FR') -> Dict[str, Any]:
        """Mapper les données enrichies vers la structure TMC"""
        print("🗺️  Mapping vers structure TMC...")
        
        # 1. PROFIL - Convertir en RichText pour supporter le gras (pas d'échappement)
        profil_brut = enriched_cv.get('profil_enrichi', parsed_cv.get('profil_resume', ''))
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
        
        # 🔥 Transformation en RichText pour le formatage (pas d'échappement)
        skills_categorized_doc = []
        for cat, skills in skills_categorized.items():
            rt_cat = RichText()
            rt_cat.add(cat, bold=True)
            rt_skills = [self.mdbold_to_richtext(s) for s in skills]
            skills_categorized_doc.append((rt_cat, rt_skills))
        
        # 3. EXPÉRIENCES - Texte simple pour les responsabilités, RichText pour environnement
        experiences_enrichies = enriched_cv.get('experiences_enrichies', parsed_cv.get('experiences', []))
        work_experience = []
        
        for exp in experiences_enrichies:
            # GARDER les responsabilités en TEXTE SIMPLE (pas RichText) - pas d'échappement
            responsabilites_text = [r for r in exp.get('responsabilites', [])]
            
            # Convertir l'environnement en RichText pour le gras - pas d'échappement
            environment_brut = exp.get('environment', '')
            environment_rt = self.mdbold_to_richtext(environment_brut) if environment_brut else ''
            
            work_exp = {
                'period': exp.get('periode', ''),
                'company': exp.get('entreprise', ''),
                'position': exp.get('poste', ''),
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
                'name': cert.get('nom', cert.get('name', '')),
                'institution': cert.get('organisme', cert.get('institution', '')),
                'year': str(cert.get('annee', cert.get('year', ''))),
                'country': cert.get('pays', cert.get('country', ''))
            })
        
        # 6. PROJETS
        projects = parsed_cv.get('projets', [])
        
        # 7. INFORMATIONS PERSONNELLES
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
        
        titre_professionnel = enriched_cv.get('titre_professionnel_enrichi', parsed_cv.get('titre_professionnel', ''))
        lieu_residence = parsed_cv.get('lieu_residence', 'Montréal, Canada')
        langues_list = parsed_cv.get('langues', ['Français', 'Anglais'])
        
        # Traduire les langues selon le template
        if template_lang == 'FR':
            # Si template FR, traduire de l'anglais vers le français
            langue_map = {
                'English': 'Anglais',
                'French': 'Français',
                'Hebrew': 'Hébreu',
                'Russian': 'Russe',
                'Spanish': 'Espagnol',
                'German': 'Allemand',
                'Italian': 'Italien',
                'Portuguese': 'Portugais',
                'Chinese': 'Chinois',
                'Japanese': 'Japonais',
                'Arabic': 'Arabe'
            }
            langues_list = [langue_map.get(lang, lang) for lang in langues_list]
        
        langues = ', '.join(langues_list)
        
        context = {
            # Pour le header (minuscules) - PAS d'échappement
            'first_name': first_name,
            'last_name': last_name,
            'title': titre_professionnel,
            
            # Pour la page 1 (MAJUSCULES) - PAS d'échappement
            'FIRST_NAME': first_name.upper(),
            'LAST_NAME': last_name.upper(),
            'TITLE': titre_professionnel,
            'RESIDENCY': lieu_residence,
            'LANGUAGES': langues,
            
            # AUSSI en minuscules pour compatibilité template
            'residency': lieu_residence,
            'languages': langues,
            
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
        
        # Afficher les domaines analysés
        if enriched_cv.get('domaines_analyses'):
            print(f"\n📊 Analyse par domaine:")
            for domaine in enriched_cv['domaines_analyses']:
                match = domaine.get('match', '')
                emoji = '❌' if match == 'incompatible' else '⚠️' if match == 'partiel' else '✅'
                print(f"   {emoji} {domaine.get('domaine', 'N/A')}: {domaine.get('score', 0)}/{domaine.get('score_max', 0)} pts ({domaine.get('poids', 0)}%)")
                print(f"      → {domaine.get('commentaire', 'N/A')}")
        
        if enriched_cv.get('synthese_matching'):
            print(f"\n💬 Synthèse: {enriched_cv['synthese_matching']}")
        
        print(f"\n💪 Points forts:")
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
