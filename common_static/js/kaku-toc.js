/* Kaku 文章目录 —— 零依赖
 *
 * 用法：在模板中放一个容器：
 *   <div class="kaku-toc-block" data-toc-for="#content" style="display:none;">
 *       <div class="kaku-toc-title">目录</div>
 *       <div class="kaku-toc-list" data-toc-list></div>
 *   </div>
 * 其中 data-toc-for 指向文章正文容器（如 #content）。
 *
 * 页面加载时会扫描标题（h1~h6）自动生成锚点目录；标题数 < 2 时整块隐藏。
 * 章节内容通过 AJAX 整体替换正文后，调用 window.KakuTOC.rebuild() 重建目录。
 */
(function () {
    'use strict';

    function findScope(block) {
        var selector = block.getAttribute('data-toc-for');
        if (selector) {
            return document.querySelector(selector);
        }
        return block.parentElement;
    }

    function buildBlock(block) {
        var scope = findScope(block);
        var listHost = block.querySelector('[data-toc-list]');
        if (!scope || !listHost) {
            return;
        }

        // 只收集正文里的标题（跳过 <pre>/<code> 内看似标题的文本）
        var headings = Array.prototype.filter.call(
            scope.querySelectorAll('h1, h2, h3, h4, h5, h6'),
            function (h) { return !h.closest('pre, code'); }
        );

        if (headings.length < 2) {
            block.style.display = 'none';
            return;
        }

        // 为每个标题分配稳定 id（顺序编号，避免中文/特殊字符的转义问题）
        headings.forEach(function (h, i) {
            if (!h.id) {
                h.id = 'kaku-toc-' + i;
            }
        });

        listHost.innerHTML = '';
        headings.forEach(function (h, i) {
            var level = parseInt(h.tagName.charAt(1), 10); // h1 -> 1
            var li = document.createElement('li');
            li.className = 'kaku-toc-level-' + Math.min(level, 6);
            var a = document.createElement('a');
            a.href = '#' + h.id;
            a.textContent = (h.textContent || '').trim();
            if (a.textContent.length > 60) {
                a.textContent = a.textContent.slice(0, 60) + '…';
            }
            a.title = (h.textContent || '').trim();
            li.appendChild(a);
            listHost.appendChild(li);
        });

        block.style.display = '';
    }

    function init() {
        var blocks = document.querySelectorAll('[data-toc-for]');
        Array.prototype.forEach.call(blocks, buildBlock);
    }

    if (window.KakuTOC) {
        // 已在其它脚本初始化过，仅合并接口
        window.KakuTOC.rebuild = init;
        return;
    }

    // 平滑滚动到标题（配合 CSS scroll-margin-top 避开固定顶栏）
    document.addEventListener('click', function (e) {
        var a = e.target && e.target.closest ? e.target.closest('a[href^="#kaku-toc-"]') : null;
        if (!a) {
            return;
        }
        var id = a.getAttribute('href').slice(1);
        var target = document.getElementById(id);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (history.replaceState) {
                history.replaceState(null, '', '#' + id);
            }
        }
    });

    window.KakuTOC = {
        init: init,
        rebuild: init
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
