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
    grid.set(i, pressed ? BLUE : WHITE);
  }

  function update(t) {
    grid.draw();
    window.requestAnimationFrame(update);
  }
  update();
}
