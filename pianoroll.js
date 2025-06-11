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
        row[x] = null;
      grid[y] = row;
    }
    return grid;
  }

  get length() {
    return this.#length;
  }

  // TODO: do not allow overlap!
  addNote(note, start, length) {
    let notes = this.#notes[note];
    if (!notes) {
      notes = [];
      this.#notes[note] = notes;
    }
    let i = 0;
    for (; i < notes.length; i++) {
      const noteToCheckStart = notes[i].start;
      if (noteToCheckStart == start)
        return false;
      else if (noteToCheckStart > start)
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
      row[x] = new GridEntry(noteToAdd, x == start);
    return true;
  }

  removeNote(note, start) {
    const notes = this.#notes[note];
    let i = 0;
    let length = 1;
    for (; i < notes.length; i++) {
      if (notes[i].start == start) {
        length = notes[i].length;
        break;
      }
    }
    notes.splice(i, 1);
    const grid = this.#grid;
    for (let i = 0; i < length; i++)
      grid[note][start + i] = null;
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

class GridEntry {
  #note;
  #isHead;

  constructor(note, isHead) {
    this.#note = note;
    this.#isHead = isHead;
  }

  get note() { return this.#note }
  get isHead() { return this.#isHead }
}
