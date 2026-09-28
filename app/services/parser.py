import re
import os
from typing import Dict, Any, List, Optional
from ..utils.helpers import clean_text

# Comprehensive skill dictionaries for categorizing technical & soft skills
SKILL_TAXONOMY = {
    'programming_languages': [
        'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'c', 'go', 'golang',
        'rust', 'php', 'ruby', 'swift', 'kotlin', 'dart', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash'
    ],
    'frameworks': [
        'react', 'react.js', 'reactjs', 'vue', 'vue.js', 'angular', 'next.js', 'nextjs', 'nuxt.js',
        'flask', 'django', 'fastapi', 'spring boot', 'express', 'express.js', 'node.js', 'nodejs',
        'laravel', 'asp.net', 'ruby on rails', 'flutter', 'react native', 'tailwind css', 'bootstrap',
        'jquery', 'redux', 'graphql'
    ],
    'databases': [
        'sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'redis', 'cassandra',
        'dynamodb', 'mariadb', 'oracle', 'firebase', 'firestore', 'supabase', 'elasticsearch'
    ],
    'cloud': [
        'aws', 'amazon web services', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes',
        'terraform', 'ci/cd', 'github actions', 'jenkins', 'gitlab ci', 'heroku', 'vercel', 'netlify'
    ],
    'tools': [
        'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'figma', 'postman',
        'linux', 'vim', 'vs code', 'docker', 'npm', 'webpack', 'vite', 'pycharm'
    ],
    'soft_skills': [
        'leadership', 'teamwork', 'communication', 'problem solving', 'critical thinking',
        'adaptability', 'collaboration', 'time management', 'project management', 'agile', 'scrum'
    ]
}

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF using PyMuPDF (pymupdf/fitz) or pypdf fallback."""
    text = ""
    # Try pymupdf / fitz first
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open(filepath)
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        doc.close()
        if text.strip():
            return clean_text(text)
    except Exception:
        pass

    # Fallback to pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        if text.strip():
            return clean_text(text)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    if not text.strip():
        raise ValueError("The uploaded PDF appears to be empty or contains scanned images without selectable text.")

    return clean_text(text)

def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(filepath)
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
        extracted = "\n".join(full_text)
        if not extracted.strip():
            raise ValueError("The DOCX file is empty.")
        return clean_text(extracted)
    except Exception as e:
        raise ValueError(f"Failed to read DOCX file: {str(e)}")


class ResumeParser:
    """Parses raw resume text into structured fields and detects sections."""

    @classmethod
    def parse_file(cls, filepath: str) -> Dict[str, Any]:
        ext = filepath.rsplit('.', 1)[-1].lower()
        if ext == 'pdf':
            raw_text = extract_text_from_pdf(filepath)
        elif ext == 'docx':
            raw_text = extract_text_from_docx(filepath)
        else:
            raise ValueError(f"Unsupported file format: .{ext}")

        structured = cls.parse_text(raw_text)
        return {
            'raw_text': raw_text,
            'structured_data': structured
        }

    @classmethod
    def parse_text(cls, text: str) -> Dict[str, Any]:
        text = clean_text(text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        contact_info = cls.extract_contact_info(text, lines)
        sections = cls.split_sections(text)

        skills = cls.extract_skills(text)
        education = cls.extract_education(sections.get('education', ''))
        experience = cls.extract_experience(sections.get('experience', ''))
        projects = cls.extract_projects(sections.get('projects', ''))
        certifications = cls.extract_certifications(sections.get('certifications', ''))
        achievements = cls.extract_achievements(sections.get('achievements', ''))
        summary = sections.get('summary', '') or contact_info.get('summary', '')

        return {
            'personal_info': {
                'full_name': contact_info.get('full_name', ''),
                'title': contact_info.get('title', ''),
                'email': contact_info.get('email', ''),
                'phone': contact_info.get('phone', ''),
                'location': contact_info.get('location', ''),
                'linkedin': contact_info.get('linkedin', ''),
                'github': contact_info.get('github', ''),
                'portfolio': contact_info.get('portfolio', ''),
                'summary': summary
            },
            'education': education,
            'skills': skills,
            'experience': experience,
            'projects': projects,
            'certifications': certifications,
            'achievements': achievements,
            'detected_sections': list(sections.keys())
        }

    @classmethod
    def extract_contact_info(cls, text: str, lines: List[str]) -> Dict[str, str]:
        info = {
            'full_name': '',
            'title': '',
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'github': '',
            'portfolio': '',
            'summary': ''
        }

        # 1. Email extraction
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
        if email_match:
            info['email'] = email_match.group(0)

        # 2. Phone extraction (international and local formats)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            info['phone'] = phone_match.group(0).strip()

        # 3. LinkedIn
        linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?', text, re.IGNORECASE)
        if linkedin_match:
            info['linkedin'] = linkedin_match.group(0).strip()

        # 4. GitHub
        github_match = re.search(r'(https?://)?(www\.)?github\.com/[A-Za-z0-9_-]+/?', text, re.IGNORECASE)
        if github_match:
            info['github'] = github_match.group(0).strip()

        # 5. Portfolio / personal website
        portfolio_match = re.search(r'(https?://)?(www\.)?([a-zA-Z0-9-]+\.)+(io|me|dev|app|tech|org|net|com)(/[a-zA-Z0-9_.-]+)*', text, re.IGNORECASE)
        if portfolio_match:
            match_str = portfolio_match.group(0).strip()
            if 'linkedin.com' not in match_str.lower() and 'github.com' not in match_str.lower():
                info['portfolio'] = match_str

        # 6. Candidate Name Detection
        # Usually the very first 1-2 non-empty lines before section headers
        for line in lines[:5]:
            clean_line = line.strip()
            # Ignore emails, phones, URLs
            if '@' in clean_line or 'http' in clean_line or 'linkedin' in clean_line.lower() or 'github' in clean_line.lower():
                continue
            if len(clean_line.split()) in [2, 3, 4] and re.match(r'^[A-Z][a-zA-Z\.\s\'-]+$', clean_line):
                # Don't pick section headings like "RESUME" or "CURRICULUM VITAE"
                if clean_line.upper() not in ['RESUME', 'CURRICULUM VITAE', 'CV', 'PROFILE', 'EXPERIENCE', 'EDUCATION']:
                    info['full_name'] = clean_line
                    break

        # 7. Professional Title (often next line after name if short)
        if info['full_name']:
            try:
                name_idx = lines.index(info['full_name'])
                if name_idx + 1 < len(lines):
                    candidate_title = lines[name_idx + 1]
                    if len(candidate_title.split()) <= 5 and '@' not in candidate_title and not re.search(r'\d', candidate_title):
                        info['title'] = candidate_title
            except Exception:
                pass

        # 8. Location heuristic (e.g. City, State or City, Country)
        loc_match = re.search(r'\b([A-Z][a-zA-Z]+(?:[\s-][A-Z][a-zA-Z]+)?),\s*([A-Z]{2}|[A-Z][a-zA-Z]+)\b', text)
        if loc_match:
            info['location'] = loc_match.group(0)

        return info

    @classmethod
    def split_sections(cls, text: str) -> Dict[str, str]:
        """Split raw text into known standard sections."""
        section_patterns = {
            'summary': r'(?:professional\s+summary|summary|profile|about\s+me|career\s+objective|objective)',
            'education': r'(?:education|academic\s+background|qualifications|academics)',
            'experience': r'(?:experience|work\s+experience|employment\s+history|professional\s+experience|internships)',
            'projects': r'(?:projects|personal\s+projects|academic\s+projects|key\s+projects)',
            'skills': r'(?:skills|technical\s+skills|core\s+competencies|technologies|expertise)',
            'certifications': r'(?:certifications|certificates|licenses|courses)',
            'achievements': r'(?:achievements|awards|honors|extracurricular|publications)'
        }

        # Build regex to find headers at start of line or with clear separation
        combined_pattern = r'(?im)^(?:\s*[\#\*\-]?\s*)(?P<sec>' + '|'.join(section_patterns.values()) + r')(?:\s*[:\-]|\s*$)'

        matches = list(re.finditer(combined_pattern, text))
        sections = {}

        if not matches:
            # Fallback: scan lines
            return cls._fallback_section_split(text, section_patterns)

        for i, match in enumerate(matches):
            header_text = match.group('sec').lower()
            # Identify which canonical section it matches
            sec_name = None
            for key, pat in section_patterns.items():
                if re.match(pat, header_text, re.IGNORECASE):
                    sec_name = key
                    break

            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sec_content = text[start:end].strip()
            if sec_name:
                sections[sec_name] = sec_content

        return sections

    @classmethod
    def _fallback_section_split(cls, text: str, patterns: Dict[str, str]) -> Dict[str, str]:
        lines = text.split('\n')
        current_sec = None
        sections = {}

        for line in lines:
            line_str = line.strip()
            found = False
            for sec, pat in patterns.items():
                if re.match(rf'^{pat}[:\s]*$', line_str, re.IGNORECASE):
                    current_sec = sec
                    sections[current_sec] = []
                    found = True
                    break
            if not found and current_sec:
                sections[current_sec].append(line_str)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    @classmethod
    def extract_skills(cls, text: str) -> Dict[str, List[str]]:
        """Extract and categorize skills into taxonomy."""
        text_lower = text.lower()
        extracted = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud': [],
            'tools': [],
            'soft_skills': [],
            'all': []
        }

        found_set = set()

        for category, skills_list in SKILL_TAXONOMY.items():
            for skill in skills_list:
                # Use word boundaries or symbol-safe matching
                escaped = re.escape(skill)
                # Ensure c++ or .net are matched correctly
                if escaped.endswith(r'\+') or escaped.endswith(r'\#'):
                    pattern = rf'(?:^|[\s,;/|•\(\)])({escaped})(?:$|[\s,;/|•\(\)])'
                else:
                    pattern = rf'\b{escaped}\b'

                if re.search(pattern, text_lower):
                    display_name = skill.title() if len(skill) > 3 and not skill.isupper() else skill.upper()
                    # Formatting custom names
                    custom_names = {
                        'javascript': 'JavaScript', 'typescript': 'TypeScript', 'python': 'Python',
                        'c++': 'C++', 'c#': 'C#', 'php': 'PHP', 'postgresql': 'PostgreSQL',
                        'mysql': 'MySQL', 'mongodb': 'MongoDB', 'sqlite': 'SQLite', 'react': 'React',
                        'react.js': 'React', 'reactjs': 'React', 'vue': 'Vue.js', 'vue.js': 'Vue.js',
                        'node.js': 'Node.js', 'nodejs': 'Node.js', 'express': 'Express.js',
                        'next.js': 'Next.js', 'aws': 'AWS', 'gcp': 'Google Cloud (GCP)', 'docker': 'Docker',
                        'kubernetes': 'Kubernetes', 'ci/cd': 'CI/CD', 'git': 'Git', 'github': 'GitHub',
                        'tailwind css': 'Tailwind CSS', 'graphql': 'GraphQL', 'rest apis': 'REST APIs'
                    }
                    formatted = custom_names.get(skill.lower(), display_name)
                    if formatted not in extracted[category]:
                        extracted[category].append(formatted)
                    if formatted not in found_set:
                        found_set.add(formatted)
                        extracted['all'].append(formatted)

        return extracted

    @classmethod
    def extract_education(cls, text: str) -> List[Dict[str, Any]]:
        entries = []
        if not text:
            return entries

        degree_keywords = [
            'Bachelor', 'B.Tech', 'B.E.', 'BS', 'B.S.', 'Master', 'M.Tech', 'MS', 'M.S.',
            'PhD', 'Doctorate', 'Associate', 'Diploma', 'Higher Secondary', 'Secondary'
        ]

        blocks = [b.strip() for b in re.split(r'\n{2,}|\n(?=[A-Z][a-zA-Z\s]+(?:University|College|Institute|School))', text) if b.strip()]

        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines:
                continue

            entry = {
                'institution': lines[0],
                'degree': '',
                'field': '',
                'start_date': '',
                'end_date': '',
                'cgpa': '',
                'percentage': '',
                'relevant_coursework': ''
            }

            # Check for degree keywords
            for line in lines:
                for kw in degree_keywords:
                    if re.search(rf'\b{re.escape(kw)}\b', line, re.IGNORECASE):
                        entry['degree'] = line
                        break
                if entry['degree']:
                    break

            # Date search
            date_match = re.search(r'\b(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|19\d{2}|Present|Current)\b', block, re.IGNORECASE)
            if date_match:
                entry['start_date'] = date_match.group(1)
                entry['end_date'] = date_match.group(2)

            # CGPA / Percentage
            cgpa_match = re.search(r'(?:cgpa|gpa)[\s:]*([0-9]\.[0-9]{1,2}(?:\s*/\s*10|\s*/\s*4)?)', block, re.IGNORECASE)
            if cgpa_match:
                entry['cgpa'] = cgpa_match.group(1)

            pct_match = re.search(r'([0-9]{2}(?:\.[0-9]+)?)\s*%', block)
            if pct_match:
                entry['percentage'] = pct_match.group(1) + '%'

            entries.append(entry)

        return entries

    @classmethod
    def extract_experience(cls, text: str) -> List[Dict[str, Any]]:
        entries = []
        if not text:
            return entries

        blocks = [b.strip() for b in re.split(r'\n{2,}|\n(?=[A-Z][a-zA-Z\s]+(?:Inc|LLC|Ltd|Corporation|Company|Technologies|Solutions|Labs))', text) if b.strip()]

        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines:
                continue

            entry = {
                'company': lines[0],
                'position': lines[1] if len(lines) > 1 and len(lines[1].split()) <= 6 else '',
                'location': '',
                'start_date': '',
                'end_date': '',
                'description': "\n".join(lines[2:]) if len(lines) > 2 else (lines[1] if len(lines) > 1 else '')
            }

            date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-9]{1,2}/)?\s*(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-9]{1,2}/)?\s*(20\d{2}|19\d{2}|Present|Current)\b', block, re.IGNORECASE)
            if date_match:
                entry['start_date'] = date_match.group(2)
                entry['end_date'] = date_match.group(4)

            entries.append(entry)

        return entries

    @classmethod
    def extract_projects(cls, text: str) -> List[Dict[str, Any]]:
        entries = []
        if not text:
            return entries

        blocks = [b.strip() for b in re.split(r'\n{2,}', text) if b.strip()]

        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines:
                continue

            entry = {
                'name': lines[0],
                'description': "\n".join(lines[1:]) if len(lines) > 1 else lines[0],
                'technologies': '',
                'github': '',
                'live_demo': ''
            }

            # Tech stack mention
            tech_match = re.search(r'(?:technologies|tech stack|built with|tools)[\s:]*([^\n]+)', block, re.IGNORECASE)
            if tech_match:
                entry['technologies'] = tech_match.group(1).strip()

            # Links
            gh_match = re.search(r'(https?://)?(www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', block)
            if gh_match:
                entry['github'] = gh_match.group(0)

            demo_match = re.search(r'(https?://[^\s]+)', block)
            if demo_match and (not entry['github'] or demo_match.group(0) != entry['github']):
                entry['live_demo'] = demo_match.group(0)

            entries.append(entry)

        return entries

    @classmethod
    def extract_certifications(cls, text: str) -> List[Dict[str, Any]]:
        entries = []
        if not text:
            return entries
        for line in text.split('\n'):
            line = line.strip().lstrip('•-* ')
            if line:
                entries.append({
                    'certification': line,
                    'issuer': '',
                    'date': '',
                    'credential_url': ''
                })
        return entries

    @classmethod
    def extract_achievements(cls, text: str) -> List[Dict[str, Any]]:
        entries = []
        if not text:
            return entries
        for line in text.split('\n'):
            line = line.strip().lstrip('•-* ')
            if line:
                entries.append({
                    'title': line,
                    'description': ''
                })
        return entries
