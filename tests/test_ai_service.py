from app.services.ai_service import AIService

def test_ai_analysis_schema(sample_resume_data, sample_raw_text):
    result = AIService.analyze_resume(sample_resume_data, sample_raw_text)

    assert 'overall_score' in result
    assert 'section_scores' in result
    assert 'strengths' in result
    assert 'weaknesses' in result
    assert 'suggestions' in result

def test_ai_rewrite_modes():
    content = "I was responsible for developing the database and wrote code for the API."
    modes = ['Professional', 'Concise', 'Technical', 'Entry-Level', 'Impact-Focused', 'ATS-Friendly']

    for mode in modes:
        rewritten = AIService.rewrite_section('Experience', content, mode)
        assert len(rewritten) > 10
        assert rewritten != content

def test_ai_chat_assistant(sample_resume_data):
    question = "How can I improve my project section?"
    reply = AIService.chat_assistant(question, resume_context=sample_resume_data)
    assert len(reply) > 20
    assert "project" in reply.lower()
