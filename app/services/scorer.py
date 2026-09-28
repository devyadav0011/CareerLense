import re
from typing import Dict, Any, List
from ..config import Config

class ResumeScorer:
    """Calculates Estimated Resume Quality Score using transparent rules and provides section insights."""

    @classmethod
    def calculate_score(cls, structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        weights = Config.SCORE_WEIGHTS
        raw_text_lower = raw_text.lower()

        # 1. Content Quality Score (0 - 100)
        content_score, content_feedback = cls._score_content_quality(structured_data, raw_text)

        # 2. Skills Score (0 - 100)
        skills_score, skills_feedback = cls._score_skills(structured_data)

        # 3. Projects Score (0 - 100)
        projects_score, projects_feedback = cls._score_projects(structured_data)

        # 4. Experience Score (0 - 100)
        experience_score, experience_feedback = cls._score_experience(structured_data)

        # 5. Education Score (0 - 100)
        education_score, education_feedback = cls._score_education(structured_data)

        # 6. Formatting Score (0 - 100)
        formatting_score, formatting_feedback = cls._score_formatting(raw_text)

        # 7. Completeness Score (0 - 100)
        completeness_score, completeness_feedback = cls._score_completeness(structured_data)

        # Calculate Overall Weighted Score
        overall = (
            content_score * weights['content'] +
            skills_score * weights['skills'] +
            projects_score * weights['projects'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            formatting_score * weights['formatting'] +
            completeness_score * weights['completeness']
        )
        overall_score = int(round(overall))
        overall_score = max(10, min(99, overall_score))  # Keep in realistic range

        # Aggregate strengths, weaknesses, missing items, and detailed suggestions
        strengths = []
        weaknesses = []
        missing_items = []
        suggestions = []

        all_feedbacks = [
            content_feedback, skills_feedback, projects_feedback,
            experience_feedback, education_feedback, formatting_feedback, completeness_feedback
        ]

        for fb in all_feedbacks:
            strengths.extend(fb.get('strengths', []))
            weaknesses.extend(fb.get('weaknesses', []))
            missing_items.extend(fb.get('missing', []))
            suggestions.extend(fb.get('suggestions', []))

        # Explanation of calculation
        explanation = {
            'formula': 'Overall = (Content × 20%) + (Skills × 15%) + (Projects × 15%) + (Experience × 15%) + (Education × 10%) + (Formatting × 10%) + (Completeness × 15%)',
            'weights': {k: f"{int(v*100)}%" for k, v in weights.items()},
            'note': 'Estimated Resume Quality Score is an analytical indicator of resume strength and completeness, not an endorsement or interview guarantee.'
        }

        return {
            'overall_score': overall_score,
            'label': 'Estimated Resume Quality Score',
            'section_scores': {
                'content': content_score,
                'skills': skills_score,
                'projects': projects_score,
                'experience': experience_score,
                'education': education_score,
                'formatting': formatting_score,
                'completeness': completeness_score
            },
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing_items': missing_items,
            'suggestions': suggestions,
            'calculation_explanation': explanation
        }

    @classmethod
    def _score_content_quality(cls, data: Dict[str, Any], text: str) -> tuple[int, Dict[str, Any]]:
        score = 65
        strengths = []
        weaknesses = []
        missing = []
        suggestions = []

        # Action verbs check
        action_verbs = [
            'developed', 'built', 'created', 'designed', 'architected', 'implemented', 'optimized',
            'reduced', 'increased', 'managed', 'led', 'delivered', 'orchestrated', 'streamlined',
            'integrated', 'automated', 'engineered', 'launched', 'spearheaded'
        ]
        found_verbs = [v for v in action_verbs if re.search(rf'\b{v}\b', text, re.IGNORECASE)]

        if len(found_verbs) >= 6:
            score += 15
            strengths.append("Strong action-oriented vocabulary used across descriptions (e.g., " + ", ".join(found_verbs[:3]) + ").")
        elif len(found_verbs) >= 3:
            score += 8
            strengths.append("Found good action verbs like " + ", ".join(found_verbs[:2]) + ".")
        else:
            weaknesses.append("Descriptions rely on passive phrasing rather than strong action verbs.")
            suggestions.append({
                'section': 'Content Quality',
                'issue': 'Passive descriptions without active achievement verbs',
                'reason': 'Recruiters and hiring managers look for candidates who take initiative and own project outcomes.',
                'recommendation': 'Start bullet points with strong past-tense action verbs such as "Engineered", "Orchestrated", "Implemented", or "Streamlined".',
                'example_improvement': 'Current: "Was responsible for building the API." -> Suggestion: "Engineered high-throughput REST APIs using Python and Flask."'
            })

        # Measurable metrics check (percentages, numbers, dollars)
        metrics_found = re.findall(r'(\d+%(?:\s+increase|\s+reduction|\s+growth)?|\$\d+[\d,]*|\b\d{2,}\b\+?\s*(?:users|clients|requests|ms|seconds|hours))', text, re.IGNORECASE)
        if len(metrics_found) >= 2:
            score += 20
            strengths.append(f"Contains quantifiable impact metrics ({metrics_found[0]}).")
        else:
            score -= 5
            weaknesses.append("Lack of quantifiable outcomes or measurable impact in bullet points.")
            suggestions.append({
                'section': 'Content Quality',
                'issue': 'Few or no measurable metrics detected',
                'reason': 'Measurable achievements provide proof of value rather than just a list of assigned duties.',
                'recommendation': 'Add a measurable result if you have one (e.g. improved latency by 20%, supported 500+ daily active users). Never fabricate numbers.',
                'example_improvement': 'Current: "Optimized database queries." -> Suggestion: "Optimized SQL queries, improving response latency if you have measured numbers."'
            })

        summary = data.get('personal_info', {}).get('summary', '')
        if summary and len(summary.split()) >= 20:
            score += 10
            strengths.append("Well-defined professional summary articulating core value proposition.")
        elif not summary:
            missing.append("Professional Summary section")
            suggestions.append({
                'section': 'Summary',
                'issue': 'No professional summary found',
                'reason': 'A concise 2-3 sentence overview immediately establishes your domain focus for recruiters.',
                'recommendation': 'Add a brief 3-sentence summary highlighting your core tech stack, experience level, and top strengths.',
                'example_improvement': 'Example: "Software Engineer with background in Python, Flask, and cloud platforms. Proven track record designing scalable web applications and RESTful APIs."'
            })

        return min(95, max(30, score)), {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing': missing,
            'suggestions': suggestions
        }

    @classmethod
    def _score_skills(cls, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        score = 50
        strengths = []
        weaknesses = []
        missing = []
        suggestions = []

        skills = data.get('skills', {})
        total_skills = len(skills.get('all', []))

        if total_skills >= 10:
            score += 25
            strengths.append(f"Diverse skill set detected with {total_skills} recognized technical competencies.")
        elif total_skills >= 5:
            score += 15
            strengths.append(f"Solid foundation with {total_skills} relevant skills listed.")
        else:
            score -= 10
            weaknesses.append("Limited number of technical skills identified.")
            suggestions.append({
                'section': 'Skills',
                'issue': 'Skills list is sparse',
                'reason': 'ATS filters and recruiters scan for specific tools, databases, and languages.',
                'recommendation': 'Add familiar technologies, tools, and libraries you have hands-on experience with.',
                'example_improvement': 'Group skills into categories: Languages (Python, JavaScript), Frameworks (React, Flask), Tools (Git, Docker).'
            })

        # Category coverage
        categories_represented = sum(1 for cat in ['programming_languages', 'frameworks', 'databases', 'cloud', 'tools'] if len(skills.get(cat, [])) > 0)
        if categories_represented >= 4:
            score += 20
            strengths.append("Skills section shows well-rounded multi-tier coverage (Languages, Frameworks, Databases, Tools).")
        elif categories_represented <= 2:
            weaknesses.append("Skills are concentrated in only 1-2 categories; lacks tooling or database representation.")

        return min(96, max(35, score)), {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing': missing,
            'suggestions': suggestions
        }

    @classmethod
    def _score_projects(cls, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        score = 55
        strengths = []
        weaknesses = []
        missing = []
        suggestions = []

        projects = data.get('projects', [])
        if len(projects) >= 3:
            score += 25
            strengths.append(f"Strong portfolio with {len(projects)} featured projects.")
        elif len(projects) in [1, 2]:
            score += 15
            strengths.append(f"Contains {len(projects)} technical project entries.")
        else:
            score -= 20
            missing.append("Projects section")
            suggestions.append({
                'section': 'Projects',
                'issue': 'No dedicated projects section detected',
                'reason': 'Hands-on projects validate problem-solving ability, especially for software and engineering roles.',
                'recommendation': 'Add 2-3 substantial projects detailing what you built, technologies used, and direct links to code/demos.',
                'example_improvement': 'Project Title | Tech: React, Flask, PostgreSQL\n- Engineered full-stack web application featuring user auth and analytics\n- Implemented responsive interface and automated test suite'
            })
            return 40, {'strengths': strengths, 'weaknesses': weaknesses, 'missing': missing, 'suggestions': suggestions}

        # Check project details
        has_tech_stack = any(p.get('technologies') for p in projects)
        has_links = any(p.get('github') or p.get('live_demo') for p in projects)
        generic_descriptions = any(len(p.get('description', '').split()) < 10 for p in projects)

        if has_tech_stack:
            score += 10
            strengths.append("Projects explicitly mention tools and technology stacks.")
        else:
            weaknesses.append("Project entries do not specify the technology stack used.")

        if has_links:
            score += 10
            strengths.append("Project repository or live demonstration links provided.")
        else:
            missing.append("GitHub / Live demo links in project section")

        if generic_descriptions:
            weaknesses.append("Some project descriptions are too brief or generic.")
            suggestions.append({
                'section': 'Projects',
                'issue': 'Project descriptions are too generic',
                'reason': 'Vague descriptions like "Created an e-commerce website" do not show technical depth or individual contribution.',
                'recommendation': 'Describe technical architecture, key challenges solved, and measurable outcomes if available.',
                'example_improvement': 'Current: "Created an e-commerce website." -> Suggestion: "Architected a responsive e-commerce web platform with Flask, SQLite, and Stripe integration; implemented secure cart checkout and order management."'
            })

        return min(95, max(35, score)), {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing': missing,
            'suggestions': suggestions
        }

    @classmethod
    def _score_experience(cls, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        score = 50
        strengths = []
        weaknesses = []
        missing = []
        suggestions = []

        experience = data.get('experience', [])
        if len(experience) >= 2:
            score += 30
            strengths.append(f"Demonstrates consistent career trajectory with {len(experience)} documented positions.")
        elif len(experience) == 1:
            score += 20
            strengths.append("Experience section contains relevant role history.")
        else:
            # Maybe a student or fresher
            score = 60
            weaknesses.append("No professional experience or internships listed.")
            suggestions.append({
                'section': 'Experience',
                'issue': 'No work experience or internships detected',
                'reason': 'If you have completed internships, freelance gigs, or relevant student leadership roles, listing them builds credibility.',
                'recommendation': 'If you have relevant internships, freelance work, or open-source contributions, document them with date ranges and duties.',
                'example_improvement': 'If entry-level, expand your Projects and Academic achievements to showcase practical capabilities.'
            })

        # Check for date ranges and descriptions
        has_dates = all(e.get('start_date') or e.get('end_date') for e in experience) if experience else False
        if has_dates:
            score += 10
            strengths.append("Clear timelines and date ranges provided for professional roles.")

        return min(95, max(45, score)), {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing': missing,
            'suggestions': suggestions
        }

    @classmethod
    def _score_education(cls, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        score = 60
        strengths = []
        weaknesses = []
        missing = []
        suggestions = []

        edu = data.get('education', [])
        if edu:
            score += 25
            strengths.append("Academic background is clearly documented.")
            if any(e.get('degree') for e in edu):
                score += 10
                strengths.append("Degree and field of study explicitly stated.")
        else:
            score -= 20
            missing.append("Education section")
            suggestions.append({
                'section': 'Education',
                'issue': 'Education details missing or unparsed',
                'reason': 'Most standard hiring guidelines require educational qualification verification.',
                'recommendation': 'Specify your degree, institution, field of study, and graduation year.',
                'example_improvement': 'Bachelor of Technology in Computer Science | XYZ University | 2021 - 2025'
            })

        return min(98, max(40, score)), {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing': missing,
            'suggestions': suggestions
        }

    @classmethod
    def _score_formatting(cls, text: str) -> tuple[int, Dict[str, Any]]:
        score = 75
        strengths = []
        weaknesses = []
        missing = []
        suggestions = []

        lines = text.split('\n')
        # Check text length / page count estimate (avg 350-500 words per page)
        words = text.split()
        if 250 <= len(words) <= 900:
            score += 15
            strengths.append("Well-proportioned document length (~1-2 pages standard density).")
        elif len(words) < 200:
            score -= 15
            weaknesses.append("Resume content is sparse (less than 200 words).")
        else:
            weaknesses.append("Document is quite lengthy; ensure content is concise and directly relevant.")

        # Check for bullet structure
        bullets = [l for l in lines if l.strip().startswith(('•', '-', '*', '✓', '▪'))]
        if len(bullets) >= 5:
            score += 10
            strengths.append("Consistent bulleted formatting enhances scanning readability.")
        else:
            weaknesses.append("Few bullet points used; dense text blocks reduce visual clarity.")
            suggestions.append({
                'section': 'Formatting',
                'issue': 'Paragraph blocks instead of concise bullet points',
                'reason': 'Recruiters spend an average of 6-8 seconds on initial resume review.',
                'recommendation': 'Break lengthy paragraphs into 2-4 concise, high-impact bullet points.',
                'example_improvement': 'Use bullet points starting with action verbs to describe responsibilities and achievements.'
            })

        return min(95, max(45, score)), {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing': missing,
            'suggestions': suggestions
        }

    @classmethod
    def _score_completeness(cls, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        score = 50
        strengths = []
        weaknesses = []
        missing = []
        suggestions = []

        info = data.get('personal_info', {})
        checks = {
            'full_name': (10, 'Full name'),
            'email': (15, 'Email address'),
            'phone': (10, 'Phone number'),
            'location': (5, 'Location'),
            'linkedin': (10, 'LinkedIn profile link'),
            'github': (10, 'GitHub profile link')
        }

        for field, (pts, label) in checks.items():
            if info.get(field):
                score += pts
            else:
                if field in ['linkedin', 'github']:
                    weaknesses.append(f"No {label} detected.")
                else:
                    missing.append(f"{label} in header")

        if not info.get('portfolio'):
            missing.append("Portfolio link not detected.")

        if score >= 85:
            strengths.append("Header contact details and professional links are comprehensively filled.")

        return min(95, max(30, score)), {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'missing': missing,
            'suggestions': suggestions
        }
