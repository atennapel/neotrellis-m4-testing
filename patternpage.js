class PatternPage {
  #macropad;
  #neotrellis;
  #screen;
  #instruments;

  #tracks = Array(12).fill(0);
  #track = 0;
  #patterns;

  #pressedKeys = [];
  #velocities = {};

  #step = 0;

  constructor(macropad, neotrellis, screen, instruments) {
    this.#macropad = macropad;
    this.#neotrellis = neotrellis;
    this.#screen = screen;
    this.#instruments = instruments;

    this.#patterns = Array(12);
    for (let i = 0; i < 12; i++)
      this.#patterns[i] = Array(patternLength).fill(null);
  }

  #drawMacropad() {
    const macropad = this.#macropad;
    macropad.clear();
    macropad.set(this.#track, GREENH)
    macropad.draw();
  }

  #drawNeotrellis() {
    const neotrellis = this.#neotrellis;
    neotrellis.clear();
    neotrellis.set(this.#step, REDH);
    const pattern = this.#patterns[this.#track];
    for (let i = 0; i < patternLength; i++) {
      if (pattern[i])
        neotrellis.set(i, i == this.#step ? PURPLE : BLUEH);
    }
    neotrellis.draw();
  }

  #text() {
    return `pattern page\ntrack: ${this.#track + 1}\ninstrument: ${this.#tracks[this.#track] + 1}`;
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
    this.#track = ix;
    this.#drawMacropad();
    this.#drawText();
  }

  macropadEncoder(diff) {
    const track = this.#track;
    this.#tracks[track]  = mod(this.#tracks[track] + diff, 12);
    this.#drawText();
  }

  keyboardOn(note, velocity) {
    const instrument = this.#instruments[this.#tracks[this.#track]].toneInstrument
    const freq = Tone.Frequency(note, "midi");
    instrument.triggerAttack(freq, Tone.now(), velocity / 127);
    this.#pressedKeys.push(note);
    this.#velocities[note] = velocity;
  }

  keyboardOff(note) {
    const instrument = this.#instruments[this.#tracks[this.#track]].toneInstrument
    const freq = Tone.Frequency(note, "midi");
    instrument.triggerRelease(freq);
    const i = this.#pressedKeys.findIndex(n => n == note);
    this.#pressedKeys.splice(i, 1);
  }

  // TODO: ability to draw note length
  neotrellisButtonDown(ix) {
    if (ix < patternLength) {
      const pressedKeys = this.#pressedKeys;
      const pattern = this.#patterns[this.#track];
      if (pressedKeys.length > 0) {
        const notes = Array(this.#pressedKeys.length);
        for (let i = 0; i < pressedKeys.length; i++) {
          const note = pressedKeys[i];
          notes[i] = new StepNote(note, this.#velocities[note]);
        }
        pattern[ix] = new Step(notes);
      } else if (pattern[ix]) {
        pattern[ix] = null;
      }
    }
    this.#drawNeotrellis();
  }

  neotrellisButtonUp(ix) {
    
  }

  neotrellisEncoder(diff) {
    
  }

  neotrellisEncoderDown() {
    
  }

  tick(t, step) {
    this.#step = step;
    const patterns = this.#patterns;
    for (let p = 0; p < 12; p++) {
      const toneInstrument = this.#instruments[this.#tracks[p]].toneInstrument;
      const pattern = patterns[p];
      const cstep = pattern[step];
      if (cstep) {
        const notes = cstep.notes;
        for (let i = 0; i < notes.length; i++) {
          const note = notes[i];
          const freq = Tone.Frequency(note.note, "midi");
          toneInstrument.triggerAttackRelease(freq, `0:0:1`, t, note.velocity / 127);
        }
      }
    }
    this.#drawNeotrellis();
  }
}

class Step {
  notes;

  constructor(notes) {
    this.notes = notes;
  }
}

class StepNote {
  note;
  velocity;
  
  constructor(note, velocity) {
    this.note = note;
    this.velocity = velocity;
  }
}
