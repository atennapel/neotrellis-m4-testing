class PianoRollPage {
  #macropad;
  #neotrellis;
  #screen;
  #instruments;

  #tracks = Array(12).fill(0);
  #track = 0;
  #pianorolls;
  #pianoroll;

  #axis = false;
  #x = 0;
  #y = 60;
  #selStart = -1;
  #selEnd = -1;
  #step = 0;

  constructor(macropad, neotrellis, screen, instruments) {
    this.#macropad = macropad;
    this.#neotrellis = neotrellis;
    this.#screen = screen;
    this.#instruments = instruments;

    this.#pianorolls = Array(12)
    for (let i = 0; i < 12; i++)
      this.#pianorolls[i] = new PianoRoll(patternLength);
    this.#pianoroll = this.#pianorolls[this.#track];
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
    const startX = this.#x;
    const startY = this.#y;
    const grid = this.#pianoroll.grid;
    for (let x = 0; x < 8; x++) {
      for (let y = 0; y < 4; y++) {
        const value = grid[y + startY][x + startX];
        if (value != null)
          neotrellis.set(x + (3 - y) * 8, value.isHead ? BLUEH : CYANH);
      }
    }
    const start = this.#selStart;
    const end = this.#selEnd;
    if (start != -1)
      neotrellis.set(start, BLUE);
    if (end != -1) {
      for (let i = start + 1; i <= end; i++)
        neotrellis.set(i, CYAN);
    }
    const step = this.#step
    if (step >= startX && step < startX + 8) {
      const x = step - startX;
      for (let y = 0; y < 4; y++)
        neotrellis.set(y * 8 + x, REDH);
    }
    neotrellis.draw();
  }

  #text() {
    return `piano roll page\ntrack: ${this.#track + 1}\ninstrument: ${this.#tracks[this.#track] + 1}\naxis: ${this.#axis ? "x" : "y"}\nx, y: ${this.#x}, ${this.#y}`;
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
    this.#pianoroll = this.#pianorolls[ix];
    this.#drawMacropad();
    this.#drawText();
  }

  macropadEncoder(diff) {
    const track = this.#track;
    this.#tracks[track]  = mod(this.#tracks[track] + diff, 12);
    this.#drawText();
  }

  keyboardOn(note, velocity) {}
  keyboardOff(note) {}

  neotrellisButtonDown(ix) {
    const start = this.#selStart;
    if (start == -1)
      this.#selStart = ix;
    else {
      const [x1, y1] = NeoTrellis.getPosition(start);
      const [x2, y2] = NeoTrellis.getPosition(ix);
      if (y1 == y2 && x2 > x1)
        this.#selEnd = ix;
    }
    this.#drawNeotrellis();
  }

  neotrellisButtonUp(ix) {
    const start = this.#selStart;
    const end = this.#selEnd;
    if (ix == start) {
      if (end == -1) {
        const x = this.#x + (ix % 8);
        const y = this.#y + (3 - Math.floor(ix / 8))
        const gridValue = this.#pianoroll.grid[y][x];
        if (gridValue && gridValue.isHead) {
          this.#selStart = -1;
          this.#pianoroll.removeNote(y, x);
          this.#drawNeotrellis();
        } else {
          this.#selStart = -1;
          const note = (3 - Math.floor(ix / 8)) + this.#y;
          const step = (ix % 8) + this.#x;
          this.#pianoroll.addNote(note, step, 1);
          this.#drawNeotrellis();
        }
      } else {
        this.#selStart = -1;
        this.#selEnd = -1;
        const note = (3 - Math.floor(ix / 8)) + this.#y;
        const step = (ix % 8) + this.#x;
        this.#pianoroll.addNote(note, step, end - start + 1);
        this.#drawNeotrellis();
      }
    } else if (ix == end) {
      this.#selEnd = -1;
      this.#drawNeotrellis();
    }
  }

  neotrellisEncoder(diff) {
    if (this.#axis) {
      const x = this.#x + diff;
      if (x >= 0 && x <= 24)
        this.#x = x;
    } else {
      const y = this.#y + diff;
      if (y >= 0 && y <= 124)
        this.#y = y;
    }
    this.#drawText();
    this.#drawNeotrellis();
  }

  neotrellisEncoderDown() {
    this.#axis = !this.#axis;
    this.#drawText();
  }

  tick(t, step) {
    this.#step = step;
    for (let i = 0; i < 128; i++) {
      for (let track = 0; track < 12; track++) {
        const toneInstrument = this.#instruments[this.#tracks[track]].toneInstrument;
        const gridValue = this.#pianorolls[track].grid[i][step];
        if (gridValue && gridValue.isHead) {
          const freq = Tone.Frequency(i, "midi");
          toneInstrument.triggerAttackRelease(freq, `0:0:${gridValue.note.length}`, t, 1);
        }
      }
    }
    this.#drawNeotrellis();
  }
}
