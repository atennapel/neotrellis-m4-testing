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
  const now = ctx.currentTime;
  master.gain.cancelAndHoldAtTime(now)
  master.gain.linearRampToValueAtTime(gain, now + 0.01);
}

function noteOn(note, gain) {
  const now = ctx.currentTime;
  const vol = gain * 0.2;
  const instr = notes[note];
  if (!instr) {
    active.add(note);
    adjustMaster();
    const newinstr = new Instrument(ctx);
    notes[note] = newinstr;
    newinstr.connect(master);
    newinstr.setNote(note);
    newinstr.setGain(vol);
    newinstr.start();
  } else {
    instr.setGain(vol);
  }
}

function noteOff(note) {
  const instr = notes[note];
  if (instr) {
    active.delete(note);
    notes[note] = null;
    instr.stop();
    adjustMaster();
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

class Instrument {
  constructor(ctx) {
    this.ctx = ctx;

    const osc = ctx.createOscillator();
    this.osc = osc;
    osc.type = "sine";

    const gain = ctx.createGain();
    this.gain = gain;
    gain.gain.value = 0;

    osc.connect(gain);
  }

  connect(tar) {
    this.gain.connect(tar);
  }

  start() {
    console.log("start");
    this.osc.start();
  }

  stop() {
    console.log("stop");
    const now = this.ctx.currentTime;
    const osc = this.osc;
    const gain = this.gain;
    gain.gain.cancelAndHoldAtTime(now);
    gain.gain.linearRampToValueAtTime(0, now + 0.05);
    osc.stop(now + 0.05);
    osc.onended = () => osc.disconnect();
  }

  setNote(note) {
    console.log("setNote", note);
    const now = this.ctx.currentTime;
    const osc = this.osc;
    osc.frequency.setValueAtTime(freq(note), now);
  }

  setGain(vol) {
    console.log("setGain", vol);
    const now = this.ctx.currentTime;
    const gain = this.gain;
    gain.gain.cancelAndHoldAtTime(now);
    gain.gain.linearRampToValueAtTime(vol, now + 0.05);
  }
}
