// Click-to-enlarge on the /releases/ pages. Each screenshot is already a link to its full image, so with no script it
// still opens; this upgrades it to a dialog: Esc closes it (<dialog>'s own), and focus goes back to the screenshot.
(() => {
  const links = document.querySelectorAll('.rn-shot a');
  if (!links.length || !window.HTMLDialogElement) return;

  const big = document.createElement('dialog');
  big.className = 'rn-big';
  const image = document.createElement('img');
  const caption = document.createElement('p');
  const close = document.createElement('button');
  close.type = 'button';
  close.textContent = 'Close';
  close.addEventListener('click', () => big.close());
  big.addEventListener('click', (event) => { if (event.target === big) big.close(); });
  big.append(image, caption, close);
  document.body.append(big);

  let opener = null;
  big.addEventListener('close', () => { if (opener) opener.focus(); opener = null; });

  links.forEach((link) => link.addEventListener('click', (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey) return;   // a new tab, as any link
    event.preventDefault();
    const shot = link.querySelector('img');
    image.src = shot.currentSrc || shot.src;   // the light or dark one on the page
    image.alt = shot.alt;
    caption.textContent = shot.alt;
    big.setAttribute('aria-label', shot.alt);
    opener = link;
    big.showModal();
    close.focus();
  }));
})();
