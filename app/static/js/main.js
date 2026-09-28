// CareerLense Global Client-Side Module
window.CareerLense = (function() {
    'use strict';

    // State
    const state = {
        theme: localStorage.getItem('careerlense_theme') || 'system',
        currentResume: null,
        user: null,
        isAiDrawerOpen: false
    };

    // Initialize
    function init() {
        initTheme();
        initNavigation();
        initAiDrawer();
        checkUserSession();
        checkCurrentResume();
    }

    // Theme Management
    function initTheme() {
        const toggleBtn = document.getElementById('themeToggleBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleTheme);
        }

        // Listen for OS color scheme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (state.theme === 'system') {
                applyTheme('system');
            }
        });
    }

    function applyTheme(theme) {
        state.theme = theme;
        localStorage.setItem('careerlense_theme', theme);
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (theme === 'dark' || (theme === 'system' && systemDark)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }

    function toggleTheme() {
        const currentIsDark = document.documentElement.classList.contains('dark');
        applyTheme(currentIsDark ? 'light' : 'dark');
        showToast(`Switched to ${currentIsDark ? 'Light' : 'Dark'} mode`, 'info');
    }

    // Navigation & Dropdowns
    function initNavigation() {
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const mobileMenu = document.getElementById('mobileMenu');
        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }

        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('hidden');
            });

            document.addEventListener('click', (e) => {
                if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
                    userDropdown.classList.add('hidden');
                }
            });
        }
    }

    // CareerLense AI Assistant Drawer
    function initAiDrawer() {
        const toggleBtn = document.getElementById('aiAssistantToggleBtn');
        const closeBtn = document.getElementById('closeAiDrawerBtn');
        const drawer = document.getElementById('aiDrawer');
        const backdrop = document.getElementById('aiDrawerBackdrop');
        const chatForm = document.getElementById('aiChatForm');

        function openDrawer() {
            drawer.classList.remove('translate-x-full');
            backdrop.classList.remove('hidden');
            state.isAiDrawerOpen = true;
            document.getElementById('aiChatInput')?.focus();
        }

        function closeDrawer() {
            drawer.classList.add('translate-x-full');
            backdrop.classList.add('hidden');
            state.isAiDrawerOpen = false;
        }

        if (toggleBtn) toggleBtn.addEventListener('click', openDrawer);
        if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
        if (backdrop) backdrop.addEventListener('click', closeDrawer);

        if (chatForm) {
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const input = document.getElementById('aiChatInput');
                const message = input.value.trim();
                if (!message) return;

                input.value = '';
                appendChatMessage('user', message);

                // Show typing indicator
                const typingId = appendTypingIndicator();

                try {
                    const res = await fetch('/api/ai/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message })
                    });
                    const data = await res.json();
                    removeMessage(typingId);

                    if (data.success) {
                        appendChatMessage('bot', data.reply);
                    } else {
                        appendChatMessage('bot', data.error || 'Sorry, I encountered an error answering that.');
                    }
                } catch (err) {
                    removeMessage(typingId);
                    appendChatMessage('bot', 'Network error. Please try again.');
                }
            });
        }
    }

    function appendChatMessage(sender, text) {
        const container = document.getElementById('aiChatMessages');
        if (!container) return;

        const isUser = sender === 'user';
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex gap-2.5 ${isUser ? 'justify-end' : ''}`;

        const bubbleClass = isUser 
            ? 'bg-brand-600 text-white rounded-2xl rounded-tr-sm ml-auto max-w-[85%] p-3'
            : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-2xl rounded-tl-sm max-w-[85%] p-3';

        // Format markdown bold/italics simply
        let formatted = escapeHtml(text)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');

        msgDiv.innerHTML = isUser ? `
            <div class="${bubbleClass} leading-relaxed">${formatted}</div>
        ` : `
            <div class="w-7 h-7 rounded-lg bg-brand-600/10 text-brand-600 dark:text-brand-400 flex items-center justify-center shrink-0">
                <i data-lucide="bot" class="w-4 h-4"></i>
            </div>
            <div class="${bubbleClass} leading-relaxed">${formatted}</div>
        `;

        container.appendChild(msgDiv);
        container.scrollTop = container.scrollHeight;
        if (window.lucide) window.lucide.createIcons();
    }

    function appendTypingIndicator() {
        const container = document.getElementById('aiChatMessages');
        const id = 'typing_' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'flex gap-2.5';
        div.innerHTML = `
            <div class="w-7 h-7 rounded-lg bg-brand-600/10 text-brand-600 dark:text-brand-400 flex items-center justify-center shrink-0">
                <i data-lucide="bot" class="w-4 h-4"></i>
            </div>
            <div class="bg-slate-100 dark:bg-slate-800 text-slate-500 rounded-2xl rounded-tl-sm p-3 flex items-center gap-1.5 text-xs">
                <span class="w-2 h-2 rounded-full bg-brand-500 animate-bounce"></span>
                <span class="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.2s]"></span>
                <span class="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.4s]"></span>
            </div>
        `;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        if (window.lucide) window.lucide.createIcons();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function sendPresetPrompt(promptText) {
        const input = document.getElementById('aiChatInput');
        if (input) {
            input.value = promptText;
            document.getElementById('aiChatForm')?.dispatchEvent(new Event('submit'));
        }
    }

    // Toast Notification System
    function showToast(message, type = 'info', duration = 3500) {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `pointer-events-auto flex items-center gap-3 p-3.5 rounded-xl shadow-xl border text-xs font-medium transition-all transform duration-300 translate-y-2 opacity-0`;

        const typeStyles = {
            success: 'bg-white dark:bg-slate-900 border-emerald-500/30 text-emerald-900 dark:text-emerald-300 shadow-emerald-500/5',
            error: 'bg-white dark:bg-slate-900 border-rose-500/30 text-rose-900 dark:text-rose-300 shadow-rose-500/5',
            warning: 'bg-white dark:bg-slate-900 border-amber-500/30 text-amber-900 dark:text-amber-300 shadow-amber-500/5',
            info: 'bg-white dark:bg-slate-900 border-brand-500/30 text-slate-800 dark:text-slate-200 shadow-brand-500/5'
        };

        const icons = {
            success: '<i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-500 shrink-0"></i>',
            error: '<i data-lucide="alert-circle" class="w-4 h-4 text-rose-500 shrink-0"></i>',
            warning: '<i data-lucide="alert-triangle" class="w-4 h-4 text-amber-500 shrink-0"></i>',
            info: '<i data-lucide="info" class="w-4 h-4 text-brand-500 shrink-0"></i>'
        };

        toast.className += ` ${typeStyles[type] || typeStyles.info}`;
        toast.innerHTML = `
            ${icons[type] || icons.info}
            <span class="flex-grow">${escapeHtml(message)}</span>
            <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                <i data-lucide="x" class="w-3.5 h-3.5"></i>
            </button>
        `;

        container.appendChild(toast);
        if (window.lucide) window.lucide.createIcons();

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-2', 'opacity-0');
        });

        // Auto remove
        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // Session Verification & Cleanup
    async function checkUserSession() {
        try {
            const res = await fetch('/api/auth/me');
            const data = await res.json();
            const label = document.getElementById('sessionUserLabel');
            const authLinks = document.getElementById('authLinks');

            if (data.authenticated && data.user) {
                state.user = data.user;
                if (label) label.textContent = `${data.user.name} (${data.user.email})`;
                if (authLinks) {
                    authLinks.innerHTML = `
                        <button onclick="window.CareerLense.logout()" class="w-full text-left flex items-center gap-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs">
                            <i data-lucide="log-out" class="w-4 h-4"></i> Sign Out
                        </button>
                    `;
                }
            }
        } catch (e) {}
    }

    async function checkCurrentResume() {
        try {
            const res = await fetch('/api/resume/current');
            const data = await res.json();
            if (data.resume) {
                state.currentResume = data.resume;
            }
        } catch (e) {}
    }

    async function clearSession() {
        if (!confirm('Are you sure you want to clear your current session and delete any temporary uploaded resume files?')) {
            return;
        }

        try {
            const res = await fetch('/api/resume/clear-session', { method: 'POST' });
            const data = await res.json();
            state.currentResume = null;
            showToast('Session and temporary files cleared.', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 800);
        } catch (e) {
            showToast('Failed to clear session.', 'error');
        }
    }

    async function logout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            showToast('Signed out successfully.', 'info');
            setTimeout(() => {
                window.location.reload();
            }, 600);
        } catch (e) {}
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Self-init on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    return {
        showToast,
        clearSession,
        logout,
        sendPresetPrompt,
        getState: () => state
    };
})();
