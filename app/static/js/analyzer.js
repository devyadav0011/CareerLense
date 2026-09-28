// CareerLense Resume Analyzer Client Logic
(function() {
    'use strict';

    let selectedFile = null;
    let loadingInterval = null;

    const STATUS_MESSAGES = [
        'Reading your resume...',
        'Extracting career sections & contact details...',
        'Analyzing your experience & active verbs...',
        'Evaluating skills against industry taxonomy...',
        'Running ATS-style readability heuristics...',
        'Generating actionable improvement suggestions...'
    ];

    function init() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('resumeFileInput');
        const browseBtn = document.getElementById('browseFileBtn');
        const startUploadBtn = document.getElementById('startUploadBtn');
        const useSampleBtn = document.getElementById('useSampleBtn');

        if (!dropZone || !fileInput) return;

        // Browse button click
        browseBtn?.addEventListener('click', () => fileInput.click());

        // File input changed
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFileSelected(e.target.files[0]);
            }
        });

        // Drag & Drop
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('border-brand-500', 'bg-brand-50/20', 'dark:bg-brand-950/20');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('border-brand-500', 'bg-brand-50/20', 'dark:bg-brand-950/20');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files[0]) {
                handleFileSelected(files[0]);
            }
        });

        // Start Upload button
        startUploadBtn?.addEventListener('click', () => {
            if (selectedFile) {
                uploadAndAnalyze(selectedFile);
            }
        });

        // Try with Sample Resume button
        useSampleBtn?.addEventListener('click', async () => {
            showLoading(true);
            try {
                // Save sample builder profile into session then analyze
                const res = await fetch('/api/builder/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        personal_info: {
                            full_name: 'Devan Yadav',
                            title: 'Senior Software Engineer',
                            email: 'devan.yadav@example.com',
                            phone: '+1 (555) 349-8201',
                            location: 'San Francisco, CA',
                            linkedin: 'linkedin.com/in/devanyadav',
                            github: 'github.com/devanyadav',
                            portfolio: 'devanyadav.dev',
                            summary: 'Full-Stack Software Engineer with 5+ years building distributed backend APIs and frontend web applications.'
                        },
                        skills: {
                            all: ['Python', 'Flask', 'React', 'TypeScript', 'SQL', 'PostgreSQL', 'Docker', 'AWS', 'Git', 'CI/CD']
                        },
                        experience: [
                            {
                                position: 'Lead Software Engineer',
                                company: 'Vanguard Cloud Technologies',
                                start_date: '2023',
                                end_date: 'Present',
                                description: 'Architected resilient microservices backend with Python and Flask supporting 100K+ daily active requests.\nSpearheaded migration to PostgreSQL, optimizing query response latency by 35%.'
                            }
                        ],
                        projects: [
                            {
                                name: 'CareerLense Platform',
                                technologies: 'Python, Flask, ReportLab',
                                description: 'Engineered an AI resume quality evaluation engine with ATS readability heuristics.'
                            }
                        ],
                        education: [
                            {
                                institution: 'UC Berkeley',
                                degree: 'B.S. in Computer Science',
                                start_date: '2017',
                                end_date: '2021',
                                cgpa: '3.85 / 4.0'
                            }
                        ]
                    })
                });

                if (res.ok) {
                    window.CareerLense?.showToast('Sample resume loaded! Redirecting to results...', 'success');
                    setTimeout(() => {
                        window.location.href = '/results';
                    }, 800);
                }
            } catch (err) {
                showLoading(false);
                window.CareerLense?.showToast('Failed to load sample resume.', 'error');
            }
        });
    }

    function handleFileSelected(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'docx'].includes(ext)) {
            window.CareerLense?.showToast('Invalid file format. Please upload a .pdf or .docx file.', 'error');
            return;
        }

        const maxBytes = 10 * 1024 * 1024;
        if (file.size > maxBytes) {
            window.CareerLense?.showToast('File size exceeds 10MB. Please upload a smaller file.', 'error');
            return;
        }

        selectedFile = file;
        const bar = document.getElementById('fileSelectionBar');
        const nameEl = document.getElementById('selectedFileName');
        if (bar && nameEl) {
            nameEl.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
            bar.classList.remove('hidden');
        }

        // Auto trigger upload
        uploadAndAnalyze(file);
    }

    async function uploadAndAnalyze(file) {
        showLoading(true);

        const formData = new FormData();
        formData.append('resume', file);

        try {
            const res = await fetch('/api/resume/upload', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            showLoading(false);

            if (data.success) {
                window.CareerLense?.showToast('Analysis completed successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/results';
                }, 600);
            } else {
                window.CareerLense?.showToast(data.error || 'Failed to process resume.', 'error');
            }
        } catch (err) {
            showLoading(false);
            window.CareerLense?.showToast('Network error during upload. Please check your file and try again.', 'error');
        }
    }

    function showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        const statusEl = document.getElementById('loadingStatusText');
        if (!overlay) return;

        if (show) {
            overlay.classList.remove('hidden');
            let idx = 0;
            if (statusEl) statusEl.textContent = STATUS_MESSAGES[0];
            loadingInterval = setInterval(() => {
                idx = (idx + 1) % STATUS_MESSAGES.length;
                if (statusEl) statusEl.textContent = STATUS_MESSAGES[idx];
            }, 1200);
        } else {
            overlay.classList.add('hidden');
            if (loadingInterval) clearInterval(loadingInterval);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
