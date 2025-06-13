class PatternPage {
  #macropad;
  #neotrellis;
  #screen;
  #instruments;

  #tracks = Array(12).fill(0);
  #track = 0;
  #patterns;

  #selStart = -1;
  #noteChanged = false;
  #pressedKeys = [];
  #velocities = {};

  #patternLength = 16
  #step = 0;

  constructor(macropad, neotrellis, screen, instruments) {
    this.#macropad = macropad;
    this.#neotrellis = neotrellis;
    this.#screen = screen;
    this.#instruments = instruments;

    this.#patterns = Array(12);
    for (let i = 0; i < 12; i++)
      this.#patterns[i] = Array(this.#patternLength).fill(null);
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
    for (let i = 0; i < this.#patternLength; i++) {
      const note = pattern[i];
      if (note)
        neotrellis.set(i, i == this.#step ? PURPLE : note.isHead ? BLUEH : CYANH);
    }
    const start = this.#selStart
    if (start != -1)
      neotrellis.set(start, BLUE);
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

  neotrellisButtonDown(ix) {
    if (ix < this.#patternLength) {
      const pattern = this.#patterns[this.#track];
      const start = this.#selStart
      if (start == -1) {
        this.#selStart = ix;
        const value = pattern[ix];
        if (value && value.isHead) {
          for (let i = ix; i < this.#patternLength; i++) {
            const c = pattern[i];
            if (!c || (c.isHead && i != ix)) break;
            pattern[i] = null;
          }
          this.#noteChanged = true;
          this.#drawNeotrellis();
        }
      } else {
        if (ix > start) {
          const pressedKeys = this.#pressedKeys;
          if (pressedKeys.length > 0) {
            const notes = Array(this.#pressedKeys.length);
            for (let i = 0; i < pressedKeys.length; i++) {
              const note = pressedKeys[i];
              notes[i] = new StepNote(note, this.#velocities[note]);
            }
            pattern[start] = new Step(notes, true, ix - start + 1);
            for (let i = start + 1; i <= ix; i++)
              pattern[i] = new Step(notes, false, 0);
            this.#noteChanged = true;
            this.#drawNeotrellis();
          }
        }
      }
    }
  }

  neotrellisButtonUp(ix) {
    if (ix < this.#patternLength) {
      if (ix == this.#selStart) {
        this.#selStart = -1
        if (this.#noteChanged)
          this.#noteChanged = false;
        else {
          const pressedKeys = this.#pressedKeys;
          if (pressedKeys.length > 0) {
            const notes = Array(this.#pressedKeys.length);
            for (let i = 0; i < pressedKeys.length; i++) {
              const note = pressedKeys[i];
              notes[i] = new StepNote(note, this.#velocities[note]);
            }
            const pattern = this.#patterns[this.#track];
            pattern[ix] = new Step(notes, true, 1);
            this.#drawNeotrellis();
          }
        }
      }
    }
  }

  neotrellisEncoder(diff) {}

  neotrellisEncoderDown() {}

  tick(t, step) {
    this.#step = step;
    const patterns = this.#patterns;
    for (let p = 0; p < 12; p++) {
      const toneInstrument = this.#instruments[this.#tracks[p]].toneInstrument;
      const pattern = patterns[p];
      const cstep = pattern[step];
      if (cstep && cstep.isHead) {
        const notes = cstep.notes;
        for (let i = 0; i < notes.length; i++) {
          const note = notes[i];
          const freq = Tone.Frequency(note.note, "midi");
          toneInstrument.triggerAttackRelease(freq, `0:0:${cstep.length}`, t, note.velocity / 127);
        }
      }
    }
    this.#drawNeotrellis();
  }
}

class Step {
  notes;
  isHead;
  length;

  constructor(notes, isHead, length) {
    this.notes = notes;
    this.isHead = isHead;
    this.length = length;
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
