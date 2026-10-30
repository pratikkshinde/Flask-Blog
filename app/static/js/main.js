// Main JavaScript for FlaskBlog Platform

document.addEventListener('DOMContentLoaded', () => {
    // 1. Confirm Delete Actions
    document.querySelectorAll('.form-delete-confirm').forEach(form => {
        form.addEventListener('submit', (e) => {
            const itemType = form.getAttribute('data-item-type') || 'item';
            const confirmed = window.confirm(`Are you sure you want to delete this ${itemType}? This action cannot be undone.`);
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });

    // 2. Markdown Editor Toolbar Functionality
    const editorTextarea = document.getElementById('post-content-editor');
    if (editorTextarea) {
        setupMarkdownToolbar(editorTextarea);
    }

    // 3. Auto-close flash alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (err) {
                alert.style.display = 'none';
            }
        }, 6000);
    });
});

/**
 * Attaches toolbar action handlers to wrap or insert markdown tokens.
 */
function setupMarkdownToolbar(textarea) {
    const toolbar = document.querySelector('.editor-toolbar');
    if (!toolbar) return;

    toolbar.addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-format]');
        if (!btn) return;
        e.preventDefault();

        const format = btn.getAttribute('data-format');
        applyFormatting(textarea, format);
    });

    // Live preview toggle if preview tab exists
    const previewTab = document.getElementById('preview-tab-btn');
    const writeTab = document.getElementById('write-tab-btn');
    const previewArea = document.getElementById('editor-preview-container');
    const editorContainer = document.getElementById('editor-write-container');

    if (previewTab && writeTab && previewArea && editorContainer) {
        previewTab.addEventListener('click', () => {
            previewTab.classList.add('active');
            writeTab.classList.remove('active');
            editorContainer.classList.add('d-none');
            previewArea.classList.remove('d-none');

            // Simple client-side Markdown rendering preview
            previewArea.innerHTML = simpleMarkdownParse(textarea.value);
        });

        writeTab.addEventListener('click', () => {
            writeTab.classList.add('active');
            previewTab.classList.remove('active');
            previewArea.classList.add('d-none');
            editorContainer.classList.remove('d-none');
            textarea.focus();
        });
    }
}

function applyFormatting(textarea, format) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    let replacement = '';

    switch (format) {
        case 'bold':
            replacement = `**${selectedText || 'bold text'}**`;
            break;
        case 'italic':
            replacement = `*${selectedText || 'italic text'}*`;
            break;
        case 'heading':
            replacement = `\n## ${selectedText || 'Heading 2'}\n`;
            break;
        case 'quote':
            replacement = `\n> ${selectedText || 'Quote'}\n`;
            break;
        case 'code':
            if (selectedText.includes('\n')) {
                replacement = `\n\`\`\`python\n${selectedText || '# code here'}\n\`\`\`\n`;
            } else {
                replacement = `\`${selectedText || 'code'}\``;
            }
            break;
        case 'list':
            replacement = `\n- ${selectedText || 'List item'}\n`;
            break;
        case 'link':
            replacement = `[${selectedText || 'link text'}](https://example.com)`;
            break;
        default:
            return;
    }

    textarea.setRangeText(replacement, start, end, 'end');
    textarea.focus();
}

/**
 * Basic client-side markdown preview renderer for instant feedback.
 */
function simpleMarkdownParse(md) {
    if (!md || !md.trim()) {
        return '<p class="text-muted fst-italic">Nothing to preview yet. Start typing your blog post!</p>';
    }

    let html = md
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Code blocks
    html = html.replace(/```([a-z]*)\n([\s\S]*?)```/gm, '<pre><code>$2</code></pre>');
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    // Bold & Italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // Blockquote
    html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    // Paragraphs
    html = html.replace(/\n\n+/g, '</p><p>');
    html = '<p>' + html + '</p>';
    // Line breaks
    html = html.replace(/\n/g, '<br>');

    return html;
}
