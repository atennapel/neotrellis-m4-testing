document.getElementById("start").addEventListener("click", init);

let ctx = null;
let master = null;
let active = new Set();

async function init() {
  ctx = new AudioContext();
  master = ctx.createGain();
  master.gain.value = 0.8;
  master.connect(ctx.destination);

  document.addEventListener("keydown", e => {
    const n = keyToNote(e.key);
    if (n >= 0) noteOn(n, 1);
  });
  document.addEventListener("keyup", e => {
    const n = keyToNote(e.key);
    if (n >= 0) noteOff(n);
  });

  const midiAccess = await navigator.requestMIDIAccess();
  for (const input of midiAccess.inputs.values()) {
    if (input.name === "Launchkey Mini MK4 25 MIDI") {
      input.onmidimessage = onMIDIMessage;
    }
  }

  function onMIDIMessage(event) {
    const data = event.data;
    if ((data[0] >= 144 && data[0] <= 159) || data[0] === 169) {
      const note = data[1];
      const vel = data[2];
      if (vel > 0) {
        noteOn(note, vel / 127);
      } else {
        noteOff(note);
      }
    } else if (data[0] >= 128 && data[0] <= 143) {
      const note = data[1];
      noteOff(note);
    } else if (data[0] !== 248) {
      // console.log(data);
    }
  }
}

function freq(note) {
  return 440 * Math.pow(2, (note - 69) / 12);
}

const notes = Array(128);

function adjustMaster() {
  const activeCount = active.size;
  const gain = activeCount > 0 ? 0.8 / Math.sqrt(activeCount) : 0.8;
  master.gain.setTargetAtTime(gain, ctx.currentTime, 0.01);
}

function noteOn(note, vel) {
  const now = ctx.currentTime;
  const vol = vel * 0.2;
  const nodes = notes[note];
  if (!nodes) {
    active.add(note);
    adjustMaster();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    notes[note] = { osc, gain };

    osc.type = "sine";
    osc.frequency.value = freq(note);

    gain.gain.value = 0;

    osc.connect(gain);
    gain.connect(master);

    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(vol, now + 0.01);
    osc.start(now);
  } else {
    const { gain } = nodes;
    gain.gain.cancelScheduledValues(now);
    gain.gain.setValueAtTime(gain.gain.value, now);
    gain.gain.linearRampToValueAtTime(vol, now + 0.01);
  }
}

function noteOff(note) {
  const nodes = notes[note];
  if (nodes) {
    active.delete(note);
    adjustMaster();
    notes[note] = null;
    const { osc, gain } = nodes;

    const now = ctx.currentTime;
    gain.gain.cancelScheduledValues(now);
    gain.gain.setValueAtTime(gain.gain.value, now);
    gain.gain.linearRampToValueAtTime(0, now + 0.05);
    osc.stop(now + 0.05);
  }
}

function keyToNote(k) {
  switch (k) {
    case "z": return 60;
    case "x": return 61;
    case "c": return 62;
    case "v": return 63;
    case "b": return 64;
    case "n": return 65;
    case "m": return 66;
    case ",": return 67;
    case ".": return 68;
    case "/": return 69;
    
    case "a": return 65;
    case "s": return 66;
    case "d": return 67;
    case "f": return 68;
    case "g": return 69;
    case "h": return 70;
    case "j": return 71;
    case "k": return 72;
    case "l": return 73;
    case ";": return 74;
    
    case "q": return 70;
    case "w": return 71;
    case "e": return 72;
    case "r": return 73;
    case "t": return 74;
    case "y": return 75;
    case "u": return 76;
    case "i": return 77;
    case "o": return 78;
    case "p": return 79;

    default: return -1;
  }
}
