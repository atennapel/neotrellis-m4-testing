const container = document.getElementById("container");
container.innerText = "click to start";
container.addEventListener("pointerdown", init);
async function init() {
  container.removeEventListener("pointerdown", init);
  container.innerText = "";

  Tone.setContext(new Tone.Context({ latencyHint: "interactive", lookAhead: 0 }));
  await Tone.start();

  const grid = new Grid(container, gridHandler);
  const patterns = Array(16);
  for (let i = 0; i < 16; i++)
    patterns[i] = Array(112).fill(false);
  let currentInstrument = 0;
  const instruments = Array(16);
  function gridHandler(i, pressed) {
    if (pressed) {
      if (i < 112)
        patterns[currentInstrument][i] = !patterns[currentInstrument][i];
      else
        currentInstrument = i - 112;
    }
  }

  const synth = new Tone.PolySynth(Tone.Synth).toDestination();
  synth.maxPolyphony = 100;

  const reverb = new Tone.Reverb({
    decay: 4,
    wet: 0.25
  }).toDestination();
  const pluck = new Tone.PluckSynth({
    attackNoise: 1.5,
    dampening: 6000,
    resonance: 0.9
  }).connect(reverb);

  const synth2 = new Tone.PolySynth(Tone.Synth, {
    oscillator: {
      type: "triangle"
    },
    envelope: {
      attack: 0.005,
      decay: 0.2,
      sustain: 0.4,
      release: 2.5
    }
  }).toDestination();
  synth2.maxPolyphony = 100;

  const synth3 = new Tone.PolySynth(Tone.AMSynth, {
    harmonicity: 2,
    oscillator: {
      type: "sawtooth"
    },
    envelope: {
      attack: 0.05,
      decay: 0.3,
      sustain: 0.6,
      release: 1.2
    }
  }).toDestination();
  synth3.maxPolyphony = 100;

  const synth4 = new Tone.PolySynth(Tone.FMSynth, {
    harmonicity: 2,
    modulationIndex: 10,
    envelope: {
      attack: 0.01,
      decay: 0.4,
      sustain: 0.2,
      release: 1.5
    }
  }).toDestination();
  synth4.maxPolyphony = 100;

  const synth5 = new Tone.PolySynth(Tone.Synth, {
    oscillator: {
      type: "square"
    },
    envelope: {
      attack: 0.005,
      decay: 0.15,
      sustain: 0,
      release: 0.8
    }
  }).toDestination();
  synth5.maxPolyphony = 100;

  const synth6 = new Tone.PolySynth(Tone.Synth, {
    oscillator: {
      type: "sawtooth"
    },
    envelope: {
      attack: 0.02,
      decay: 0.4,
      sustain: 0.7,
      release: 2
    }
  }).toDestination();
  synth6.maxPolyphony = 100;

  const kits = Array(KITS.length);
  for (let i = 0; i < KITS.length; i++) {
    const kit = KITS[i];
    const sampler = new Tone.Sampler({
      urls: {
        "C4": "kick.mp3",
        "D4": "snare.mp3",
        "E4": "hihat.mp3",
        "F4": "tom1.mp3",
        "G4": "tom2.mp3",
        "A4": "tom3.mp3",
      },
      baseUrl: `https://tonejs.github.io/audio/drum-samples/${kit}/`,
    }).toDestination();
    kits[i] = sampler;
  }

  for (let i = 0; i < 16; i++)
    instruments[i] = synth;
  instruments[0] = kits[0];
  instruments[1] = synth;
  instruments[2] = synth;
  instruments[3] = pluck;
  instruments[4] = synth2;
  instruments[5] = synth3;
  instruments[6] = synth4;
  instruments[7] = synth5;
  instruments[8] = synth6;

  const transport = Tone.getTransport()
  transport.bpm.value = 120;
  transport.swing = 0;
  transport.scheduleRepeat(tick, "16n");
  transport.stop();

  let step = -1;
  function tick(t) {
    step = (step + 1) % 16;

    for (let i = 0; i < 7; i++) {
      const j = step + 16 * i;
      const octave = Math.floor((6 - i) / 6);
      const note = 60 + MAJOR[(6 - i) % 6] + 12 * octave;
      for (let instr = 0; instr < 16; instr++) {
        if (patterns[instr][j]) {
          const freq = Tone.Frequency(note + (instr === 2 ? -24 : 0), "midi");
          instruments[instr].triggerAttackRelease(freq, "16n", t, 1);
        }
      }
    }
  }

  const keys = new Map();
  window.addEventListener("keydown", e => {
    if (!keys.get(e.key)) {
      keys.set(e.key, true);
      const note = key2note(e.key);
      if (note >= 0) {
        const freq = Tone.Frequency(note, "midi");
        instruments[currentInstrument].triggerAttack(freq, Tone.now(), 0.8);
      }
    }
  });
  window.addEventListener("keyup", e => {
    if (keys.get(e.key)) {
      keys.set(e.key, false);
      const note = key2note(e.key);
      if (note >= 0) {
        const freq = Tone.Frequency(note, "midi");
        instruments[currentInstrument].triggerRelease(freq);
      }
    }
  });

  function key2note(k) {
    switch (k) {
      case "z": return 60; // c
      case "s": return 61; // c#
      case "x": return 62; // d
      case "d": return 63; // d#
      case "c": return 64; // e
      case "v": return 65; // f
      case "g": return 66; // f#
      case "b": return 67; // g
      case "h": return 68; // g#
      case "n": return 69; // a
      case "j": return 70; // a#
      case "m": return 71; // b
      case ",": return 72; // c
      case "l": return 73; // c#
      case ".": return 74; // d
      case ";": return 75; // d#
      case "/": return 76; // e
      default: -1;
    }
  }

  function draw() {
    grid.clear();
    for (let i = 0; i < 112; i++) {
      if (patterns[currentInstrument][i]) {
        grid.set(i, BLUE);
      }
    }
    for (let i = 0; i < 7; i++) {
      const j = step + 16 * i;
      const set = patterns[currentInstrument][j];
      grid.set(j, set ? DARKBLUE : GREY);
    }
    for (let i = 0; i < 16; i++)
      grid.set(i + 112, currentInstrument === i ? RED : PINK);
  }

  function update(t) {
    draw();
    grid.draw();
    window.requestAnimationFrame(update);
  }
  update();

  transport.start();

  for (let i = 0; i < 16; i++)
    grid.setText(i + 112, `${i + 1}`);
}
