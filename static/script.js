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
    } else {
      show('That mode is not available yet', false, false);
    }
  } catch (error) {
    show('Could not reach the organizer', false, false);
  }

  cards.forEach(c => c.disabled = c.dataset.mode !== 'extension' && c.dataset.mode !== 'ai');
}

cards.forEach(card => {
  card.addEventListener('click', () => {
    if (!card.disabled) run(card.dataset.mode, card);
  });
});
