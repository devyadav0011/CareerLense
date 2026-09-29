from flask import Blueprint, render_template, session, redirect, url_for, Response

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
@main_bp.route('/resume-builder')
def builder():
    return render_template('builder.html')

@main_bp.route('/analyzer')
@main_bp.route('/resume-analyzer')
def analyzer():
    return render_template('analyzer.html')

@main_bp.route('/ats-resume-checker')
def ats_resume_checker():
    return render_template('ats_checker.html')

@main_bp.route('/job-matcher')
def job_matcher():
    return render_template('job_matcher.html')

@main_bp.route('/skill-gap-analysis')
def skill_gap_analysis():
    return render_template('skill_gap_analysis.html')

@main_bp.route('/improver')
@main_bp.route('/ai-resume-writer')
def improver():
    return render_template('improver.html')

@main_bp.route('/results')
def results():
    return render_template('results.html')

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

@main_bp.route('/robots.txt')
def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /results
Disallow: /preview
Disallow: /login
Disallow: /register
Disallow: /saved-resumes
Disallow: /history

Sitemap: https://careerlense.xyz/sitemap.xml
"""
    return Response(content, mimetype='text/plain')

@main_bp.route('/sitemap.xml')
def sitemap_xml():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://careerlense.xyz/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/resume-builder</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/resume-analyzer</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/ats-resume-checker</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/job-matcher</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/skill-gap-analysis</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/ai-resume-writer</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/features</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/how-it-works</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/about</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/privacy</loc>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://careerlense.xyz/terms</loc>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>"""
    return Response(xml_content, mimetype='application/xml')
