class InstrumentsPage {
  static TYPES = ["kit", "synth"];
  static PARAMETERS = [
    ["type", "kit", "volume", "curve", "attack", "release"],
    ["type", "volume", "attack", "decay", "release"],
  ];
  static KITS = [
    "4OP-FM",
    "Bongos",
    "CR78",
    "KPR77",
    "Kit3",
    "Kit8",
    "LINN",
    "R8",
    "Stark",
    "Techno",
    "TheCheebacabra1",
    "TheCheebacabra2",
    "acoustic-kit",
    "breakbeat13",
    "breakbeat8",
    "breakbeat9",
  ];

  #macropad;
  #neotrellis;
  #screen;
  #dest;
  #instruments;
  #selectedInstrument = 0;
  #parameter = 0;

  constructor(macropad, neotrellis, screen, dest) {
    this.#macropad = macropad;
    this.#neotrellis = neotrellis;
    this.#screen = screen;
    this.#dest = dest;
    this.#instruments = InstrumentsPage.#initializeInstruments(dest);
  }

  static #initializeInstruments(dest) {
    const instruments = [];
    for (let i = 0; i < 12; i++) {
      const toneInstrument = InstrumentsPage.#createDrumsSampler(InstrumentsPage.KITS[0]).connect(dest);
      instruments.push({type: 0, toneInstrument, kit: 0, volume: 0, curve: 1, attack: 0, release: 10});
    }
    return instruments;
  }

  static #createDrumsSampler(kit) {
    return new Tone.Sampler({
      urls: {
        "C4": "kick.mp3",
        "D4": "snare.mp3",
        "E4": "hihat.mp3",
        "F4": "tom1.mp3",
        "G4": "tom2.mp3",
        "A4": "tom3.mp3",
      },
      baseUrl: `https://tonejs.github.io/audio/drum-samples/${kit}/`,
    });
  }

  get instruments() {
    return this.#instruments;
  }

  #drawMacropad() {
    const macropad = this.#macropad;
    macropad.clear();
    macropad.set(this.#selectedInstrument, GREENH);
    macropad.draw();
  }

  #drawNeotrellis() {
    const neotrellis = this.#neotrellis;
    neotrellis.clear();
    const parameters = InstrumentsPage.PARAMETERS[this.#instruments[this.#selectedInstrument].type];
    for (let i = 0; i < parameters.length; i++)
      neotrellis.set(i, BLUEH);
    neotrellis.set(this.#parameter, GREENH);
    neotrellis.draw();
  }

  #displayValue(instrument, parameter) {
    const value = instrument[parameter];
    if (parameter == "type")
      return InstrumentsPage.TYPES[value];
    if (parameter == "kit")
      return InstrumentsPage.KITS[value];
    if (parameter == "curve")
      return value == 0 ? "linear" : "exponential";
    if (parameter == "attack" || parameter == "decay" || parameter == "release")
      return `${(value / 100).toFixed(2)}s`;
    return value;
  }

  #text() {
    const instrumentIx = this.#selectedInstrument;
    const instrument = this.#instruments[instrumentIx];
    const type = instrument.type;
    const parameter = InstrumentsPage.PARAMETERS[type][this.#parameter];
    return `instruments page\ninstrument ${instrumentIx + 1}\nparameter: ${parameter}\nvalue: ${this.#displayValue(instrument, parameter)}`;
  }

  #drawText() {
    this.#screen.innerText = this.#text();
  }

  draw() {
    this.#drawMacropad();
    this.#drawNeotrellis();
    this.#drawText();
  }

  macropadButton(ix) {
    this.#selectedInstrument = ix;
    const instrument = this.#instruments[ix];
    const type = instrument.type;
    const parameters = InstrumentsPage.PARAMETERS[type];
    if (this.#parameter >= parameters.length)
      this.#parameter = parameters.length - 1;
    this.draw();
  }

  neotrellisButton(ix) {
    const instrumentIx = this.#selectedInstrument;
    const instrument = this.#instruments[instrumentIx];
    const type = instrument.type;
    const parameters = InstrumentsPage.PARAMETERS[type];
    if (ix < parameters.length)
      this.#parameter = ix;
    this.draw();
  }

  keyboardOn(note, velocity) {
    const instrumentIx = this.#selectedInstrument;
    const instrument = this.#instruments[instrumentIx];
    const freq = Tone.Frequency(note, "midi");
    instrument.toneInstrument.triggerAttack(freq, Tone.now(), velocity / 127);
  }

  keyboardOff(note) {
    const instrumentIx = this.#selectedInstrument;
    const instrument = this.#instruments[instrumentIx];
    const freq = Tone.Frequency(note, "midi");
    instrument.toneInstrument.triggerRelease(freq);
  }

  encoder(diff) {
    const instrumentIx = this.#selectedInstrument;
    const instrument = this.#instruments[instrumentIx];
    const parameters = InstrumentsPage.PARAMETERS[instrument.type];
    const parameter = parameters[this.#parameter]
    if (parameter == "type") {
      const newtype = mod(instrument.type + diff, InstrumentsPage.TYPES.length)
      if (instrument.type != newtype) {
        instrument.type = newtype;
        instrument.toneInstrument.disconnect();
        instrument.toneInstrument.dispose();
        if (newtype == 0) {
          const toneInstrument = InstrumentsPage.#createDrumsSampler(InstrumentsPage.KITS[instrument.kit]).connect(this.#dest);
          instrument.toneInstrument = toneInstrument;
          instrument.volume = 0;
          instrument.curve = 1;
          instrument.attack = 0;
          instrument.release = 10;
        } else if (newtype == 1) {
          const toneInstrument = new Tone.PolySynth(Tone.Synth, {maxPolyphony: 12}).connect(this.#dest);
          instrument.toneInstrument = toneInstrument;
          instrument.volume = 0;
          instrument.attack = 0;
          instrument.decay = 10;
          instrument.release = 100;
        }
      }
    } else if (parameter == "kit") {
      const newkit = mod(instrument.kit + diff, InstrumentsPage.KITS.length);
      if (newkit != instrument.kit) {
        instrument.kit = newkit;
        instrument.toneInstrument.disconnect();
        instrument.toneInstrument.dispose();
        const toneInstrument = InstrumentsPage.#createDrumsSampler(InstrumentsPage.KITS[newkit]).connect(this.#dest);
        instrument.toneInstrument = toneInstrument;
      }
    } else if (parameter == "volume") {
      instrument.volume += diff;
      instrument.toneInstrument.volume.value += diff;
    } else if (parameter == "curve") {
      instrument.curve = mod(instrument.curve + diff, 2);
      instrument.toneInstrument.curve = instrument.curve == 0 ? "linear" : "exponential";
    } else if (parameter == "attack" || parameter == "decay" || parameter == "release") {
      const value = instrument[parameter] + diff;
      if (value >= 0) {
        instrument[parameter] = value;
        if (instrument.type == 0) {
          instrument.toneInstrument[parameter] = value / 100;
        } else if (instrument.type == 1) {
          instrument.toneInstrument.set({
            envelope: {
              [parameter]: value / 100
            }
          })
        }
      }
    }
    this.draw();
  }
}
