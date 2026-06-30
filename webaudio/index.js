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
    switch (e.key) {
      case "z": return noteOn(60, 1);
      case "x": return noteOn(62, 1);
      case "c": return noteOn(64, 1);
      case "v": return noteOn(65, 1);
      case "b": return noteOn(67, 1);
      case "n": return noteOn(69, 1);
      case "m": return noteOn(71, 1);
      case ",": return noteOn(72, 1);
    }
  });
  document.addEventListener("keyup", e => {
    switch (e.key) {
      case "z": return noteOff(60);
      case "x": return noteOff(62);
      case "c": return noteOff(64);
      case "v": return noteOff(65);
      case "b": return noteOff(67);
      case "n": return noteOff(69);
      case "m": return noteOff(71);
      case ",": return noteOff(72);
    }
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
