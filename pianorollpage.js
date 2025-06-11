class PianoRollPage {
  #macropad;
  #neotrellis;
  #screen;
  #axis = false;
  #x = 0;
  #y = 60;
  #pianoroll;
  #selStart = -1;
  #selEnd = -1;
  #step = 0;

  constructor(macropad, neotrellis, screen) {
    this.#macropad = macropad;
    this.#neotrellis = neotrellis;
    this.#screen = screen;
    this.#pianoroll = new PianoRoll(32);
  }

  #drawMacropad() {
    const macropad = this.#macropad;
    macropad.clear();
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
        if (value > 0)
          neotrellis.set(x + (3 - y) * 8, value == 1 ? BLUEH : CYANH);
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
    if (step >= startX && step < startX + 8) {
      const x = step - startX;
      for (let y = 0; y < 4; y++)
        neotrellis.set(y * 8 + x, REDH);
    }
    neotrellis.draw();
  }

  #text() {
    return `piano roll page\naxis: ${this.#axis ? "x" : "y"}\nx, y: ${this.#x}, ${this.#y}`;
  }

  #drawText() {
    this.#screen.innerText = this.#text();
  }

  draw() {
    this.#drawMacropad();
    this.#drawNeotrellis();
    this.#drawText();
  }

  macropadButton(ix) {}
  macropadEncoder(diff) {}

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
    this.draw();
  }

  neotrellisButtonUp(ix) {
    const start = this.#selStart;
    const end = this.#selEnd;
    if (ix == start) {
      if (end == -1) {
        this.#selStart = -1;
        const note = (3 - Math.floor(ix / 8)) + this.#y;
        const step = (ix % 8) + this.#x;
        this.#pianoroll.addNote(note, step, 1);
        this.draw();
      } else {
        this.#selStart = -1;
        this.#selEnd = -1;
        const note = (3 - Math.floor(ix / 8)) + this.#y;
        const step = (ix % 8) + this.#x;
        this.#pianoroll.addNote(note, step, end - start + 1);
        this.draw();
      }
    } else if (ix == end) {
      this.#selEnd = -1;
      this.draw();
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
    this.draw();
  }

  neotrellisEncoderDown() {
    this.#axis = !this.#axis;
    this.draw();
  }

  tick(t, step) {
    this.#step = step;
    this.draw();
  }
}
