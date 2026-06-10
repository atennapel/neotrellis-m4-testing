const container = document.getElementById("container");
//container.addEventListener("pointermove", pointerMove);
//container.addEventListener("pointerdown", pointerDown);
//container.addEventListener("pointerup", pointerUp);

let width = window.innerWidth;
let height = window.innerHeight;
window.addEventListener("resize", function () {
  width = window.innerWidth;
  height = window.innerHeight;
});

const buttons = [];

for (let i = 0; i < 128; i++) {
  const button = document.createElement("div");
  button.classList.add("button");
  container.appendChild(button);
  buttons.push(button);
}

function changeColor(i, color) {
  buttons[i].style.backgroundColor = color;
}
function resetButton(i) {
  changeColor(i, "white");
}
function highlightButton(i) {
  changeColor(i, "lightblue");
}

function calcIx(e, ox = 0, oy = 0) {
  const x = Math.floor(((e.pageX + ox) / width) * 16);
  const y = Math.floor(((e.pageY + oy) / height) * 8);
  const i = y * 16 + x;
  return i;
}

function pointerMove(e) {
  const i = calcIx(e);
  const pi = calcIx(e, -e.movementX, -e.movementY);
  if (e.buttons === 1) {
    highlightButton(i);
    if (pi !== i) resetButton(pi);
  } else {
    resetButton(i);
  }
}

function pointerDown(e) {
  const i = calcIx(e);
  highlightButton(i);
}

function pointerUp(e) {
  const i = calcIx(e);
  resetButton(i);
}

const ongoingTouches = new Map();
const buttonTouches = new Map();
for (let i = 0; i < 128; i++)
  buttonTouches.set(i, new Set());

function handleStart(e) {
  e.preventDefault();
  for (const changedTouch of e.changedTouches) {
    const id = changedTouch.identifier;
    const i = calcIx(e);
    ongoingTouches.set(id, i);
    buttonTouches.get(i).add(id);
    highlightButton(i);
  }
}
function handleEnd(e) {
  e.preventDefault();
  for (const changedTouch of e.changedTouches) {
    const id = changedTouch.identifier;
    if (!ongoingTouches.has(id)) {
      console.error(`End: Could not find touch ${id}`);
      continue;
    }
    const i = ongoingTouches.get(id);
    ongoingTouches.delete(id);
    buttonTouches.get(i).delete(id);
    if (buttonTouches.get(i).size === 0)
      resetButton(i);
  }
}
function handleCancel(e) {
  e.preventDefault();
  for (const changedTouch of e.changedTouches) {
    const id = changedTouch.identifier;
    if (!ongoingTouches.has(id)) {
      console.error(`Cancel: Could not find touch ${id}`);
      continue;
    }
    const i = ongoingTouches.get(id);
    ongoingTouches.delete(id);
    buttonTouches.get(i).delete(id);
    if (buttonTouches.get(i).size === 0)
      resetButton(i);
  }
}
function handleMove(e) {
  e.preventDefault();
  for (const changedTouch of e.changedTouches) {
    const id = changedTouch.identifier;
    if (!ongoingTouches.has(id)) {
      console.error(`Move: Could not find touch ${id}`);
      continue;
    }
    const pi = ongoingTouches.get(id);
    const i = calcIx(e);
    ongoingTouches.set(id, i);
    buttonTouches.get(i).add(id);
    if (pi !== i) {
      buttonTouches.get(pi).delete(id);
      if (buttonTouches.get(pi).size === 0)
        resetButton(pi);
    }
  }
}

container.addEventListener("touchstart", handleStart);
container.addEventListener("touchend", handleEnd);
container.addEventListener("touchcancel", handleCancel);
container.addEventListener("touchmove", handleMove);
