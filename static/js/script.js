const nav = document.getElementById('nav');
const btn = document.querySelector('.menu-btn');
if (btn && nav) {
  btn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open);
  });
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false');
  }));
}
const links = [...document.querySelectorAll('nav a[data-s]')];
const secs = links.map(a => document.getElementById(a.dataset.s));
if (secs.every(Boolean)) {
  addEventListener('scroll', () => {
    const y = scrollY + 140; let i = 0;
    secs.forEach((s, k) => { if (s.offsetTop <= y) i = k; });
    links.forEach((a, k) => a.classList.toggle('on', k === i));
  }, { passive: true });
}