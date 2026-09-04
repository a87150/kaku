/* Kaku 前端工具 —— CSRF 与轻量请求封装
 *
 * 替代全站此前依赖的 jQuery.ajax：
 *   - KakuAjax.post(url, data, success[, failure])   表单式 POST（返回 JSON）
 *   - KakuAjax.getJSON(url[, params], success[, failure])
 *   - KakuAjax.csrf()                                 返回当前 CSRF token
 *
 * CSRF token 来源：base.html 注入 window.KAKU_CSRF（模板 {{ csrf_token }}），
 * 缺失时回退读取 csrftoken cookie。
 */
(function () {
    'use strict';

    function getCookie(name) {
        var m = document.cookie.match('(?:^|;\\s*)' + name + '=([^;]*)');
        return m ? decodeURIComponent(m[1]) : '';
    }

    function csrfToken() {
        if (window.KAKU_CSRF) {
            return window.KAKU_CSRF;
        }
        return getCookie('csrftoken') || '';
    }

    function buildHeaders() {
        return {
            'X-CSRFToken': csrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    function toJson(response) {
        return response.json().catch(function () { return {}; });
    }

    function post(url, data, success, failure) {
        var body = new URLSearchParams();
        if (data) {
            Object.keys(data).forEach(function (key) {
                body.append(key, data[key] == null ? '' : data[key]);
            });
        }
        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: Object.assign(buildHeaders(), {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }),
            body: body.toString()
        })
            .then(toJson)
            .then(function (json) {
                if (success) { success(json); }
            })
            .catch(function () {
                if (failure) { failure(); }
            });
    }

    function getJSON(url, params, success, failure) {
        var qs = '';
        if (params) {
            var usp = new URLSearchParams();
            Object.keys(params).forEach(function (key) {
                usp.append(key, params[key]);
            });
            qs = '?' + usp.toString();
        }
        fetch(url + qs, {
            credentials: 'same-origin',
            headers: buildHeaders()
        })
            .then(toJson)
            .then(function (json) {
                if (success) { success(json); }
            })
            .catch(function () {
                if (failure) { failure(); }
            });
    }

    window.KakuAjax = { post: post, getJSON: getJSON, csrf: csrfToken };
})();
