from app.services.pdf_service import PDFService

def test_resume_pdf_templates(sample_resume_data):
    for template in ['minimal', 'modern', 'professional']:
        pdf_stream = PDFService.generate_resume_pdf(sample_resume_data, template=template)
        data = pdf_stream.read()
        assert len(data) > 1000
        assert data.startswith(b'%PDF')

def test_analysis_report_pdf(sample_resume_data):
    analysis_data = {
        'overall_score': 82,
        'ats_style_score': 88,
        'section_scores': {'content': 84, 'skills': 88, 'projects': 81, 'experience': 76, 'education': 90, 'formatting': 86, 'completeness': 82},
        'strengths': ['Strong action verbs', 'Diverse skill coverage'],
        'weaknesses': ['Generic project descriptions'],
        'missing_items': ['Portfolio link'],
        'suggestions': [
            {'section': 'Projects', 'issue': 'Generic descriptions', 'reason': 'Lack of proof', 'recommendation': 'Add tech stack'}
        ]
    }

    pdf_stream = PDFService.generate_analysis_report_pdf(analysis_data, sample_resume_data)
    data = pdf_stream.read()
    assert len(data) > 1000
    assert data.startswith(b'%PDF')
