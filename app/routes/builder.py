from flask import Blueprint, request, jsonify, session, send_file
from ..services.scorer import ResumeScorer
from ..services.ats_checker import ATSChecker
from ..services.pdf_service import PDFService
from ..utils.session_store import SessionStore
from ..models import db, Resume

builder_bp = Blueprint('builder', __name__, url_prefix='/api/builder')

@builder_bp.route('/save', methods=['POST'])
def save_builder():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No resume data provided.'}), 400

    # Build raw text equivalent for scoring
    raw_lines = []
    info = data.get('personal_info', {})
    raw_lines.append(info.get('full_name', ''))
    raw_lines.append(info.get('title', ''))
    raw_lines.append(f"{info.get('email', '')} {info.get('phone', '')} {info.get('location', '')}")
    raw_lines.append(info.get('summary', ''))

    raw_lines.append("EXPERIENCE")
    for exp in data.get('experience', []):
        raw_lines.append(f"{exp.get('position', '')} at {exp.get('company', '')}")
        raw_lines.append(exp.get('description', ''))

    raw_lines.append("EDUCATION")
    for edu in data.get('education', []):
        raw_lines.append(f"{edu.get('degree', '')} from {edu.get('institution', '')}")

    raw_lines.append("SKILLS")
    skills = data.get('skills', {})
    if isinstance(skills, dict):
        all_s = skills.get('all', [])
        raw_lines.append(", ".join(all_s))
    elif isinstance(skills, list):
        raw_lines.append(", ".join(skills))

    raw_lines.append("PROJECTS")
    for proj in data.get('projects', []):
        raw_lines.append(f"{proj.get('name', '')} {proj.get('technologies', '')}")
        raw_lines.append(proj.get('description', ''))

    raw_text = "\n".join([l for l in raw_lines if l])

    # Score resume
    score_res = ResumeScorer.calculate_score(data, raw_text)
    ats_res = ATSChecker.evaluate(raw_text, data)

    # Store in server-side session
    SessionStore.set_current_resume({
        'filename': f"{info.get('full_name', 'Resume')}.pdf",
        'raw_text': raw_text,
        'structured_data': data,
        'scores': score_res,
        'ats': ats_res
    })

    return jsonify({
        'success': True,
        'scores': score_res,
        'ats': ats_res,
        'message': 'Resume saved to current session successfully!'
    })


@builder_bp.route('/update', methods=['PUT'])
def update_builder():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided.'}), 400

    curr = session.get('current_resume') or {'structured_data': {}}
    structured = curr.get('structured_data', {})

    section = data.get('section')
    content = data.get('content')

    if section and content is not None:
        structured[section] = content
        curr['structured_data'] = structured
        session['current_resume'] = curr
        session.modified = True
        return jsonify({'success': True, 'structured_data': structured})

    return jsonify({'error': 'Section and content required.'}), 400


@builder_bp.route('/preview', methods=['POST'])
def preview_builder():
    data = request.get_json() or {}
    template = data.get('template', 'modern')
    structured = data.get('resume_data') or session.get('current_resume', {}).get('structured_data')

    if not structured:
        return jsonify({'error': 'No resume data available for preview.'}), 400

    return jsonify({
        'success': True,
        'template': template,
        'resume_data': structured
    })


@builder_bp.route('/export', methods=['POST'])
def export_builder():
    data = request.get_json() or {}
    curr = SessionStore.get_current_resume() or {}
    structured = data.get('resume_data') or curr.get('structured_data')
    template = data.get('template', 'modern')

    if not structured:
        return jsonify({'error': 'No resume data to export.'}), 400

    try:
        pdf_stream = PDFService.generate_resume_pdf(structured, template=template)
        name = structured.get('personal_info', {}).get('full_name', 'Resume')
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip() or 'Resume'
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{clean_name}_CareerLense.pdf"
        )
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
