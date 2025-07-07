// content script to unblock right-click and F12
(function () {
  ['contextmenu', 'keydown', 'keyup', 'keypress'].forEach(type => {
    window.addEventListener(type, evt => {
      evt.stopImmediatePropagation();
    }, true);
  });

  document.addEventListener('DOMContentLoaded', () => {
    document.oncontextmenu = null;
  });

  const origAdd = EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener = function (type, listener, opts) {
    if (['contextmenu', 'keydown', 'keyup', 'keypress'].includes(type)) {
      return origAdd.call(this, type, () => {}, opts);
    }
    return origAdd.call(this, type, listener, opts);
  };
})();
