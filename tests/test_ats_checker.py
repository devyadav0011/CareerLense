from app.services.ats_checker import ATSChecker

def test_ats_checker(sample_raw_text, sample_resume_data):
    result = ATSChecker.evaluate(sample_raw_text, sample_resume_data)

    assert 'ats_score' in result
    assert 50 <= result['ats_score'] <= 100
    assert 'checks' in result
    assert len(result['checks']) >= 4

    assert "estimated ATS-style readability indicator" in result['disclaimer']
    assert "not a guarantee" in result['disclaimer']
