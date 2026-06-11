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
