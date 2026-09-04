/* Kaku 标签选择器 —— 搜索选择已有标签 + 回车新建标签
 *
 * 结构约定（写在模板里）：
 *   <div class="kaku-tags-picker">
 *     <input type="text" class="kaku-tag-input" .../>
 *     <div class="kaku-tags-selected"></div>
 *     <div class="kaku-tags-available"></div>
 *     <div class="kaku-tags-errors"></div>
 *     <input type="hidden" name="tags_raw" id="id_tags_raw" />
 *   </div>
 * 已有标签清单通过 <script type="application/json" id="kaku-available-tags">
 * （Django json_script）注入。
 *
 * 提交给服务端的是逗号分隔的标签名字符串（字段 tags_raw）。
 */
(function () {
    'use strict';

    var LIMIT = 10;     // 与 kaku.tagfields.MAX_TAGS_PER_ITEM 一致
    var MAX_LEN = 30;   // 与 Tag.name.max_length 一致

    function parseNames(text) {
        return (text || '').split(/[,，]/).map(function (s) { return s.trim(); })
            .filter(Boolean);
    }

    function init(root) {
        if (root.getAttribute('data-init')) {
            return;
        }
        root.setAttribute('data-init', '1');

        var input = root.querySelector('.kaku-tag-input');
        var selectedBox = root.querySelector('.kaku-tags-selected');
        var availBox = root.querySelector('.kaku-tags-available');
        var errorBox = root.querySelector('.kaku-tags-errors');
        var hidden = root.querySelector('input[name="tags_raw"]');
        var jsonEl = document.getElementById('kaku-available-tags');

        var available = [];
        if (jsonEl && jsonEl.textContent) {
            try {
                available = JSON.parse(jsonEl.textContent) || [];
            } catch (e) {
                available = [];
            }
        }

        var selected = new Set();
        if (hidden && hidden.value) {
            parseNames(hidden.value).forEach(function (n) { selected.add(n); });
        }

        function sync() {
            if (hidden) {
                hidden.value = Array.from(selected).join(', ');
            }
        }

        function showError(msg) {
            errorBox.textContent = msg || '';
        }

        function render() {
            // 已选标签
            selectedBox.innerHTML = '';
            selected.forEach(function (name) {
                var span = document.createElement('span');
                span.className = 'kaku-tag-chip kaku-tag-selected';
                span.textContent = '# ' + name;

                var x = document.createElement('button');
                x.type = 'button';
                x.className = 'kaku-tag-chip-x';
                x.setAttribute('aria-label', '移除 ' + name);
                x.title = '移除';
                x.innerHTML = '&times;';
                x.addEventListener('click', function () {
                    selected.delete(name);
                    render();
                    sync();
                });
                span.appendChild(x);
                selectedBox.appendChild(span);
            });

            // 可候选标签（随输入过滤）
            var q = (input.value || '').trim().toLowerCase();
            var shown = 0;
            availBox.innerHTML = '';
            available.forEach(function (name) {
                if (q && name.toLowerCase().indexOf(q) === -1) {
                    return;
                }
                shown += 1;
                var span = document.createElement('span');
                span.className = 'kaku-tag-chip' + (selected.has(name) ? ' is-picked' : '');
                span.textContent = '# ' + name;
                span.title = selected.has(name) ? '已选择，点击取消' : '点击选择';
                span.addEventListener('click', function () {
                    if (selected.has(name)) {
                        selected.delete(name);
                    } else {
                        if (selected.size >= LIMIT) {
                            showError('最多选择 ' + LIMIT + ' 个标签');
                            return;
                        }
                        selected.add(name);
                    }
                    showError('');
                    render();
                    sync();
                });
                availBox.appendChild(span);
            });

            if (!shown) {
                var tip = document.createElement('div');
                tip.className = 'kaku-tags-tip';
                tip.textContent = q
                    ? '没有匹配的标签：按回车把它创建为新标签'
                    : '还没有标签可选：输入新标签后回车即可创建';
                availBox.appendChild(tip);
            }
        }

        // 回车 / 逗号添加新标签
        function commitNew(rawText) {
            var names = parseNames(rawText);
            if (!names.length) {
                showError('请输入标签');
                return;
            }
            for (var i = 0; i < names.length; i++) {
                var name = names[i];
                if (name.length > MAX_LEN) {
                    showError('标签「' + name + '」太长（最多 ' + MAX_LEN + ' 字）');
                    return;
                }
                if (selected.has(name)) {
                    continue;
                }
                if (selected.size >= LIMIT) {
                    showError('最多选择 ' + LIMIT + ' 个标签');
                    return;
                }
                selected.add(name);
            }
            showError('');
            input.value = '';
            render();
            sync();
        }

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                commitNew(input.value);
            } else if (e.key === 'Backspace' && !input.value && selected.size) {
                var last = Array.from(selected).pop();
                selected.delete(last);
                render();
                sync();
            }
        });
        input.addEventListener('input', render);

        render();
        sync();
    }

    function initAll() {
        var nodes = document.querySelectorAll('.kaku-tags-picker');
        Array.prototype.forEach.call(nodes, init);
    }

    window.KakuTagsPicker = { init: init, initAll: initAll };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})();
