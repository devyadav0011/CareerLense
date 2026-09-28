from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    title = db.Column(db.String(150), nullable=False, default='Untitled Resume')
    filename = db.Column(db.String(255), nullable=True)
    raw_text = db.Column(db.Text, nullable=True)
    structured_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    analyses = db.relationship('ResumeAnalysis', backref='resume', lazy=True, cascade='all, delete-orphan')
    job_matches = db.relationship('JobMatch', backref='resume', lazy=True, cascade='all, delete-orphan')
    suggestions = db.relationship('ResumeSuggestion', backref='resume', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'filename': self.filename,
            'raw_text': self.raw_text,
            'structured_data': self.structured_data or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analyses'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    overall_score = db.Column(db.Integer, nullable=False, default=0)
    content_score = db.Column(db.Integer, nullable=False, default=0)
    skills_score = db.Column(db.Integer, nullable=False, default=0)
    projects_score = db.Column(db.Integer, nullable=False, default=0)
    experience_score = db.Column(db.Integer, nullable=False, default=0)
    education_score = db.Column(db.Integer, nullable=False, default=0)
    formatting_score = db.Column(db.Integer, nullable=False, default=0)
    completeness_score = db.Column(db.Integer, nullable=False, default=0)
    ats_style_score = db.Column(db.Integer, nullable=False, default=0)
    score_breakdown = db.Column(db.JSON, nullable=True)
    strengths = db.Column(db.JSON, nullable=True)
    weaknesses = db.Column(db.JSON, nullable=True)
    missing_items = db.Column(db.JSON, nullable=True)
    ats_issues = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'overall_score': self.overall_score,
            'content_score': self.content_score,
            'skills_score': self.skills_score,
            'projects_score': self.projects_score,
            'experience_score': self.experience_score,
            'education_score': self.education_score,
            'formatting_score': self.formatting_score,
            'completeness_score': self.completeness_score,
            'ats_style_score': self.ats_style_score,
            'score_breakdown': self.score_breakdown or {},
            'strengths': self.strengths or [],
            'weaknesses': self.weaknesses or [],
            'missing_items': self.missing_items or [],
            'ats_issues': self.ats_issues or [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class JobMatch(db.Model):
    __tablename__ = 'job_matches'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    job_title = db.Column(db.String(150), nullable=True)
    job_description = db.Column(db.Text, nullable=False)
    match_score = db.Column(db.Integer, nullable=False, default=0)
    score_breakdown = db.Column(db.JSON, nullable=True)
    matched_skills = db.Column(db.JSON, nullable=True)
    missing_skills = db.Column(db.JSON, nullable=True)
    keyword_analysis = db.Column(db.JSON, nullable=True)
    suggestions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_title': self.job_title,
            'match_score': self.match_score,
            'score_breakdown': self.score_breakdown or {},
            'matched_skills': self.matched_skills or [],
            'missing_skills': self.missing_skills or [],
            'keyword_analysis': self.keyword_analysis or [],
            'suggestions': self.suggestions or [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ResumeSuggestion(db.Model):
    __tablename__ = 'resume_suggestions'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    section = db.Column(db.String(50), nullable=False)
    issue = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    suggestion = db.Column(db.Text, nullable=False)
    example_improvement = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'section': self.section,
            'issue': self.issue,
            'reason': self.reason,
            'suggestion': self.suggestion,
            'example_improvement': self.example_improvement,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
