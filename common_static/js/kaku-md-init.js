/* Kaku Markdown 编辑器 —— 基于 EasyMDE（本地化）
 *
 * 依赖脚本需先于本文件加载（本文件在页面底部按顺序引入）：
 *   1. vendor/marked/marked.min.js      —— 预览渲染
 *   2. vendor/dompurify/purify.min.js   —— 预览内容净化（防 XSS）
 *   3. vendor/easymde/easymde.min.js    —— 编辑器本体（内含 CodeMirror）
 *
 * 页面结构约定（模板里直接输出，避免运行时插入造成工具栏丢失）：
 *   <div class="kaku-md-host">
 *       <div class="kaku-md-bar" data-md-bar>
 *           <button type="button" data-md-method="toggleBold">加粗</button>
 *           ...
 *       </div>
 *       <textarea data-md-editor ...></textarea>
 *   </div>
 *
 * EasyMDE 接管 textarea 时会把它所在位置替换为 .EasyMDEContainer，
 * 工具栏保持在上方（静态 HTML，不依赖容器探测）。
 */
(function () {
    'use strict';

    function safeRender(plainText) {
        if (!window.marked) {
            return plainText;
        }
        var html = window.marked.parse(plainText || '');
        if (window.DOMPurify) {
            return window.DOMPurify.sanitize(html);
        }
        return html;
    }

    function bindButton(btn, editor) {
        var method = btn.getAttribute('data-md-method');
        if (!method || !editor || typeof editor[method] !== 'function') {
            return;
        }
        btn.addEventListener('click', function () {
            editor[method]();
            if (editor.codemirror) {
                editor.codemirror.focus();
            }
        });
    }

    function bindBar(host, editor) {
        var bar = host ? host.querySelector('[data-md-bar]') : null;
        if (!bar) {
            bar = document.querySelector('[data-md-bar]');
        }
        if (!bar) {
            return;
        }
        var buttons = bar.querySelectorAll('button[data-md-method]');
        Array.prototype.forEach.call(buttons, function (btn) {
            bindButton(btn, editor);
        });
    }

    function initEditor(textarea) {
        if (!window.EasyMDE || textarea.getAttribute('data-md-init')) {
            return;
        }
        textarea.setAttribute('data-md-init', '1');

        var host = textarea.closest ? textarea.closest('.kaku-md-host') : null;

        var editor = new window.EasyMDE({
            element: textarea,
            autofocus: false,
            spellChecker: false,
            status: false,
            autoDownloadFontAwesome: false,
            toolbar: false, // 工具栏由页面静态 .kaku-md-bar 提供
            placeholder: textarea.getAttribute('placeholder') || '在这里用 Markdown 写作…',
            renderingConfig: {
                singleLineBreaks: false,
                codeSyntaxHighlighting: false
            },
            previewRender: safeRender
        });

        // 工具栏按钮是静态 HTML，只需绑定点击（EasyMDE 完成后 DOM 已就位）
        bindBar(host, editor);
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
