(function () {
  ['contextmenu', 'keydown', 'keyup', 'keypress'].forEach(type => {
    window.addEventListener(type, evt => {
      // Allow Enter key (key code 13)
      if (evt.key === 'Enter' || evt.keyCode === 13) return;
      evt.stopImmediatePropagation();
    }, true);
  });

  document.addEventListener('DOMContentLoaded', () => {
    document.oncontextmenu = null;
  });

  const origAdd = EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener = function (type, listener, opts) {
    if (['contextmenu', 'keydown', 'keyup', 'keypress'].includes(type)) {
      return origAdd.call(this, type, function (evt) {
        if (evt.key === 'Enter' || evt.keyCode === 13) {
          listener(evt); // allow Enter key events to trigger
        }
      }, opts);
    }
    return origAdd.call(this, type, listener, opts);
  };
})();
