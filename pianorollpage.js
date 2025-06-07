class PianoRollPage {
  #macropad;
  #neotrellis;
  #screen;
  #axis = false;
  #x = 0;
  #y = 60;
  #grid;

  constructor(macropad, neotrellis, screen) {
    this.#macropad = macropad;
    this.#neotrellis = neotrellis;
    this.#screen = screen;
    this.#grid = PianoRollPage.#initializeGrid();
  }

  static #initializeGrid() {
    const y = [];
    for (let i = 0; i < 128; i++) {
      const x = [];
      for (let j = 0; j < 32; j++)
        x.push(false);
      y.push(x);
    }
    return y;
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
    const grid = this.#grid;
    for (let x = 0; x < 8; x++) {
      for (let y = 0; y < 4; y++) {
        const value = grid[startY + y][startX + x];
        if (value) neotrellis.set(x + (3 - y) * 8, BLUEH);
      }
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

  neotrellisButton(ix) {
    const x = (ix % 8) + this.#x;
    const y = (3 - Math.floor(ix / 8)) + this.#y;
    this.#grid[y][x] = !this.#grid[y][x];
    this.draw();
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
}
