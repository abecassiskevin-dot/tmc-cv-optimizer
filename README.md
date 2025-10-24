# 🚀 TMC CV Optimizer

**Professional CV optimization tool powered by Claude AI**

Generate TMC-formatted CVs perfectly aligned with job descriptions in French or English.

> 🧪 **MCP Test Badge** - This line was added via Claude MCP GitHub integration!

## ✨ Features

- 📄 **Multi-format support**: PDF, DOCX, DOC, TXT
- 🌍 **Bilingual**: French & English CV generation
- 🤖 **AI-powered**: Claude Sonnet 4.5 for intelligent parsing and optimization
- 📊 **Matching score**: Get alignment percentage with job description
- 💪 **Key strengths**: Automatic identification of candidate strengths
- 🎨 **Professional design**: TMC-branded templates

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: Anthropic Claude API
- **Document Processing**: python-docx, docxtpl, PyPDF2
- **Template Engine**: Jinja2

## 🚀 Quick Start

### Local Installation

```bash
# Clone repository
git clone https://github.com/abecassiskevin-dot/tmc-cv-optimizer.git
cd tmc-cv-optimizer

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Run app
streamlit run app.py
```

### Usage

1. Upload your resume (PDF, DOCX, DOC, or TXT)
2. Upload the job description
3. Select output language (French or English)
4. Click "Generate my TMC CV"
5. Download your optimized TMC CV!

## 📝 Configuration

### API Key Setup

For local development, set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

For Streamlit Cloud deployment, add it in the Secrets management section.

## 📂 Project Structure

```
tmc-cv-optimizer/
├── app.py                      # Main Streamlit application
├── tmc_universal_enricher.py   # CV processing backend
├── TMC_NA_template_FR.docx     # French template
├── TMC_NA_template_EN.docx     # English template
├── TMC big logo.png            # TMC logo
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

## 🔐 Security & Privacy

- All processing is done in-memory
- Files are automatically deleted after processing
- No data is stored permanently
- Secure API communication with Anthropic

## 👨‍💻 Author

**Kevin Abecassis**  
TMC Business Manager & Automation Specialist

## 📄 License

Internal TMC use only

---

Made by Kevin ABECASSIS
