/* Kaku Markdown 编辑器 —— 基于 EasyMDE（本地化）
 *
 * 依赖脚本需先于本文件加载（本文件在页面底部按顺序引入）：
 *   1. vendor/marked/marked.min.js      —— 预览渲染
 *   2. vendor/dompurify/purify.min.js   —— 预览内容净化（防 XSS）
 *   3. vendor/easymde/easymde.min.js    —— 编辑器本体（内含 CodeMirror）
 *
 * 页面里放 <textarea data-md-editor>，初始化后自动接管：
 * 原 textarea 保留并与编辑器双向同步，直接随表单提交原始 Markdown。
 *
 * 不使用 EasyMDE 自带的图标工具栏（图标字体依赖易错位），改为自绘的
 * 文本按钮工具栏（.kaku-md-bar），排布完全可控。
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

    /* 自绘工具栏按钮配置：label 为按钮文字，method 为 EasyMDE 实例方法 */
    var BAR_ITEMS = [
        { label: '加粗', method: 'toggleBold' },
        { label: '斜体', method: 'toggleItalic' },
        { label: '删除线', method: 'toggleStrikethrough' },
        { label: '标题', method: 'toggleHeading1' },
        { label: '引用', method: 'toggleBlockquote' },
        { label: '无序列表', method: 'toggleUnorderedList' },
        { label: '有序列表', method: 'toggleOrderedList' },
        { label: '链接', method: 'drawLink' },
        { label: '图片', method: 'drawImage' },
        { label: '表格', method: 'drawTable' },
        { label: '代码块', method: 'toggleCodeBlock' },
        { label: '分隔线', method: 'drawHorizontalRule' },
        { label: '撤销', method: 'undo' },
        { label: '重做', method: 'redo' }
    ];

    var MODE_ITEMS = [
        { label: '预览', method: 'togglePreview' },
        { label: '左右分屏', method: 'toggleSideBySide' },
        { label: '全屏', method: 'toggleFullScreen' }
    ];

    function makeBar(editor, textarea) {
        var bar = document.createElement('div');
        bar.className = 'kaku-md-bar';

        BAR_ITEMS.forEach(function (item) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = item.label;
            btn.addEventListener('click', function () {
                if (editor && typeof editor[item.method] === 'function') {
                    editor[item.method]();
                    if (editor.codemirror) {
                        editor.codemirror.focus();
                    }
                }
            });
            bar.appendChild(btn);
        });

        var sep = document.createElement('span');
        sep.className = 'kaku-md-bar-sep';
        bar.appendChild(sep);

        MODE_ITEMS.forEach(function (item) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = item.label;
            btn.addEventListener('click', function () {
                if (editor && typeof editor[item.method] === 'function') {
                    editor[item.method]();
                }
            });
            bar.appendChild(btn);
        });
        return bar;
    }

    function initEditor(textarea) {
        if (!window.EasyMDE || textarea.getAttribute('data-md-init')) {
            return;
        }
        textarea.setAttribute('data-md-init', '1');

        var editor = new window.EasyMDE({
            element: textarea,
            autofocus: false,
            spellChecker: false,
            status: false,
            autoDownloadFontAwesome: false,
            toolbar: false, // 不使用自带图标工具栏，改用自绘文本工具栏
            placeholder: textarea.getAttribute('placeholder') || '在这里用 Markdown 写作…',
            renderingConfig: {
                singleLineBreaks: false,
                codeSyntaxHighlighting: false
            },
            previewRender: safeRender
        });

        // 把自绘工具栏插到 EasyMDE 容器最前面
        var container = textarea.closest ? textarea.closest('.EasyMDEContainer')
            : document.querySelector('.EasyMDEContainer');
        if (!container) {
            return;
        }
        var bar = makeBar(editor, textarea);
        container.insertBefore(bar, container.firstChild);
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
