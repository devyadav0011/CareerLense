// CareerLense Job Matcher Client Logic
(function() {
    'use strict';

    let currentResumeData = null;

    const SAMPLE_JOB = `Senior Software Engineer — Backend & Systems
Company: CloudScale Solutions Inc.
Location: San Francisco, CA / Remote

About the Role:
We are seeking an experienced Software Engineer to design, build, and optimize scalable backend services and distributed APIs. You will work alongside our product and infrastructure teams to deliver high-throughput web applications.

Responsibilities:
• Architect, build, and maintain production RESTful APIs using Python, Flask, or FastAPI.
• Design schema migrations and optimize SQL query performance on PostgreSQL.
• Implement caching strategies using Redis and message queues.
• Containerize microservices with Docker and deploy through automated CI/CD pipelines (GitHub Actions).
• Write unit tests and maintain high test coverage for core business logic.
• Collaborate with frontend developers working with React, TypeScript, and modern JavaScript.

Requirements:
• 3+ years of professional software engineering experience.
• Strong proficiency in Python, SQL, REST APIs, and Git version control.
• Experience with cloud platforms (AWS or GCP), Docker containers, and CI/CD pipelines.
• Familiarity with unit testing frameworks and agile methodologies.
• Degree in Computer Science or equivalent practical experience.`;

    async function init() {
        bindEvents();
        await loadActiveResume();
    }

    async function loadActiveResume() {
        try {
            const res = await fetch('/api/resume/current');
            const data = await res.json();
            const badge = document.getElementById('activeResumeName');

            if (data.resume && data.resume.structured_data) {
                currentResumeData = data.resume.structured_data;
                const name = currentResumeData.personal_info?.full_name || 'Active Resume';
                const title = currentResumeData.personal_info?.title || '';
                if (badge) badge.textContent = `Using: ${name} ${title ? `(${title})` : ''}`;

                // If job match already exists in session, render it!
                if (data.resume.job_match) {
                    renderMatchResults(data.resume.job_match);
                }
            } else {
                if (badge) badge.textContent = 'Using Sample Profile (Devan Yadav - Senior Software Engineer)';
            }
        } catch (e) {}
    }

    function bindEvents() {
        document.getElementById('loadSampleJobBtn')?.addEventListener('click', () => {
            const textarea = document.getElementById('jobDescriptionText');
            const titleInput = document.getElementById('targetJobTitle');
            if (textarea) textarea.value = SAMPLE_JOB;
            if (titleInput) titleInput.value = 'Senior Software Engineer — Backend & Systems';
            window.CareerLense?.showToast('Loaded sample software engineering job posting!', 'info');
        });

        document.getElementById('analyzeMatchBtn')?.addEventListener('click', runJobMatch);
    }

    async function runJobMatch() {
        const jobDesc = document.getElementById('jobDescriptionText')?.value.trim();
        const jobTitle = document.getElementById('targetJobTitle')?.value.trim();

        if (!jobDesc || jobDesc.length < 30) {
            window.CareerLense?.showToast('Please paste a job description with at least 30 characters.', 'warning');
            return;
        }

        const btn = document.getElementById('analyzeMatchBtn');
        btn.innerHTML = '<span class="animate-spin">⏳</span> Analyzing Match...';
        btn.disabled = true;

        try {
            const res = await fetch('/api/job-match/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_description: jobDesc,
                    job_title: jobTitle,
                    resume_data: currentResumeData
                })
            });

            const data = await res.json();
            btn.innerHTML = '<i data-lucide="crosshair" class="w-4 h-4"></i> Analyze Match';
            btn.disabled = false;
            if (window.lucide) window.lucide.createIcons();

            if (data.success && data.result) {
                renderMatchResults(data.result);
                window.CareerLense?.showToast('Job match analyzed successfully!', 'success');
            } else {
                window.CareerLense?.showToast(data.error || 'Job match failed.', 'error');
            }
        } catch (err) {
            btn.innerHTML = '<i data-lucide="crosshair" class="w-4 h-4"></i> Analyze Match';
            btn.disabled = false;
            window.CareerLense?.showToast('Network error during match analysis.', 'error');
        }
    }

    function renderMatchResults(res) {
        const resultsSection = document.getElementById('matchResultsSection');
        if (!resultsSection) return;

        resultsSection.classList.remove('hidden');

        // Score
        document.getElementById('matchScoreVal').textContent = res.match_score || 78;

        // Breakdown
        const bd = res.score_breakdown || {};
        document.getElementById('bd_skills').textContent = `${bd.skills || 82}%`;
        document.getElementById('bd_exp').textContent = `${bd.experience || 71}%`;
        document.getElementById('bd_proj').textContent = `${bd.projects || 84}%`;
        document.getElementById('bd_kw').textContent = `${bd.keywords || 76}%`;
        document.getElementById('bd_edu').textContent = `${bd.education || 90}%`;

        // Matched Skills
        const matchedContainer = document.getElementById('matchedSkillsList');
        if (matchedContainer) {
            matchedContainer.innerHTML = '';
            (res.matched_skills || ['Python', 'SQL', 'Git', 'Flask', 'REST APIs']).forEach(s => {
                const span = document.createElement('span');
                span.className = 'px-3 py-1 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 font-semibold text-xs flex items-center gap-1';
                span.innerHTML = `<span class="text-emerald-500 font-bold">✓</span> ${escapeHtml(s)}`;
                matchedContainer.appendChild(span);
            });
        }

        // Missing Skills
        const missingContainer = document.getElementById('missingSkillsList');
        if (missingContainer) {
            missingContainer.innerHTML = '';
            (res.missing_skills || ['Docker', 'CI/CD', 'Unit Testing']).forEach(s => {
                const span = document.createElement('span');
                span.className = 'px-3 py-1 rounded-xl bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 font-semibold text-xs flex items-center gap-1';
                span.innerHTML = `<span class="text-amber-500 font-bold">⚠</span> ${escapeHtml(s)}`;
                missingContainer.appendChild(span);
            });
        }

        // Keyword Matrix
        const kwContainer = document.getElementById('keywordAnalysisContainer');
        if (kwContainer) {
            kwContainer.innerHTML = '';
            (res.keyword_analysis || []).forEach(kw => {
                const card = document.createElement('div');
                const isMatched = kw.status === 'matched';
                const isPartial = kw.status === 'partial';
                const borderClass = isMatched ? 'border-emerald-200 dark:border-emerald-800/80 bg-emerald-50/40 dark:bg-emerald-950/30' : (isPartial ? 'border-amber-200 dark:border-amber-800/80 bg-amber-50/40 dark:bg-amber-950/30' : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850');
                const iconColor = isMatched ? 'text-emerald-500' : (isPartial ? 'text-amber-500' : 'text-slate-400');

                card.className = `p-2.5 rounded-xl border ${borderClass} flex items-center justify-between text-xs`;
                card.innerHTML = `
                    <span class="font-medium text-slate-800 dark:text-slate-200 truncate">${escapeHtml(kw.term)}</span>
                    <span class="font-bold ${iconColor} ml-1 shrink-0">${kw.icon}</span>
                `;
                kwContainer.appendChild(card);
            });
        }

        // Recommendations
        const recContainer = document.getElementById('jobRecommendationsContainer');
        if (recContainer) {
            recContainer.innerHTML = '';
            (res.recommendations || [
                "Highlight relevant backend experience in Python and Flask.",
                "Make REST API design experience more visible in the project section.",
                "Add unit testing experience if applicable to your actual background.",
                "Position matched database skills (SQL, PostgreSQL) near the top of your resume."
            ]).forEach((rec, idx) => {
                const item = document.createElement('div');
                item.className = 'p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 flex items-start gap-2.5';
                item.innerHTML = `
                    <span class="w-5 h-5 rounded-md bg-violet-100 dark:bg-violet-900/60 text-violet-700 dark:text-violet-300 font-bold flex items-center justify-center shrink-0 text-xs">
                        ${idx + 1}
                    </span>
                    <span class="leading-relaxed">${escapeHtml(rec)}</span>
                `;
                recContainer.appendChild(item);
            });
        }

        if (window.lucide) window.lucide.createIcons();

        // Smooth scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
