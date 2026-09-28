from app.services.job_matcher import JobMatcher

def test_job_matcher(sample_resume_data, sample_raw_text):
    job_desc = """We are looking for a Senior Backend Software Engineer with expertise in Python, Flask, SQL, Docker, and Kubernetes.
Experience building REST APIs and microservices is required. CI/CD experience with GitHub Actions is a plus."""

    result = JobMatcher.match(sample_resume_data, sample_raw_text, job_desc)

    assert 'match_score' in result
    assert 50 <= result['match_score'] <= 100

    # Skills check
    matched = [s.lower() for s in result['matched_skills']]
    assert 'python' in matched
    assert 'flask' in matched
    assert 'docker' in matched

    missing = [s.lower() for s in result['missing_skills']]
    assert 'kubernetes' in missing

    # Disclaimers and notices
    assert "Estimated match based on the provided resume" in result['disclaimer']
    assert "accurately reflect your actual experience" in result['missing_notice']

    # Recommendations
    assert len(result['recommendations']) > 0
