(function () {
  // Step 1: Remove existing right-click block
  document.addEventListener('DOMContentLoaded', () => {
    document.oncontextmenu = null;
  });

  // Step 2: Stop event propagation for contextmenu (right-click)
  window.addEventListener('contextmenu', function (e) {
    e.stopImmediatePropagation(); // prevent other handlers from blocking it
  }, true);

  // Step 3: Patch addEventListener to ignore future contextmenu blockers
  const origAdd = EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener = function (type, listener, opts) {
    if (type === 'contextmenu') {
      // Ignore attempts to block right-click
      return origAdd.call(this, type, function () {}, opts);
    }
    return origAdd.call(this, type, listener, opts); // allow all keys
  };
})();
