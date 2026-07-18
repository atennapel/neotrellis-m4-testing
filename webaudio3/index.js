const startButton = document.getElementById("start");
const infoDiv = document.getElementById("info");
function info(msg) { console.log(msg); infoDiv.innerText = msg }
startButton.addEventListener("click", init);
let ctx;
async function init() {
  if (!ctx) {
    info("starting...");
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    document.addEventListener("keydown", e => {
      const n = keyToNote(e.key);
      if (n >= 0) down(n);
    });
    document.addEventListener("keyup", e => {
      const n = keyToNote(e.key);
      if (n >= 0) up(n);
    });
    info("started");
    startButton.innerText = "resume";

    // testing
    const notes = new Map();
    const voices = new Map();
    function up(n) {
      if (!notes.get(n)) return;
      notes.set(n, false);
      voices.get(n).stop(ctx.currentTime);
    }
    function down(n) {
      if (notes.get(n)) return;
      notes.set(n, true);
      if (!voices.has(n)) {
        const voice = new Voice(ctx);
        voice.connect(ctx.destination);
        voices.set(n, voice);
      }
      voices.get(n).start(ctx.currentTime, n, 0.8);
    }
  } else if (ctx.state === "suspended") {
    info("resuming...");
    await ctx.resume();
    info("resumed");
  }
}

// voices
class Voice {
  constructor(ctx) {
    this.ctx = ctx;
    const gain = ctx.createGain();
    this.gain = gain;
    gain.gain.value = 0;

    this.osc = null;

    this.attack = 0.2;
    this.hold = 0.05;
    this.decay = 0.2;
    this.sustain = 0.7;
    this.release = 0.6;
  }

  connect(tar) {
    this.gain.connect(tar);
  }

  start(t, note, vol) {
    if (this.osc) stop(t);

    const osc = this.ctx.createOscillator();
    this.osc = osc;
    osc.type = "sine";
    osc.frequency.value = freq(note);
    const gain = this.gain;
    osc.connect(gain);

    const env = gain.gain;
    env.cancelScheduledValues(t);
    env.setValueAtTime(0.0001, t);
    const attack = this.attack;
    const hold = this.hold;
    env.exponentialRampToValueAtTime(vol, t + attack);
    env.setValueAtTime(vol, t + attack + hold);
    env.exponentialRampToValueAtTime(vol * this.sustain, t + attack + hold + this.decay);

    osc.start(t);
  }

  stop(t) {
    const osc = this.osc;
    if (!osc) return;
    const gain = this.gain;
    const env = gain.gain;
    env.cancelAndHoldAtTime(t);
    const release = this.release;
    env.exponentialRampToValueAtTime(0.0001, t + release);
    env.setValueAtTime(0, t + release + 0.001);
    
    osc.onended = () => {
      if (this.osc === osc) this.osc = null;
      osc.disconnect();
    };
    osc.stop(t + this.release + 0.002);
  }
}

// util
function freq(note) {
  return 440 * Math.pow(2, (note - 69) / 12);
}

function keyToNote(k) {
  switch (k) {
    case "z": return 60;
    case "x": return 61;
    case "c": return 62;
    case "v": return 63;
    case "b": return 64;
    case "n": return 65;
    case "m": return 66;
    case ",": return 67;
    case ".": return 68;
    case "/": return 69;
    
    case "a": return 65;
    case "s": return 66;
    case "d": return 67;
    case "f": return 68;
    case "g": return 69;
    case "h": return 70;
    case "j": return 71;
    case "k": return 72;
    case "l": return 73;
    case ";": return 74;
    
    case "q": return 70;
    case "w": return 71;
    case "e": return 72;
    case "r": return 73;
    case "t": return 74;
    case "y": return 75;
    case "u": return 76;
    case "i": return 77;
    case "o": return 78;
    case "p": return 79;

    default: return -1;
  }
}
