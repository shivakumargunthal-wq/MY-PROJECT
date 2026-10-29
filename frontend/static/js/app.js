const $ = (selector) => document.querySelector(selector);
const setup = $('#setup');
const testArea = $('#test-area');
const results = $('#results');
const loading = $('#loading');
const errorBanner = $('#error-banner');
const input = $('#typing-input');
const passageElement = $('#passage');

let current = null;
let timerHandle = null;
let submitting = false;

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
}
function clearError() { errorBanner.hidden = true; }
function setLoading(value) { loading.hidden = !value; $('#start-button').disabled = value; }

async function api(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({ error: 'The server returned an invalid response.' }));
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
}

async function startTest() {
  clearError();
  setLoading(true);
  const difficulty = $('input[name="difficulty"]:checked').value;
  const duration = Number($('input[name="duration"]:checked').value);
  try {
    const data = await api('/api/test/start', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ difficulty, duration })
    });
    current = { ...data, clientStart: Date.now() / 1000 }; // wall-clock countdown anchored to server
    input.value = '';
    setup.hidden = true;
    results.hidden = true;
    testArea.hidden = false;
    renderPassage();
    updateLiveStats();
    input.focus({ preventScroll: true });
    beginTimer();
  } catch (error) {
    showError(error.message || 'Unable to start the test. Please try again.');
  } finally { setLoading(false); }
}

function beginTimer() {
  clearInterval(timerHandle);
  submitting = false;
  timerHandle = setInterval(() => {
    if (!current || submitting) return;
    const elapsed = Date.now() / 1000 - current.clientStart;
    let remaining = Math.max(0, current.duration - elapsed);
    const rounded = Math.ceil(remaining);
    $('#timer').textContent = `${Math.floor(rounded / 60)}:${String(rounded % 60).padStart(2, '0')}`;
    $('#progress').style.width = `${Math.max(0, remaining / current.duration * 100)}%`;
    updateLiveStats();
    if (remaining <= 0) finishTest(false);
  }, 100);
}

function renderPassage() {
  if (!current) return;
  const typed = input.value;
  passageElement.innerHTML = current.passage.split('').map((character, index) => {
    let className = '';
    if (index < typed.length) className = typed[index] === character ? 'correct' : 'incorrect';
    else if (index === typed.length) className = 'current';
    const safe = character === ' ' ? '&nbsp;' : character.replace(/[&<>]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;' }[c]));
    return `<span class="${className}">${safe}</span>`;
  }).join('') + (typed.length >= current.passage.length ? '<span class="current"> </span>' : '');
}

function compareLive(typed) {
  let correct = 0;
  for (let i = 0; i < typed.length; i++) {
    if (i < current.passage.length && typed[i] === current.passage[i]) correct++;
  }
  const incorrect = typed.length - correct;
  return { correct, incorrect };
}

function updateLiveStats() {
  if (!current) return;
  const typed = input.value;
  const counts = compareLive(typed);
  const elapsedMinutes = Math.max(1, (Date.now() / 1000 - current.clientStart)) / 60;
  const gross = (typed.length / 5) / elapsedMinutes;
  $('#live-wpm').textContent = Math.max(0, Math.round(gross));
  $('#live-accuracy').textContent = typed.length ? `${Math.round(counts.correct / typed.length * 100)}%` : '100%';
  $('#correct-count').textContent = counts.correct;
  $('#incorrect-count').textContent = counts.incorrect;
  renderPassage();
}

async function finishTest(completedByTyping) {
  if (!current || submitting) return;
  submitting = true;
  clearInterval(timerHandle);
  setLoading(true);
  clearError();
  try {
    const data = await api('/api/test/finish', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ test_id: current.test_id, typed_text: input.value })
    });
    displayResults(data.result);
  } catch (error) {
    showError(`${error.message} You can retry submission; your text is preserved.`);
    submitting = false;
    if (completedByTyping) {
      beginTimer(); // allow another automatic submission attempt before server expiry
    }
  } finally { setLoading(false); }
}

function displayResults(result) {
  testArea.hidden = true;
  results.hidden = false;
  $('#result-wpm').textContent = Math.round(result.net_wpm);
  $('#result-accuracy').textContent = `${result.accuracy.toFixed(1)}%`;
  $('#result-gross').textContent = Math.round(result.gross_wpm);
  $('#result-errors').textContent = result.incorrect_characters;
  $('#feedback').textContent = result.feedback;
  results.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

input.addEventListener('input', () => {
  updateLiveStats();
  if (!current) return;
  if (input.value.trim() === current.passage.trim()) finishTest(true);
});
$('#start-button').addEventListener('click', startTest);
$('#restart-button').addEventListener('click', startTest);
$('#try-again').addEventListener('click', () => {
  results.hidden = true;
  setup.hidden = false;
  setup.scrollIntoView({ behavior: 'smooth' });
});
$('#return-home').addEventListener('click', () => {
  results.hidden = true;
  setup.hidden = false;
  document.querySelector('#test').scrollIntoView({ behavior: 'smooth' });
});
