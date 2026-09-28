import os
import json
import re
from typing import Dict, Any, List, Optional
from ..config import Config

SYSTEM_SAFETY_INSTRUCTION = """You are CareerLense AI, an expert resume and career advisor.
STRICT SAFETY & FACTUAL ACCURACY RULES:
1. NEVER fabricate, hallucinate, or invent jobs, companies, degrees, certifications, skills, projects, achievements, or numbers/metrics.
2. If the user's resume lacks metrics or measurable results, provide advice stating: "Add a measurable result if you have one. Never fabricate numbers."
3. Work strictly with the actual resume information provided.
4. Output must be constructive, professional, and directly actionable.
"""

class BaseAIProvider:
    def analyze_resume(self, structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        raise NotImplementedError

    def rewrite_section(self, section: str, content: str, mode: str, job_context: Optional[str] = None) -> str:
        raise NotImplementedError

    def chat_assistant(self, message: str, resume_context: Optional[Dict[str, Any]] = None, job_context: Optional[str] = None) -> str:
        raise NotImplementedError


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize Google GenAI client
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            self.client = None

    def analyze_resume(self, structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized.")

        prompt = f"""{SYSTEM_SAFETY_INSTRUCTION}
Analyze this resume text and structured resume data.
Return ONLY valid JSON matching this schema:
{{
  "overall_score": <number 0-100>,
  "section_scores": {{
    "content": <number 0-100>,
    "skills": <number 0-100>,
    "projects": <number 0-100>,
    "experience": <number 0-100>,
    "education": <number 0-100>,
    "formatting": <number 0-100>,
    "completeness": <number 0-100>
  }},
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>", "<weakness 4>"],
  "missing_items": ["<missing item 1>", "<missing item 2>"],
  "suggestions": [
    {{
      "section": "<section name>",
      "problem": "<issue description>",
      "why_it_matters": "<explanation>",
      "recommendation": "<actionable fix>",
      "example_improvement": "<clear grounded example>"
    }}
  ],
  "ats_style_issues": ["<ats issue 1>", "<ats issue 2>"]
}}

Resume text:
{raw_text[:4000]}
"""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return self._extract_json(response.text)

    def rewrite_section(self, section: str, content: str, mode: str, job_context: Optional[str] = None) -> str:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized.")

        job_note = f"\nTarget Job Context: {job_context[:1000]}" if job_context else ""
        prompt = f"""{SYSTEM_SAFETY_INSTRUCTION}
Rewrite the following resume {section} text in "{mode}" mode.
Rules:
- Do NOT invent companies, credentials, or fake metrics.
- If no metric was present, keep the factual content and suggest: "(Add measurable result if available)".
- Mode styles:
  * Professional: refined, polished executive tone
  * Concise: brief, punchy, eliminates fluff
  * Technical: emphasizes technical mechanisms, tools, and architecture
  * Entry-Level: highlights academic rigor, foundational concepts, and curiosity
  * Impact-Focused: structures sentences around actions and results
  * ATS-Friendly: uses standard vocabulary, clear action verbs, and no unusual symbols
{job_note}

Original Content:
{content}

Provide ONLY the rewritten text without conversational preamble or quotes.
"""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()

    def chat_assistant(self, message: str, resume_context: Optional[Dict[str, Any]] = None, job_context: Optional[str] = None) -> str:
        if not self.client:
            raise RuntimeError("Gemini Client not initialized.")

        context_str = ""
        if resume_context:
            context_str += f"\nUser's Current Resume Summary:\n{json.dumps(resume_context, indent=2)[:2000]}"
        if job_context:
            context_str += f"\nTarget Job Description:\n{job_context[:1500]}"

        prompt = f"""{SYSTEM_SAFETY_INSTRUCTION}
You are CareerLense AI, an interactive career assistant on the CareerLense platform.
User Question: {message}
{context_str}

Give a clear, helpful, highly professional response tailored specifically to their resume context. Do not invent any false details.
"""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()

    def _extract_json(self, text: str) -> Dict[str, Any]:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except Exception:
            self.client = None

    def analyze_resume(self, structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("OpenAI Client not initialized.")

        prompt = f"""{SYSTEM_SAFETY_INSTRUCTION}
Analyze this resume text and return ONLY valid JSON:
{{
  "overall_score": <number 0-100>,
  "section_scores": {{
    "content": <number 0-100>,
    "skills": <number 0-100>,
    "projects": <number 0-100>,
    "experience": <number 0-100>,
    "education": <number 0-100>,
    "formatting": <number 0-100>,
    "completeness": <number 0-100>
  }},
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>", "<weakness 4>"],
  "missing_items": ["<missing item 1>", "<missing item 2>"],
  "suggestions": [
    {{
      "section": "<section name>",
      "problem": "<issue description>",
      "why_it_matters": "<explanation>",
      "recommendation": "<actionable fix>",
      "example_improvement": "<clear grounded example>"
    }}
  ],
  "ats_style_issues": ["<ats issue 1>", "<ats issue 2>"]
}}

Resume text:
{raw_text[:4000]}
"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_SAFETY_INSTRUCTION},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def rewrite_section(self, section: str, content: str, mode: str, job_context: Optional[str] = None) -> str:
        if not self.client:
            raise RuntimeError("OpenAI Client not initialized.")

        job_note = f"\nTarget Job Context: {job_context[:1000]}" if job_context else ""
        prompt = f"""Rewrite the following resume {section} in "{mode}" mode.
Never invent fake metrics or companies.
{job_note}

Content:
{content}
"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_SAFETY_INSTRUCTION},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def chat_assistant(self, message: str, resume_context: Optional[Dict[str, Any]] = None, job_context: Optional[str] = None) -> str:
        if not self.client:
            raise RuntimeError("OpenAI Client not initialized.")

        context_str = ""
        if resume_context:
            context_str += f"\nUser's Current Resume:\n{json.dumps(resume_context, indent=2)[:2000]}"
        if job_context:
            context_str += f"\nTarget Job:\n{job_context[:1500]}"

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_SAFETY_INSTRUCTION},
                {"role": "user", "content": f"Context: {context_str}\n\nQuestion: {message}"}
            ]
        )
        return response.choices[0].message.content.strip()


class HeuristicFallbackProvider(BaseAIProvider):
    """Reliable, offline rule-based AI engine that produces intelligent, grounded results without API keys."""

    def analyze_resume(self, structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        from .scorer import ResumeScorer
        score_res = ResumeScorer.calculate_score(structured_data, raw_text)

        ats_issues = []
        if len(structured_data.get('skills', {}).get('all', [])) < 6:
            ats_issues.append("Low keyword volume may reduce ATS semantic discovery.")
        if not structured_data.get('personal_info', {}).get('email'):
            ats_issues.append("Missing or unparsed email header.")
        if not ats_issues:
            ats_issues.append("Header structure and standard typography are ATS-friendly.")

        # Reformat suggestions to match expected schema
        formatted_suggestions = []
        for s in score_res['suggestions']:
            formatted_suggestions.append({
                'section': s.get('section', 'General'),
                'problem': s.get('issue', ''),
                'why_it_matters': s.get('reason', ''),
                'recommendation': s.get('recommendation', ''),
                'example_improvement': s.get('example_improvement', '')
            })

        return {
            'overall_score': score_res['overall_score'],
            'section_scores': score_res['section_scores'],
            'strengths': score_res['strengths'][:4],
            'weaknesses': score_res['weaknesses'][:4],
            'missing_items': score_res['missing_items'][:4],
            'suggestions': formatted_suggestions[:6],
            'ats_style_issues': ats_issues
        }

    def rewrite_section(self, section: str, content: str, mode: str, job_context: Optional[str] = None) -> str:
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        rewritten_lines = []

        action_starters = {
            'Professional': ['Engineered', 'Spearheaded', 'Orchestrated', 'Delivered', 'Implemented'],
            'Concise': ['Built', 'Developed', 'Maintained', 'Deployed', 'Optimized'],
            'Technical': ['Architected full-stack implementation of', 'Engineered resilient architecture for', 'Designed and benchmarked', 'Implemented RESTful APIs and schemas for'],
            'Entry-Level': ['Designed and implemented', 'Applied core concepts to build', 'Collaborated on developing', 'Constructed modular solution for'],
            'Impact-Focused': ['Optimized core workflow to accelerate', 'Engineered high-performance solution for', 'Streamlined system pipeline, improving throughput for'],
            'ATS-Friendly': ['Developed and maintained', 'Collaborated across teams to engineer', 'Implemented software features using standard patterns for']
        }

        starters = action_starters.get(mode, action_starters['Professional'])

        for i, line in enumerate(lines):
            starter = starters[i % len(starters)]
            clean_l = re.sub(r'^(?:was responsible for|helped to|worked on|did|created|built|developed)\s+', '', line, flags=re.IGNORECASE)
            clean_l = clean_l.lstrip('•-* 0123456789.)')

            if mode == 'Concise':
                # Remove filler words
                clean_l = re.sub(r'\b(in order to|as well as|very|really|basically)\b', '', clean_l, flags=re.IGNORECASE).strip()
                rewritten_lines.append(f"• {starter} {clean_l}.")
            elif mode == 'Impact-Focused':
                rewritten_lines.append(f"• {starter} {clean_l} (add measurable result if you have one, e.g. latency, users, or throughput).")
            elif mode == 'Technical':
                rewritten_lines.append(f"• {starter} {clean_l} with focus on modularity, error resilience, and maintainability.")
            else:
                rewritten_lines.append(f"• {starter} {clean_l}.")

        return "\n".join(rewritten_lines) if rewritten_lines else f"• {starters[0]} {content}."

    def chat_assistant(self, message: str, resume_context: Optional[Dict[str, Any]] = None, job_context: Optional[str] = None) -> str:
        msg_lower = message.lower()
        skills = resume_context.get('skills', {}).get('all', []) if resume_context else []
        name = resume_context.get('personal_info', {}).get('full_name', 'there') if resume_context else 'there'

        if 'weak' in msg_lower or 'improve my resume' in msg_lower or 'suggestions' in msg_lower:
            return (
                f"Hello {name}! Based on your current resume evaluation, here are key areas to boost:\n\n"
                "1. **Quantifiable Impact**: Wherever possible, add measurable outcomes (e.g. latency reduction, users served, features shipped). *Remember: only add metrics if you have actual figures; never fabricate numbers.*\n"
                "2. **Strong Action Verbs**: Begin every bullet point with strong active verbs like *Engineered, Spearheaded, Architected, Streamlined* instead of passive phrases like *Was responsible for*.\n"
                "3. **Skill Organization**: Group your technical skills into distinct categories (Languages, Frameworks, Databases, Tools) so ATS scanners and hiring managers can parse them instantly."
            )
        elif 'project' in msg_lower:
            return (
                "To make your **Projects** stand out:\n\n"
                "- State the **problem** and the **technical architecture** (e.g., 'Architected a real-time analytics dashboard with React, Flask, and SQLite').\n"
                "- Explicitly list the **tech stack** and provide links to public GitHub repositories or live demos.\n"
                "- Describe key architectural decisions (e.g., caching, authentication, responsive design) rather than just listing basic features."
            )
        elif 'summary' in msg_lower:
            skills_str = ", ".join(skills[:3]) if skills else "relevant modern technologies"
            return (
                "A high-impact **Professional Summary** should be 2 to 3 sentences following this formula:\n\n"
                f"1. **Identity & Focus**: 'Software Engineer specializing in {skills_str} and scalable web platforms.'\n"
                "2. **Core Competency**: 'Demonstrated track record building end-to-end applications, designing RESTful APIs, and implementing automated testing.'\n"
                "3. **Career Value**: 'Passionate about code quality, system performance, and delivering user-centric solutions.'"
            )
        elif 'match' in msg_lower or 'job' in msg_lower:
            return (
                "To optimize your resume for a target job:\n\n"
                "1. Use our **Job Matcher** tool to compare your resume against the specific job description.\n"
                "2. Align your skills section by prioritizing matched keywords that reflect your actual experience.\n"
                "3. Frame your project and experience bullet points around the challenges mentioned in the job posting."
            )
        else:
            return (
                f"Thanks for asking! I'm CareerLense AI. I can review your resume sections, suggest powerful action verbs, optimize your bullet points, or guide your preparation for specific job descriptions.\n\n"
                "Try asking:\n"
                "- *'What is weak in my resume?'*\n"
                "- *'How can I improve my project section?'*\n"
                "- *'How should I write my professional summary?'*"
            )


class AIService:
    """Unified AI service with provider abstraction, validation, and safety rules."""

    _provider: Optional[BaseAIProvider] = None

    @classmethod
    def get_provider(cls) -> BaseAIProvider:
        provider_name = Config.AI_PROVIDER.lower()

        if provider_name == 'gemini' and Config.GEMINI_API_KEY:
            try:
                return GeminiProvider(Config.GEMINI_API_KEY)
            except Exception:
                pass
        elif provider_name == 'openai' and Config.OPENAI_API_KEY:
            try:
                return OpenAIProvider(Config.OPENAI_API_KEY)
            except Exception:
                pass

        # If keys not provided or provider fails, return robust HeuristicFallbackProvider
        return HeuristicFallbackProvider()

    @classmethod
    def analyze_resume(cls, structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        provider = cls.get_provider()
        try:
            result = provider.analyze_resume(structured_data, raw_text)
            cls._validate_analysis_output(result)
            return result
        except Exception:
            # Fallback to local heuristic provider to guarantee 100% uptime
            fallback = HeuristicFallbackProvider()
            result = fallback.analyze_resume(structured_data, raw_text)
            cls._validate_analysis_output(result)
            return result

    @classmethod
    def rewrite_section(cls, section: str, content: str, mode: str, job_context: Optional[str] = None) -> str:
        provider = cls.get_provider()
        try:
            return provider.rewrite_section(section, content, mode, job_context)
        except Exception:
            fallback = HeuristicFallbackProvider()
            return fallback.rewrite_section(section, content, mode, job_context)

    @classmethod
    def chat_assistant(cls, message: str, resume_context: Optional[Dict[str, Any]] = None, job_context: Optional[str] = None) -> str:
        provider = cls.get_provider()
        try:
            return provider.chat_assistant(message, resume_context, job_context)
        except Exception:
            fallback = HeuristicFallbackProvider()
            return fallback.chat_assistant(message, resume_context, job_context)

    @classmethod
    def _validate_analysis_output(cls, data: Dict[str, Any]) -> None:
        """Validate required fields in AI output (spec requirement 49)."""
        required_keys = ['overall_score', 'section_scores', 'strengths', 'weaknesses', 'suggestions']
        for k in required_keys:
            if k not in data:
                raise ValueError(f"AI response missing required field: {k}")

        if not isinstance(data['overall_score'], (int, float)):
            data['overall_score'] = 75
        data['overall_score'] = int(round(data['overall_score']))
