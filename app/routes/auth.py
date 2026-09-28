from flask import Blueprint, request, jsonify, session
from ..models import db, User, Resume, ResumeAnalysis
from ..utils.security import hash_password, verify_password, validate_email
from ..utils.session_store import SessionStore

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Please provide a valid email address.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists.'}), 409

    try:
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session.modified = True

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'Account created successfully!'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_email'] = user.email
    session.modified = True

    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'message': f'Welcome back, {user.name}!'
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.modified = True
    return jsonify({'success': True, 'message': 'Logged out successfully.'})


@auth_bp.route('/me', methods=['GET'])
def get_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'user': None, 'authenticated': False})

    user = db.session.get(User, user_id)
    if not user:
        session.pop('user_id', None)
        return jsonify({'user': None, 'authenticated': False})

    return jsonify({
        'user': user.to_dict(),
        'authenticated': True
    })


@auth_bp.route('/save-resume', methods=['POST'])
def save_resume_to_account():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Please log in to permanently save your resume to your account.'}), 401

    curr = SessionStore.get_current_resume()
    if not curr:
        return jsonify({'error': 'No active resume found in session to save.'}), 400

    data = request.get_json(silent=True) or {}
    title = data.get('title') or curr.get('structured_data', {}).get('personal_info', {}).get('full_name', 'My Resume')

    try:
        new_resume = Resume(
            user_id=user_id,
            title=title,
            filename=curr.get('filename'),
            raw_text=curr.get('raw_text'),
            structured_data=curr.get('structured_data')
        )
        db.session.add(new_resume)
        db.session.commit()

        scores = curr.get('scores', {})
        if scores:
            sec_scores = scores.get('section_scores', {})
            analysis = ResumeAnalysis(
                resume_id=new_resume.id,
                overall_score=scores.get('overall_score', 0),
                content_score=sec_scores.get('content', 0),
                skills_score=sec_scores.get('skills', 0),
                projects_score=sec_scores.get('projects', 0),
                experience_score=sec_scores.get('experience', 0),
                education_score=sec_scores.get('education', 0),
                formatting_score=sec_scores.get('formatting', 0),
                completeness_score=sec_scores.get('completeness', 0),
                ats_style_score=curr.get('ats', {}).get('ats_score', 0),
                score_breakdown=sec_scores,
                strengths=scores.get('strengths', []),
                weaknesses=scores.get('weaknesses', []),
                missing_items=scores.get('missing_items', [])
            )
            db.session.add(analysis)
            db.session.commit()

        return jsonify({
            'success': True,
            'resume': new_resume.to_dict(),
            'message': 'Resume saved to your account successfully!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save resume: {str(e)}'}), 500


@auth_bp.route('/saved-resumes', methods=['GET'])
def get_saved_resumes():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required.'}), 401

    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
    results = []
    for r in resumes:
        latest_analysis = ResumeAnalysis.query.filter_by(resume_id=r.id).order_by(ResumeAnalysis.created_at.desc()).first()
        res_data = r.to_dict()
        res_data['latest_analysis'] = latest_analysis.to_dict() if latest_analysis else None
        results.append(res_data)

    return jsonify({'resumes': results})


@auth_bp.route('/saved-resumes/<int:resume_id>', methods=['DELETE'])
def delete_saved_resume(resume_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required.'}), 401

    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return jsonify({'error': 'Resume not found.'}), 404

    try:
        db.session.delete(resume)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Resume deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500
