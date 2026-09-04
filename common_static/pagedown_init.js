/* django-pagedown 2.2.1 配套的编辑器初始化（本地化副本）
 *
 * 注意：必须与本版本 pagedown widget 的输出结构一致 ——
 *   文本域  id="wmd-input-<field>"
 *   工具栏  id="wmd-button-bar-<field>"
 *   预览区  id="wmd-preview-<field>"
 * Markdown.Editor 通过 postfix=<field> 拼接查找到这三个面板。
 * 使用 Markdown.getSanitizingConverter()（净化 HTML）并启用 Markdown.Extra。
 */
var DjangoPagedown = DjangoPagedown || {};

DjangoPagedown = (function() {
  var converter = Markdown.getSanitizingConverter();
  var editors = {};
  var elements;

  Markdown.Extra.init(converter, {
    extensions: "all"
  });

  var createEditor = function(element) {
    var input = element.getElementsByClassName("wmd-input")[0];
    if (input === undefined) {
      return
    }
    // input.id 形如 "wmd-input-id_content"，去掉 "wmd-input-" 前缀得到 postfix
    var id = input.id.substr(9);
    if (!editors.hasOwnProperty(id)) {
      var editor = new Markdown.Editor(converter, id, {});

      editor.run();
      editors[id] = editor;
    }
  };

  var destroyEditor = function(element) {
    if (editors.hasOwnProperty(element.id)) {
      delete editors[element.id];
      return true;
    }
    return false;
  };

  var init = function() {
    elements = document.getElementsByClassName("wmd-wrapper");
    for (var i = 0; i < elements.length; ++i) {
      createEditor(elements[i]);
    }
  };

  return {
    init: function() {
      return init();
    },
    createEditor: function(element) {
      return createEditor(element);
    },
    destroyEditor: function(element) {
      return destroyEditor(element);
    }
  };
})();

window.onload = DjangoPagedown.init;
