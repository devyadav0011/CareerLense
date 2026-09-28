import re
from typing import Dict, Any, List, Set
from ..config import Config
from .parser import ResumeParser, SKILL_TAXONOMY

class JobMatcher:
    """Matches a resume against a target job description and analyzes skill gaps."""

    DISCLAIMER = "Estimated match based on the provided resume and job description. This indicator does not claim or guarantee employment probability."
    MISSING_SKILLS_NOTICE = "Consider adding missing skills only if they accurately reflect your actual experience."

    @classmethod
    def match(cls, resume_data: Dict[str, Any], raw_resume_text: str, job_description: str) -> Dict[str, Any]:
        if not job_description or len(job_description.strip()) < 30:
            raise ValueError("Please provide a more detailed job description (minimum 30 characters).")

        job_desc_clean = job_description.strip()
        job_desc_lower = job_desc_clean.lower()
        raw_resume_lower = raw_resume_text.lower()

        # 1. Extract requirements from Job Description
        job_skills = cls._extract_job_skills(job_desc_clean)
        job_keywords = cls._extract_important_keywords(job_desc_clean)

        # 2. Extract resume skills
        resume_skills_set = set(s.lower() for s in resume_data.get('skills', {}).get('all', []))
        # Also check raw resume text for any skill mentions
        resume_full_words = set(re.findall(r'\b[a-zA-Z0-9\+#\.]+\b', raw_resume_lower))

        # 3. Categorize Matched vs Missing Skills
        matched_skills = []
        missing_skills = []

        for skill in job_skills:
            skill_lower = skill.lower()
            # Direct match or partial token match
            if skill_lower in resume_skills_set or skill_lower in raw_resume_lower or skill_lower in resume_full_words:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # 4. Keyword Analysis (Target keywords with ✓ / ⚠ / ✕)
        keyword_analysis = []
        all_target_terms = list(dict.fromkeys(job_skills + job_keywords))[:18]

        for term in all_target_terms:
            t_lower = term.lower()
            if t_lower in raw_resume_lower:
                keyword_analysis.append({
                    'term': term,
                    'status': 'matched',
                    'icon': '✓',
                    'label': 'Present in resume'
                })
            elif any(word in raw_resume_lower for word in t_lower.split() if len(word) > 3):
                keyword_analysis.append({
                    'term': term,
                    'status': 'partial',
                    'icon': '⚠',
                    'label': 'Partially matched / context weak'
                })
            else:
                keyword_analysis.append({
                    'term': term,
                    'status': 'missing',
                    'icon': '✕',
                    'label': 'Missing from resume'
                })

        # 5. Calculate Sub-Scores
        # Skills match score
        if job_skills:
            skills_match_pct = int(round((len(matched_skills) / len(job_skills)) * 100))
        else:
            skills_match_pct = 70

        # Experience match score
        experience_entries = resume_data.get('experience', [])
        exp_score = cls._score_experience_match(experience_entries, job_desc_lower)

        # Projects match score
        projects_entries = resume_data.get('projects', [])
        proj_score = cls._score_projects_match(projects_entries, job_desc_lower)

        # Keyword match score
        matched_keywords_count = sum(1 for k in keyword_analysis if k['status'] == 'matched')
        partial_keywords_count = sum(1 for k in keyword_analysis if k['status'] == 'partial')
        if keyword_analysis:
            keyword_score = int(round(((matched_keywords_count + 0.5 * partial_keywords_count) / len(keyword_analysis)) * 100))
        else:
            keyword_score = 70

        # Education match score
        edu_score = cls._score_education_match(resume_data.get('education', []), job_desc_lower)

        # Overall weighted match score
        weights = Config.JOB_MATCH_WEIGHTS
        overall_match = int(round(
            skills_match_pct * weights['skills'] +
            exp_score * weights['experience'] +
            proj_score * weights['projects'] +
            keyword_score * weights['keywords'] +
            edu_score * weights['education']
        ))
        overall_match = max(15, min(97, overall_match))

        # 6. Generate Job-Specific Recommendations
        recommendations = cls._generate_recommendations(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            keyword_analysis=keyword_analysis,
            job_desc=job_desc_clean,
            resume_data=resume_data
        )

        return {
            'match_score': overall_match,
            'label': 'Estimated Job Match Score',
            'disclaimer': cls.DISCLAIMER,
            'missing_notice': cls.MISSING_SKILLS_NOTICE,
            'score_breakdown': {
                'skills': skills_match_pct,
                'experience': exp_score,
                'projects': proj_score,
                'keywords': keyword_score,
                'education': edu_score
            },
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'keyword_analysis': keyword_analysis,
            'recommendations': recommendations
        }

    @classmethod
    def _extract_job_skills(cls, job_desc: str) -> List[str]:
        """Extract skills mentioned in the job description using taxonomy."""
        job_lower = job_desc.lower()
        found = []

        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                escaped = re.escape(skill)
                if escaped.endswith(r'\+') or escaped.endswith(r'\#'):
                    pat = rf'(?:^|[\s,;/|•\(\)])({escaped})(?:$|[\s,;/|•\(\)])'
                else:
                    pat = rf'\b{escaped}\b'

                if re.search(pat, job_lower):
                    custom_names = {
                        'javascript': 'JavaScript', 'typescript': 'TypeScript', 'python': 'Python',
                        'c++': 'C++', 'c#': 'C#', 'php': 'PHP', 'postgresql': 'PostgreSQL',
                        'mysql': 'MySQL', 'mongodb': 'MongoDB', 'sqlite': 'SQLite', 'react': 'React',
                        'vue': 'Vue.js', 'vue.js': 'Vue.js', 'node.js': 'Node.js', 'nodejs': 'Node.js',
                        'flask': 'Flask', 'django': 'Django', 'fastapi': 'FastAPI', 'aws': 'AWS',
                        'docker': 'Docker', 'kubernetes': 'Kubernetes', 'ci/cd': 'CI/CD', 'git': 'Git',
                        'rest apis': 'REST APIs', 'graphql': 'GraphQL', 'unit testing': 'Unit Testing'
                    }
                    display = custom_names.get(skill.lower(), skill.title() if len(skill) > 3 else skill.upper())
                    if display not in found:
                        found.append(display)

        # Check common high-frequency tech terms
        extras = ['REST APIs', 'Unit Testing', 'System Design', 'Microservices', 'Clean Architecture']
        for extra in extras:
            if extra.lower() in job_lower and extra not in found:
                found.append(extra)

        return found

    @classmethod
    def _extract_important_keywords(cls, job_desc: str) -> List[str]:
        """Extract important technical and contextual keywords from job description."""
        ignore_words = {
            'the', 'and', 'with', 'for', 'that', 'this', 'will', 'have', 'from', 'your', 'about',
            'work', 'team', 'experience', 'years', 'skills', 'role', 'responsibilities', 'qualifications',
            'opportunity', 'company', 'looking', 'ability', 'knowledge', 'understanding', 'working'
        }
        words = re.findall(r'\b[a-zA-Z]{4,}\b', job_desc.lower())
        freq: Dict[str, int] = {}
        for w in words:
            if w not in ignore_words:
                freq[w] = freq.get(w, 0) + 1

        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w[0].capitalize() for w in sorted_words[:10]]

    @classmethod
    def _score_experience_match(cls, experience: List[Dict[str, Any]], job_desc_lower: str) -> int:
        if not experience:
            return 50
        score = 65
        all_exp_text = " ".join([e.get('position', '') + " " + e.get('description', '') for e in experience]).lower()

        # Check job roles matching
        role_matches = ['developer', 'engineer', 'architect', 'analyst', 'lead', 'manager', 'intern']
        for r in role_matches:
            if r in job_desc_lower and r in all_exp_text:
                score += 5

        # Check common responsibilities
        if any(term in all_exp_text for term in ['api', 'database', 'frontend', 'backend', 'cloud', 'testing']):
            score += 15

        return min(95, max(40, score))

    @classmethod
    def _score_projects_match(cls, projects: List[Dict[str, Any]], job_desc_lower: str) -> int:
        if not projects:
            return 45
        score = 60
        all_proj_text = " ".join([p.get('name', '') + " " + p.get('technologies', '') + " " + p.get('description', '') for p in projects]).lower()

        overlap_count = 0
        common_tech = ['python', 'react', 'sql', 'flask', 'django', 'javascript', 'api', 'docker', 'aws']
        for t in common_tech:
            if t in job_desc_lower and t in all_proj_text:
                overlap_count += 1

        score += min(30, overlap_count * 8)
        return min(95, max(45, score))

    @classmethod
    def _score_education_match(cls, education: List[Dict[str, Any]], job_desc_lower: str) -> int:
        if not education:
            return 60
        edu_text = " ".join([e.get('degree', '') + " " + e.get('field', '') for e in education]).lower()
        if 'computer science' in job_desc_lower and 'computer science' in edu_text:
            return 95
        if any(deg in edu_text for deg in ['bachelor', 'master', 'b.tech', 'b.e.', 'bs']):
            return 85
        return 75

    @classmethod
    def _generate_recommendations(
        cls,
        matched_skills: List[str],
        missing_skills: List[str],
        keyword_analysis: List[Dict[str, Any]],
        job_desc: str,
        resume_data: Dict[str, Any]
    ) -> List[str]:
        recs = []

        if missing_skills:
            top_missing = missing_skills[:3]
            recs.append(f"Highlight any hands-on background you have in {', '.join(top_missing)} (if applicable to your real experience).")

        if matched_skills:
            top_matched = matched_skills[:3]
            recs.append(f"Prominently position your confirmed matched skills ({', '.join(top_matched)}) higher up in your Skills and Summary sections.")

        # Check if project descriptions could connect more to the job
        projects = resume_data.get('projects', [])
        if projects:
            recs.append("Tailor your project descriptions to emphasize architecture, scalability, or performance metrics relevant to this position.")
        else:
            recs.append("Add a relevant technical project that demonstrates problem solving aligned with this job description.")

        recs.append("Ensure your professional summary directly addresses the seniority level and primary tech stack requested in the job description.")
        recs.append("Review the missing keywords list and weave relevant terminology into your bullet points where you have authentic experience.")

        return recs[:5]
