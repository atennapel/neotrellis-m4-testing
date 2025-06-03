const infoDiv = document.getElementById("info");
function info(msg) { infoDiv.innerText = msg }
document.addEventListener("click", start);
info("click to start");

const MIDI_KEYBOARD = "LPK"
let macropad = null;
let neotrellis = null;
let midikeyboard = null;

let synth = null;
let delay = null;
let transport = null;
let samplers = null;
let samplerIx = 0;
let sampler = null;

let encoderValue = [0, 0, 0, 120];
const MODES = 7;
let encoderMode = 0;
let encoderLayer = 0;
function updateStatus() {
  info(`mode: ${encoderMode}, enc: ${encoderValue[encoderMode]}`);
}

function showNote(note) {
  return note < 0 ? `--` : note < 10 ? `0${note}` : `${note}`;
}

const pattern = [];
let currentStep = 0;
let step = 0;
for (let i = 0; i < 32; i++) pattern.push(-1);
let selectedSample = -1;
let recording = false;
let metronome = false;

const screenDiv = document.getElementById("screen");
function updateScreen() {
  const txt =
`${encoderMode == 0 && encoderLayer == 0 ? ">" : " "} volume ${encoderMode == 0 && encoderLayer == 1 ? ">" : " "} ${encoderValue[0]}
${encoderMode == 1 && encoderLayer == 0 ? ">" : " "} wet    ${encoderMode == 1 && encoderLayer == 1 ? ">" : " "} ${encoderValue[1]}
${encoderMode == 2 && encoderLayer == 0 ? ">" : " "} attack ${encoderMode == 2 && encoderLayer == 1 ? ">" : " "} ${encoderValue[2]}
${encoderMode == 3 && encoderLayer == 0 ? ">" : " "} bpm    ${encoderMode == 3 && encoderLayer == 1 ? ">" : " "} ${encoderValue[3]}
${encoderMode == 4 && encoderLayer == 0 ? ">" : " "} rec    ${encoderMode == 4 && encoderLayer == 1 ? ">" : " "} ${recording}
${encoderMode == 5 && encoderLayer == 0 ? ">" : " "} tick   ${encoderMode == 5 && encoderLayer == 1 ? ">" : " "} ${metronome}
${encoderMode == 6 && encoderLayer == 0 ? ">" : " "} kit    ${encoderMode == 6 && encoderLayer == 1 ? ">" : " "} ${samplerIx}`;
  screenDiv.innerText = txt;
}
updateScreen();

function createDrumsSampler(sample) {
  return new Tone.Sampler({
    urls: {
      "C4": "kick.mp3",
      "D4": "snare.mp3",
      "E4": "hihat.mp3",
      "F4": "tom1.mp3",
      "G4": "tom2.mp3",
      "A4": "tom3.mp3",
    },
    baseUrl: `https://tonejs.github.io/audio/drum-samples/${sample}/`,
  });
}

async function start() {
  info("started");
  document.removeEventListener("click", start);

  info("initializing ToneJS");
  Tone.setContext(new Tone.Context({ latencyHint: "interactive", lookAhead: 0 }));
  await Tone.start();

  // delay = new Tone.PingPongDelay("4n", 0).toDestination();
  delay = new Tone.Reverb(1).toDestination();
  delay.wet.value = 0.5;
  synth = new Tone.PolySynth(Tone.Synth, {maxPolyphony: 12}).connect(delay);
  samplers = [
    createDrumsSampler("4OP-FM"),
    createDrumsSampler("Bongos"),
    createDrumsSampler("CR78"),
    createDrumsSampler("KPR77"),
    createDrumsSampler("Kit3"),
    createDrumsSampler("Kit8"),
    createDrumsSampler("LINN"),
    createDrumsSampler("R8"),
    createDrumsSampler("Stark"),
    createDrumsSampler("Techno"),
    createDrumsSampler("TheCheebacabra1"),
    createDrumsSampler("TheCheebacabra2"),
    createDrumsSampler("acoustic-kit"),
    createDrumsSampler("breakbeat13"),
    createDrumsSampler("breakbeat8"),
    createDrumsSampler("breakbeat9"),
  ];
  samplers.forEach(s => s.connect(delay));
  samplerIx = 0;
  sampler = samplers[samplerIx];

  transport = Tone.getTransport()
  transport.bpm.value = 120;
  transport.swing = 0;
  transport.scheduleRepeat(tick, "16n");
  transport.stop();

  info("requesting midi input");
  const access = await navigator.requestMIDIAccess();
  info("got midi access");
  const inputs = [];
  const outputs = [];
  for (const input of access.inputs.values()) {
    inputs.push(input.name);
    if (input.name.indexOf(MIDI_KEYBOARD) >= 0) {
      midikeyboard = input;
      midikeyboard.addEventListener("midimessage", onKeyboardMidi);
    }
  }
  for (const output of access.outputs.values())
    outputs.push(output.name);
  console.log(`midi inputs: [${inputs.join(", ")}], midi outputs: [${outputs.join(", ")}]`);
  macropad = new Macropad(access, onMacropadEvent);
  neotrellis = new NeoTrellis(access, onNeoTrellisEvent);
  if (!midikeyboard) {
    info(`LPK25 not found, midi inputs: [${inputs.join(", ")}], midi outputs: [${outputs.join(", ")}]`);
    return;
  } else
    info("macropad, neotrellis and LPK25 found");

  transport.start();

  info("successfully started");
}

const MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11];

function key2note(k) {
  const x = k % 3;
  const y = 3 - Math.floor(k / 3);
  const i = y * 3 + x;
  const octave = Math.floor(i / MAJOR_SCALE.length);
  return MAJOR_SCALE[i % MAJOR_SCALE.length] + 60 + octave * 12;
}

function key2noteTrellis(k) {
  const x = k % 8;
  const y = 3 - Math.floor(k / 8);
  const i = y * 8 + x;
  const octave = Math.floor(i / MAJOR_SCALE.length);
  return MAJOR_SCALE[i % MAJOR_SCALE.length] + 60 + octave * 12;
}

function clamp(min, max, v) {
  return v < min ? min : v > max ? max: v;
}

function onMacropadEvent(macropad, event) {
  if (event.type == Macropad.BUTTON_DOWN) {
    const value = event.index;
    const note = key2note(value);
    const freq = Tone.Frequency(note, "midi");
    sampler.triggerAttack(freq);
    macropad.set(value, 1);
    if (selectedSample != -1)
      macropad.unset(selectedSample);
    selectedSample = value;
    if (recording) pattern[step] = value;
  } else if (event.type == Macropad.BUTTON_UP) {
    const value = event.index;
    const note = key2note(value);
    const freq = Tone.Frequency(note, "midi");
    sampler.triggerRelease(freq);
    if (selectedSample == value)
      macropad.set(value, 4);
    else
      macropad.unset(value);
  } else if (event.type == Macropad.ENCODER_DOWN) {
    encoderLayer = (encoderLayer + 1) % 2;
  } else if (event.type == Macropad.ENCODER) {
    if (encoderLayer == 0) {
      const diff = event.diff;
      let v = encoderMode + diff;
      while (v < 0) v += MODES;
      v = v % MODES;
      encoderMode = v;
    } else if (encoderLayer == 1) {
      const v = encoderValue[encoderMode] + event.diff;
      if (encoderMode == 0) {
        synth.volume.value = v;
        encoderValue[encoderMode] = v;
      } else if (encoderMode == 1) {
        const x = clamp(0, 100, v);
        encoderValue[encoderMode] = x;
        delay.wet.value = x / 100;
      } else if (encoderMode == 2) {
        const x = clamp(0, 100, v);
        encoderValue[encoderMode] = x;
        synth.set({ envelope: { attack: x / 50 } });
      } else if (encoderMode == 3) {
        const x = clamp(1, 500, v);
        transport.bpm.value = x;
      } else if (encoderMode == 4) {
        recording = !recording;
      } else if (encoderMode == 5) {
        metronome = !metronome;
      } else if (encoderMode == 6) {
        const diff = event.diff;
        let v = samplerIx + diff;
        while (v < 0) v += samplers.length;
        v = v % samplers.length;
        samplerIx = v;
        sampler = samplers[samplerIx];
      }
    }
  }
  updateStatus();
  updateScreen();
  macropad.draw();
}

function onNeoTrellisEvent(neotrellis, event) {
  if (event.type == NeoTrellis.BUTTON_DOWN) {
    const value = event.index;
    if (pattern[value] >= 0) {
      pattern[value] = -1;
      neotrellis.unset(value);
    } else if (selectedSample != -1) {
      pattern[value] = selectedSample;
      neotrellis.set(value, 4);
    }
    neotrellis.draw();
  }
}

function onKeyboardMidi(msg) {
  const data = msg.data;
  if (data[0] == NOTE_ON) {
    const freq = Tone.Frequency(data[1], "midi");
    synth.triggerAttack(freq, Tone.now(), data[2] / 127);
  } else if (data[0] == NOTE_OFF) {
    const freq = Tone.Frequency(data[1], "midi");
    synth.triggerRelease(freq);
  }
}

function tick(t) {
  step = (step + 1) % 32;
  const note = pattern[step]
  if (metronome && step % 4 == 0)
    sampler.triggerAttackRelease("F4", "16n", t);
  if (note >= 0) {
    const freq = Tone.Frequency(key2note(note), "midi");
    sampler.triggerAttackRelease(freq, "16n", t);
  }

  for (let i = 0; i < 32; i++) {
    if (i == step)
      neotrellis.set(i, 1);
    else if (pattern[i] >= 0)
      neotrellis.set(i, 4);
    else
      neotrellis.unset(i);
  }
  neotrellis.draw();
}
