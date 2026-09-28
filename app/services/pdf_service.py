import os
import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Color Palettes
PALETTES = {
    'minimal': {
        'primary': colors.HexColor('#1E293B'),      # Slate 800
        'secondary': colors.HexColor('#475569'),    # Slate 600
        'accent': colors.HexColor('#0F172A'),       # Slate 900
        'line': colors.HexColor('#CBD5E1'),         # Slate 300
        'bg_subtle': colors.HexColor('#F8FAFC')
    },
    'modern': {
        'primary': colors.HexColor('#4338CA'),      # Indigo 700
        'secondary': colors.HexColor('#475569'),    # Slate 600
        'accent': colors.HexColor('#6366F1'),       # Indigo 500
        'line': colors.HexColor('#E2E8F0'),         # Slate 200
        'bg_subtle': colors.HexColor('#EEF2FF')
    },
    'professional': {
        'primary': colors.HexColor('#0F172A'),      # Deep Navy 900
        'secondary': colors.HexColor('#334155'),    # Slate 700
        'accent': colors.HexColor('#2563EB'),       # Blue 600
        'line': colors.HexColor('#94A3B8'),         # Slate 400
        'bg_subtle': colors.HexColor('#F1F5F9')
    }
}

class PDFService:
    """Generates production-quality A4 PDF resumes and analysis reports using ReportLab."""

    @classmethod
    def generate_resume_pdf(cls, data: Dict[str, Any], template: str = 'modern') -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        palette = PALETTES.get(template, PALETTES['modern'])
        styles = getSampleStyleSheet()

        # Custom typography styles
        name_style = ParagraphStyle(
            'ResumeName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=palette['primary'],
            alignment=TA_LEFT if template != 'minimal' else TA_CENTER
        )

        title_style = ParagraphStyle(
            'ResumeTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=palette['accent'],
            alignment=TA_LEFT if template != 'minimal' else TA_CENTER
        )

        contact_style = ParagraphStyle(
            'ResumeContact',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=palette['secondary'],
            alignment=TA_LEFT if template != 'minimal' else TA_CENTER
        )

        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=palette['primary'],
            spaceAfter=4,
            textTransform='uppercase'
        )

        item_title_style = ParagraphStyle(
            'ItemTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14,
            textColor=palette['primary']
        )

        item_sub_style = ParagraphStyle(
            'ItemSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=palette['secondary']
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#1E293B')
        )

        bullet_style = ParagraphStyle(
            'Bullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            leftIndent=12,
            textColor=colors.HexColor('#1E293B')
        )

        story = []

        # 1. Header (Name, Title, Contacts)
        info = data.get('personal_info', {})
        full_name = info.get('full_name', 'Your Name')
        title = info.get('title', '')

        story.append(Paragraph(full_name, name_style))
        if title:
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 3))

        # Contacts list
        contact_parts = []
        if info.get('email'):
            contact_parts.append(info['email'])
        if info.get('phone'):
            contact_parts.append(info['phone'])
        if info.get('location'):
            contact_parts.append(info['location'])
        if info.get('linkedin'):
            contact_parts.append(info['linkedin'])
        if info.get('github'):
            contact_parts.append(info['github'])
        if info.get('portfolio'):
            contact_parts.append(info['portfolio'])

        if contact_parts:
            story.append(Paragraph(" • ".join(contact_parts), contact_style))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=palette['line'], spaceBefore=1, spaceAfter=8))

        # 2. Professional Summary
        summary = info.get('summary', '')
        if summary:
            story.append(Paragraph("Professional Summary", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=palette['accent'], spaceBefore=1, spaceAfter=4))
            story.append(Paragraph(summary, body_style))
            story.append(Spacer(1, 10))

        # 3. Skills
        skills_dict = data.get('skills', {})
        all_skills = skills_dict.get('all', []) if isinstance(skills_dict, dict) else skills_dict
        if all_skills:
            story.append(Paragraph("Skills & Technologies", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=palette['accent'], spaceBefore=1, spaceAfter=4))

            if isinstance(skills_dict, dict) and any(skills_dict.get(cat) for cat in ['programming_languages', 'frameworks', 'databases', 'tools', 'cloud']):
                cat_rows = []
                labels = {
                    'programming_languages': 'Languages',
                    'frameworks': 'Frameworks & Libraries',
                    'databases': 'Databases',
                    'cloud': 'Cloud & DevOps',
                    'tools': 'Tools',
                    'soft_skills': 'Soft Skills'
                }
                for cat_key, cat_label in labels.items():
                    sub_list = skills_dict.get(cat_key, [])
                    if sub_list:
                        cat_rows.append(Paragraph(f"<b>{cat_label}:</b> {', '.join(sub_list)}", body_style))
                for cr in cat_rows:
                    story.append(cr)
                    story.append(Spacer(1, 2))
            else:
                skills_str = ", ".join(all_skills) if isinstance(all_skills, list) else str(all_skills)
                story.append(Paragraph(skills_str, body_style))

            story.append(Spacer(1, 10))

        # 4. Experience
        experience = data.get('experience', [])
        if experience:
            story.append(Paragraph("Experience", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=palette['accent'], spaceBefore=1, spaceAfter=4))

            for exp in experience:
                role = exp.get('position', 'Position')
                company = exp.get('company', 'Company')
                dates = f"{exp.get('start_date', '')} – {exp.get('end_date', 'Present')}".strip(" –")
                loc = exp.get('location', '')

                header_left = f"<b>{role}</b> — {company}"
                header_right = f"{dates}" + (f" | {loc}" if loc else "")

                # Table for clean left/right alignment
                header_table = Table(
                    [[Paragraph(header_left, item_title_style), Paragraph(header_right, ParagraphStyle('RightDates', parent=item_sub_style, alignment=TA_RIGHT))]],
                    colWidths=[380, 140]
                )
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                ]))

                story.append(header_table)

                desc = exp.get('description', '')
                if desc:
                    lines = [l.strip() for l in desc.split('\n') if l.strip()]
                    for l in lines:
                        clean_line = l.lstrip('•-* ')
                        story.append(Paragraph(f"• {clean_line}", bullet_style))
                story.append(Spacer(1, 6))

            story.append(Spacer(1, 4))

        # 5. Projects
        projects = data.get('projects', [])
        if projects:
            story.append(Paragraph("Key Projects", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=palette['accent'], spaceBefore=1, spaceAfter=4))

            for proj in projects:
                name = proj.get('name', 'Project')
                tech = proj.get('technologies', '')
                gh = proj.get('github', '')
                demo = proj.get('live_demo', '')

                title_part = f"<b>{name}</b>"
                if tech:
                    title_part += f" | <i>{tech}</i>"

                links_part = []
                if gh:
                    links_part.append(f"<a href='{gh}' color='blue'>GitHub</a>")
                if demo:
                    links_part.append(f"<a href='{demo}' color='blue'>Live Demo</a>")
                links_str = " | ".join(links_part)

                proj_table = Table(
                    [[Paragraph(title_part, item_title_style), Paragraph(links_str, ParagraphStyle('RightLinks', parent=item_sub_style, alignment=TA_RIGHT))]],
                    colWidths=[400, 120]
                )
                proj_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(proj_table)

                desc = proj.get('description', '')
                if desc:
                    lines = [l.strip() for l in desc.split('\n') if l.strip()]
                    for l in lines:
                        clean_line = l.lstrip('•-* ')
                        story.append(Paragraph(f"• {clean_line}", bullet_style))
                story.append(Spacer(1, 6))

            story.append(Spacer(1, 4))

        # 6. Education
        education = data.get('education', [])
        if education:
            story.append(Paragraph("Education", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=palette['accent'], spaceBefore=1, spaceAfter=4))

            for edu in education:
                deg = edu.get('degree', 'Degree')
                inst = edu.get('institution', 'Institution')
                field = edu.get('field', '')
                dates = f"{edu.get('start_date', '')} – {edu.get('end_date', '')}".strip(" –")
                gpa = edu.get('cgpa') or edu.get('percentage') or ''

                deg_str = f"<b>{deg}</b>" + (f" in {field}" if field else "") + f" — {inst}"
                meta_str = f"{dates}" + (f" | Score: {gpa}" if gpa else "")

                edu_table = Table(
                    [[Paragraph(deg_str, item_title_style), Paragraph(meta_str, ParagraphStyle('RightEdu', parent=item_sub_style, alignment=TA_RIGHT))]],
                    colWidths=[380, 140]
                )
                edu_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(edu_table)

                coursework = edu.get('relevant_coursework', '')
                if coursework:
                    story.append(Paragraph(f"<b>Relevant Coursework:</b> {coursework}", body_style))
                story.append(Spacer(1, 5))

            story.append(Spacer(1, 4))

        # 7. Certifications & Achievements
        certs = data.get('certifications', [])
        achieves = data.get('achievements', [])
        if certs or achieves:
            story.append(Paragraph("Certifications & Achievements", section_heading_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=palette['accent'], spaceBefore=1, spaceAfter=4))

            for c in certs:
                cert_title = c.get('certification') or c.get('name', '')
                issuer = c.get('issuer', '')
                date = c.get('date', '')
                line = f"• <b>{cert_title}</b>" + (f" — {issuer}" if issuer else "") + (f" ({date})" if date else "")
                story.append(Paragraph(line, bullet_style))

            for a in achieves:
                title_a = a.get('title', '')
                desc_a = a.get('description', '')
                line = f"• <b>{title_a}</b>" + (f": {desc_a}" if desc_a else "")
                story.append(Paragraph(line, bullet_style))

        # Build document
        doc.build(story)
        buffer.seek(0)
        return buffer

    @classmethod
    def generate_analysis_report_pdf(cls, analysis_data: Dict[str, Any], resume_data: Dict[str, Any]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        palette = PALETTES['professional']

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=palette['primary'],
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=palette['secondary'],
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'SectionHead',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=palette['primary'],
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor('#1E293B')
        )

        story = []

        # Header
        story.append(Paragraph("CareerLense — Resume Quality & ATS Analysis Report", title_style))
        story.append(Spacer(1, 4))
        name = resume_data.get('personal_info', {}).get('full_name', 'Candidate')
        story.append(Paragraph(f"Comprehensive Evaluation for <b>{name}</b> | Generated by CareerLense AI", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=palette['primary'], spaceBefore=2, spaceAfter=12))

        # Scores Summary Table
        overall_score = analysis_data.get('overall_score', 82)
        ats_score = analysis_data.get('ats_style_score', 88)

        score_table_data = [
            [
                Paragraph("<b>Estimated Resume Quality Score</b>", body_style),
                Paragraph(f"<b><font size=18 color='#2563EB'>{overall_score} / 100</font></b>", body_style),
                Paragraph("<b>ATS Readability Indicator</b>", body_style),
                Paragraph(f"<b><font size=18 color='#059669'>{ats_score}%</font></b>", body_style)
            ]
        ]
        score_table = Table(score_table_data, colWidths=[150, 110, 150, 110])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 12))

        # Section Score Breakdown
        story.append(Paragraph("Score Breakdown by Section", heading_style))
        breakdown = analysis_data.get('section_scores', {})
        bd_data = [
            ["Section", "Score", "Weight", "Assessment"]
        ]
        labels = [
            ('Content Quality', 'content', '20%'),
            ('Technical Skills', 'skills', '15%'),
            ('Key Projects', 'projects', '15%'),
            ('Experience Trajectory', 'experience', '15%'),
            ('Academic Background', 'education', '10%'),
            ('Formatting & Structure', 'formatting', '10%'),
            ('Header Completeness', 'completeness', '15%')
        ]
        for name_label, key, wt in labels:
            val = breakdown.get(key, 80)
            status = "Strong" if val >= 80 else ("Needs Polish" if val >= 65 else "Attention Required")
            bd_data.append([name_label, f"{val}/100", wt, status])

        bd_table = Table(bd_data, colWidths=[160, 90, 80, 190])
        bd_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(bd_table)
        story.append(Spacer(1, 12))

        # Strengths & Weaknesses
        story.append(Paragraph("Identified Strengths", heading_style))
        strengths = analysis_data.get('strengths', [])
        for s in strengths[:4]:
            story.append(Paragraph(f"✓ <b>{s}</b>", body_style))
            story.append(Spacer(1, 3))

        story.append(Spacer(1, 6))
        story.append(Paragraph("Areas Needing Attention", heading_style))
        weaknesses = analysis_data.get('weaknesses', [])
        for w in weaknesses[:4]:
            story.append(Paragraph(f"⚠ <b>{w}</b>", body_style))
            story.append(Spacer(1, 3))

        # Missing Items
        missing = analysis_data.get('missing_items', [])
        if missing:
            story.append(Spacer(1, 6))
            story.append(Paragraph("Missing Items", heading_style))
            for m in missing[:4]:
                story.append(Paragraph(f"✕ <b>{m}</b>", body_style))
                story.append(Spacer(1, 3))

        # Suggestions
        story.append(Spacer(1, 6))
        story.append(Paragraph("AI Recommendations & Action Plan", heading_style))
        suggestions = analysis_data.get('suggestions', [])
        for i, sug in enumerate(suggestions[:4], 1):
            sec = sug.get('section', 'General')
            prob = sug.get('problem') or sug.get('issue', '')
            rec = sug.get('recommendation') or sug.get('suggestion', '')
            ex = sug.get('example_improvement', '')

            story.append(Paragraph(f"<b>{i}. [{sec}] {prob}</b>", body_style))
            story.append(Paragraph(f"<i>Recommendation:</i> {rec}", body_style))
            if ex:
                story.append(Paragraph(f"<i>Example:</i> <font color='#475569'>{ex}</font>", body_style))
            story.append(Spacer(1, 6))

        # Disclaimer footer
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceBefore=4, spaceAfter=6))
        story.append(Paragraph(
            "<b>Disclaimer:</b> CareerLense scores and suggestions are analytical estimates meant for self-improvement and readability optimization. They do not constitute a guarantee of employment, hiring outcomes, or specific ATS algorithm pass rates.",
            ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#64748B'))
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer
