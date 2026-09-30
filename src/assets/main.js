(function () {
  // Мобильное меню
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Форма обратной связи: отправка через сервис Web3Forms (api.web3forms.com),
  // который пересылает обращение на почту компании. Адрес почты на сайте не публикуется.
  var form = document.getElementById('contact-form');
  if (!form) return;
  var key = form.getAttribute('data-key');
  var msg = document.getElementById('form-msg');
  var btn = form.querySelector('button[type=submit]');

  function show(text, type) {
    msg.textContent = text;
    msg.className = 'form-msg ' + type;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!key) return;
    var name = form.elements.name.value.trim();
    var contact = form.elements.contact.value.trim();
    var text = form.elements.message.value.trim();

    if (!name || !contact || !text) {
      show('Заполните, пожалуйста, все поля формы.', 'err');
      return;
    }
    if (!form.elements.consent.checked) {
      show('Для отправки обращения необходимо согласие на обработку персональных данных.', 'err');
      return;
    }

    btn.disabled = true;
    show('Отправляем…', '');
    fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        access_key: key,
        subject: 'Обращение с сайта ООО «Альбектус» — ' + name,
        from_name: 'Сайт ООО «Альбектус»',
        'Имя': name,
        'Контакт для связи': contact,
        'Сообщение': text,
        'Согласие на обработку ПДн': 'дано',
        botcheck: form.elements.botcheck.checked
      })
    })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (data) {
        if (data && data.success) {
          form.reset();
          show('Спасибо! Обращение отправлено, мы свяжемся с вами.', 'ok');
        } else {
          show('Не удалось отправить обращение. Попробуйте ещё раз немного позже.', 'err');
        }
      })
      .catch(function () {
        show('Не удалось отправить обращение: проверьте подключение к интернету и попробуйте ещё раз.', 'err');
      })
      .then(function () { btn.disabled = false; });
  });
})();
