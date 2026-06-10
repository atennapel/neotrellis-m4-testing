const container = document.getElementById("container");

let width = window.innerWidth;
let height = window.innerHeight;
window.addEventListener("resize", function () {
  width = window.innerWidth;
  height = window.innerHeight;
});

const buttons = [];

const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
function note2text(note) {
  const n = note % 12;
  const o = Math.floor(note / 12) - 1;
  return notes[n] + o;
}

for (let i = 0; i < 128; i++) {
  const button = document.createElement("div");
  button.classList.add("button");
  container.appendChild(button);
  buttons.push(button);
  const note = calcNote(i);
  changeColor(i, isWhite(note) ? "white" : "grey");
  button.innerText = note2text(note);
  button.style.color = isWhite(note) ? "grey" : "white";
}

function changeColor(i, color) {
  buttons[i].style.backgroundColor = color;
}

function calcIx(e) {
  const x = Math.min(15, Math.floor((e.pageX / width) * 16));
  const y = Math.min(7, Math.floor((e.pageY / height) * 8));
  const i = y * 16 + x;
  return i;
}

const ongoingTouches = new Map();
const buttonTouches = new Map();
for (let i = 0; i < 128; i++)
  buttonTouches.set(i, new Set());

function handleStart(e) {
  e.preventDefault();
  const id = e.pointerId;
  container.setPointerCapture(id);
  const i = calcIx(e);
  ongoingTouches.set(id, i);
  if (buttonTouches.get(i).size === 0)
    highlightButton(i);
  buttonTouches.get(i).add(id);
}
function handleEnd(e) {
  e.preventDefault();
  const id = e.pointerId;
  if (!ongoingTouches.has(id)) {
    console.error(`End: Could not find touch ${id}`);
    return;
  }
  const i = ongoingTouches.get(id);
  ongoingTouches.delete(id);
  buttonTouches.get(i).delete(id);
  if (buttonTouches.get(i).size === 0)
    resetButton(i);
}
function handleMove(e) {
  e.preventDefault();
  const id = e.pointerId;
  if (!ongoingTouches.has(id))
    return;
  const pi = ongoingTouches.get(id);
  const i = calcIx(e);
  if (pi !== i) {
    ongoingTouches.set(id, i);
    if (buttonTouches.get(i).size === 0)
      highlightButton(i);
    buttonTouches.get(i).add(id);

    buttonTouches.get(pi).delete(id);
    if (buttonTouches.get(pi).size === 0)
      resetButton(pi);
  }
}

container.addEventListener("pointerdown", e => handleStart(e));
container.addEventListener("pointerup", e => handleEnd(e));
container.addEventListener("pointercancel", e => handleEnd(e));
container.addEventListener("pointermove", e => handleMove(e));

let synth;

container.addEventListener("pointerdown", init);
function init() {
  Tone.setContext(new Tone.Context({ latencyHint: "interactive", lookAhead: 0 }));
  Tone.start();
  synth = new Tone.PolySynth(Tone.Synth).toDestination();
  synth.maxPolyphony = 10;
  container.removeEventListener("pointerdown", init);
}

function calcNote(i) {
  const x = i % 16;
  const y = 7 - Math.floor(i / 16);
  return 60 - 24 + x + (y * 5);
}
function trigger(note) {
  if (!synth) return;
  const freq = Tone.Frequency(note, "midi");
  synth.triggerAttack(freq, Tone.now(), 0.8);
}
function release(note) {
  const freq = Tone.Frequency(note, "midi");
  synth.triggerRelease(freq);
}

function resetButton(i) {
  const note = calcNote(i);
  changeColor(i, isWhite(note) ? "white" : "grey");
  release(note);
}
function highlightButton(i) {
  const note = calcNote(i);
  changeColor(i, isWhite(note) ? "lightblue" : "darkblue");
  trigger(note);
}

function isWhite(note) {
  const n = note % 12;
  return n === 0 || n === 2 || n === 4 || n === 5 || n === 7 || n === 9 || n === 11;
}
