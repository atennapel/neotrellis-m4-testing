class PianoRoll {
  #length;
  #notes = {};
  #grid;

  constructor(length) {
    this.#length = length;
    this.#grid = PianoRoll.#initializeGrid(length);
  }

  static #initializeGrid(length) {
    const grid = Array(128);
    for (let y = 0; y < 128; y++) {
      const row = Array(length);
      for (let x = 0; x < length; x++)
        row[x] = 0;
      grid[y] = row;
    }
    return grid;
  }

  get length() {
    return this.#length;
  }

  addNote(note, start, length) {
    let notes = this.#notes[note];
    if (!notes) {
      notes = [];
      this.#notes[note] = notes;
    }
    let i = 0;
    for (; i < notes.length; i++) {
      const noteToCheck = notes[i];
      if (noteToCheck.start > start)
        break;
    }
    const noteToAdd = new Note(note, start, length);
    if (i == notes.length)
      notes.push(noteToAdd)
    else
      notes.splice(i, 0, noteToAdd);
    const maxLength = this.#length;
    const row = this.#grid[note];
    for (let x = start; x < start + length && x < maxLength; x++)
      row[x] = x == start ? 1 : 2;
  }

  get grid() {
    return this.#grid;
  }
}

class Note {
  #note;
  #start;
  #length;

  constructor(note, start, length) {
    this.#note = note;
    this.#start = start;
    this.#length = length;
  }

  get note() { return this.#note }
  get start() { return this.#start }
  get length() { return this.#length }
}
