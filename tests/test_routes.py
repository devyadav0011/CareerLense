import io
import json

def test_public_pages(client):
    pages = ['/', '/features', '/how-it-works', '/about', '/privacy', '/terms', '/builder', '/analyzer', '/job-matcher', '/results', '/improver', '/preview']
    for p in pages:
        res = client.get(p)
        assert res.status_code == 200
        assert b"CareerLense" in res.data

def test_builder_save_and_current(client, sample_resume_data):
    res = client.post('/api/builder/save', json=sample_resume_data)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'scores' in data

    # Get current resume
    res2 = client.get('/api/resume/current')
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2['resume'] is not None

def test_job_matcher_route(client, sample_resume_data):
    # Prime session
    client.post('/api/builder/save', json=sample_resume_data)

    res = client.post('/api/job-match/analyze', json={
        'job_description': 'Seeking a Python engineer experienced with Flask and SQL and Docker containers.',
        'job_title': 'Software Engineer'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'result' in data
    assert 'match_score' in data['result']

def test_ai_improve_route(client):
    res = client.post('/api/ai/improve', json={
        'section': 'Experience',
        'content': 'Worked on Python backend and fixed database bugs.',
        'mode': 'Professional'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'improved' in data

def test_clear_session_route(client, sample_resume_data):
    client.post('/api/builder/save', json=sample_resume_data)
    res = client.post('/api/resume/clear-session')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

    # Current should be empty
    res2 = client.get('/api/resume/current')
    data2 = res2.get_json()
    assert data2['resume'] is None

def test_optional_auth_flow(client):
    # Register
    res = client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'tester@example.com',
        'password': 'password123'
    })
    assert res.status_code == 201

    # Me
    res_me = client.get('/api/auth/me')
    assert res_me.status_code == 200
    assert res_me.get_json()['authenticated'] is True

    # Logout
    res_out = client.post('/api/auth/logout')
    assert res_out.status_code == 200

    # Me after logout
    res_me2 = client.get('/api/auth/me')
    assert res_me2.get_json()['authenticated'] is False


def test_resume_upload_success_and_validation(client, sample_pdf_bytes):
    # Test valid PDF upload
    data = {
        'resume': (io.BytesIO(sample_pdf_bytes), 'jane_doe_resume.pdf')
    }
    res = client.post('/api/resume/upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_json = res.get_json()
    assert res_json['success'] is True
    assert 'structured_data' in res_json
    assert 'scores' in res_json

    # Test invalid file format
    invalid_data = {
        'resume': (io.BytesIO(b'some binary content'), 'malicious.exe')
    }
    res_inv = client.post('/api/resume/upload', data=invalid_data, content_type='multipart/form-data')
    assert res_inv.status_code == 400
    assert 'Invalid file format' in res_inv.get_json()['error']


def test_export_endpoints(client, sample_resume_data):
    # Prime session
    client.post('/api/builder/save', json=sample_resume_data)

    # Export Resume PDF
    for tpl in ['modern', 'minimal', 'professional']:
        res = client.get(f'/api/export/resume?template={tpl}')
        assert res.status_code == 200
        assert res.headers['Content-Type'] == 'application/pdf'
        assert res.data.startswith(b'%PDF')

    # Export Report PDF
    res_rep = client.get('/api/export/report')
    assert res_rep.status_code == 200
    assert res_rep.headers['Content-Type'] == 'application/pdf'
    assert res_rep.data.startswith(b'%PDF')


def test_ai_helper_endpoints(client, sample_resume_data):
    # Summarize
    res_sum = client.post('/api/ai/summarize', json={'resume_data': sample_resume_data})
    assert res_sum.status_code == 200
    assert 'summary' in res_sum.get_json()

    # Project bullet points
    res_proj = client.post('/api/ai/project', json={
        'name': 'E-Commerce Platform',
        'tech': 'Flask, Stripe, Redis',
        'details': 'Built checkout and payment webhooks'
    })
    assert res_proj.status_code == 200
    assert 'bullet_points' in res_proj.get_json()

    # AI Chat Assistant
    res_chat = client.post('/api/ai/chat', json={
        'message': 'How can I make my bullet points more impactful?',
        'resume_context': sample_resume_data
    })
    assert res_chat.status_code == 200
    assert 'reply' in res_chat.get_json()


def test_builder_preview_route(client, sample_resume_data):
    res = client.post('/api/builder/preview', json={
        'resume_data': sample_resume_data,
        'template': 'modern'
    })
    assert res.status_code == 200
    assert res.get_json()['success'] is True


def test_auth_save_and_manage_resumes(client, sample_resume_data):
    # Register & Login
    client.post('/api/auth/register', json={
        'name': 'Alex Smith',
        'email': 'alex@example.com',
        'password': 'securepassword123'
    })
    client.post('/api/auth/login', json={
        'email': 'alex@example.com',
        'password': 'securepassword123'
    })

    # Save resume to current session first
    client.post('/api/builder/save', json=sample_resume_data)

    # Save resume to user account
    res_save = client.post('/api/auth/save-resume', json={'title': 'Alex Smith CV'})
    assert res_save.status_code == 200
    saved_data = res_save.get_json()
    assert saved_data['success'] is True
    resume_id = saved_data['resume']['id']

    # List saved resumes
    res_list = client.get('/api/auth/saved-resumes')
    assert res_list.status_code == 200
    resumes = res_list.get_json()['resumes']
    assert len(resumes) >= 1
    assert any(r['id'] == resume_id for r in resumes)

    # Delete saved resume
    res_del = client.delete(f'/api/auth/saved-resumes/{resume_id}')
    assert res_del.status_code == 200
    assert res_del.get_json()['success'] is True

    # Verify deleted
    res_list2 = client.get('/api/auth/saved-resumes')
    resumes2 = res_list2.get_json()['resumes']
    assert not any(r['id'] == resume_id for r in resumes2)


def test_seo_routes_and_canonicals(client):
    landing_pages = [
        ('/', 'https://careerlense.xyz/'),
        ('/resume-builder', 'https://careerlense.xyz/resume-builder'),
        ('/builder', 'https://careerlense.xyz/resume-builder'),
        ('/resume-analyzer', 'https://careerlense.xyz/resume-analyzer'),
        ('/analyzer', 'https://careerlense.xyz/resume-analyzer'),
        ('/ats-resume-checker', 'https://careerlense.xyz/ats-resume-checker'),
        ('/job-matcher', 'https://careerlense.xyz/job-matcher'),
        ('/skill-gap-analysis', 'https://careerlense.xyz/skill-gap-analysis'),
        ('/ai-resume-writer', 'https://careerlense.xyz/ai-resume-writer'),
        ('/improver', 'https://careerlense.xyz/ai-resume-writer'),
        ('/features', 'https://careerlense.xyz/features'),
        ('/how-it-works', 'https://careerlense.xyz/how-it-works'),
        ('/about', 'https://careerlense.xyz/about'),
        ('/privacy', 'https://careerlense.xyz/privacy'),
        ('/terms', 'https://careerlense.xyz/terms'),
    ]
    for path, expected_canonical in landing_pages:
        res = client.get(path)
        assert res.status_code == 200
        html = res.data.decode('utf-8')
        assert f'<link rel="canonical" href="{expected_canonical}">' in html
        assert 'CareerLense' in html
        assert 'name="description"' in html
        assert 'property="og:title"' in html
        assert 'property="og:image"' in html
        assert 'careerlense-og.png' in html


def test_robots_txt(client):
    res = client.get('/robots.txt')
    assert res.status_code == 200
    assert res.content_type.startswith('text/plain')
    content = res.data.decode('utf-8')
    assert 'User-agent: *' in content
    assert 'Allow: /' in content
    assert 'Disallow: /api/' in content
    assert 'Disallow: /results' in content
    assert 'Disallow: /preview' in content
    assert 'Disallow: /login' in content
    assert 'Disallow: /register' in content
    assert 'Disallow: /saved-resumes' in content
    assert 'Disallow: /history' in content
    assert 'Sitemap: https://careerlense.xyz/sitemap.xml' in content


def test_sitemap_xml(client):
    res = client.get('/sitemap.xml')
    assert res.status_code == 200
    assert 'application/xml' in res.content_type or 'text/xml' in res.content_type
    xml = res.data.decode('utf-8')
    assert '<urlset' in xml
    assert 'http://www.sitemaps.org/schemas/sitemap/0.9' in xml
    expected_urls = [
        'https://careerlense.xyz/',
        'https://careerlense.xyz/resume-builder',
        'https://careerlense.xyz/resume-analyzer',
        'https://careerlense.xyz/ats-resume-checker',
        'https://careerlense.xyz/job-matcher',
        'https://careerlense.xyz/skill-gap-analysis',
        'https://careerlense.xyz/ai-resume-writer',
        'https://careerlense.xyz/features',
        'https://careerlense.xyz/how-it-works',
        'https://careerlense.xyz/about',
        'https://careerlense.xyz/privacy',
        'https://careerlense.xyz/terms',
    ]
    for url in expected_urls:
        assert f'<loc>{url}</loc>' in xml


def test_private_pages_noindex(client):
    private_pages = [
        '/results',
        '/preview',
        '/login',
        '/register',
        '/saved-resumes',
        '/history',
        '/nonexistent-page-404-check'
    ]
    for path in private_pages:
        res = client.get(path)
        html = res.data.decode('utf-8')
        assert 'name="robots" content="noindex, nofollow"' in html


def test_render_domain_301_redirect(client):
    res = client.get('/', headers={'Host': 'careerlense-wtv4.onrender.com'})
    assert res.status_code == 301
    assert res.headers['Location'] == 'https://careerlense.xyz/'

    res_path = client.get('/features?ref=test', headers={'Host': 'careerlense-wtv4.onrender.com'})
    assert res_path.status_code == 301
    assert res_path.headers['Location'] == 'https://careerlense.xyz/features?ref=test'

