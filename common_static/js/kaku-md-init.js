/* Kaku Markdown 编辑器 —— 基于 EasyMDE（本地化）
 *
 * 依赖脚本需先于本文件加载（本文件在页面底部按顺序引入）：
 *   1. vendor/marked/marked.min.js      —— 预览渲染
 *   2. vendor/dompurify/purify.min.js   —— 预览内容净化（防 XSS）
 *   3. vendor/easymde/easymde.min.js    —— 编辑器本体（内含 CodeMirror）
 *
 * 页面里放 <textarea data-md-editor>，初始化后自动接管：
 * 原 textarea 保留并与编辑器双向同步，直接随表单提交原始 Markdown。
 */
(function () {
    'use strict';

    function initEditor(textarea) {
        if (!window.EasyMDE || textarea.getAttribute('data-md-init')) {
            return;
        }
        textarea.setAttribute('data-md-init', '1');

        var safeRender = function (plainText) {
            if (!window.marked) {
                return plainText;
            }
            var html = window.marked.parse(plainText || '');
            if (window.DOMPurify) {
                return window.DOMPurify.sanitize(html);
            }
            return html;
        };

        // 常用工具栏，标题悬停提示使用中文
        var toolbar = [
            'bold', 'italic', 'strikethrough', '|',
            'heading', '|',
            'quote', 'unordered-list', 'ordered-list', '|',
            'link', 'image', 'table', '|',
            'code', '|',
            'preview', 'side-by-side', 'fullscreen'
        ];

        new window.EasyMDE({
            element: textarea,
            autofocus: false,
            spellChecker: false,
            status: false,
            autoDownloadFontAwesome: false,
            toolbar: toolbar,
            placeholder: textarea.getAttribute('placeholder') || '在这里用 Markdown 写作…',
            renderingConfig: {
                singleLineBreaks: false,
                codeSyntaxHighlighting: false
            },
            previewRender: safeRender
        });
    }

    function initAll() {
        var nodes = document.querySelectorAll('textarea[data-md-editor]');
        Array.prototype.forEach.call(nodes, initEditor);
    }

    window.KakuMdEditor = { init: initAll };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})();
