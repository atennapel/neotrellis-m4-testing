class Grid {
  #container;
  #eventHandler;

  #buttons = Array(128);
  #pressed = Array(128).fill(false);
  #buttonTouches;

  #front = Array(128).fill(0);
  #back = Array(128).fill(0);

  constructor(container, eventHandler) {
    this.#container = container;
    this.#eventHandler = eventHandler;

    const ongoingTouches = new Map();
    const buttonTouches = new Map();
    this.#buttonTouches = buttonTouches;

    for (let i = 0; i < 128; i++) {
      const button = document.createElement("div");
      button.classList.add("button");
      container.appendChild(button);
      this.#buttons[i] = button;
      buttonTouches.set(i, new Set());
    }

    function handleStart(grid, e) {
      e.preventDefault();
      const id = e.pointerId;
      container.setPointerCapture(id);
      const i = Grid.#calcIx(e);
      ongoingTouches.set(id, i);
      if (buttonTouches.get(i).size === 0) {
        grid.#pressed[i] = true;
        eventHandler(i, true);
      }
      buttonTouches.get(i).add(id);
    }
    function handleEnd(grid, e) {
      e.preventDefault();
      const id = e.pointerId;
      if (!ongoingTouches.has(id)) {
        console.error(`End: Could not find touch ${id}`);
        return;
      }
      const i = ongoingTouches.get(id);
      ongoingTouches.delete(id);
      buttonTouches.get(i).delete(id);
      if (buttonTouches.get(i).size === 0) {
        grid.#pressed[i] = false;
        eventHandler(i, false);
      }
    }
    function handleMove(grid, e) {
      e.preventDefault();
      const id = e.pointerId;
      if (!ongoingTouches.has(id))
        return;
      const pi = ongoingTouches.get(id);
      const i = Grid.#calcIx(e);
      if (pi !== i) {
        buttonTouches.get(pi).delete(id);
        if (buttonTouches.get(pi).size === 0) {
          grid.#pressed[pi] = false;
          eventHandler(pi, false);
        }

        ongoingTouches.set(id, i);
        if (buttonTouches.get(i).size === 0) {
          grid.#pressed[i] = true;
          eventHandler(i, true);
        }
        buttonTouches.get(i).add(id);
      }
    }

    container.addEventListener("pointerdown", e => handleStart(this, e));
    container.addEventListener("pointerup", e => handleEnd(this, e));
    container.addEventListener("pointercancel", e => handleEnd(this, e));
    container.addEventListener("pointermove", e => handleMove(this, e));
  }

  isPressed(i) {
    return this.#pressed[i];
  }

  set(ix, color) {
    this.#back[ix] = color;
  }

  unset(ix) {
    this.#back[ix] = 0;
  }

  clear() {
    const back = this.#back;
    for (let i = 0; i < 128; i++) back[i] = 0;
  }

  draw() {
    const buttons = this.#buttons;
    const front = this.#front;
    const back = this.#back;
    for (let i = 0; i < 128; i++) {
      const b = back[i];
      if (front[i] != b) {
        front[i] = b;
        buttons[i].style.backgroundColor = COLORS[b];
      }
    }
  }

  reset() {
    const buttons = this.#buttons;
    const front = this.#front;
    const back = this.#back;
    for (let i = 0; i < 32; i++) {
      front[i] = 0;
      back[i] = 0;
      buttons[i].style.backgroundColor = COLORS[0];
    }
  }

  static #calcIx(e) {
    const x = Math.max(0, Math.min(15, Math.floor((e.pageX / window.innerWidth) * 16)));
    const y = Math.max(0, Math.min(7, Math.floor((e.pageY / window.innerHeight) * 8)));
    const i = y * 16 + x;
    return i;
  }

  static fromPos(x, y) {
    return y * 16 + x;
  }
}