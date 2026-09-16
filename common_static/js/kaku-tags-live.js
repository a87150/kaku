/* Kaku 详情页标签即时增删 —— 替代原先“操作后 location.reload()”的整页刷新
 *
 * 与两个模板配合：
 *   - tag.html     渲染标签块容器 #kaku-tag-chips（带 data-tags-type / data-tags-pk / data-can-edit）
 *   - post_tag.html 顶部的“添加标签”输入框，成功后调用 KakuTagsLive.addTag()
 *
 * 依赖 base.html 已加载的 kaku-util.js（window.KakuAjax + CSRF）。
 * tag.html 在详情页里先于 post_tag.html 出现，因此本文件先把 window.KakuTagsLive 挂好。
 */
(function () {
    'use strict';

    function boot() {
        var box = document.getElementById('kaku-tag-chips');
        if (!box) {
            return;
        }

        var type = box.getAttribute('data-tags-type') || '';
        var pk = box.getAttribute('data-tags-pk') || '';
        var canEdit = box.getAttribute('data-can-edit') === '1';
        var msgEl = document.getElementById('kaku-tag-live-msg');
        var configured = !!(type && pk);

        function showMsg(text, ok) {
            if (!msgEl) {
                return;
            }
            msgEl.textContent = text || '';
            msgEl.classList.toggle('is-ok', !!text && !!ok);
            msgEl.classList.toggle('is-error', !!text && !ok);
        }

        // 不用属性选择器查标签名：标签里可能含引号/反斜杠，遍历比对最稳
        function findItem(name) {
            var items = box.querySelectorAll('.kaku-tag-item');
            for (var i = 0; i < items.length; i += 1) {
                if (items[i].getAttribute('data-tag') === name) {
                    return items[i];
                }
            }
            return null;
        }

        function makeRemoveBtn(name) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'kaku-tag-remove';
            btn.setAttribute('data-tag', name);
            btn.setAttribute('title', '移除标签 ' + name);
            btn.setAttribute('aria-label', '移除标签 ' + name);
            btn.textContent = '×';
            return btn;
        }

        // 全部用 createElement + textContent 构造，标签名不会被当成 HTML 解析
        function makeItem(name) {
            var wrap = document.createElement('span');
            wrap.className = 'kaku-tag-item';
            wrap.setAttribute('data-tag', name);

            var link = document.createElement('a');
            link.className = 'mdui-chip';
            link.href = '/search/?query=' + encodeURIComponent(name);
            link.target = '_blank';

            var icon = document.createElement('i');
            icon.className = 'mdui-chip-icon mdui-icon material-icons';
            icon.textContent = 'label';
            link.appendChild(icon);

            var title = document.createElement('span');
            title.className = 'mdui-chip-title';
            title.textContent = name;
            link.appendChild(title);
            wrap.appendChild(link);

            if (canEdit) {
                wrap.appendChild(makeRemoveBtn(name));
            }
            return wrap;
        }

        function syncEmpty() {
            var hasAny = !!box.querySelector('.kaku-tag-item');
            var empty = box.querySelector('.kaku-tag-empty');
            if (!empty && !hasAny) {
                empty = document.createElement('span');
                empty.className = 'kaku-text-muted kaku-tag-empty';
                empty.textContent = '暂无标签';
                box.appendChild(empty);
            }
            if (empty) {
                empty.hidden = hasAny;
            }
        }

        function addTag(name) {
            name = (name || '').trim();
            if (!name) {
                return false;
            }
            if (findItem(name)) {
                showMsg('已添加过该标签', false);
                return false;
            }
            box.appendChild(makeItem(name));
            syncEmpty();
            showMsg('已添加标签「' + name + '」', true);
            return true;
        }

        // 移除按钮用事件委托：新增的标签块无需重新绑定
        box.addEventListener('click', function (event) {
            var target = event.target;
            var btn = target && target.closest ? target.closest('.kaku-tag-remove') : null;
            if (!btn || btn.disabled || !configured) {
                return;
            }
            event.preventDefault();

            var name = btn.getAttribute('data-tag');
            btn.disabled = true;
            window.KakuAjax.post(
                '/tags/delete/',
                {tag: name, pk: pk, type: type},
                function (ret) {
                    ret = ret || {};
                    if (ret.ok) {
                        var item = findItem(name);
                        if (item && item.parentNode) {
                            item.parentNode.removeChild(item);
                        }
                        syncEmpty();
                        showMsg(ret.msg || '已移除', true);
                    } else {
                        btn.disabled = false;
                        showMsg(ret.msg || '移除失败', false);
                    }
                },
                function () {
                    btn.disabled = false;
                    showMsg('网络异常，请稍后重试', false);
                }
            );
        });

        window.KakuTagsLive = {
            addTag: addTag,
            showMsg: showMsg,
            canEdit: canEdit,
            configured: configured
        };
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
