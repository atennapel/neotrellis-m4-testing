const container = document.getElementById("container");
container.innerText = "click to start";
container.addEventListener("pointerdown", init);
function init() {
  container.removeEventListener("pointerdown", init);
  container.innerText = "";

  Tone.setContext(new Tone.Context({ latencyHint: "interactive", lookAhead: 0 }));
  Tone.start();

  const grid = new Grid(container, gridHandler);
  function gridHandler(i, pressed) {
    console.log("pressed", i, pressed);
  }

  function update(t) {
    for (let i = 0; i < 128; i++) {
      grid.set(i, Math.floor(Math.random() * 9));
    }

    grid.draw();
    window.requestAnimationFrame(update);
  }
  update();
}
