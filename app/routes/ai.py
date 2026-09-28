from flask import Blueprint, request, jsonify, session
from ..services.ai_service import AIService
from ..utils.session_store import SessionStore

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/analyze', methods=['POST'])
def ai_analyze():
    data = request.get_json(silent=True) or {}
    structured = data.get('structured_data')
    raw_text = data.get('raw_text')

    if not structured:
        curr = SessionStore.get_current_resume()
        if curr:
            structured = curr.get('structured_data')
            raw_text = raw_text or curr.get('raw_text')

    if not structured:
        return jsonify({'error': 'No resume found for AI analysis.'}), 400

    try:
        analysis = AIService.analyze_resume(structured, raw_text or "")
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        return jsonify({'error': f'AI analysis failed: {str(e)}'}), 500


@ai_bp.route('/improve', methods=['POST'])
def ai_improve():
    data = request.get_json(silent=True) or {}
    section = data.get('section', 'General')
    content = data.get('content', '').strip()
    mode = data.get('mode', 'Professional')
    job_context = data.get('job_context')

    if not content:
        return jsonify({'error': 'Please provide text content to improve.'}), 400

    valid_modes = ['Professional', 'Concise', 'Technical', 'Entry-Level', 'Impact-Focused', 'ATS-Friendly']
    if mode not in valid_modes:
        mode = 'Professional'

    try:
        improved = AIService.rewrite_section(section, content, mode, job_context)
        return jsonify({
            'success': True,
            'original': content,
            'improved': improved,
            'mode': mode,
            'section': section
        })
    except Exception as e:
        return jsonify({'error': f'AI rewrite failed: {str(e)}'}), 500


@ai_bp.route('/summarize', methods=['POST'])
def ai_summarize():
    data = request.get_json(silent=True) or {}
    summary = data.get('summary', '').strip()
    if not summary and 'resume_data' in data:
        summary = data['resume_data'].get('personal_info', {}).get('summary', '').strip()

    mode = data.get('mode', 'Professional')

    if not summary:
        curr = SessionStore.get_current_resume() or {}
        summary = curr.get('structured_data', {}).get('personal_info', {}).get('summary', '').strip()

    if not summary:
        return jsonify({'error': 'No summary text provided to optimize.'}), 400

    try:
        improved = AIService.rewrite_section('Summary', summary, mode)
        return jsonify({
            'success': True,
            'original': summary,
            'improved': improved,
            'summary': improved
        })
    except Exception as e:
        return jsonify({'error': f'Summary optimization failed: {str(e)}'}), 500


@ai_bp.route('/project', methods=['POST'])
def ai_project():
    data = request.get_json(silent=True) or {}
    project_desc = data.get('description', '').strip() or data.get('details', '').strip()
    mode = data.get('mode', 'Technical')

    if not project_desc:
        return jsonify({'error': 'No project description provided.'}), 400

    try:
        improved = AIService.rewrite_section('Project Description', project_desc, mode)
        return jsonify({
            'success': True,
            'original': project_desc,
            'improved': improved,
            'bullet_points': [improved] if isinstance(improved, str) else improved
        })
    except Exception as e:
        return jsonify({'error': f'Project optimization failed: {str(e)}'}), 500


@ai_bp.route('/chat', methods=['POST'])
def ai_chat():
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Please provide a message or question.'}), 400

    curr = session.get('current_resume')
    resume_context = curr.get('structured_data') if curr else None
    job_match = curr.get('job_match') if curr else None
    job_context = job_match.get('job_description') if job_match else None

    try:
        reply = AIService.chat_assistant(message, resume_context, job_context)
        return jsonify({
            'success': True,
            'reply': reply
        })
    except Exception as e:
        return jsonify({'error': f'CareerLense AI encountered an error: {str(e)}'}), 500
