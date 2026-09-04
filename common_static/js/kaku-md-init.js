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
 *           <button type="button" data-md-action="preview">预览</button>
 *           <button type="button" data-md-action="fullscreen">全屏</button>
 *       </div>
 *       <textarea data-md-editor ...></textarea>
 *       <div class="kaku-live-preview" data-live-preview hidden></div>
 *   </div>
 *
 * 说明：
 * - EasyMDE 自带的“预览/分屏/全屏”依赖其内置 toolbar DOM，工具栏被禁用后
 *   这些功能会异常（分屏不显示、全屏后无法退出），因此这里不调用它们；
 * - “预览/全屏”由本脚本自研实现（无内部依赖），行为完全可控。
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

    function bindMethodButton(btn, editor) {
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

    function renderLivePreview(host, editor) {
        var panel = host.querySelector('[data-live-preview]');
        if (!panel || !editor || !editor.codemirror) {
            return;
        }
        var value = editor.codemirror.getValue() || '';
        panel.innerHTML = safeRender(value);
    }

    function toggleLivePreview(host, btn, editor) {
        var panel = host.querySelector('[data-live-preview]');
        if (!panel) {
            return;
        }
        var showing = !panel.hidden;
        panel.hidden = showing; // 下一次点击 = 关闭
        if (!panel.hidden) {
            renderLivePreview(host, editor);
        }
        if (btn) {
            btn.classList.toggle('is-active', !showing);
        }
    }

    function setFullscreen(host, active) {
        host.classList.toggle('is-fullscreen', !!active);
        document.body.classList.toggle('kaku-md-fs-lock', !!active);
        if (active && host.scrollIntoView) {
            host.scrollIntoView({ block: 'start' });
        }
    }

    function bindViewButton(btn, host, editor) {
        var action = btn.getAttribute('data-md-action');
        if (action === 'preview') {
            btn.addEventListener('click', function () {
                toggleLivePreview(host, btn, editor);
            });
        } else if (action === 'fullscreen') {
            btn.addEventListener('click', function () {
                setFullscreen(host, !host.classList.contains('is-fullscreen'));
                btn.classList.toggle('is-active', host.classList.contains('is-fullscreen'));
            });
        }
    }

    function bindBar(host, editor) {
        var bar = host ? host.querySelector('[data-md-bar]') : document.querySelector('[data-md-bar]');
        if (!bar) {
            return;
        }
        var buttons = bar.querySelectorAll('button[data-md-method]');
        Array.prototype.forEach.call(buttons, function (btn) {
            bindMethodButton(btn, editor);
        });
        var viewButtons = bar.querySelectorAll('button[data-md-action]');
        Array.prototype.forEach.call(viewButtons, function (btn) {
            bindViewButton(btn, host, editor);
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

        if (editor && editor.codemirror) {
            // 输入变化时若预览面板可见则即时刷新（简单防抖）
            var timer = null;
            editor.codemirror.on('change', function () {
                if (!host) {
                    return;
                }
                var panel = host.querySelector('[data-live-preview]');
                if (!panel || panel.hidden) {
                    return;
                }
                if (timer) {
                    clearTimeout(timer);
                }
                timer = setTimeout(function () {
                    renderLivePreview(host, editor);
                }, 250);
            });
        }

        bindBar(host, editor);
    }

    function initAll() {
        document.querySelectorAll('textarea[data-md-editor]').forEach(initEditor);
    }

    // Esc 退出“全屏”模式
    document.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape') {
            return;
        }
        var host = document.querySelector('.kaku-md-host.is-fullscreen');
        if (host) {
            setFullscreen(host, false);
            var bar = host.querySelector('[data-md-bar]');
            if (bar) {
                var btn = bar.querySelector('button[data-md-action="fullscreen"]');
                if (btn) {
                    btn.classList.remove('is-active');
                }
            }
        }
    });

    window.KakuMdEditor = { init: initAll };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})();
