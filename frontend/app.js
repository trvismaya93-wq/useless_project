// =========================================================================
// WakeVerify - Core Client Application & Alarm Engine
// =========================================================================

let audioCtx = null;
let sirenInterval = null;
let sirenOsc1 = null;
let sirenOsc2 = null;
let sirenGain = null;
let isSirenPlaying = false;

let scheduledAlarms = [];
let currentRingingAlarm = null;
let activeTab = 'reason'; // 'reason' or 'photo'
let cameraStream = null;
let capturedBlob = null;
let recognition = null;

// Verification flags for "both" mode
let reasonPassed = false;
let photoPassed = false;

// -------------------------------------------------------------------------
// 1. Audio Siren Synthesizer (Web Audio API)
// -------------------------------------------------------------------------
function initAudio() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
}

function startAlarmSound() {
  initAudio();
  if (!audioCtx || isSirenPlaying) return;

  try {
    isSirenPlaying = true;
    sirenGain = audioCtx.createGain();
    sirenGain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    sirenGain.connect(audioCtx.destination);

    sirenOsc1 = audioCtx.createOscillator();
    sirenOsc2 = audioCtx.createOscillator();

    sirenOsc1.type = 'sawtooth';
    sirenOsc2.type = 'square';

    sirenOsc1.connect(sirenGain);
    sirenOsc2.connect(sirenGain);

    sirenOsc1.start();
    sirenOsc2.start();

    // Frequency modulation cycle for loud alternating siren
    let high = true;
    sirenInterval = setInterval(() => {
      if (!isSirenPlaying || !audioCtx) return;
      const now = audioCtx.currentTime;
      const freq1 = high ? 960 : 720;
      const freq2 = high ? 1280 : 850;
      sirenOsc1.frequency.setValueAtTime(freq1, now);
      sirenOsc2.frequency.setValueAtTime(freq2, now);
      high = !high;
    }, 320);

  } catch (err) {
    console.error('Web Audio Siren Error:', err);
  }
}

function stopAlarmSound() {
  if (sirenInterval) {
    clearInterval(sirenInterval);
    sirenInterval = null;
  }
  if (sirenOsc1) {
    try { sirenOsc1.stop(); sirenOsc1.disconnect(); } catch (e) {}
    sirenOsc1 = null;
  }
  if (sirenOsc2) {
    try { sirenOsc2.stop(); sirenOsc2.disconnect(); } catch (e) {}
    sirenOsc2 = null;
  }
  if (sirenGain) {
    try { sirenGain.disconnect(); } catch (e) {}
    sirenGain = null;
  }
  isSirenPlaying = false;
}

// -------------------------------------------------------------------------
// 2. Digital Clock & Schedule Polling
// -------------------------------------------------------------------------
function updateClock() {
  const now = new Date();
  
  // Format Time
  let hours = now.getHours();
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // 0 becomes 12
  const formattedHours = String(hours).padStart(2, '0');

  document.getElementById('clockTime').textContent = `${formattedHours}:${minutes}:${seconds}`;
  document.getElementById('clockAmPm').textContent = ampm;

  // Format Date
  const options = { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' };
  document.getElementById('clockDate').textContent = now.toLocaleDateString(undefined, options);

  // Check Alarms
  checkAlarms(now);
}

function checkAlarms(now) {
  const currentHH = String(now.getHours()).padStart(2, '0');
  const currentMM = String(now.getMinutes()).padStart(2, '0');
  const currentTimeStr = `${currentHH}:${currentMM}`;
  const currentSeconds = now.getSeconds();

  if (currentRingingAlarm) return; // Already ringing

  for (const alarm of scheduledAlarms) {
    if (alarm.is_active && alarm.time === currentTimeStr && currentSeconds === 0) {
      ringAlarm(alarm);
      break;
    }
  }
}

// -------------------------------------------------------------------------
// 3. Ringing Alarm Interlock Controls
// -------------------------------------------------------------------------
function triggerImmediateAlarm() {
  initAudio();
  const testAlarm = {
    id: 'test-' + Date.now(),
    label: '⚡ Test Instant Alarm',
    reason: 'Hit the gym and study Chapter 4 with high focus',
    dismiss_mode: 'either',
    photo_target: 'Running shoes or desk setup',
    time: 'NOW'
  };
  ringAlarm(testAlarm);
}

function ringAlarm(alarm) {
  currentRingingAlarm = alarm;
  reasonPassed = false;
  photoPassed = false;

  // Start unstoppable siren
  startAlarmSound();

  // Populate Ringing Screen UI
  document.getElementById('ringingAlarmLabel').textContent = alarm.label || 'Accountability Alarm';
  document.getElementById('ringingAlarmReasonDisplay').innerHTML = `Reason: <span class="text-indigo-300 font-semibold italic">"${alarm.reason}"</span>`;
  document.getElementById('requiredTargetLabel').textContent = alarm.photo_target || 'Target Object';

  let reqText = 'Reason OR Photo';
  if (alarm.dismiss_mode === 'reason') reqText = 'Reason Only';
  if (alarm.dismiss_mode === 'photo') reqText = 'Photo Only';
  if (alarm.dismiss_mode === 'both') reqText = 'Must Pass BOTH';
  document.getElementById('ringingRequirementPill').textContent = reqText;

  // Clear previous input/state
  document.getElementById('userExplanationInput').value = '';
  document.getElementById('alarmFeedbackBox').classList.add('hidden');
  resetCameraUI();

  // Show Overlay
  document.getElementById('alarmOverlay').classList.remove('hidden');

  // Select initial tab based on mode
  if (alarm.dismiss_mode === 'photo') {
    switchAlarmTab('photo');
  } else {
    switchAlarmTab('reason');
  }
}

function switchAlarmTab(tab) {
  activeTab = tab;
  const tabReasonBtn = document.getElementById('tabReasonBtn');
  const tabPhotoBtn = document.getElementById('tabPhotoBtn');
  const contentReason = document.getElementById('tabContentReason');
  const contentPhoto = document.getElementById('tabContentPhoto');

  if (tab === 'reason') {
    tabReasonBtn.className = 'flex-1 py-2.5 px-4 font-bold text-sm text-center border-b-2 border-indigo-500 text-indigo-400 transition flex items-center justify-center gap-2';
    tabPhotoBtn.className = 'flex-1 py-2.5 px-4 font-bold text-sm text-center border-b-2 border-transparent text-gray-400 hover:text-gray-200 transition flex items-center justify-center gap-2';
    contentReason.classList.remove('hidden');
    contentPhoto.classList.add('hidden');
  } else {
    tabPhotoBtn.className = 'flex-1 py-2.5 px-4 font-bold text-sm text-center border-b-2 border-rose-500 text-rose-400 transition flex items-center justify-center gap-2';
    tabReasonBtn.className = 'flex-1 py-2.5 px-4 font-bold text-sm text-center border-b-2 border-transparent text-gray-400 hover:text-gray-200 transition flex items-center justify-center gap-2';
    contentPhoto.classList.remove('hidden');
    contentReason.classList.add('hidden');
  }
}

function showAlarmFeedback(success, message, engine) {
  const box = document.getElementById('alarmFeedbackBox');
  box.classList.remove('hidden');

  if (success) {
    box.className = 'mt-4 p-3.5 rounded-xl text-xs font-semibold bg-emerald-950/80 border border-emerald-600 text-emerald-300 flex items-start gap-2 shadow-lg';
    box.innerHTML = `
      <span class="text-emerald-400 text-base">✅</span>
      <div>
        <p class="font-bold text-emerald-200">VERIFICATION SUCCESSFUL</p>
        <p class="mt-0.5 text-emerald-300">${message}</p>
        ${engine ? `<p class="mt-1 text-[10px] text-emerald-400/80">Verified by: ${engine}</p>` : ''}
      </div>
    `;
  } else {
    box.className = 'mt-4 p-3.5 rounded-xl text-xs font-semibold bg-red-950/80 border border-red-600 text-red-300 flex items-start gap-2 shadow-lg';
    box.innerHTML = `
      <span class="text-red-400 text-base">❌</span>
      <div>
        <p class="font-bold text-red-200">VERIFICATION REJECTED — ALARM STILL RINGING</p>
        <p class="mt-0.5 text-red-300">${message}</p>
      </div>
    `;
  }
}

function evaluateDismissalConditions() {
  const mode = currentRingingAlarm.dismiss_mode;
  let canDismiss = false;

  if (mode === 'either' && (reasonPassed || photoPassed)) {
    canDismiss = true;
  } else if (mode === 'reason' && reasonPassed) {
    canDismiss = true;
  } else if (mode === 'photo' && photoPassed) {
    canDismiss = true;
  } else if (mode === 'both' && reasonPassed && photoPassed) {
    canDismiss = true;
  }

  if (canDismiss) {
    // STOP UNSTOPPABLE SIREN!
    stopAlarmSound();
    stopCamera();

    setTimeout(() => {
      document.getElementById('alarmOverlay').classList.add('hidden');
      currentRingingAlarm = null;
      loadHistory();
      loadAlarms();
    }, 1800);
  } else if (mode === 'both') {
    // Still needs other half
    if (reasonPassed && !photoPassed) {
      showAlarmFeedback(true, "Reason verified! Now submit Photo Proof to turn off the alarm completely.");
      switchAlarmTab('photo');
    } else if (photoPassed && !reasonPassed) {
      showAlarmFeedback(true, "Photo verified! Now explain your Reason to turn off the alarm completely.");
      switchAlarmTab('reason');
    }
  }
}

// -------------------------------------------------------------------------
// 4. Verification API Calls
// -------------------------------------------------------------------------
async function submitReasonVerification() {
  const explanation = document.getElementById('userExplanationInput').value.trim();
  if (!explanation) {
    showAlarmFeedback(false, "Please type or speak your reason first!");
    return;
  }

  const spinner = document.getElementById('reasonSpinner');
  const btn = document.getElementById('verifyReasonBtn');
  spinner.classList.remove('hidden');
  btn.disabled = true;

  try {
    const res = await fetch('/api/verify/reason', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        alarm_id: currentRingingAlarm?.id,
        alarm_reason: currentRingingAlarm?.reason || '',
        user_explanation: explanation
      })
    });

    const data = await res.json();
    if (data.success) {
      reasonPassed = true;
      showAlarmFeedback(true, data.feedback, data.engine);
      evaluateDismissalConditions();
    } else {
      showAlarmFeedback(false, data.feedback);
    }
  } catch (err) {
    showAlarmFeedback(false, "Network error validating reason: " + err.message);
  } finally {
    spinner.classList.add('hidden');
    btn.disabled = false;
  }
}

async function submitPhotoVerification() {
  if (!capturedBlob) {
    showAlarmFeedback(false, "Please take a photo or upload an image file first!");
    return;
  }

  const spinner = document.getElementById('photoSpinner');
  const btn = document.getElementById('verifyPhotoBtn');
  const scannerLine = document.getElementById('scannerLine');
  spinner.classList.remove('hidden');
  scannerLine.classList.remove('hidden');
  btn.disabled = true;

  try {
    const formData = new FormData();
    formData.append('target_description', currentRingingAlarm?.photo_target || 'Target Object');
    formData.append('file', capturedBlob, 'proof.jpg');

    const res = await fetch('/api/verify/photo', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    if (data.success) {
      photoPassed = true;
      showAlarmFeedback(true, `${data.feedback} (Detected: ${data.detected})`, data.engine);
      evaluateDismissalConditions();
    } else {
      showAlarmFeedback(false, `${data.feedback} (Detected: ${data.detected || 'Unidentified'})`);
    }
  } catch (err) {
    showAlarmFeedback(false, "Network error verifying image: " + err.message);
  } finally {
    spinner.classList.add('hidden');
    scannerLine.classList.add('hidden');
    btn.disabled = false;
  }
}

// -------------------------------------------------------------------------
// 5. Speech Recognition & Camera Handlers
// -------------------------------------------------------------------------
function startSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. You can type your reason directly!");
    return;
  }

  if (recognition) {
    recognition.abort();
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  const micBtn = document.getElementById('micBtn');
  micBtn.classList.add('bg-red-600', 'text-white', 'animate-pulse');

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById('userExplanationInput').value = transcript;
  };

  recognition.onerror = (e) => {
    console.warn("Speech error:", e);
  };

  recognition.onend = () => {
    micBtn.classList.remove('bg-red-600', 'text-white', 'animate-pulse');
  };

  recognition.start();
}

async function startCamera() {
  const video = document.getElementById('cameraVideo');
  const placeholder = document.getElementById('cameraPlaceholder');
  const imgPreview = document.getElementById('imagePreview');
  const btnStart = document.getElementById('btnStartCamera');
  const btnCapture = document.getElementById('btnCapture');

  imgPreview.classList.add('hidden');
  placeholder.classList.add('hidden');
  video.classList.remove('hidden');

  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
    });
    video.srcObject = cameraStream;
    btnStart.classList.add('hidden');
    btnCapture.classList.remove('hidden');
  } catch (err) {
    console.error("Camera access failed:", err);
    alert("Camera permission denied or camera not found. You can upload an image file instead!");
    resetCameraUI();
  }
}

function captureSnapshot() {
  const video = document.getElementById('cameraVideo');
  const canvas = document.getElementById('photoCanvas');
  const imgPreview = document.getElementById('imagePreview');
  const btnStart = document.getElementById('btnStartCamera');
  const btnCapture = document.getElementById('btnCapture');

  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob((blob) => {
    capturedBlob = blob;
    imgPreview.src = URL.createObjectURL(blob);
    imgPreview.classList.remove('hidden');
    video.classList.add('hidden');
    stopCamera();
    btnCapture.classList.add('hidden');
    btnStart.classList.remove('hidden');
    btnStart.textContent = '🔄 Retake Camera';
  }, 'image/jpeg', 0.9);
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  capturedBlob = file;
  const imgPreview = document.getElementById('imagePreview');
  const placeholder = document.getElementById('cameraPlaceholder');
  const video = document.getElementById('cameraVideo');

  stopCamera();
  video.classList.add('hidden');
  placeholder.classList.add('hidden');
  imgPreview.src = URL.createObjectURL(file);
  imgPreview.classList.remove('hidden');
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
}

function resetCameraUI() {
  stopCamera();
  capturedBlob = null;
  document.getElementById('cameraVideo').classList.add('hidden');
  document.getElementById('imagePreview').classList.add('hidden');
  document.getElementById('cameraPlaceholder').classList.remove('hidden');
  document.getElementById('btnCapture').classList.add('hidden');
  document.getElementById('btnStartCamera').classList.remove('hidden');
  document.getElementById('btnStartCamera').textContent = '📹 Open Camera';
}

// -------------------------------------------------------------------------
// 6. Alarms & History Management
// -------------------------------------------------------------------------
async function loadStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    const pill = document.getElementById('engineStatusPill');
    const text = document.getElementById('engineStatusText');
    pill.classList.remove('hidden');
    text.textContent = data.has_api_key ? 'Gemini AI Active' : 'Local Heuristic Mode';
  } catch (e) {}
}

async function loadAlarms() {
  try {
    const res = await fetch('/api/alarms');
    scheduledAlarms = await res.json();
    renderAlarmsList();
  } catch (err) {
    console.error("Error loading alarms:", err);
  }
}

function renderAlarmsList() {
  const container = document.getElementById('alarmsList');
  const badge = document.getElementById('alarmCountBadge');
  const notice = document.getElementById('nextAlarmNotice');

  badge.textContent = `${scheduledAlarms.length} active`;

  if (scheduledAlarms.length === 0) {
    container.innerHTML = `<p class="text-sm text-gray-500 text-center py-8">No scheduled alarms. Create one above!</p>`;
    notice.innerHTML = `<span class="inline-block w-2 h-2 rounded-full bg-indigo-500"></span> No alarms currently scheduled`;
    return;
  }

  // Find next alarm
  notice.innerHTML = `<span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> ${scheduledAlarms.length} smart alarm(s) armed & ready`;

  container.innerHTML = scheduledAlarms.map(a => {
    let modeBadge = '⚡ Reason or Photo';
    if (a.dismiss_mode === 'reason') modeBadge = '🧠 Reason Only';
    if (a.dismiss_mode === 'photo') modeBadge = '📸 Photo Only';
    if (a.dismiss_mode === 'both') modeBadge = '🔒 Hardcore (Both)';

    return `
      <div class="p-4 rounded-xl bg-gray-900/80 border border-gray-800 hover:border-gray-700 transition flex items-center justify-between">
        <div class="space-y-1">
          <div class="flex items-center gap-3">
            <span class="text-2xl font-black font-mono text-white tracking-tight">${a.time}</span>
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-900/60 border border-indigo-700/50 text-indigo-300">${modeBadge}</span>
          </div>
          <p class="text-xs font-semibold text-gray-200">${a.label}</p>
          <p class="text-xs text-gray-400 italic">"${a.reason}"</p>
          ${a.photo_target ? `<p class="text-[11px] text-rose-400">Target Photo: ${a.photo_target}</p>` : ''}
        </div>
        <div class="flex items-center gap-2">
          <button onclick="ringAlarm(${JSON.stringify(a).replace(/"/g, '&quot;')})" title="Test this alarm now" class="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition">
            ▶️
          </button>
          <button onclick="deleteAlarm('${a.id}')" title="Delete alarm" class="p-2 rounded-lg bg-gray-800 hover:bg-red-900/40 text-gray-400 hover:text-red-400 transition">
            🗑️
          </button>
        </div>
      </div>
    `;
  }).join('');
}

async function handleCreateAlarm(e) {
  e.preventDefault();
  initAudio();

  const time = document.getElementById('alarmTime').value;
  const label = document.getElementById('alarmLabel').value.trim();
  const reason = document.getElementById('alarmReason').value.trim();
  const dismiss_mode = document.getElementById('dismissMode').value;
  const photo_target = document.getElementById('photoTarget').value.trim();

  try {
    const res = await fetch('/api/alarms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time, label, reason, dismiss_mode, photo_target, is_active: true })
    });
    if (res.ok) {
      await loadAlarms();
      document.getElementById('alarmLabel').value = '';
      document.getElementById('alarmReason').value = '';
    }
  } catch (err) {
    alert("Error scheduling alarm: " + err.message);
  }
}

async function deleteAlarm(id) {
  try {
    await fetch(`/api/alarms/${id}`, { method: 'DELETE' });
    await loadAlarms();
  } catch (err) {
    console.error(err);
  }
}

async function loadHistory() {
  try {
    const res = await fetch('/api/history');
    const history = await res.json();
    const container = document.getElementById('historyList');
    document.getElementById('statTotalProofs').textContent = history.length;

    if (history.length === 0) {
      container.innerHTML = `<p class="text-sm text-gray-500 text-center py-8">No verified wakeups recorded yet.</p>`;
      return;
    }

    container.innerHTML = history.map(item => {
      const dt = new Date(item.timestamp);
      const timeStr = dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const dateStr = dt.toLocaleDateString([], { month: 'short', day: 'numeric' });

      return `
        <div class="p-3.5 rounded-xl bg-gray-900/70 border border-gray-800/80 text-xs space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="font-bold text-emerald-400 flex items-center gap-1.5">
              <span>✅</span> ${item.method}
            </span>
            <span class="text-[11px] text-gray-500 font-mono">${dateStr} ${timeStr}</span>
          </div>
          ${item.proof_text ? `<p class="text-gray-300 italic font-mono bg-gray-950/60 p-2 rounded">"${item.proof_text}"</p>` : ''}
          ${item.target ? `<p class="text-gray-300">Target: <span class="text-indigo-300">${item.target}</span></p>` : ''}
          ${item.detected ? `<p class="text-gray-400 text-[11px]">AI Detected: <span class="text-gray-200">${item.detected}</span></p>` : ''}
          <p class="text-[10px] text-gray-500">${item.engine || 'AI Engine'}</p>
        </div>
      `;
    }).join('');

  } catch (err) {
    console.error("Error loading history:", err);
  }
}

// -------------------------------------------------------------------------
// 7. Settings & Presets
// -------------------------------------------------------------------------
function applyPreset(time, label, reason, photoTarget, mode) {
  document.getElementById('alarmTime').value = time;
  document.getElementById('alarmLabel').value = label;
  document.getElementById('alarmReason').value = reason;
  document.getElementById('dismissMode').value = mode;
  document.getElementById('photoTarget').value = photoTarget;
  togglePhotoTargetInput();
}

function togglePhotoTargetInput() {
  const mode = document.getElementById('dismissMode').value;
  const container = document.getElementById('photoTargetContainer');
  if (mode === 'reason') {
    container.classList.add('opacity-40', 'pointer-events-none');
  } else {
    container.classList.remove('opacity-40', 'pointer-events-none');
  }
}

function openSettingsModal() {
  document.getElementById('settingsModal').classList.remove('hidden');
}

function closeSettingsModal() {
  document.getElementById('settingsModal').classList.add('hidden');
}

async function saveSettings() {
  const key = document.getElementById('geminiApiKeyInput').value.trim();
  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gemini_api_key: key })
    });
    const data = await res.json();
    alert(data.message || "Settings saved!");
    closeSettingsModal();
    loadStatus();
  } catch (err) {
    alert("Failed to save settings: " + err.message);
  }
}

// -------------------------------------------------------------------------
// 8. Initialization
// -------------------------------------------------------------------------
window.addEventListener('DOMContentLoaded', () => {
  // Set default alarm time to current time + 1 minute
  const d = new Date();
  d.setMinutes(d.getMinutes() + 1);
  const defHH = String(d.getHours()).padStart(2, '0');
  const defMM = String(d.getMinutes()).padStart(2, '0');
  document.getElementById('alarmTime').value = `${defHH}:${defMM}`;

  updateClock();
  setInterval(updateClock, 1000);

  loadStatus();
  loadAlarms();
  loadHistory();

  // Unlock AudioContext on first user interaction
  document.body.addEventListener('click', () => initAudio(), { once: true });
});
