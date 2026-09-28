import os
import sys
import io
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.config import Config
from app.models import db

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_resume_data():
    return {
        'personal_info': {
            'full_name': 'Jane Doe',
            'title': 'Senior Backend Engineer',
            'email': 'jane.doe@example.com',
            'phone': '+1 (555) 234-5678',
            'location': 'Seattle, WA',
            'linkedin': 'linkedin.com/in/janedoe',
            'github': 'github.com/janedoe',
            'portfolio': 'janedoe.dev',
            'summary': 'Experienced Backend Engineer with 6 years building distributed APIs in Python and Flask.'
        },
        'skills': {
            'programming_languages': ['Python', 'SQL', 'Go'],
            'frameworks': ['Flask', 'FastAPI'],
            'databases': ['PostgreSQL', 'Redis'],
            'cloud': ['Docker', 'AWS'],
            'tools': ['Git', 'Linux'],
            'all': ['Python', 'SQL', 'Go', 'Flask', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker', 'AWS', 'Git', 'Linux']
        },
        'experience': [
            {
                'position': 'Backend Engineer',
                'company': 'Tech Corp',
                'start_date': '2021',
                'end_date': 'Present',
                'description': 'Engineered scalable RESTful APIs with Flask and PostgreSQL. Reduced latency by 25%.'
            }
        ],
        'projects': [
            {
                'name': 'Cloud Scaler',
                'technologies': 'Python, Docker, Redis',
                'github': 'github.com/janedoe/scaler',
                'description': 'Architected microservices worker system handling 10,000 tasks per minute.'
            }
        ],
        'education': [
            {
                'institution': 'University of Washington',
                'degree': 'B.S. in Computer Science',
                'start_date': '2016',
                'end_date': '2020',
                'cgpa': '3.9'
            }
        ]
    }

@pytest.fixture
def sample_raw_text():
    return """Jane Doe
Senior Backend Engineer
jane.doe@example.com | +1 (555) 234-5678 | Seattle, WA
LinkedIn: linkedin.com/in/janedoe | GitHub: github.com/janedoe

PROFESSIONAL SUMMARY
Experienced Backend Engineer with 6 years building distributed APIs in Python and Flask.

TECHNICAL SKILLS
Languages: Python, SQL, Go
Frameworks: Flask, FastAPI
Databases: PostgreSQL, Redis
Cloud & Tools: Docker, AWS, Git, Linux

EXPERIENCE
Backend Engineer — Tech Corp
2021 – Present | Seattle, WA
• Engineered scalable RESTful APIs with Flask and PostgreSQL.
• Reduced query latency by 25% across 50,000 daily requests.
• Orchestrated automated container deployments with Docker and CI/CD.

PROJECTS
Cloud Scaler | Python, Docker, Redis
github.com/janedoe/scaler
• Architected microservices worker system handling 10,000 tasks per minute.

EDUCATION
B.S. in Computer Science — University of Washington
2016 – 2020 | CGPA: 3.9 / 4.0
"""

@pytest.fixture
def sample_pdf_bytes(sample_resume_data):
    from app.services.pdf_service import PDFService
    stream = PDFService.generate_resume_pdf(sample_resume_data, template='modern')
    return stream.getvalue()
