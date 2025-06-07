const infoDiv = document.getElementById("info");
function info(msg) { infoDiv.innerText = msg }
document.addEventListener("click", start);
info("click to start");

const MIDI_KEYBOARD = "LPK"
let macropad = null;
let neotrellis = null;
let midikeyboard = null;
let instrumentsPage = null;
let pianorollPage = null;
let page = null;

let delay = null;
let transport = null;
let instruments = null;
let instrument = null;
let recording = false;

let notesPressed = 0;
const keyboardPressed = [];
for (let i = 0; i < 128; i++) keyboardPressed[i] = null;
let lastPressed = [];

const patterns = [[]];
let step = 0;
for (let t = 0; t < 6; t++) {
  const pattern = [];
  patterns[t] = pattern;
  for (let i = 0; i < 32; i++)
    pattern.push(null);
}

let currentTrack = 0;
const tracks = [0, 1, 2, 16, 17, 18];
const mutes = [false, false, false, false, false, false];
const trackNotes = [60, 60, 60, 60, 60, 60];
const trackVelocities = [127, 127, 127, 127, 127, 127];

function drawTracks() {
  for (let i = 0; i < 6; i++) {
    macropad.set(i, i == currentTrack ? 4 : 0);
    macropad.set(i + 6, mutes[i] ? 0 : 6);
  }
  macropad.draw();
}
function drawPattern() {
  const pattern = patterns[currentTrack];
  for (let i = 0; i < 32; i++) {
    if (i == step)
      neotrellis.set(i, 1);
    else if (pattern[i] != null)
      neotrellis.set(i, 4);
    else
      neotrellis.unset(i);
  }
  neotrellis.draw();
}

const screenDiv = document.getElementById("screen");
function updateScreen() {
  const t = `
Track ${currentTrack + 1}${mutes[currentTrack] ? " (muted)" : ""}
instrument ${tracks[currentTrack] + 1}
recording ${recording}
  `.trim();
  screenDiv.innerText = t;
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
  instruments = [
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
    new Tone.PolySynth(Tone.Synth, {maxPolyphony: 12}),
    new Tone.PolySynth(Tone.Synth, {maxPolyphony: 12}),
    new Tone.PolySynth(Tone.Synth, {maxPolyphony: 12}),
  ];
  instruments.forEach(s => s.connect(delay));
  instrument = instruments[tracks[currentTrack]];

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

  drawTracks();

  instrumentsPage = new InstrumentsPage(macropad, neotrellis, screenDiv, delay);
  pianorollPage = new PianoRollPage(macropad, neotrellis, screenDiv);
  page = instrumentsPage;
  page.draw();
}

function onMacropadEvent(macropad, event) {
  if (page != null) {
    if (event.type == Macropad.BUTTON_DOWN) {
      page.macropadButton(event.index);
    } else if (event.type == Macropad.ENCODER) {
      page.macropadEncoder(event.diff);
    } else if (event.type == Macropad.ENCODER_DOWN) {
      page = page == instrumentsPage ? pianorollPage : instrumentsPage;
      page.draw();
    }
  } else {
    if (event.type == Macropad.BUTTON_DOWN) {
      const value = event.index;
      if (value < 6) {
        currentTrack = value;
        instrument = instruments[tracks[value]];
        drawPattern();
      } else {
        const i = value - 6;
        mutes[i] = !mutes[i];
      }
    } else if (event.type == Macropad.ENCODER_DOWN) {
      recording = !recording;
    } else if (event.type == Macropad.ENCODER) {
      const diff = event.diff;
      const next = mod(tracks[currentTrack] + diff, instruments.length);
      tracks[currentTrack] = next;
      instrument = instruments[next];
    }
    updateScreen();
    drawTracks();
  }
}

function onNeoTrellisEvent(neotrellis, event) {
  if (page != null) {
    if (event.type == NeoTrellis.BUTTON_DOWN) {
      page.neotrellisButton(event.index);
    } else if (event.type == NeoTrellis.ENCODER) {
      page.neotrellisEncoder(event.diff);
    } else if (event.type == NeoTrellis.ENCODER_DOWN) {
      page.neotrellisEncoderDown();
    }
  } else {
    if (event.type == NeoTrellis.BUTTON_DOWN) {
      const value = event.index;
      const pattern = patterns[currentTrack];
      if (pattern[value] != null) {
        pattern[value] = null;
      } else {
        pattern[value] = lastPressed;
      }
      drawPattern();
    }
  }
}

function onKeyboardMidi(msg) {
  if (page != null) {
    const data = msg.data;
    const type = data[0];
    if (type == NOTE_ON)
      page.keyboardOn(data[1], data[2]);
    else if (type == NOTE_OFF)
      page.keyboardOff(data[1]);
  } else {
    const data = msg.data;
    if (data[0] == NOTE_ON) {
      notesPressed++;
      const note = data[1];
      const velocity = data[2];
      keyboardPressed[note] = {note, velocity};
      const freq = Tone.Frequency(note, "midi");
      instrument.triggerAttack(freq, Tone.now(), velocity / 127);
      trackNotes[currentTrack] = note;
      trackVelocities[currentTrack] = velocity;
      lastPressed = [];
      for (let i = 0; i < 128; i++) {
        if (keyboardPressed[i] != null)
          lastPressed.push(keyboardPressed[i]);
      }
      if (recording) {
        const pattern = patterns[currentTrack];
        pattern[step] = lastPressed;
        drawPattern();
      }
    } else if (data[0] == NOTE_OFF) {
      const note = data[1];
      keyboardPressed[note] = null;
      const freq = Tone.Frequency(note, "midi");
      instrument.triggerRelease(freq);
    }
  }
}

function tick(t) {
  if (page == null) {
    step = (step + 1) % 32;

    for (let i = 0; i < 6; i++) {
      if (!mutes[i]) {
        const pattern = patterns[i]
        const data = pattern[step]
        if (data != null) {
          const instrument = instruments[tracks[i]];
          for (let j = 0; j < data.length; j++) {
            const notedata = data[j];
            const freq = Tone.Frequency(notedata.note, "midi");
            instrument.triggerAttackRelease(freq, "16n", t, notedata.velocity / 127);
          }
        }
      }
    }
    
    drawPattern();
  }
}
