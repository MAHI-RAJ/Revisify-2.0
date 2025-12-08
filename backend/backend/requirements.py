"""Programmatic dependency list (optional helper)"""
REQUIREMENTS = [
    "Flask==3.0.0",
    "Flask-SQLAlchemy==3.1.1",
    "Flask-JWT-Extended==4.6.0",
    "Flask-Mail==0.10.0",
    "Flask-CORS==4.0.0",
    "Werkzeug==3.0.1",
    "python-dotenv==1.0.0",
    "pdfplumber==0.10.3",
    "pypdf==3.17.4",
    "python-pptx==0.6.23",
    "python-docx==1.1.0",
    "openai==1.12.0",
    "anthropic==0.18.1",
    "sentence-transformers==2.2.2",
    "faiss-cpu==1.7.4",
    "numpy==1.26.3",
    "requests==2.31.0",
]


def as_pip_args():
    """Return requirements as pip install arguments"""
    return REQUIREMENTS

