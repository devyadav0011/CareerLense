import re
from typing import Dict, Any, List

class ATSChecker:
    """Analyzes resume text against Applicant Tracking System (ATS) readability heuristics."""

    DISCLAIMER = "This is an estimated ATS-style readability indicator, not a guarantee of ATS performance."

    @classmethod
    def evaluate(cls, raw_text: str, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        score = 100

        # 1. Standard Headings Check
        detected_sections = structured_data.get('detected_sections', [])
        expected_standard = ['experience', 'education', 'skills', 'projects', 'summary']
        matched_standards = [s for s in expected_standard if s in detected_sections]

        if len(matched_standards) >= 4:
            checks.append({
                'name': 'Standard Section Headings',
                'status': 'passed',
                'icon': '✓',
                'description': f'Recognized standard headings: {", ".join([s.capitalize() for s in matched_standards])}.'
            })
        elif len(matched_standards) >= 2:
            score -= 10
            checks.append({
                'name': 'Standard Section Headings',
                'status': 'warning',
                'icon': '⚠',
                'description': 'Some conventional headings missing or non-standard (e.g., "Work History" instead of "Experience").'
            })
        else:
            score -= 25
            checks.append({
                'name': 'Standard Section Headings',
                'status': 'failed',
                'icon': '✕',
                'description': 'Lacks standard headings. ATS parsers rely on canonical section titles to categorize content.'
            })

        # 2. Contact Information Check
        info = structured_data.get('personal_info', {})
        has_email = bool(info.get('email'))
        has_phone = bool(info.get('phone'))
        has_name = bool(info.get('full_name'))

        if has_email and has_phone and has_name:
            checks.append({
                'name': 'Contact Information Detectability',
                'status': 'passed',
                'icon': '✓',
                'description': 'Full name, email address, and phone number cleanly extracted from top header.'
            })
        elif has_email:
            score -= 8
            checks.append({
                'name': 'Contact Information Detectability',
                'status': 'warning',
                'icon': '⚠',
                'description': 'Email found, but phone number or candidate name was not clearly isolated.'
            })
        else:
            score -= 20
            checks.append({
                'name': 'Contact Information Detectability',
                'status': 'failed',
                'icon': '✕',
                'description': 'No contact email detected in plain text. Automated systems will reject submissions without contact info.'
            })

        # 3. Clean Text Extraction & Encoding
        non_ascii = [ch for ch in raw_text if ord(ch) > 127 and ch not in ['•', '–', '—', '’', '“', '”', '…']]
        if len(non_ascii) > 20:
            score -= 10
            checks.append({
                'name': 'Character Encoding & Symbols',
                'status': 'warning',
                'icon': '⚠',
                'description': f'Detected {len(non_ascii)} unusual non-ASCII or decorative icon characters that could cause parsing garble.'
            })
        else:
            checks.append({
                'name': 'Character Encoding & Symbols',
                'status': 'passed',
                'icon': '✓',
                'description': 'Text extracted cleanly with UTF-8 compatibility and standard punctuation.'
            })

        # 4. Multi-column / Table Layout Heuristic
        # Lines with multiple pipes or tabs often indicate multi-column text that could scramble in old parsers
        multi_col_lines = [l for l in raw_text.split('\n') if l.count('|') >= 2 or l.count('\t') >= 3]
        if len(multi_col_lines) > 5:
            score -= 8
            checks.append({
                'name': 'Table & Column Complexity',
                'status': 'warning',
                'icon': '⚠',
                'description': 'Complex tables or horizontal multi-column splits detected. Single-column layouts parse with higher reliability.'
            })
        else:
            checks.append({
                'name': 'Table & Column Complexity',
                'status': 'passed',
                'icon': '✓',
                'description': 'Flow-friendly vertical structure without unparseable table nesting.'
            })

        # 5. Length & Word Density
        words = raw_text.split()
        if 300 <= len(words) <= 1200:
            checks.append({
                'name': 'Keyword Density & Word Count',
                'status': 'passed',
                'icon': '✓',
                'description': f'Optimal length ({len(words)} words) provides sufficient indexable keywords without keyword stuffing.'
            })
        elif len(words) < 250:
            score -= 15
            checks.append({
                'name': 'Keyword Density & Word Count',
                'status': 'failed',
                'icon': '✕',
                'description': f'Low word count ({len(words)} words). May lack sufficient technical keywords to match job parameters.'
            })
        else:
            score -= 5
            checks.append({
                'name': 'Keyword Density & Word Count',
                'status': 'warning',
                'icon': '⚠',
                'description': f'Word count ({len(words)} words) is high. Consider streamlining descriptions for concise scanning.'
            })

        # 6. Dates & Timeline Consistency
        dates_found = re.findall(r'\b(20\d{2}|19\d{2})\b', raw_text)
        if len(dates_found) >= 3:
            checks.append({
                'name': 'Chronological Timeline Parsing',
                'status': 'passed',
                'icon': '✓',
                'description': 'Standard year representations (e.g. 2022 - Present) found for timeline indexing.'
            })
        else:
            score -= 8
            checks.append({
                'name': 'Chronological Timeline Parsing',
                'status': 'warning',
                'icon': '⚠',
                'description': 'Few year milestones identified. Ensure work experiences and education clearly state date ranges.'
            })

        # Final score bounding
        score = max(35, min(98, score))

        return {
            'ats_score': score,
            'label': 'Estimated ATS-style Readability Indicator',
            'disclaimer': cls.DISCLAIMER,
            'checks': checks,
            'summary': f"Resume scored {score}% for ATS readability. Standard linear formatting and common headings ensure high parse accuracy."
        }
