const infoDiv = document.getElementById("info");
function info(msg) { infoDiv.innerText = msg }
document.addEventListener("click", start);
info("click to start");

let macropad = null;
let macropadOutput = null;

let synth = null;
let delay = null;
let transport = null;
let sampler = null;

let encoderValue = [0, 0, 0, 120, 0];
let encoderMode = 0;
function updateStatus() {
  info(`mode: ${encoderMode}, enc: ${encoderValue[encoderMode]}`);
}

function showNote(note) {
  return note < 0 ? `--` : note < 10 ? `0${note}` : `${note}`;
}

const pattern = [];
let currentStep = 0;
let step = 0;
for (let i = 0; i < 16; i++) pattern.push(-1);
const patternDiv = document.getElementById("pattern");
function updatePattern() {
  patternDiv.innerText = pattern.map((n, i) => `${i == currentStep ? ">" : " "}${showNote(n)}${i == step ? "<" : " "}`).join(`|`);
}
updatePattern();

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
  synth = new Tone.PolySynth(Tone.Synth, {maxPolyphony: 12}).connect(delay);
  sampler = createDrumsSampler("Kit3").connect(delay);

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
    if (input.name == "CircuitPython Audio" || input.name == "Adafruit Macropad RP2040" || input.name == "Macropad RP2040") {
      macropad = input;
      macropad.addEventListener("midimessage", onMidi);
    }
  }
  for (const output of access.outputs.values()) {
    outputs.push(output.name);
    if (output.name == "CircuitPython Audio" || output.name == "Adafruit Macropad RP2040" || output.name == "Macropad RP2040") {
      macropadOutput = output;
    }
  }
  console.log(`midi inputs: [${inputs.join(", ")}], midi outputs: [${outputs.join(", ")}]`);
  if (!macropad || !macropadOutput)
    info(`macropad not found, midi inputs: [${inputs.join(", ")}], midi outputs: [${outputs.join(", ")}]`);
  else
    info("macropad found");

  transport.start();
}

const NOTE_ON = 144;
const NOTE_OFF = 128;
const MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11];

function key2note(k) {
  const x = k % 3;
  const y = 3 - Math.floor(k / 3);
  const i = y * 3 + x;
  const octave = Math.floor(i / MAJOR_SCALE.length);
  return MAJOR_SCALE[i % MAJOR_SCALE.length] + 60 + octave * 12;
}

function clamp(min, max, v) {
  return v < min ? min : v > max ? max: v;
}

function onMidi(msg) {
  const data = msg.data;
  if (data[0] == NOTE_ON) {
    const value = data[1];
    if (value < 12) {
      const note = key2note(data[1]);
      const freq = Tone.Frequency(note, "midi");
      sampler.triggerAttack(freq);
      macropadOutput.send([NOTE_ON, data[1], 1]);
      if (encoderMode == 4) {
        pattern[currentStep] = note;
        updatePattern();
      }
    } else if (value == 12) {
      const v = encoderValue[encoderMode] + (data[2] - 100);
      encoderValue[encoderMode] = v;
      updateStatus()
      if (encoderMode == 0)
        synth.volume.value = v;
      else if (encoderMode == 1)
        delay.wet.value = clamp(0, 100, v) / 100;
      else if (encoderMode == 2)
        synth.set({ envelope: { attack: clamp(0, 100, v) / 50 } });
      else if (encoderMode == 3)
        transport.bpm.value = clamp(1, 500, v);
      else if (encoderMode == 4) {
        let x = v;
        while (x < 0) x += 16;
        currentStep = x % 16;
        updatePattern();
      }
    } else if (value == 13) {
      encoderMode = (encoderMode + 1) % 5;
      updateStatus();
    }
  } else if (data[0] == NOTE_OFF) {
    const value = data[1];
    if (value < 12) {
      const note = key2note(data[1]);
      const freq = Tone.Frequency(note, "midi");
      sampler.triggerRelease(freq);
      macropadOutput.send([NOTE_OFF, data[1], 0]);
    } else if (value == 13) {
    }
  }
}

function tick(t) {
  step = (step + 1) % 16;
  updatePattern();
  const note = pattern[step]
  if (note >= 0) {
    const freq = Tone.Frequency(note, "midi");
    sampler.triggerAttackRelease(freq, "16n", t);
  }
}
