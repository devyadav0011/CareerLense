// CareerLense AI Resume Rewriter Client Logic
(function() {
    'use strict';

    let currentResume = null;
    let lastImprovedText = '';

    const WEAK_SAMPLES = {
        Experience: "I was responsible for making the website faster and worked on the Python backend.\nHelped the team with databases and fixed some bugs in the API.",
        Projects: "Created an e-commerce website with shopping cart.\nBuilt user login and added product pages using Python.",
        Summary: "Hardworking developer looking for a good software engineering job where I can use my skills in programming.",
        General: "Worked on frontend and backend features. Responsible for code reviews and meetings."
    };

    async function init() {
        bindEvents();
        await loadResumeContext();
    }

    async function loadResumeContext() {
        try {
            const res = await fetch('/api/resume/current');
            const data = await res.json();
            if (data.resume && data.resume.structured_data) {
                currentResume = data.resume.structured_data;
                populateFromCurrentResume('Experience');
            } else {
                insertSample('Experience');
            }
        } catch (e) {
            insertSample('Experience');
        }
    }

    function populateFromCurrentResume(section) {
        if (!currentResume) return;

        const input = document.getElementById('originalTextInput');
        if (!input) return;

        if (section === 'Experience' && currentResume.experience && currentResume.experience[0]) {
            input.value = currentResume.experience[0].description || WEAK_SAMPLES.Experience;
        } else if (section === 'Projects' && currentResume.projects && currentResume.projects[0]) {
            input.value = currentResume.projects[0].description || WEAK_SAMPLES.Projects;
        } else if (section === 'Summary' && currentResume.personal_info?.summary) {
            input.value = currentResume.personal_info.summary;
        } else {
            insertSample(section);
        }
    }

    function insertSample(section) {
        const input = document.getElementById('originalTextInput');
        if (input) {
            input.value = WEAK_SAMPLES[section] || WEAK_SAMPLES.Experience;
        }
    }

    function bindEvents() {
        const sectionPicker = document.getElementById('sectionPicker');
        const modePicker = document.getElementById('modePicker');
        const sampleBtn = document.getElementById('loadSampleTextBtn');
        const generateBtn = document.getElementById('generateImprovementBtn');
        const regenerateBtn = document.getElementById('regenerateBtn');
        const copyBtn = document.getElementById('copyImprovedBtn');

        sectionPicker?.addEventListener('change', (e) => {
            populateFromCurrentResume(e.target.value);
        });

        modePicker?.addEventListener('change', (e) => {
            const badge = document.getElementById('activeModeBadge');
            if (badge) badge.textContent = e.target.value;
        });

        sampleBtn?.addEventListener('click', () => {
            const sec = sectionPicker?.value || 'Experience';
            insertSample(sec);
            window.CareerLense?.showToast('Inserted sample bullet points!', 'info');
        });

        generateBtn?.addEventListener('click', () => runImprovement());
        regenerateBtn?.addEventListener('click', () => runImprovement());

        copyBtn?.addEventListener('click', () => {
            if (!lastImprovedText) {
                window.CareerLense?.showToast('No improved text to copy yet.', 'warning');
                return;
            }
            navigator.clipboard.writeText(lastImprovedText).then(() => {
                window.CareerLense?.showToast('Copied improved text to clipboard!', 'success');
            }).catch(() => {
                window.CareerLense?.showToast('Failed to copy text.', 'error');
            });
        });
    }

    async function runImprovement() {
        const content = document.getElementById('originalTextInput')?.value.trim();
        const section = document.getElementById('sectionPicker')?.value || 'Experience';
        const mode = document.getElementById('modePicker')?.value || 'Professional';
        const jobContext = document.getElementById('jobContextInput')?.value.trim();

        if (!content) {
            window.CareerLense?.showToast('Please enter or paste text to improve.', 'warning');
            return;
        }

        const output = document.getElementById('improvedTextOutput');
        const generateBtn = document.getElementById('generateImprovementBtn');

        if (output) {
            output.innerHTML = `
                <div class="flex flex-col items-center justify-center p-6 space-y-2 text-slate-400">
                    <span class="w-5 h-5 rounded-full border-2 border-brand-500 border-t-transparent animate-spin"></span>
                    <span class="text-xs">Rewriting in ${mode} mode...</span>
                </div>
            `;
        }
        if (generateBtn) generateBtn.disabled = true;

        try {
            const res = await fetch('/api/ai/improve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    section: section,
                    content: content,
                    mode: mode,
                    job_context: jobContext
                })
            });

            const data = await res.json();
            if (generateBtn) generateBtn.disabled = false;

            if (data.success && data.improved) {
                lastImprovedText = data.improved;
                if (output) {
                    output.className = 'w-full h-48 overflow-y-auto text-xs p-3.5 rounded-2xl border border-emerald-500/40 bg-emerald-50/20 dark:bg-emerald-950/20 text-slate-900 dark:text-white font-mono leading-relaxed whitespace-pre-wrap';
                    output.textContent = data.improved;
                }
                window.CareerLense?.showToast(`Generated ${mode} rewrite!`, 'success');
            } else {
                if (output) output.textContent = data.error || 'Failed to rewrite text.';
                window.CareerLense?.showToast(data.error || 'Rewrite failed.', 'error');
            }
        } catch (err) {
            if (generateBtn) generateBtn.disabled = false;
            if (output) output.textContent = 'Network error while contacting AI service.';
            window.CareerLense?.showToast('Network error.', 'error');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
