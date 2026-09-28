// CareerLense Results Presentation Logic
(function() {
    'use strict';

    let chartInstance = null;

    async function init() {
        try {
            const res = await fetch('/api/resume/current');
            const data = await res.json();

            if (data.resume && (data.resume.scores || data.resume.structured_data)) {
                renderResults(data.resume);
            } else {
                // If visited directly without upload, load default sample
                loadDefaultResults();
            }
        } catch (e) {
            loadDefaultResults();
        }
    }

    function renderResults(resume) {
        const scores = resume.scores || {};
        const ats = resume.ats || {};
        const structured = resume.structured_data || {};
        const pi = structured.personal_info || {};

        // Title and Candidate Subtitle
        if (pi.full_name) {
            document.getElementById('candidateNameSub').textContent = `Evaluation for ${pi.full_name} (${pi.title || 'Candidate'})`;
        }

        // 1. Overall Score Dial
        const overall = scores.overall_score || 82;
        const scoreVal = document.getElementById('overallScoreValue');
        if (scoreVal) scoreVal.textContent = overall;

        const circle = document.getElementById('scoreProgressCircle');
        if (circle) {
            const maxCircumference = 314.15;
            const offset = maxCircumference - (overall / 100) * maxCircumference;
            circle.style.strokeDashoffset = offset;
            
            // Adjust circle color based on score
            if (overall >= 80) circle.classList.add('text-emerald-500');
            else if (overall >= 65) circle.classList.add('text-brand-600');
            else circle.classList.add('text-amber-500');
        }

        const gradeEl = document.getElementById('overallScoreGrade');
        if (gradeEl) {
            if (overall >= 85) gradeEl.textContent = 'Excellent Executive Profile';
            else if (overall >= 75) gradeEl.textContent = 'Competitive Candidate Profile';
            else if (overall >= 60) gradeEl.textContent = 'Needs Minor Improvements';
            else gradeEl.textContent = 'Substantial Revisions Recommended';
        }

        // 2. ATS Score & Checks
        const atsVal = ats.ats_score || 88;
        const atsValEl = document.getElementById('atsScoreValue');
        if (atsValEl) atsValEl.textContent = `${atsVal}%`;

        const atsContainer = document.getElementById('atsChecksContainer');
        if (atsContainer && ats.checks) {
            atsContainer.innerHTML = '';
            ats.checks.slice(0, 4).forEach(chk => {
                const colorClass = chk.status === 'passed' ? 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/60' : (chk.status === 'warning' ? 'text-amber-500 bg-amber-50 dark:bg-amber-950/60' : 'text-rose-500 bg-rose-50 dark:bg-rose-950/60');
                const row = document.createElement('div');
                row.className = 'flex items-start gap-2.5 p-2 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800';
                row.innerHTML = `
                    <span class="w-5 h-5 rounded-md ${colorClass} flex items-center justify-center font-bold text-xs shrink-0">${chk.icon}</span>
                    <div>
                        <span class="font-bold text-slate-800 dark:text-slate-200 block">${escapeHtml(chk.name)}</span>
                        <span class="text-[11px] text-slate-500 leading-tight block">${escapeHtml(chk.description)}</span>
                    </div>
                `;
                atsContainer.appendChild(row);
            });
        }

        // 3. Section Scores Chart (Radar or Bar)
        const secScores = scores.section_scores || {
            content: 84, skills: 88, projects: 81, experience: 76, education: 90, formatting: 86, completeness: 82
        };
        renderChart(secScores);

        // 4. Strengths List (✓)
        const strengthsList = document.getElementById('strengthsList');
        if (strengthsList) {
            strengthsList.innerHTML = '';
            const strengths = scores.strengths || [
                "Strong action-oriented vocabulary used across work descriptions.",
                "Multi-tier skill set with high programming and database coverage.",
                "Document length is well proportioned for 1-2 page standard density."
            ];
            strengths.slice(0, 5).forEach(s => {
                const li = document.createElement('li');
                li.className = 'flex items-start gap-2 leading-relaxed';
                li.innerHTML = `<span class="text-emerald-500 font-bold shrink-0">✓</span><span>${escapeHtml(s)}</span>`;
                strengthsList.appendChild(li);
            });
        }

        // 5. Weaknesses List (⚠)
        const weaknessesList = document.getElementById('weaknessesList');
        if (weaknessesList) {
            weaknessesList.innerHTML = '';
            const weaknesses = scores.weaknesses || [
                "Project descriptions would benefit from measurable outcomes or metrics.",
                "No open-source repository link detected for academic projects."
            ];
            weaknesses.slice(0, 5).forEach(w => {
                const li = document.createElement('li');
                li.className = 'flex items-start gap-2 leading-relaxed';
                li.innerHTML = `<span class="text-amber-500 font-bold shrink-0">⚠</span><span>${escapeHtml(w)}</span>`;
                weaknessesList.appendChild(li);
            });
        }

        // 6. Missing Items List (✕)
        const missingList = document.getElementById('missingList');
        if (missingList) {
            missingList.innerHTML = '';
            const missing = scores.missing_items || [
                "Personal portfolio website link",
                "Cloud deployment certifications"
            ];
            if (missing.length === 0) {
                missingList.innerHTML = '<li class="text-slate-400 italic">No critical sections missing.</li>';
            } else {
                missing.slice(0, 5).forEach(m => {
                    const li = document.createElement('li');
                    li.className = 'flex items-start gap-2 leading-relaxed';
                    li.innerHTML = `<span class="text-rose-500 font-bold shrink-0">✕</span><span>${escapeHtml(m)}</span>`;
                    missingList.appendChild(li);
                });
            }
        }

        // 7. Suggestions Cards
        const sugContainer = document.getElementById('suggestionsContainer');
        if (sugContainer) {
            sugContainer.innerHTML = '';
            const suggestions = scores.suggestions || [
                {
                    section: 'Key Projects',
                    issue: 'Project descriptions are too generic',
                    reason: 'Descriptions like "Built an e-commerce website" lack technical depth.',
                    recommendation: 'Describe tech stack, architecture, and measurable outcomes if available.',
                    example_improvement: 'Current: "Built an e-commerce app." -> Suggestion: "Architected an e-commerce store with Flask and SQLite, cutting checkout drop-off by 15% (if measured)."'
                },
                {
                    section: 'Content Quality',
                    issue: 'Few measurable metrics detected',
                    reason: 'Quantifiable achievements prove your value to recruiters.',
                    recommendation: 'Add a measurable result if you have one. Never fabricate numbers.',
                    example_improvement: 'Example: "Engineered automated test suite covering 85% of codebase."'
                }
            ];

            suggestions.slice(0, 6).forEach(sug => {
                const card = document.createElement('div');
                card.className = 'p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700/80 space-y-2.5 text-xs';
                card.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-[11px] uppercase tracking-wider text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/80 px-2.5 py-0.5 rounded-full border border-brand-200 dark:border-brand-800">
                            ${escapeHtml(sug.section || 'General')}
                        </span>
                    </div>
                    <h3 class="font-bold text-slate-900 dark:text-white text-sm">
                        ${escapeHtml(sug.problem || sug.issue || '')}
                    </h3>
                    <p class="text-slate-600 dark:text-slate-300 leading-relaxed">
                        <strong>Why it matters:</strong> ${escapeHtml(sug.why_it_matters || sug.reason || '')}
                    </p>
                    <div class="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-slate-700 dark:text-slate-300 space-y-1">
                        <div class="font-semibold text-brand-600 dark:text-brand-400">Recommendation:</div>
                        <div class="leading-relaxed">${escapeHtml(sug.recommendation || sug.suggestion || '')}</div>
                        ${sug.example_improvement ? `
                            <div class="pt-1.5 border-t border-slate-100 dark:border-slate-800 text-slate-500 font-mono text-[11px]">
                                ${escapeHtml(sug.example_improvement)}
                            </div>
                        ` : ''}
                    </div>
                `;
                sugContainer.appendChild(card);
            });
        }

        if (window.lucide) window.lucide.createIcons();
    }

    function renderChart(secScores) {
        const canvas = document.getElementById('sectionScoresChart');
        if (!canvas) return;

        const isDark = document.documentElement.classList.contains('dark');
        const textColor = isDark ? '#94A3B8' : '#475569';
        const gridColor = isDark ? 'rgba(51, 65, 85, 0.4)' : 'rgba(226, 232, 240, 0.8)';

        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(canvas, {
            type: 'radar',
            data: {
                labels: ['Content', 'Skills', 'Projects', 'Experience', 'Education', 'Formatting', 'Completeness'],
                datasets: [{
                    label: 'Quality Score',
                    data: [
                        secScores.content || 84,
                        secScores.skills || 88,
                        secScores.projects || 81,
                        secScores.experience || 76,
                        secScores.education || 90,
                        secScores.formatting || 86,
                        secScores.completeness || 82
                    ],
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderColor: '#6366F1',
                    borderWidth: 2,
                    pointBackgroundColor: '#4F46E5',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#4F46E5'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: gridColor },
                        grid: { color: gridColor },
                        pointLabels: {
                            color: textColor,
                            font: { size: 10, weight: '600' }
                        },
                        ticks: {
                            display: false,
                            min: 0,
                            max: 100
                        }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    function loadDefaultResults() {
        renderResults({
            scores: {
                overall_score: 82,
                section_scores: { content: 84, skills: 88, projects: 81, experience: 76, education: 90, formatting: 86, completeness: 82 },
                strengths: [
                    "Strong action-oriented vocabulary used across work descriptions.",
                    "Multi-tier skill set with high programming and database coverage.",
                    "Document length is well proportioned for 1-2 page standard density."
                ],
                weaknesses: [
                    "Project descriptions would benefit from measurable outcomes or metrics.",
                    "No open-source repository link detected for academic projects."
                ],
                missing_items: ["Personal portfolio website link"],
                suggestions: [
                    {
                        section: 'Key Projects',
                        issue: 'Project descriptions are too generic',
                        reason: 'Descriptions like "Built an e-commerce website" lack technical depth.',
                        recommendation: 'Describe tech stack, architecture, and measurable outcomes if available.',
                        example_improvement: 'Current: "Built an e-commerce app." -> Suggestion: "Architected an e-commerce store with Flask and SQLite, cutting checkout drop-off by 15% (if measured)."'
                    },
                    {
                        section: 'Content Quality',
                        issue: 'Few measurable metrics detected',
                        reason: 'Quantifiable achievements prove your value to recruiters.',
                        recommendation: 'Add a measurable result if you have one. Never fabricate numbers.',
                        example_improvement: 'Example: "Engineered automated test suite covering 85% of codebase."'
                    }
                ]
            },
            ats: {
                ats_score: 88,
                checks: [
                    { name: 'Standard Section Headings', status: 'passed', icon: '✓', description: 'Recognized headings: Experience, Education, Skills, Projects.' },
                    { name: 'Contact Information Detectability', status: 'passed', icon: '✓', description: 'Full name, email address, and phone number cleanly extracted.' },
                    { name: 'Character Encoding & Symbols', status: 'passed', icon: '✓', description: 'Text extracted cleanly with UTF-8 compatibility.' },
                    { name: 'Table & Column Complexity', status: 'passed', icon: '✓', description: 'Flow-friendly vertical structure without unparseable table nesting.' }
                ]
            },
            structured_data: {
                personal_info: { full_name: 'Devan Yadav', title: 'Software Engineer' }
            }
        });
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
