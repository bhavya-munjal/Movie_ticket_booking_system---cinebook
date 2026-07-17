function showToast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `show ${type}`;
  setTimeout(() => t.className = '', 3000);
}

function confirmDialog(msg, onConfirm) {
  const overlay = document.getElementById('confirm-modal');
  document.getElementById('confirm-msg').textContent = msg;
  overlay.classList.add('open');
  document.getElementById('confirm-yes').onclick = () => {
    overlay.classList.remove('open');
    onConfirm();
  };
  document.getElementById('confirm-no').onclick = () => overlay.classList.remove('open');
}

async function apiPost(url, data) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return r.json();
}
