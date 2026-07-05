class Node {
  get inputs() {
    return [];
  }

  get outputs() {
    return [];
  }

  init(ctx) {
    return { inputs: [], outputs: [] };
  }

  start(ctx) {}

  stop(ctx) {}
}

class FrequencyNode extends Node {
  constructor(output, value) {
    super();
    this.output = output;
    this.value = value;
  }

  get inputs() {
    return [];
  }

  get outputs() {
    return [this.output];
  }

  init(ctx) {
    return { inputs: [], outputs: [this.value] };
  }
}

class OscNode extends Node {
    constructor(input, output, type) {
      super();
      this.input = input;
      this.output = output;
      this.type = type;
    }

    get inputs() {
      return [this.input];
    }

    get outputs() {
      return [this.output];
    }

    init(ctx) {
      const gain = ctx.createGain();
      gain.gain.value = 1;
      const osc = ctx.createOscillator();
      osc.frequency.value = 440;
      osc.type = "sine";
      osc.connect(gain);
      this.osc = osc;
      return { inputs: [osc.frequency], outputs: [gain] };
    }

    start(ctx, time) {
      this.osc.start(time);
    }
}

const nodes = [
  new FrequencyNode(1, 440),
  new OscNode(1, 0, "sine"),
];

document.getElementById("start").addEventListener("click", init);

async function init() {
  const ctx = new AudioContext();

  const master = ctx.createGain();
  master.gain.value = 0.8;
  master.connect(ctx.destination);

  const nodeInit = nodes.map(n => n.init(ctx));

  const portMap = new Map();
  let i = 0;
  for (const node of nodes) {
    const init = nodeInit[i++];
    let j = 0;
    for (const input of node.inputs) {
      if (!portMap.has(input)) portMap.set(input, []);
      portMap.get(input).push(init.inputs[j++]);
    }
  }

  i = 0;
  for (const node of nodes) {
    const init = nodeInit[i++];
    let j = 0;
    for (const output of node.outputs) {
      const outputInit = init.outputs[j++];
      if (output === 0) {
        outputInit.connect(master);
      } else {
        if (typeof outputInit === "number") {
          if (portMap.has(output)) {
            const inputs = portMap.get(output);
            for (const input of inputs) {
              console.log("connect", outputInit, input);
              input.value = outputInit;
            }
          }
        } else {
          if (portMap.has(output)) {
            const inputs = portMap.get(output);
            for (const input of inputs) {
              console.log("connect", outputInit, input);
              outputInit.connect(input);
            }
          }
        }
      }
    }
  }

  const now = ctx.currentTime;
  nodes.forEach(n => n.start(ctx, now));
}
