// CareerLense Resume Builder Client Logic
(function() {
    'use strict';

    let currentTemplate = 'modern';
    let saveTimeout = null;

    // Default Resume Data State
    const resumeData = {
        personal_info: {
            full_name: '',
            title: '',
            email: '',
            phone: '',
            location: '',
            linkedin: '',
            github: '',
            portfolio: '',
            summary: ''
        },
        skills: {
            programming_languages: [],
            frameworks: [],
            databases: [],
            cloud: [],
            tools: [],
            all: []
        },
        experience: [],
        projects: [],
        education: [],
        certifications: [],
        achievements: []
    };

    // Realistic Sample Profile
    const SAMPLE_RESUME = {
        personal_info: {
            full_name: 'Devan Yadav',
            title: 'Senior Full-Stack Software Engineer',
            email: 'devan.yadav@example.com',
            phone: '+1 (555) 349-8201',
            location: 'San Francisco, CA',
            linkedin: 'linkedin.com/in/devanyadav',
            github: 'github.com/devanyadav',
            portfolio: 'devanyadav.dev',
            summary: 'Results-driven Full-Stack Engineer with 5+ years of experience designing and building high-performance web applications, scalable REST APIs, and distributed cloud services using Python, Flask, React, and PostgreSQL. Passionate about system reliability, clean architecture, and developer productivity.'
        },
        skills: {
            programming_languages: ['Python', 'JavaScript', 'TypeScript', 'C++', 'SQL'],
            frameworks: ['React', 'Flask', 'Django', 'FastAPI', 'Node.js', 'Tailwind CSS'],
            databases: ['PostgreSQL', 'SQLite', 'Redis', 'MongoDB'],
            cloud: ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'GitHub Actions'],
            tools: ['Git', 'Postman', 'Linux', 'Vim', 'Agile / Scrum'],
            all: ['Python', 'JavaScript', 'TypeScript', 'C++', 'SQL', 'React', 'Flask', 'Django', 'FastAPI', 'Node.js', 'Tailwind CSS', 'PostgreSQL', 'SQLite', 'Redis', 'MongoDB', 'AWS', 'Docker', 'Kubernetes', 'CI/CD', 'GitHub Actions', 'Git', 'Postman', 'Linux', 'Agile / Scrum']
        },
        experience: [
            {
                position: 'Lead Software Engineer',
                company: 'Vanguard Cloud Technologies',
                location: 'San Francisco, CA',
                start_date: '2023',
                end_date: 'Present',
                description: '• Architected resilient microservices backend with Python and Flask supporting 100K+ daily active requests.\n• Spearheaded migration from monolithic database to PostgreSQL and Redis cache, optimizing query response latency by 35%.\n• Designed and enforced automated CI/CD deployment pipelines using GitHub Actions and Docker.'
            },
            {
                position: 'Full-Stack Developer',
                company: 'Apex Digital Labs',
                location: 'San Jose, CA',
                start_date: '2021',
                end_date: '2023',
                description: '• Developed responsive single-page web applications with React, TypeScript, and RESTful Flask backends.\n• Integrated third-party payment gateways and secure token-based user authentication workflows.\n• Collaborated with product designers to streamline UI accessibility and cross-browser rendering.'
            }
        ],
        projects: [
            {
                name: 'CareerLense — AI Career & Resume Platform',
                technologies: 'Python, Flask, SQLite, ReportLab, Tailwind CSS',
                github: 'github.com/devanyadav/careerlense',
                live_demo: 'careerlense.dev',
                description: '• Engineered a full-stack career platform with instant PDF parsing, multi-dimensional scoring, and job gap analysis.\n• Implemented client-side reactive resume builder with instant template switching and A4 PDF export engine.'
            },
            {
                name: 'Distributed Task Queue Engine',
                technologies: 'Python, Redis, Docker, WebSockets',
                github: 'github.com/devanyadav/task-queue',
                live_demo: '',
                description: '• Built a lightweight asynchronous job processing daemon with retry backoffs and live heartbeat monitoring.\n• benchmarked system performance to handle 2,000 concurrent jobs per worker instance.'
            }
        ],
        education: [
            {
                institution: 'University of California, Berkeley',
                degree: 'Bachelor of Science',
                field: 'Computer Science',
                start_date: '2017',
                end_date: '2021',
                cgpa: '3.85 / 4.0',
                percentage: '',
                relevant_coursework: 'Data Structures & Algorithms, Distributed Systems, Database Systems, Computer Networks'
            }
        ],
        certifications: [
            { certification: 'AWS Certified Solutions Architect – Associate', issuer: 'Amazon Web Services', date: '2024' },
            { certification: 'Professional Scrum Master I (PSM I)', issuer: 'Scrum.org', date: '2023' }
        ],
        achievements: [
            { title: 'First Place Winner', description: 'Silicon Valley Open AI Hackathon 2024 (Team Lead)' },
            { title: 'Open Source Contributor', description: 'Authored and maintained 3 popular Python developer utility libraries' }
        ]
    };

    function init() {
        bindInputs();
        bindTemplateButtons();
        bindAddButtons();
        bindExportButtons();
        bindAiButtons();

        // Check if session has resume data already
        loadInitialResumeData();
    }

    function setInputValue(id, val) {
        const el = document.getElementById(id);
        if (el) el.value = val || '';
    }

    function hasResumeContent(data) {
        if (!data) return false;
        const pi = data.personal_info || {};
        for (const k in pi) {
            if (typeof pi[k] === 'string' && pi[k].trim().length > 0) return true;
        }
        const sk = data.skills || {};
        for (const k in sk) {
            if (Array.isArray(sk[k]) && sk[k].length > 0) return true;
            if (typeof sk[k] === 'string' && sk[k].trim().length > 0) return true;
        }
        if (Array.isArray(data.experience) && data.experience.some(e => (e.position && e.position.trim()) || (e.company && e.company.trim()) || (e.description && e.description.trim()))) return true;
        if (Array.isArray(data.projects) && data.projects.some(p => (p.name && p.name.trim()) || (p.description && p.description.trim()))) return true;
        if (Array.isArray(data.education) && data.education.some(ed => (ed.institution && ed.institution.trim()) || (ed.degree && ed.degree.trim()))) return true;
        if (Array.isArray(data.certifications) && data.certifications.some(c => (c.certification && c.certification.trim()) || (c.name && c.name.trim()))) return true;
        if (Array.isArray(data.achievements) && data.achievements.some(a => (a.title && a.title.trim()) || (a.description && a.description.trim()))) return true;
        return false;
    }

    async function loadInitialResumeData() {
        try {
            const res = await fetch('/api/resume/current');
            const data = await res.json();
            if (data.resume && data.resume.structured_data && hasResumeContent(data.resume.structured_data)) {
                populateForm(data.resume.structured_data);
                return;
            }
        } catch (e) {}

        // Default: Open with empty fields. Do not automatically populate dummy data.
        clearAllForm(false);
    }

    function clearAllForm(syncServer = true) {
        if (saveTimeout) {
            clearTimeout(saveTimeout);
            saveTimeout = null;
        }

        resumeData.personal_info = {
            full_name: '',
            title: '',
            email: '',
            phone: '',
            location: '',
            linkedin: '',
            github: '',
            portfolio: '',
            summary: ''
        };
        resumeData.skills = {
            programming_languages: [],
            frameworks: [],
            databases: [],
            cloud: [],
            tools: [],
            all: []
        };
        resumeData.experience = [];
        resumeData.projects = [];
        resumeData.education = [];
        resumeData.certifications = [];
        resumeData.achievements = [];

        const inputIds = [
            'pi_fullName', 'pi_title', 'pi_email', 'pi_phone', 'pi_location',
            'pi_linkedin', 'pi_github', 'pi_portfolio', 'pi_summary',
            'skills_lang', 'skills_frameworks', 'skills_databases', 'skills_cloud', 'skills_tools',
            'certifications_text', 'achievements_text'
        ];
        inputIds.forEach(id => setInputValue(id, ''));

        renderExperienceList();
        renderProjectsList();
        renderEducationList();
        renderLivePreview();

        if (syncServer) {
            try {
                fetch('/api/resume/current', { method: 'DELETE' });
            } catch (e) {}
            window.CareerLense?.showToast('Resume form cleared', 'info');
        }
    }

    function populateForm(data) {
        if (!data) return;

        // Personal info
        const pi = data.personal_info || {};
        setInputValue('pi_fullName', pi.full_name || '');
        setInputValue('pi_title', pi.title || '');
        setInputValue('pi_email', pi.email || '');
        setInputValue('pi_phone', pi.phone || '');
        setInputValue('pi_location', pi.location || '');
        setInputValue('pi_linkedin', pi.linkedin || '');
        setInputValue('pi_github', pi.github || '');
        setInputValue('pi_portfolio', pi.portfolio || '');
        setInputValue('pi_summary', pi.summary || '');

        // Skills
        const sk = data.skills || {};
        setInputValue('skills_lang', (sk.programming_languages || []).join(', '));
        setInputValue('skills_frameworks', (sk.frameworks || []).join(', '));
        setInputValue('skills_databases', (sk.databases || []).join(', '));
        setInputValue('skills_cloud', (sk.cloud || []).join(', '));
        setInputValue('skills_tools', (sk.tools || []).join(', '));

        // Experience
        resumeData.experience = JSON.parse(JSON.stringify(data.experience || []));
        renderExperienceList();

        // Projects
        resumeData.projects = JSON.parse(JSON.stringify(data.projects || []));
        renderProjectsList();

        // Education
        resumeData.education = JSON.parse(JSON.stringify(data.education || []));
        renderEducationList();

        // Certifications & Achievements
        if (data.certifications && data.certifications.length > 0) {
            setInputValue('certifications_text', data.certifications.map(c => 
                `${c.certification || c.name || ''} | ${c.issuer || ''} | ${c.date || ''}`
            ).join('\n'));
        } else {
            setInputValue('certifications_text', '');
        }

        if (data.achievements && data.achievements.length > 0) {
            setInputValue('achievements_text', data.achievements.map(a => 
                a.title ? `${a.title}: ${a.description || ''}` : (a.description || '')
            ).join('\n'));
        } else {
            setInputValue('achievements_text', '');
        }

        syncModelFromInputs();
        renderLivePreview();
    }

    function bindInputs() {
        const inputIds = [
            'pi_fullName', 'pi_title', 'pi_email', 'pi_phone', 'pi_location',
            'pi_linkedin', 'pi_github', 'pi_portfolio', 'pi_summary',
            'skills_lang', 'skills_frameworks', 'skills_databases', 'skills_cloud', 'skills_tools',
            'certifications_text', 'achievements_text'
        ];

        inputIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', () => {
                    syncModelFromInputs();
                    renderLivePreview();
                    scheduleAutoSave();
                });
            }
        });

        // Load sample resume button
        document.getElementById('loadSampleBtn')?.addEventListener('click', () => {
            populateForm(SAMPLE_RESUME);
            scheduleAutoSave();
            window.CareerLense?.showToast('Loaded sample software engineer resume!', 'success');
        });

        // Clear all button
        document.getElementById('clearAllBtn')?.addEventListener('click', () => {
            clearAllForm(true);
        });
    }

    function syncModelFromInputs() {
        if (!document.getElementById('pi_fullName')) return;
        resumeData.personal_info.full_name = document.getElementById('pi_fullName')?.value.trim() || '';
        resumeData.personal_info.title = document.getElementById('pi_title')?.value.trim() || '';
        resumeData.personal_info.email = document.getElementById('pi_email')?.value.trim() || '';
        resumeData.personal_info.phone = document.getElementById('pi_phone')?.value.trim() || '';
        resumeData.personal_info.location = document.getElementById('pi_location')?.value.trim() || '';
        resumeData.personal_info.linkedin = document.getElementById('pi_linkedin')?.value.trim() || '';
        resumeData.personal_info.github = document.getElementById('pi_github')?.value.trim() || '';
        resumeData.personal_info.portfolio = document.getElementById('pi_portfolio')?.value.trim() || '';
        resumeData.personal_info.summary = document.getElementById('pi_summary')?.value.trim() || '';

        // Skills split
        function parseTags(id) {
            const val = document.getElementById(id)?.value || '';
            return val.split(',').map(s => s.trim()).filter(Boolean);
        }

        resumeData.skills.programming_languages = parseTags('skills_lang');
        resumeData.skills.frameworks = parseTags('skills_frameworks');
        resumeData.skills.databases = parseTags('skills_databases');
        resumeData.skills.cloud = parseTags('skills_cloud');
        resumeData.skills.tools = parseTags('skills_tools');

        const allSet = new Set([
            ...resumeData.skills.programming_languages,
            ...resumeData.skills.frameworks,
            ...resumeData.skills.databases,
            ...resumeData.skills.cloud,
            ...resumeData.skills.tools
        ]);
        resumeData.skills.all = Array.from(allSet);

        // Certs
        const certLines = (document.getElementById('certifications_text')?.value || '').split('\n').filter(Boolean);
        resumeData.certifications = certLines.map(line => {
            const parts = line.split('|').map(p => p.trim());
            return {
                certification: parts[0] || '',
                issuer: parts[1] || '',
                date: parts[2] || ''
            };
        });

        // Achievements
        const achLines = (document.getElementById('achievements_text')?.value || '').split('\n').filter(Boolean);
        resumeData.achievements = achLines.map(line => {
            const parts = line.split(':');
            return {
                title: parts[0]?.trim() || '',
                description: parts[1]?.trim() || ''
            };
        });
    }

    function bindTemplateButtons() {
        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.template-btn').forEach(b => {
                    b.classList.remove('active', 'bg-white', 'dark:bg-slate-700', 'text-brand-700', 'dark:text-brand-300', 'shadow-sm');
                    b.classList.add('text-slate-600', 'dark:text-slate-400');
                });

                btn.classList.add('active', 'bg-white', 'dark:bg-slate-700', 'text-brand-700', 'dark:text-brand-300', 'shadow-sm');
                btn.classList.remove('text-slate-600', 'dark:text-slate-400');

                currentTemplate = btn.dataset.template;
                const sheet = document.getElementById('resumePreviewSheet');
                if (sheet) {
                    sheet.className = `resume-preview-sheet template-${currentTemplate} max-w-[800px] mx-auto text-xs leading-relaxed`;
                }
                renderLivePreview();
                window.CareerLense?.showToast(`Switched to ${currentTemplate.toUpperCase()} template`, 'info');
            });
        });
    }

    function bindAddButtons() {
        document.getElementById('addExperienceBtn')?.addEventListener('click', () => {
            resumeData.experience.unshift({
                position: '',
                company: '',
                location: '',
                start_date: '',
                end_date: '',
                description: ''
            });
            renderExperienceList();
            renderLivePreview();
        });

        document.getElementById('addProjectBtn')?.addEventListener('click', () => {
            resumeData.projects.unshift({
                name: '',
                technologies: '',
                github: '',
                live_demo: '',
                description: ''
            });
            renderProjectsList();
            renderLivePreview();
        });

        document.getElementById('addEducationBtn')?.addEventListener('click', () => {
            resumeData.education.unshift({
                institution: '',
                degree: '',
                field: '',
                start_date: '',
                end_date: '',
                cgpa: '',
                percentage: '',
                relevant_coursework: ''
            });
            renderEducationList();
            renderLivePreview();
        });
    }

    // Dynamic Lists Rendering & Event Binding
    function renderExperienceList() {
        const container = document.getElementById('experienceList');
        if (!container) return;

        container.innerHTML = '';
        if (resumeData.experience.length === 0) {
            container.innerHTML = '<p class="text-xs text-slate-400 dark:text-slate-500 italic py-2">No work experience added yet. Click "+ Add Position" above to add your experience.</p>';
            return;
        }

        resumeData.experience.forEach((exp, idx) => {
            const card = document.createElement('div');
            card.className = 'p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700 space-y-3';
            card.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-bold text-xs text-slate-700 dark:text-slate-200">Role #${idx + 1}</span>
                    <div class="flex items-center gap-2">
                        <button type="button" class="ai-improve-exp-btn text-[11px] text-brand-600 hover:underline flex items-center gap-1" data-idx="${idx}">
                            <i data-lucide="sparkles" class="w-3 h-3"></i> AI Polish
                        </button>
                        <button type="button" class="text-rose-500 hover:text-rose-700 text-xs" onclick="window.CareerLenseBuilder.removeExp(${idx})">
                            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <input type="text" placeholder="Position Title" value="${escapeHtml(exp.position)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateExp(${idx}, 'position', this.value)">
                    <input type="text" placeholder="Company Name" value="${escapeHtml(exp.company)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateExp(${idx}, 'company', this.value)">
                    <input type="text" placeholder="Start Year / Date" value="${escapeHtml(exp.start_date)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateExp(${idx}, 'start_date', this.value)">
                    <input type="text" placeholder="End Year / Present" value="${escapeHtml(exp.end_date)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateExp(${idx}, 'end_date', this.value)">
                </div>
                <textarea rows="3" placeholder="Bullet points describing responsibilities and achievements..." class="w-full text-xs p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateExp(${idx}, 'description', this.value)">${escapeHtml(exp.description)}</textarea>
            `;
            container.appendChild(card);
        });

        // Bind AI Polish buttons
        container.querySelectorAll('.ai-improve-exp-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const i = parseInt(btn.dataset.idx);
                const desc = resumeData.experience[i]?.description;
                if (!desc) {
                    window.CareerLense?.showToast('Please enter description text to improve.', 'warning');
                    return;
                }
                btn.innerHTML = '<span class="animate-spin">⏳</span> Improving...';
                try {
                    const res = await fetch('/api/ai/improve', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ section: 'Experience', content: desc, mode: 'Professional' })
                    });
                    const d = await res.json();
                    if (d.success) {
                        resumeData.experience[i].description = d.improved;
                        renderExperienceList();
                        renderLivePreview();
                        scheduleAutoSave();
                        window.CareerLense?.showToast('Bullet points improved!', 'success');
                    }
                } catch (err) {
                    window.CareerLense?.showToast('AI polish failed.', 'error');
                }
            });
        });

        if (window.lucide) window.lucide.createIcons();
    }

    function renderProjectsList() {
        const container = document.getElementById('projectsList');
        if (!container) return;

        container.innerHTML = '';
        if (resumeData.projects.length === 0) {
            container.innerHTML = '<p class="text-xs text-slate-400 dark:text-slate-500 italic py-2">No projects added yet. Click "+ Add Project" above to showcase your projects.</p>';
            return;
        }

        resumeData.projects.forEach((proj, idx) => {
            const card = document.createElement('div');
            card.className = 'p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700 space-y-3';
            card.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-bold text-xs text-slate-700 dark:text-slate-200">Project #${idx + 1}</span>
                    <div class="flex items-center gap-2">
                        <button type="button" class="ai-improve-proj-btn text-[11px] text-brand-600 hover:underline flex items-center gap-1" data-idx="${idx}">
                            <i data-lucide="sparkles" class="w-3 h-3"></i> AI Polish
                        </button>
                        <button type="button" class="text-rose-500 hover:text-rose-700 text-xs" onclick="window.CareerLenseBuilder.removeProj(${idx})">
                            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <input type="text" placeholder="Project Name" value="${escapeHtml(proj.name)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateProj(${idx}, 'name', this.value)">
                    <input type="text" placeholder="Tech Stack (e.g. React, Flask)" value="${escapeHtml(proj.technologies)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateProj(${idx}, 'technologies', this.value)">
                    <input type="text" placeholder="GitHub Repository URL" value="${escapeHtml(proj.github)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateProj(${idx}, 'github', this.value)">
                    <input type="text" placeholder="Live Demo URL (optional)" value="${escapeHtml(proj.live_demo)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateProj(${idx}, 'live_demo', this.value)">
                </div>
                <textarea rows="2" placeholder="Description of architectural choices and features..." class="w-full text-xs p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateProj(${idx}, 'description', this.value)">${escapeHtml(proj.description)}</textarea>
            `;
            container.appendChild(card);
        });

        // Bind AI Polish for project
        container.querySelectorAll('.ai-improve-proj-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const i = parseInt(btn.dataset.idx);
                const desc = resumeData.projects[i]?.description;
                if (!desc) {
                    window.CareerLense?.showToast('Please enter project description to improve.', 'warning');
                    return;
                }
                btn.innerHTML = '<span class="animate-spin">⏳</span> Improving...';
                try {
                    const res = await fetch('/api/ai/project', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ description: desc, mode: 'Technical' })
                    });
                    const d = await res.json();
                    if (d.success) {
                        resumeData.projects[i].description = d.improved;
                        renderProjectsList();
                        renderLivePreview();
                        scheduleAutoSave();
                        window.CareerLense?.showToast('Project description improved!', 'success');
                    }
                } catch (err) {
                    window.CareerLense?.showToast('Project polish failed.', 'error');
                }
            });
        });

        if (window.lucide) window.lucide.createIcons();
    }

    function renderEducationList() {
        const container = document.getElementById('educationList');
        if (!container) return;

        container.innerHTML = '';
        if (resumeData.education.length === 0) {
            container.innerHTML = '<p class="text-xs text-slate-400 dark:text-slate-500 italic py-2">No education added yet. Click "+ Add Education" above to add degrees or courses.</p>';
            return;
        }
        resumeData.education.forEach((edu, idx) => {
            const card = document.createElement('div');
            card.className = 'p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700 space-y-3';
            card.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-bold text-xs text-slate-700 dark:text-slate-200">Education #${idx + 1}</span>
                    <button type="button" class="text-rose-500 hover:text-rose-700 text-xs" onclick="window.CareerLenseBuilder.removeEdu(${idx})">
                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <input type="text" placeholder="Institution / University" value="${escapeHtml(edu.institution)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateEdu(${idx}, 'institution', this.value)">
                    <input type="text" placeholder="Degree (e.g. B.S., B.Tech)" value="${escapeHtml(edu.degree)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateEdu(${idx}, 'degree', this.value)">
                    <input type="text" placeholder="Field of Study" value="${escapeHtml(edu.field)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateEdu(${idx}, 'field', this.value)">
                    <input type="text" placeholder="CGPA or Percentage" value="${escapeHtml(edu.cgpa || edu.percentage)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateEdu(${idx}, 'cgpa', this.value)">
                    <input type="text" placeholder="Start Date" value="${escapeHtml(edu.start_date)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateEdu(${idx}, 'start_date', this.value)">
                    <input type="text" placeholder="End Date" value="${escapeHtml(edu.end_date)}" class="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateEdu(${idx}, 'end_date', this.value)">
                </div>
                <input type="text" placeholder="Relevant Coursework..." value="${escapeHtml(edu.relevant_coursework)}" class="w-full text-xs px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-white" oninput="window.CareerLenseBuilder.updateEdu(${idx}, 'relevant_coursework', this.value)">
            `;
            container.appendChild(card);
        });

        if (window.lucide) window.lucide.createIcons();
    }

    // Live Resume HTML Renderer
    function renderLivePreview() {
        const sheet = document.getElementById('resumePreviewSheet');
        if (!sheet) return;

        const pi = resumeData.personal_info || {};
        const skills = resumeData.skills || {};
        const exp = resumeData.experience || [];
        const projs = resumeData.projects || [];
        const edu = resumeData.education || [];
        const certs = resumeData.certifications || [];
        const ach = resumeData.achievements || [];

        if (!hasResumeContent(resumeData)) {
            sheet.innerHTML = `
                <!-- Resume Header Placeholder -->
                <div class="preview-header">
                    <h1 class="text-2xl font-black tracking-tight opacity-40 italic">Your Full Name</h1>
                    <p class="text-xs opacity-50 mt-1">Professional Title</p>
                </div>
                <div class="py-16 text-center text-slate-400 dark:text-slate-500 space-y-2">
                    <i data-lucide="file-edit" class="w-8 h-8 mx-auto text-slate-300 dark:text-slate-600 mb-2"></i>
                    <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Your live resume preview will appear here as you type.</p>
                    <p class="text-xs text-slate-400">Fill in the fields on the left, or click <button type="button" class="text-brand-600 dark:text-brand-400 font-semibold underline hover:no-underline" onclick="window.CareerLenseBuilder.loadSample()">Load Sample Resume</button> to see an example.</p>
                </div>
            `;
            if (window.lucide) window.lucide.createIcons();
            return;
        }

        let contactParts = [];
        if (pi.email) contactParts.push(`<a href="mailto:${escapeHtml(pi.email)}" class="hover:underline">${escapeHtml(pi.email)}</a>`);
        if (pi.phone) contactParts.push(escapeHtml(pi.phone));
        if (pi.location) contactParts.push(escapeHtml(pi.location));
        if (pi.linkedin) contactParts.push(`<a href="https://${escapeHtml(pi.linkedin.replace(/^https?:\/\//, ''))}" target="_blank" class="hover:underline text-brand-600 dark:text-brand-400">LinkedIn</a>`);
        if (pi.github) contactParts.push(`<a href="https://${escapeHtml(pi.github.replace(/^https?:\/\//, ''))}" target="_blank" class="hover:underline text-brand-600 dark:text-brand-400">GitHub</a>`);
        if (pi.portfolio) contactParts.push(`<a href="https://${escapeHtml(pi.portfolio.replace(/^https?:\/\//, ''))}" target="_blank" class="hover:underline text-brand-600 dark:text-brand-400">Portfolio</a>`);

        let html = `
            <!-- Resume Header -->
            <div class="preview-header">
                <h1 class="text-2xl font-black text-slate-900 tracking-tight">${escapeHtml(pi.full_name || 'Your Full Name')}</h1>
                ${pi.title ? `<p class="text-sm font-semibold text-brand-600 mt-0.5">${escapeHtml(pi.title)}</p>` : ''}
                ${contactParts.length ? `<div class="mt-2 text-[11px] text-slate-600 flex flex-wrap gap-x-3 gap-y-1">${contactParts.join(' • ')}</div>` : ''}
            </div>
        `;

        // Summary
        if (pi.summary) {
            html += `
                <div class="preview-sec-title">Professional Summary</div>
                <p class="text-slate-700 leading-relaxed text-[11.5px]">${escapeHtml(pi.summary)}</p>
            `;
        }

        // Skills
        if (skills.all && skills.all.length > 0) {
            html += `<div class="preview-sec-title">Skills &amp; Technologies</div><div class="space-y-1 text-[11.5px]">`;
            if (skills.programming_languages.length) {
                html += `<div><strong>Languages:</strong> ${escapeHtml(skills.programming_languages.join(', '))}</div>`;
            }
            if (skills.frameworks.length) {
                html += `<div><strong>Frameworks:</strong> ${escapeHtml(skills.frameworks.join(', '))}</div>`;
            }
            if (skills.databases.length) {
                html += `<div><strong>Databases:</strong> ${escapeHtml(skills.databases.join(', '))}</div>`;
            }
            if (skills.cloud.length) {
                html += `<div><strong>Cloud &amp; DevOps:</strong> ${escapeHtml(skills.cloud.join(', '))}</div>`;
            }
            if (skills.tools.length) {
                html += `<div><strong>Tools:</strong> ${escapeHtml(skills.tools.join(', '))}</div>`;
            }
            html += `</div>`;
        }

        // Experience
        if (exp && exp.length > 0) {
            html += `<div class="preview-sec-title">Experience</div><div class="space-y-3">`;
            exp.forEach(e => {
                if (!e.position && !e.company) return;
                const dates = [e.start_date, e.end_date || 'Present'].filter(Boolean).join(' – ');
                html += `
                    <div>
                        <div class="flex justify-between items-baseline text-[11.5px]">
                            <span><strong>${escapeHtml(e.position || 'Position')}</strong> — ${escapeHtml(e.company || 'Company')}</span>
                            <span class="text-slate-500 font-medium">${escapeHtml(dates)}</span>
                        </div>
                        ${e.description ? `
                            <ul class="list-disc list-outside ml-4 mt-1 space-y-0.5 text-slate-700 text-[11px]">
                                ${e.description.split('\n').filter(Boolean).map(l => `<li>${escapeHtml(l.replace(/^[•\-\*]\s*/, ''))}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                `;
            });
            html += `</div>`;
        }

        // Projects
        if (projs && projs.length > 0) {
            html += `<div class="preview-sec-title">Key Projects</div><div class="space-y-3">`;
            projs.forEach(p => {
                if (!p.name) return;
                const links = [];
                if (p.github) links.push(`<a href="https://${escapeHtml(p.github.replace(/^https?:\/\//, ''))}" target="_blank" class="text-brand-600 hover:underline">GitHub</a>`);
                if (p.live_demo) links.push(`<a href="https://${escapeHtml(p.live_demo.replace(/^https?:\/\//, ''))}" target="_blank" class="text-brand-600 hover:underline">Live Demo</a>`);

                html += `
                    <div>
                        <div class="flex justify-between items-baseline text-[11.5px]">
                            <span><strong>${escapeHtml(p.name)}</strong> ${p.technologies ? `<span class="text-slate-500 font-normal">| ${escapeHtml(p.technologies)}</span>` : ''}</span>
                            ${links.length ? `<span class="text-[10px] space-x-2">${links.join(' | ')}</span>` : ''}
                        </div>
                        ${p.description ? `
                            <ul class="list-disc list-outside ml-4 mt-1 space-y-0.5 text-slate-700 text-[11px]">
                                ${p.description.split('\n').filter(Boolean).map(l => `<li>${escapeHtml(l.replace(/^[•\-\*]\s*/, ''))}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                `;
            });
            html += `</div>`;
        }

        // Education
        if (edu && edu.length > 0) {
            html += `<div class="preview-sec-title">Education</div><div class="space-y-2">`;
            edu.forEach(ed => {
                if (!ed.institution && !ed.degree) return;
                const dates = [ed.start_date, ed.end_date].filter(Boolean).join(' – ');
                const scoreStr = ed.cgpa || ed.percentage ? ` | Score: ${ed.cgpa || ed.percentage}` : '';
                html += `
                    <div class="text-[11.5px]">
                        <div class="flex justify-between items-baseline">
                            <span><strong>${escapeHtml(ed.degree || 'Degree')}</strong> ${ed.field ? `in ${escapeHtml(ed.field)}` : ''} — ${escapeHtml(ed.institution || 'University')}</span>
                            <span class="text-slate-500 font-medium">${escapeHtml(dates)}${escapeHtml(scoreStr)}</span>
                        </div>
                        ${ed.relevant_coursework ? `<div class="text-[11px] text-slate-600 mt-0.5"><em>Relevant Coursework:</em> ${escapeHtml(ed.relevant_coursework)}</div>` : ''}
                    </div>
                `;
            });
            html += `</div>`;
        }

        // Certs & Achievements
        if ((certs && certs.length > 0) || (ach && ach.length > 0)) {
            html += `<div class="preview-sec-title">Certifications &amp; Achievements</div><ul class="list-disc list-outside ml-4 space-y-0.5 text-slate-700 text-[11px]">`;
            (certs || []).forEach(c => {
                if (c.certification) {
                    html += `<li><strong>${escapeHtml(c.certification)}</strong> ${c.issuer ? `— ${escapeHtml(c.issuer)}` : ''} ${c.date ? `(${escapeHtml(c.date)})` : ''}</li>`;
                }
            });
            (ach || []).forEach(a => {
                if (a.title || a.description) {
                    html += `<li>${a.title ? `<strong>${escapeHtml(a.title)}:</strong> ` : ''}${escapeHtml(a.description || '')}</li>`;
                }
            });
            html += `</ul>`;
        }

        sheet.innerHTML = html;
    }

    function scheduleAutoSave() {
        if (saveTimeout) clearTimeout(saveTimeout);
        saveTimeout = setTimeout(async () => {
            try {
                if (hasResumeContent(resumeData)) {
                    await fetch('/api/builder/save', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(resumeData)
                    });
                }
            } catch (e) {}
        }, 1200);
    }

    function bindExportButtons() {
        document.getElementById('exportPdfBtn')?.addEventListener('click', async () => {
            if (!hasResumeContent(resumeData)) {
                window.CareerLense?.showToast('Please enter your resume details or load a sample first.', 'warning');
                return;
            }

            const btn = document.getElementById('exportPdfBtn');
            btn.innerHTML = '<span class="animate-spin">⏳</span> Generating...';

            try {
                const response = await fetch('/api/builder/export', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume_data: resumeData, template: currentTemplate })
                });

                if (!response.ok) throw new Error('PDF Export failed');

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const name = (resumeData.personal_info.full_name || 'Resume').replace(/[^a-zA-Z0-9]/g, '_');
                a.download = `${name}_CareerLense.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                window.CareerLense?.showToast('PDF downloaded successfully!', 'success');
            } catch (err) {
                window.CareerLense?.showToast('Failed to generate PDF.', 'error');
            } finally {
                btn.innerHTML = '<i data-lucide="download" class="w-3.5 h-3.5"></i> Download PDF';
                if (window.lucide) window.lucide.createIcons();
            }
        });

        document.getElementById('printResumeBtn')?.addEventListener('click', () => {
            if (!hasResumeContent(resumeData)) {
                window.CareerLense?.showToast('Please enter your resume details or load a sample first.', 'warning');
                return;
            }
            window.print();
        });

        document.getElementById('analyzeThisResumeBtn')?.addEventListener('click', async (e) => {
            if (!hasResumeContent(resumeData)) {
                e.preventDefault();
                window.CareerLense?.showToast('Please enter your resume details or load a sample first.', 'warning');
                return;
            }
            e.preventDefault();
            const btn = document.getElementById('analyzeThisResumeBtn');
            btn.innerHTML = '<span class="animate-spin">⏳</span> Saving...';
            try {
                await fetch('/api/builder/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(resumeData)
                });
                window.location.href = btn.getAttribute('href');
            } catch (err) {
                window.location.href = btn.getAttribute('href');
            }
        });
    }

    function bindAiButtons() {
        document.getElementById('aiImproveSummaryBtn')?.addEventListener('click', async () => {
            const summary = document.getElementById('pi_summary')?.value.trim();
            if (!summary) {
                window.CareerLense?.showToast('Please enter summary text first to improve.', 'warning');
                return;
            }

            const btn = document.getElementById('aiImproveSummaryBtn');
            btn.innerHTML = '<span class="animate-spin">⏳</span> Improving...';

            try {
                const res = await fetch('/api/ai/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ summary, mode: 'Professional' })
                });
                const d = await res.json();
                if (d.success) {
                    document.getElementById('pi_summary').value = d.improved;
                    syncModelFromInputs();
                    renderLivePreview();
                    scheduleAutoSave();
                    window.CareerLense?.showToast('Professional summary improved!', 'success');
                }
            } catch (err) {
                window.CareerLense?.showToast('Summary optimization failed.', 'error');
            } finally {
                btn.innerHTML = '<i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Improve Summary';
                if (window.lucide) window.lucide.createIcons();
            }
        });
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    // Public API for inline onclick handlers in dynamic cards & programmatic controls
    window.CareerLenseBuilder = {
        updateExp: (idx, field, val) => {
            if (resumeData.experience[idx]) {
                resumeData.experience[idx][field] = val;
                renderLivePreview();
                scheduleAutoSave();
            }
        },
        removeExp: (idx) => {
            resumeData.experience.splice(idx, 1);
            renderExperienceList();
            renderLivePreview();
            scheduleAutoSave();
        },
        updateProj: (idx, field, val) => {
            if (resumeData.projects[idx]) {
                resumeData.projects[idx][field] = val;
                renderLivePreview();
                scheduleAutoSave();
            }
        },
        removeProj: (idx) => {
            resumeData.projects.splice(idx, 1);
            renderProjectsList();
            renderLivePreview();
            scheduleAutoSave();
        },
        updateEdu: (idx, field, val) => {
            if (resumeData.education[idx]) {
                resumeData.education[idx][field] = val;
                renderLivePreview();
                scheduleAutoSave();
            }
        },
        removeEdu: (idx) => {
            resumeData.education.splice(idx, 1);
            renderEducationList();
            renderLivePreview();
            scheduleAutoSave();
        },
        clearAll: () => clearAllForm(true),
        loadSample: () => {
            populateForm(SAMPLE_RESUME);
            scheduleAutoSave();
            window.CareerLense?.showToast('Loaded sample software engineer resume!', 'success');
        },
        getResumeData: () => JSON.parse(JSON.stringify(resumeData)),
        hasResumeContent: () => hasResumeContent(resumeData)
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
