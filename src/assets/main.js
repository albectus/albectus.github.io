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

  // Форма обратной связи: данные не отправляются на сервер,
  // а передаются в почтовую программу пользователя (mailto).
  var form = document.getElementById('contact-form');
  if (!form) return;
  var email = form.getAttribute('data-email');
  var msg = document.getElementById('form-msg');

  function show(text, type) {
    msg.textContent = text;
    msg.className = 'form-msg ' + type;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!email) return;
    var name = form.elements.name.value.trim();
    var contact = form.elements.contact.value.trim();
    var text = form.elements.message.value.trim();
    var consent = form.elements.consent.checked;

    if (!name || !contact || !text) {
      show('Заполните, пожалуйста, все поля формы.', 'err');
      return;
    }
    if (!consent) {
      show('Для отправки обращения необходимо согласие на обработку персональных данных.', 'err');
      return;
    }

    var subject = 'Обращение с сайта — ' + name;
    var body = 'Имя: ' + name + '\n' +
               'Контакт для связи: ' + contact + '\n\n' +
               'Сообщение:\n' + text + '\n';
    window.location.href = 'mailto:' + email +
      '?subject=' + encodeURIComponent(subject) +
      '&body=' + encodeURIComponent(body);
    show('Открывается ваша почтовая программа с подготовленным письмом. Отправьте его, чтобы мы получили обращение. Если программа не открылась, напишите нам на ' + email + '.', 'ok');
  });
})();
