(function() {
  const form = document.getElementById('form-setup');
  const btnSubmit = document.getElementById('btn-submit');
  const message = document.getElementById('message');

  form.addEventListener('submit', function(e) {
    e.preventDefault();

    const hiddenClass = 'setup-hidden';
    const http = new XMLHttpRequest();

    message.classList.add(hiddenClass);

    if (form.password.value !== form.confirm.value) {
      message.innerText = 'Specified passwords do not match.';
      message.classList.remove(hiddenClass);

      return;
    }

    btnSubmit.classList.add(hiddenClass);

    http.open('POST', '/save-pwd', true);
    http.setRequestHeader('Content-Type', 'application/json');
    http.onload = function() {
      message.innerText = http.status === 200
        ? 'Password has been saved! Please reboot your device for changes to take effect.'
        : 'Connection error! Please try again.';

      btnSubmit.classList.remove(hiddenClass);
      message.classList.remove(hiddenClass);

      form.reset();
    };

    const data = JSON.stringify({
      password: form.password.value,
    });

    http.send(data);
  });
})();
