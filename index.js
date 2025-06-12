const MIDI_KEYBOARD = "LPK"
let macropad = null;
let neotrellis = null;
let midikeyboard = null;

let instrumentsPage = null;
let pianorollPage = null;
let patternPage = null;
let page = null;

let delay = null;
let transport = null;

let step = 0;
const patternLength = 16;

document.addEventListener("click", start);
const screenDiv = document.getElementById("screen");
function info(msg) { screenDiv.innerText = msg }
info("click to start");

async function start() {
  info("started");
  document.removeEventListener("click", start);

  info("initializing ToneJS");
  Tone.setContext(new Tone.Context({ latencyHint: "interactive", lookAhead: 0 }));
  await Tone.start();

  // delay = new Tone.PingPongDelay("4n", 0).toDestination();
  delay = new Tone.Reverb(1).toDestination();
  delay.wet.value = 0.5;

  transport = Tone.getTransport()
  transport.bpm.value = 80;
  transport.swing = 0;
  transport.scheduleRepeat(tick, "16n");
  transport.stop();

  info("requesting midi input");
  const access = await navigator.requestMIDIAccess();
  info("got midi access");
  const inputs = [];
  const outputs = [];
  for (const input of access.inputs.values()) {
    inputs.push(input.name);
    if (input.name.indexOf(MIDI_KEYBOARD) >= 0) {
      midikeyboard = input;
      midikeyboard.addEventListener("midimessage", onKeyboardMidi);
    }
  }
  for (const output of access.outputs.values())
    outputs.push(output.name);
  console.log(`midi inputs: [${inputs.join(", ")}], midi outputs: [${outputs.join(", ")}]`);
  macropad = new Macropad(access, onMacropadEvent);
  neotrellis = new NeoTrellis(access, onNeoTrellisEvent);
  if (!midikeyboard) {
    info(`LPK25 not found, midi inputs: [${inputs.join(", ")}], midi outputs: [${outputs.join(", ")}]`);
    return;
  } else
    info("macropad, neotrellis and LPK25 found");

  transport.start();

  info("loading pages...");

  instrumentsPage = new InstrumentsPage(macropad, neotrellis, screenDiv, delay);
  pianorollPage = new PianoRollPage(macropad, neotrellis, screenDiv, instrumentsPage.instruments);
  patternPage = new PatternPage(macropad, neotrellis, screenDiv, instrumentsPage.instruments);
  page = instrumentsPage;

  info("successfully started");

  page.draw();
}

function onMacropadEvent(macropad, event) {
  if (event.type == Macropad.BUTTON_DOWN) {
    page.macropadButton(event.index);
  } else if (event.type == Macropad.ENCODER) {
    page.macropadEncoder(event.diff);
  } else if (event.type == Macropad.ENCODER_DOWN) {
    page = page == instrumentsPage ? pianorollPage : page == pianorollPage ? patternPage : instrumentsPage;
    page.draw();
  }
}

function onNeoTrellisEvent(neotrellis, event) {
  if (event.type == NeoTrellis.BUTTON_DOWN) {
    page.neotrellisButtonDown(event.index);
  } else if (event.type == NeoTrellis.BUTTON_UP) {
    page.neotrellisButtonUp(event.index);
  } else if (event.type == NeoTrellis.ENCODER) {
    page.neotrellisEncoder(event.diff);
  } else if (event.type == NeoTrellis.ENCODER_DOWN) {
    page.neotrellisEncoderDown();
  }
}

function onKeyboardMidi(msg) {
  const data = msg.data;
  const type = data[0];
  if (type == NOTE_ON)
    page.keyboardOn(data[1], data[2]);
  else if (type == NOTE_OFF)
    page.keyboardOff(data[1]);
}

function tick(t) {
  step = (step + 1) % patternLength;
  page.tick(t, step);
}
