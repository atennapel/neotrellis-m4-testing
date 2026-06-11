var curKit = 8;

const container = document.getElementById("container");
container.innerText = "click to start";
container.addEventListener("pointerdown", init);
async function init() {
  container.removeEventListener("pointerdown", init);
  container.innerText = "";

  Tone.setContext(new Tone.Context({ latencyHint: "interactive", lookAhead: 0 }));
  await Tone.start();

  const grid = new Grid(container, gridHandler);
  const pattern = Array(128).fill(false);
  function gridHandler(i, pressed) {
    if (pressed) {
      pattern[i] = !pattern[i];
    }
  }

  const synth = new Tone.PolySynth(Tone.Synth).toDestination();
  synth.maxPolyphony = 128;

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

  const transport = Tone.getTransport()
  transport.bpm.value = 120;
  transport.swing = 0;
  transport.scheduleRepeat(tick, "16n");
  transport.stop();

  let step = -1;
  function tick(t) {
    step = (step + 1) % 16;

    for (let i = 0; i < 8; i++) {
      const j = step + 16 * i;
      if (pattern[j]) {
        const octave = Math.floor((7 - i) / 7);
        const note = 60 + MAJOR[(7 - i) % 7] + 12 * octave;
        const freq = Tone.Frequency(note, "midi");
        kits[curKit].triggerAttackRelease(freq, "16n", t, 1);
      }
    }
  }

  const keys = new Map();
  window.addEventListener("keydown", e => {
    keys.set(e.key, true);
    const note = key2note(e.key);
    if (note >= 0) {
      const freq = Tone.Frequency(note, "midi");
      kits[curKit].triggerAttack(freq, Tone.now(), 0.8);
    }
  });
  window.addEventListener("keyup", e => {
    if (keys.get(e.key)) {
      keys.set(e.key, false);
      const note = key2note(e.key);
      if (note >= 0) {
        const freq = Tone.Frequency(note, "midi");
        synth.triggerRelease(freq);
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
    for (let i = 0; i < 128; i++) {
      if (pattern[i]) {
        grid.set(i, BLUE);
      }
    }
    for (let i = 0; i < 8; i++) {
      const j = step + 16 * i;
      const set = pattern[j];
      grid.set(j, set ? DARKBLUE : GREY);
    }
  }

  function update(t) {
    draw();
    grid.draw();
    window.requestAnimationFrame(update);
  }
  update();

  transport.start();
}
