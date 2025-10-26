# 🚀 TMC CV Optimizer

**Professional CV optimization powered by Claude AI**

Generate TMC-formatted CVs perfectly aligned with job descriptions.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

## ✨ Features

- 📄 **Multi-format support**: PDF, DOCX, DOC, TXT
- 🌍 **Bilingual**: French & English CV generation
- 🔒 **Anonymous mode**: Option to anonymize candidate information
- 🤖 **AI-powered**: Claude Sonnet 4.5 for intelligent analysis
- 📊 **Weighted matching**: Domain-by-domain scoring with detailed analysis
- 💪 **Key strengths identification**: Automatic highlighting
- 🎨 **Professional templates**: TMC-branded DOCX with logo

---

## 🏗️ Project Structure
```
cv-optimizer/
├── app.py                              # Main Streamlit application
├── tmc_universal_enricher.py           # CV processing backend (Claude AI)
├── requirements.txt                    # Python dependencies
├── README.md                           # Documentation
├── .streamlit/
│   └── config.toml                     # Streamlit configuration
├── .devcontainer/                      # VS Code Dev Container
├── .gitignore                          # Git ignore rules
│
├── TMC_NA_template_FR.docx             # French template
├── TMC_NA_template_FR_Anonymisé.docx   # French anonymous template
├── TMC_NA_template_EN.docx             # English template
├── TMC_NA_template_EN_Anonymisé.docx   # English anonymous template
├── TMC big logo.png                    # TMC logo (large)
└── TMC mini logo.png                   # TMC logo (small)
```

---

## 🚀 Deployment

### Render.com (Recommended)

1. Fork or clone this repository
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variables:
   - `ANTHROPIC_API_KEY`: Your Claude API key
   - `APP_PASSWORD`: Login password
   - `AIRTABLE_API_KEY`: (Optional) For analytics tracking
6. Deploy! 🎉

### Local Development
```bash
# Clone repository
git clone https://github.com/KAbecassis/cv-optimizer.git
cd cv-optimizer

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-api-key"
export APP_PASSWORD="your-password"

# Run application
streamlit run app.py
```

---

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key from Anthropic | ✅ Yes |
| `APP_PASSWORD` | Password for accessing the app | ✅ Yes |
| `AIRTABLE_API_KEY` | For usage analytics (optional) | ⚠️ Optional |

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Engine**: Anthropic Claude Sonnet 4.5
- **Document Processing**: python-docx, docxtpl, PyPDF2
- **Template Engine**: Jinja2

---

## 📊 Features Breakdown

### 1. Intelligent CV Parsing
- Extracts structured data from any CV format
- Identifies experience, education, skills, languages

### 2. Weighted Matching Analysis
- Domain-by-domain comparison with job description
- Customizable weights per domain
- Detailed scoring with comments

### 3. AI-Powered Enrichment
- Rewrites experience bullets to match JD keywords
- Enhances professional titles
- Identifies transferable skills
- Bilingual optimization (FR/EN)

### 4. Anonymous Mode
- Removes personal information (name, contact)
- Complies with blind recruitment requirements
- Optional toggle (enabled/disabled)

### 5. Professional TMC Formatting
- Generates Word documents with TMC branding
- Automatic bold keywords highlighting
- Clean, recruiter-friendly layout

---

## 🔒 Privacy & Security

- ✅ All processing is done in-memory
- ✅ No data stored permanently
- ✅ Files automatically deleted after generation
- ✅ Secure API communication with Anthropic
- ✅ Authentication required (password protected)

---

## 📈 Usage Analytics

Optional Airtable integration tracks:
- Candidate name (anonymized if needed)
- Matching scores
- Language selection
- User location
- Processing time & token usage

---

## 👨‍💻 Author

**Kevin Abecassis**  
Business Manager & Automation Specialist @ TMC

---

## 📝 Version History

- **v1.3.2** (Current) - Anonymous mode + bilingual support
- **v1.3.1** - Two-step generation workflow
- **v1.3.0** - Client selector feature
- **v1.0** - Initial production release

---

## 📄 License

Internal TMC use only - All rights reserved

---

**Made with ❤️ for TMC Recruiters**
```

4. **Scroll en bas → Message de commit :** `docs: improve README with complete documentation`
5. **Cliquez "Commit changes"**

---

### **ÉTAPE 3 : Créer une structure de branches (Optionnel mais PRO)**

Si tu veux être vraiment organisé, crée des branches :

1. **Va dans ton repo → Clique sur "main" (en haut à gauche)**
2. **Dans le champ "Find or create a branch", tape :** `production`
3. **Clique "Create branch: production from main"**
4. **Répète pour créer une branche :** `test`

**Structure recommandée :**
- `main` → Code stable, synchronisé avec prod
- `test` → Version de test pour expérimenter
- `production` → Version actuellement déployée sur Render

---

## ✅ RÉSULTAT FINAL

Après ces actions, ton GitHub aura cette structure **propre** :
```
cv-optimizer/
├── .devcontainer/
├── .streamlit/
├── .gitignore
├── README.md ⭐ (amélioré)
├── requirements.txt
├── app.py
├── tmc_universal_enricher.py
├── TMC_NA_template_EN.docx
├── TMC_NA_template_EN_Anonymisé.docx
├── TMC_NA_template_FR.docx
├── TMC_NA_template_FR_Anonymisé.docx
├── TMC big logo.png
└── TMC mini logo.png
