(function() {
  document.getElementById('button-garage')
    .addEventListener('click', function(e) {
      const http = new XMLHttpRequest();

      http.open('GET', '/pressed');
      http.send();
    });
})();
