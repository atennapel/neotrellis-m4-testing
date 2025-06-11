class Macropad {
  static MIDI_NAME = "Macropad";
  static NOTE_ON = 144;
  static NOTE_OFF = 128;

  static BUTTON_DOWN = "button_down";
  static BUTTON_UP = "button_up";
  static ENCODER_DOWN = "encoder_down";
  static ENCODER_UP = "encoder_up";
  static ENCODER = "encoder";

  #output;
  #callback;

  #front = Array(12);
  #back = Array(12);

  #pressed = Array(12).fill(false);
  #encoderPressed = false;
  #encoder = 0;

  constructor(midiaccess, callback) {
    this.#callback = callback;
    let inputFound = false;
    for (const input of midiaccess.inputs.values()) {
      if (input.name.indexOf(Macropad.MIDI_NAME) >= 0) {
        input.addEventListener("midimessage", this.#onMidiEvent.bind(this));
        inputFound = true;
        break;
      }
    }
    if (!inputFound) throw new Error("Macropad input not found");
    let outputFound = false;
    for (const output of midiaccess.outputs.values()) {
      if (output.name.indexOf(Macropad.MIDI_NAME) >= 0) {
        this.#output = output;
        outputFound = true;
        break;
      }
    }
    if (!outputFound) throw new Error("Macropad output not found");
    this.reset();
  }

  #onMidiEvent(msg) {
    const pressed = this.#pressed;
    const data = msg.data;
    const type = data[0];
    let event;
    if (type == Macropad.NOTE_ON) {
      const i = data[1];
      if (i < 12) {
        pressed[i] = true;
        event = {type: Macropad.BUTTON_DOWN, index: i};
      } else if (i == 13) {
        this.#encoderPressed = true;
        event = {type: Macropad.ENCODER_DOWN};
      } else if (i == 12) {
        const diff = data[2] - 100;
        this.#encoder += diff;
        event = {type: Macropad.ENCODER, diff: diff};
      }
    } else if (type == Macropad.NOTE_OFF) {
      const i = data[1];
      if (i < 12) {
        pressed[i] = false;
        event = {type: Macropad.BUTTON_UP, index: i};
      } else if (i == 13) {
        this.#encoderPressed = false;
        event = {type: Macropad.ENCODER_UP};
      }
    }
    this.#callback(this, event);
  }

  isPressed(i) {
    return this.#pressed[i];
  }

  isEncoderPressed() {
    return this.#encoderPressed;
  }

  get encoder() {
    return this.#encoder;
  }

  set(ix, color) {
    this.#back[ix] = color;
  }

  unset(ix) {
    this.#back[ix] = 0;
  }

  clear() {
    const back = this.#back;
    for (let i = 0; i < 12; i++) back[i] = 0;
  }

  draw() {
    const output = this.#output;
    const front = this.#front;
    const back = this.#back;
    //let count = 0;
    for (let i = 0; i < 12; i++) {
      const b = back[i];
      if (front[i] != b) {
        front[i] = b;
        output.send([NOTE_ON, i, b]);
    //    count++;
      }
    }
    //if (count > 0) console.log(`macropad draw: ${count} commands`);
  }

  reset() {
    const output = this.#output;
    const front = this.#front;
    const back = this.#back;
    for (let i = 0; i < 12; i++) {
      front[i] = 0;
      back[i] = 0;
      output.send([NOTE_ON, i, 0]);
    }
  }
}
