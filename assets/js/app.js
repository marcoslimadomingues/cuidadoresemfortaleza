(function () {
  var body = document.body, GA = body.dataset.ga, KEY = 'consent_v1';
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  var AI = /chatgpt\.com|openai\.com|perplexity\.ai|gemini\.google|copilot\.microsoft|claude\.ai|you\.com|bing\.com\/chat/i;
  var ref = document.referrer || '';
  var base = {
    page_type: body.dataset.pageType, page_path: body.dataset.pagePath,
    ai_referrer: AI.test(ref) ? 'yes' : 'no',
    source_hint: (new URLSearchParams(location.search).get('utm_source') || '')
  };

  function track(name, extra) {
    var p = Object.assign({}, base, extra || {});
    dataLayer.push(Object.assign({ event: name }, p));
    if (window.__gaOn) gtag('event', name, p);
  }

  function loadGA() {
    if (!GA || window.__gaOn) return;
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA; document.head.appendChild(s);
    gtag('js', new Date()); gtag('config', GA, { anonymize_ip: true }); window.__gaOn = true;
    if (body.dataset.pageType === 'service') track('service_view', { service: base.page_path });
  }

  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  var box = document.getElementById('consent'), c = read();
  if (c === 'yes') loadGA();
  else if (!c && GA && box) box.hidden = false;
  if (box) box.addEventListener('click', function (e) {
    var v = e.target.getAttribute && e.target.getAttribute('data-consent'); if (!v) return;
    store(v); box.hidden = true; if (v === 'yes') loadGA();
  });

  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-event]'); if (!a) return;
    var ev = a.getAttribute('data-event'), where = a.getAttribute('data-where') || '';
    track(ev, { where: where });
    if (ev !== 'cta_click') track('cta_click', { where: where, kind: ev });
  });

  var form = document.querySelectorAll('[data-lead-form]');
  Array.prototype.forEach.call(form, function (f) {
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var d = new FormData(f);
      if (!d.get('nome') || !d.get('whatsapp') || !f.querySelector('[name=consent]').checked) {
        var old = f.querySelector('.err'); if (old) old.remove();
        var m = document.createElement('p'); m.className = 'err'; m.setAttribute('role', 'alert');
        m.textContent = 'Preencha nome, WhatsApp e aceite o consentimento.'; f.appendChild(m); return;
      }
      var msg = 'Olá! Gostaria de solicitar atendimento.\nNome: ' + d.get('nome') + '\nWhatsApp: ' + d.get('whatsapp') +
        '\nCidade: ' + d.get('cidade') + '\nTipo de cuidado: ' + d.get('tipo') + '\nPeríodo: ' + d.get('periodo');
      var num = document.querySelector('a[href^="https://wa.me/"]').href.split('wa.me/')[1].split('?')[0];
      track('form_submit', { tipo: d.get('tipo'), cidade: d.get('cidade') });
      track('quote_request', { tipo: d.get('tipo'), cidade: d.get('cidade') });
      window.open('https://wa.me/' + num + '?text=' + encodeURIComponent(msg), '_blank', 'noopener');
    });
  });

  var q = document.querySelector('[data-blog-search]');
  if (q) q.addEventListener('input', function () {
    var t = q.value.trim().toLowerCase(), n = 0;
    document.querySelectorAll('.post').forEach(function (p) {
      var ok = !t || p.dataset.title.indexOf(t) > -1; p.style.display = ok ? '' : 'none'; if (ok) n++;
    });
    document.getElementById('none').hidden = n > 0;
  });
})();
