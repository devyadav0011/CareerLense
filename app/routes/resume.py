import os
import uuid
from flask import Blueprint, request, jsonify, session, current_app
from ..utils.security import is_allowed_file, sanitize_filename
from ..utils.helpers import safe_remove_file
from ..utils.session_store import SessionStore
from ..services.parser import ResumeParser
from ..services.scorer import ResumeScorer
from ..services.ats_checker import ATSChecker
from ..services.ai_service import AIService
from ..models import db, Resume, ResumeAnalysis

resume_bp = Blueprint('resume', __name__, url_prefix='/api/resume')

@resume_bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded.'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    if not is_allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Only PDF and DOCX files are supported.'}), 400

    # Ensure uploads directory exists
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    # Secure unique filename
    safe_name = sanitize_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex[:12]}_{safe_name}"
    filepath = os.path.join(upload_folder, unique_filename)

    try:
        file.save(filepath)

        # Check file size
        file_size = os.path.getsize(filepath)
        max_size = current_app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            safe_remove_file(filepath)
            return jsonify({'error': f'File size exceeds {current_app.config["MAX_UPLOAD_SIZE_MB"]}MB limit.'}), 400

        # Parse file
        parsed = ResumeParser.parse_file(filepath)
        raw_text = parsed['raw_text']
        structured = parsed['structured_data']

        if not raw_text.strip():
            safe_remove_file(filepath)
            return jsonify({'error': 'Uploaded resume has no readable text content.'}), 400

        # Score resume
        score_res = ResumeScorer.calculate_score(structured, raw_text)

        # ATS check
        ats_res = ATSChecker.evaluate(raw_text, structured)

        # AI analysis
        ai_res = AIService.analyze_resume(structured, raw_text)

        # Save into server-side session for anonymous access
        SessionStore.set_current_resume({
            'filename': safe_name,
            'filepath': filepath,
            'raw_text': raw_text,
            'structured_data': structured,
            'scores': score_res,
            'ats': ats_res,
            'ai_analysis': ai_res
        })

        return jsonify({
            'success': True,
            'filename': safe_name,
            'structured_data': structured,
            'scores': score_res,
            'ats': ats_res,
            'ai_analysis': ai_res,
            'message': 'Resume parsed and analyzed successfully!'
        })

    except Exception as e:
        safe_remove_file(filepath)
        return jsonify({'error': f'Resume processing error: {str(e)}'}), 500


@resume_bp.route('/analyze', methods=['POST'])
def analyze_resume():
    data = request.get_json(silent=True) or {}
    structured = data.get('structured_data')
    raw_text = data.get('raw_text')

    curr = SessionStore.get_current_resume()
    if not structured or not raw_text:
        if curr:
            structured = structured or curr.get('structured_data')
            raw_text = raw_text or curr.get('raw_text')

    if not structured:
        return jsonify({'error': 'No resume data found to analyze.'}), 400

    raw_text = raw_text or ""
    score_res = ResumeScorer.calculate_score(structured, raw_text)
    ats_res = ATSChecker.evaluate(raw_text, structured)
    ai_res = AIService.analyze_resume(structured, raw_text)

    # Update session
    SessionStore.update_current_resume(
        scores=score_res,
        ats=ats_res,
        ai_analysis=ai_res
    )

    return jsonify({
        'success': True,
        'scores': score_res,
        'ats': ats_res,
        'ai_analysis': ai_res
    })


@resume_bp.route('/current', methods=['GET'])
def get_current_resume():
    curr = SessionStore.get_current_resume()
    if not curr:
        return jsonify({'resume': None, 'message': 'No active resume in session.'}), 200

    return jsonify({
        'resume': {
            'filename': curr.get('filename'),
            'structured_data': curr.get('structured_data', {}),
            'scores': curr.get('scores', {}),
            'ats': curr.get('ats', {}),
            'ai_analysis': curr.get('ai_analysis', {}),
            'job_match': curr.get('job_match', {})
        }
    })


@resume_bp.route('/current', methods=['DELETE'])
def delete_current_resume():
    curr = SessionStore.get_current_resume()
    if curr and curr.get('filepath'):
        safe_remove_file(curr['filepath'])

    SessionStore.clear()
    return jsonify({'success': True, 'message': 'Resume data and temporary files deleted successfully.'})


@resume_bp.route('/clear-session', methods=['POST'])
def clear_session():
    curr = SessionStore.get_current_resume()
    if curr and curr.get('filepath'):
        safe_remove_file(curr['filepath'])

    SessionStore.clear()
    session.clear()
    return jsonify({'success': True, 'message': 'Session cleared successfully.'})
