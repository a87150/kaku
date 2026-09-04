/* Kaku 轻量灯箱 —— 零依赖、事件委托实现
 *
 * 用法：给任意可点击元素添加 data-lightbox 属性即可（<a> 或 <img> 均可）：
 *   data-lightbox          标记可点开大图（点击时阻止默认跳转）
 *   data-lightbox-src      大图 URL；缺省时取元素自身/内部 <img> 的当前 src
 *   data-lightbox-caption  说明文字；缺省取 <img> 的 alt
 *   data-lightbox-group    分组名；同一分组内支持 ←/→ 前后翻页
 *
 * 全部按需创建覆盖层，键盘 Esc 关闭、←/→ 翻页，点击背景关闭。
 */
(function () {
    'use strict';

    var root = null;        // 覆盖层容器
    var imgEl = null;       // 覆盖层内 <img>
    var figureEl = null;    // <figure>
    var captionEl = null;   // 说明文字
    var counterEl = null;   // 页码（n / total）
    var closeEl = null;     // 关闭按钮
    var prevEl = null;      // 上一张
    var nextEl = null;      // 下一张

    var groupItems = [];    // 当前分组元素（按 DOM 顺序）
    var groupIndex = 0;     // 当前展示的下标
    var lastFocused = null; // 打开前获得焦点的元素，关闭后还给它

    function buildRoot() {
        if (root) {
            return;
        }
        root = document.createElement('div');
        root.className = 'kaku-lb';
        root.setAttribute('hidden', 'hidden');

        var backdrop = document.createElement('div');
        backdrop.className = 'kaku-lb-backdrop';

        figureEl = document.createElement('figure');
        figureEl.className = 'kaku-lb-figure';

        imgEl = document.createElement('img');
        imgEl.className = 'kaku-lb-img';
        imgEl.alt = '';

        var spinner = document.createElement('div');
        spinner.className = 'kaku-lb-spinner';

        captionEl = document.createElement('figcaption');
        captionEl.className = 'kaku-lb-caption';

        counterEl = document.createElement('div');
        counterEl.className = 'kaku-lb-counter';

        closeEl = document.createElement('button');
        closeEl.type = 'button';
        closeEl.className = 'kaku-lb-close';
        closeEl.setAttribute('aria-label', '关闭');
        closeEl.innerHTML = '&times;';

        prevEl = document.createElement('button');
        prevEl.type = 'button';
        prevEl.className = 'kaku-lb-nav kaku-lb-prev';
        prevEl.setAttribute('aria-label', '上一张');
        prevEl.innerHTML = '&#8249;';

        nextEl = document.createElement('button');
        nextEl.type = 'button';
        nextEl.className = 'kaku-lb-nav kaku-lb-next';
        nextEl.setAttribute('aria-label', '下一张');
        nextEl.innerHTML = '&#8250;';

        figureEl.appendChild(imgEl);
        figureEl.appendChild(spinner);
        figureEl.appendChild(captionEl);
        figureEl.appendChild(counterEl);
        figureEl.appendChild(prevEl);
        figureEl.appendChild(nextEl);
        root.appendChild(backdrop);
        root.appendChild(figureEl);
        root.appendChild(closeEl); // 关闭按钮相对视口右上角，避免被裁切
        document.body.appendChild(root);

        backdrop.addEventListener('click', hide);
        closeEl.addEventListener('click', hide);
        prevEl.addEventListener('click', function () { show(groupIndex - 1); });
        nextEl.addEventListener('click', function () { show(groupIndex + 1); });
    }

    function srcOf(el) {
        var custom = el.getAttribute('data-lightbox-src');
        if (custom) {
            return custom;
        }
        var img = el.tagName === 'IMG' ? el : el.querySelector('img');
        if (img) {
            return img.currentSrc || img.src;
        }
        return el.getAttribute('href') || '';
    }

    function captionOf(el) {
        var custom = el.getAttribute('data-lightbox-caption');
        if (custom != null) {
            return custom;
        }
        var img = el.tagName === 'IMG' ? el : el.querySelector('img');
        if (img) {
            return img.getAttribute('alt') || '';
        }
        return '';
    }

    function openFor(el) {
        var group = el.getAttribute('data-lightbox-group');
        if (group) {
            var all = document.querySelectorAll('[data-lightbox]');
            groupItems = Array.prototype.filter.call(all, function (it) {
                return it.getAttribute('data-lightbox-group') === group;
            });
            groupIndex = groupItems.indexOf(el);
            if (groupIndex < 0) {
                groupIndex = 0;
            }
        } else {
            groupItems = [el];
            groupIndex = 0;
        }
        show(groupIndex);
    }

    function show(i) {
        buildRoot();
        var total = groupItems.length;
        if (total === 0) {
            return;
        }
        groupIndex = ((i % total) + total) % total; // 循环
        var el = groupItems[groupIndex];
        if (!el) {
            return;
        }
        if (!root.hasAttribute('hidden')) {
            // 正在展示中切换（翻页）
        } else {
            lastFocused = document.activeElement;
        }

        imgEl.classList.add('kaku-lb-loading');
        figureEl.classList.add('kaku-lb-busy');
        imgEl.onload = imgEl.onerror = function () {
            imgEl.classList.remove('kaku-lb-loading');
            figureEl.classList.remove('kaku-lb-busy');
        };
        imgEl.src = srcOf(el);
        imgEl.alt = captionOf(el) || '';
        captionEl.textContent = captionOf(el);
        counterEl.textContent = total > 1 ? (groupIndex + 1) + ' / ' + total : '';
        prevEl.style.display = total > 1 ? '' : 'none';
        nextEl.style.display = total > 1 ? '' : 'none';

        root.removeAttribute('hidden');
        document.body.classList.add('kaku-lb-open');
        closeEl.focus();
    }

    function hide() {
        if (!root) {
            return;
        }
        root.setAttribute('hidden', 'hidden');
        document.body.classList.remove('kaku-lb-open');
        if (lastFocused && lastFocused.focus) {
            lastFocused.focus();
        }
    }

    // 事件委托：点击 data-lightbox 元素打开灯箱
    document.addEventListener('click', function (e) {
        var el = e.target && e.target.closest ? e.target.closest('[data-lightbox]') : null;
        if (el) {
            e.preventDefault();
            openFor(el);
        }
    });

    // 键盘控制
    document.addEventListener('keydown', function (e) {
        if (!root || root.hasAttribute('hidden')) {
            return;
        }
        if (e.key === 'Escape' || e.key === 'Esc') {
            e.preventDefault();
            hide();
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            show(groupIndex - 1);
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            show(groupIndex + 1);
        }
    });
})();
