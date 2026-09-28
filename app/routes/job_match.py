from flask import Blueprint, request, jsonify, session
from ..services.job_matcher import JobMatcher
from ..utils.session_store import SessionStore

job_match_bp = Blueprint('job_match', __name__, url_prefix='/api/job-match')

@job_match_bp.route('/analyze', methods=['POST'])
def analyze_job_match():
    data = request.get_json(silent=True) or {}
    job_description = data.get('job_description', '').strip()
    job_title = data.get('job_title', '').strip()

    if not job_description:
        return jsonify({'error': 'Please provide a job description to analyze.'}), 400

    # Obtain resume from payload or session
    resume_data = data.get('resume_data')
    raw_text = data.get('raw_resume_text')

    curr = SessionStore.get_current_resume()
    if not resume_data and curr:
        resume_data = curr.get('structured_data')
        raw_text = curr.get('raw_text')

    if not resume_data:
        return jsonify({'error': 'No resume detected. Please upload a resume or build one first.'}), 400

    try:
        match_result = JobMatcher.match(
            resume_data=resume_data,
            raw_resume_text=raw_text or "",
            job_description=job_description
        )

        match_result['job_title'] = job_title or "Target Role"

        # Save match into server-side session
        SessionStore.update_current_resume(job_match=match_result)

        return jsonify({
            'success': True,
            'result': match_result
        })

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Job match calculation failed: {str(e)}'}), 500
