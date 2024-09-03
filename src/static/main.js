(function() {
  let longPressTimeout;
  const button = document.getElementById('button-garage');

  const pressRequest = function() {
    const http = new XMLHttpRequest();

    http.open('GET', '/pressed');
    http.send();
  };

  const buttonHandler = function(event) {
    event.preventDefault();
    button.classList.add('pressed');

    longPressTimeout = setTimeout(pressRequest, 500);
  };

  const buttonReleaseHandler = function() {
    clearTimeout(longPressTimeout);
    button.classList.remove('pressed');
  };

  button.addEventListener('touchstart', buttonHandler);
  button.addEventListener('mousedown', buttonHandler);

  button.addEventListener('touchend', buttonReleaseHandler);
  button.addEventListener('mouseup', buttonReleaseHandler);
})();
