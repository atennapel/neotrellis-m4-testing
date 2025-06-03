class NeoTrellis {
  static MIDI_NAME = "NeoTrellis";
  static NOTE_ON = 144;
  static NOTE_OFF = 128;

  static BUTTON_DOWN = "button_down";
  static BUTTON_UP = "button_up";
  static ENCODER_DOWN = "encoder_down";
  static ENCODER_UP = "encoder_up";
  static ENCODER = "encoder";

  #output;
  #callback;

  #front = Array(32);
  #back = Array(32);

  #pressed = Array(32).fill(false);
  #encoderPressed = false;
  #encoder = 0;

  constructor(midiaccess, callback) {
    this.#callback = callback;
    let inputFound = false;
    for (const input of midiaccess.inputs.values()) {
      if (input.name.indexOf(NeoTrellis.MIDI_NAME) >= 0) {
        input.addEventListener("midimessage", this.#onMidiEvent.bind(this));
        inputFound = true;
        break;
      }
    }
    if (!inputFound) throw new Error("NeoTrellis input not found");
    let outputFound = false;
    for (const output of midiaccess.outputs.values()) {
      if (output.name.indexOf(NeoTrellis.MIDI_NAME) >= 0) {
        this.#output = output;
        outputFound = true;
        break;
      }
    }
    if (!outputFound) throw new Error("NeoTrellis output not found");
    this.reset();
  }

  #onMidiEvent(msg) {
    const pressed = this.#pressed;
    const data = msg.data;
    const type = data[0];
    let event;
    if (type == NeoTrellis.NOTE_ON) {
      const i = data[1];
      if (i < 32) {
        pressed[i] = true;
        event = {type: NeoTrellis.BUTTON_DOWN, index: i};
      } else if (i == 33) {
        this.#encoderPressed = true;
        event = {type: NeoTrellis.ENCODER_DOWN};
      } else if (i == 32) {
        const diff = data[2] - 100;
        this.#encoder += diff;
        event = {type: NeoTrellis.ENCODER, diff: diff};
      }
    } else if (type == NeoTrellis.NOTE_OFF) {
      const i = data[1];
      if (i < 32) {
        pressed[i] = false;
        event = {type: NeoTrellis.BUTTON_UP, index: i};
      } else if (i == 33) {
        this.#encoderPressed = false;
        event = {type: NeoTrellis.ENCODER_UP};
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

  draw() {
    const output = this.#output;
    const front = this.#front;
    const back = this.#back;
    for (let i = 0; i < 32; i++) {
      const b = back[i];
      if (front[i] != b) {
        front[i] = b;
        output.send([NOTE_ON, i, b]);
        console.log("draw", i, b);
      }
    }
  }

  reset() {
    const output = this.#output;
    const front = this.#front;
    const back = this.#back;
    for (let i = 0; i < 32; i++) {
      front[i] = 0;
      back[i] = 0;
      output.send([NOTE_ON, i, 0]);
    }
  }
}
