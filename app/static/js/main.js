// Blogify Professional UI/UX JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Delete Confirmation Handlers
    initDeleteConfirmations();

    // 2. Post Editor Tools (Markdown Toolbar, Live Preview, Word Count & Reading Time)
    initPostEditor();

    // 3. Share Buttons & Copy Link Functionality
    initShareButtons();

    // 4. Auto-dismiss Flash Alerts
    initAlertDismiss();
});

/**
 * Attaches confirmation prompts to delete forms.
 */
function initDeleteConfirmations() {
    document.querySelectorAll('.form-delete-confirm').forEach(form => {
        form.addEventListener('submit', (e) => {
            const itemType = form.getAttribute('data-item-type') || 'item';
            const confirmed = window.confirm(`Are you sure you want to permanently delete this ${itemType}? This action cannot be undone.`);
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Post Editor Enhancements: Toolbar, Live Word Count, Reading Time, and Preview.
 */
function initPostEditor() {
    const editor = document.getElementById('post-content-editor');
    if (!editor) return;

    const wordCountEl = document.getElementById('editor-word-count');
    const readTimeEl = document.getElementById('editor-read-time');
    const charCountEl = document.getElementById('editor-char-count');

    function updateMetrics() {
        const text = editor.value.trim();
        const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
        const chars = text.length;
        const readingTime = Math.max(1, Math.round(words / 200));

        if (wordCountEl) wordCountEl.textContent = `${words} words`;
        if (charCountEl) charCountEl.textContent = `${chars} characters`;
        if (readTimeEl) readTimeEl.textContent = `~${readingTime} min read`;
    }

    editor.addEventListener('input', updateMetrics);
    updateMetrics(); // Initial calculation

    // Formatting Toolbar Actions
    const toolbar = document.querySelector('.editor-toolbar');
    if (toolbar) {
        toolbar.addEventListener('click', (e) => {
            const btn = e.target.closest('button[data-format]');
            if (!btn) return;
            e.preventDefault();
            const format = btn.getAttribute('data-format');
            applyFormatting(editor, format);
            updateMetrics();
        });
    }

    // Write / Preview Tabs
    const writeTab = document.getElementById('write-tab-btn');
    const previewTab = document.getElementById('preview-tab-btn');
    const writeContainer = document.getElementById('editor-write-container');
    const previewContainer = document.getElementById('editor-preview-container');

    if (writeTab && previewTab && writeContainer && previewContainer) {
        previewTab.addEventListener('click', () => {
            previewTab.classList.add('active');
            writeTab.classList.remove('active');
            writeContainer.classList.add('d-none');
            previewContainer.classList.remove('d-none');
            previewContainer.innerHTML = renderMarkdownClient(editor.value);
        });

        writeTab.addEventListener('click', () => {
            writeTab.classList.add('active');
            previewTab.classList.remove('active');
            previewContainer.classList.add('d-none');
            writeContainer.classList.remove('d-none');
            editor.focus();
        });
    }
}

/**
 * Inserts markdown formatting syntax at the cursor or around selected text.
 */
function applyFormatting(textarea, format) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = textarea.value.substring(start, end);
    let replacement = '';

    switch (format) {
        case 'bold':
            replacement = `**${selected || 'bold text'}**`;
            break;
        case 'italic':
            replacement = `*${selected || 'italic text'}*`;
            break;
        case 'heading':
            replacement = `\n## ${selected || 'Heading 2'}\n`;
            break;
        case 'subheading':
            replacement = `\n### ${selected || 'Subheading'}\n`;
            break;
        case 'quote':
            replacement = `\n> ${selected || 'Quote'}\n`;
            break;
        case 'code':
            if (selected.includes('\n')) {
                replacement = `\n\`\`\`python\n${selected || '# Write code here'}\n\`\`\`\n`;
            } else {
                replacement = `\`${selected || 'code'}\``;
            }
            break;
        case 'list':
            replacement = `\n- ${selected || 'List item'}\n`;
            break;
        case 'numlist':
            replacement = `\n1. ${selected || 'Numbered item'}\n`;
            break;
        case 'link':
            replacement = `[${selected || 'link text'}](https://example.com)`;
            break;
        case 'hr':
            replacement = `\n---\n`;
            break;
        default:
            return;
    }

    textarea.setRangeText(replacement, start, end, 'end');
    textarea.focus();
}

/**
 * Client-side lightweight markdown parser for instant editor preview.
 */
function renderMarkdownClient(md) {
    if (!md || !md.trim()) {
        return '<p class="text-muted fst-italic py-4 text-center">Nothing to preview yet. Start typing your story in the editor!</p>';
    }

    let html = md
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Fenced Code blocks
    html = html.replace(/```([a-z]*)\n([\s\S]*?)```/gm, '<pre><code>$2</code></pre>');
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Horizontal Rule
    html = html.replace(/^---$/gm, '<hr>');
    // Headings
    html = html.replace(/^### (.*$)/gim, '<h3 class="fw-bold mt-4 mb-2">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="fw-bold mt-4 mb-3">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="fw-bold mt-4 mb-3">$1</h1>');
    // Bold & Italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // Blockquote
    html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    // Unordered lists
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
    // Paragraphs
    html = html.replace(/\n\n+/g, '</p><p>');
    html = '<p>' + html + '</p>';
    // Clean remaining single newlines
    html = html.replace(/\n/g, '<br>');

    return html;
}

/**
 * Copy to clipboard and share button actions.
 */
function initShareButtons() {
    const copyBtn = document.getElementById('btn-copy-link');
    if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(window.location.href);
                const originalHtml = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="bi bi-check2 me-1"></i> Copied!';
                copyBtn.classList.remove('btn-outline-secondary');
                copyBtn.classList.add('btn-success');
                setTimeout(() => {
                    copyBtn.innerHTML = originalHtml;
                    copyBtn.classList.remove('btn-success');
                    copyBtn.classList.add('btn-outline-secondary');
                }, 2500);
            } catch (err) {
                prompt('Copy this link:', window.location.href);
            }
        });
    }
}

/**
 * Automatically dismisses flash alert banners.
 */
function initAlertDismiss() {
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (err) {
                alert.style.display = 'none';
            }
        }, 5000);
    });
}
