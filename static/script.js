const cards = document.querySelectorAll('.card');
const status = document.getElementById('status');
const statusText = document.getElementById('statusText');
const spinner = document.getElementById('spinner');

function show(message, spinning, ok) {
  status.hidden = false;
  status.classList.toggle('ok', Boolean(ok));
  spinner.hidden = !spinning;
  statusText.textContent = message;
}

async function run(mode, card) {
  cards.forEach(c => c.disabled = true);
  show('Waiting for you to choose a folder...', true, false);

  try {
    const response = await fetch('/organize/' + mode, { method: 'POST' });
    const data = await response.json();

    if (data.status === 'done') {
      const label = data.count === 1 ? 'file' : 'files';
      show(`Organized ${data.count} ${label} in ${data.folder}`, false, true);
    } else if (data.status === 'cancelled') {
      show('No folder selected', false, false);
    } else if (data.status === 'ai_limit') {
      if (data.count === 0) {
        show('AI limit reached. Wait about a minute and try again.', false, false);
      } else {
        const label = data.count === 1 ? 'file' : 'files';
        show(`AI limit reached after sorting ${data.count} ${label}. Wait a minute and run again for the rest.`, false, false);
      }
    } else if (data.status === 'ai_unavailable') {
      if (data.count === 0) {
        show('No internet connection, could not reach the AI service', false, false);
      } else {
        const label = data.count === 1 ? 'file' : 'files';
        show(`Connection dropped after sorting ${data.count} ${label}. The rest were left untouched.`, false, false);
      }
    } else {
      show('That mode is not available yet', false, false);
    }
  } catch (error) {
    show('Could not reach the organizer', false, false);
  }

  cards.forEach(c => c.disabled = c.dataset.mode !== 'extension' && c.dataset.mode !== 'ai' && c.dataset.mode !== 'both');
}

cards.forEach(card => {
  card.addEventListener('click', () => {
    if (!card.disabled) run(card.dataset.mode, card);
  });
});

async function loadInfo() {
  try {
    const response = await fetch('/info');
    const data = await response.json();

    document.getElementById('modelList').innerHTML = data.models
      .map((m, i) => `<li><span class="rank">${i + 1}</span>${m}</li>`)
      .join('');

    document.getElementById('categoryList').innerHTML = data.categories
      .map(c => `<span>${c}</span>`)
      .join('');

    document.getElementById('batchHint').textContent = `${data.batch_size} files per request`;
  } catch (error) {}
}

loadInfo();

document.getElementById('themeToggle').addEventListener('click', () => {
  const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
});
