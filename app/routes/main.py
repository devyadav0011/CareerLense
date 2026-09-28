from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/features')
def features():
    return render_template('features.html')

@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/builder')
def builder():
    return render_template('builder.html')

@main_bp.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

@main_bp.route('/job-matcher')
def job_matcher():
    return render_template('job_matcher.html')

@main_bp.route('/results')
def results():
    return render_template('results.html')

@main_bp.route('/improver')
def improver():
    return render_template('improver.html')

@main_bp.route('/preview')
def preview():
    return render_template('preview.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/register')
def register():
    return render_template('register.html')

@main_bp.route('/saved-resumes')
def saved_resumes():
    return render_template('saved_resumes.html')

@main_bp.route('/history')
def history():
    return render_template('history.html')
