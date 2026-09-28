from app.services.scorer import ResumeScorer

def test_resume_scorer(sample_resume_data, sample_raw_text):
    result = ResumeScorer.calculate_score(sample_resume_data, sample_raw_text)

    assert 'overall_score' in result
    assert isinstance(result['overall_score'], int)
    assert 50 <= result['overall_score'] <= 100

    assert result['label'] == 'Estimated Resume Quality Score'

    sec_scores = result['section_scores']
    assert 'content' in sec_scores
    assert 'skills' in sec_scores
    assert 'projects' in sec_scores
    assert 'experience' in sec_scores
    assert 'education' in sec_scores
    assert 'formatting' in sec_scores
    assert 'completeness' in sec_scores

    assert len(result['strengths']) > 0
    assert 'calculation_explanation' in result
    assert 'weights' in result['calculation_explanation']
