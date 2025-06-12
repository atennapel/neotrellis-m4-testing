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

  addNote(note, start, length) {
    let notes = this.#notes[note];
    if (!notes) {
      notes = [];
      this.#notes[note] = notes;
    }
    const row = this.#grid[note];

    // find where to add the new note
    let i = 0;
    for (; i < notes.length; i++) {
      const noteToCheckStart = notes[i].start;
      if (noteToCheckStart == start)
        return false;
      else if (noteToCheckStart > start)
        break;
    }

    // cut short previous note
    const prevIx = i - 1;
    if (prevIx >= 0 && prevIx < notes.length) {
      const prev = notes[prevIx];
      const oldLength = prev.length;
      if (prev.start + oldLength - 1 >= start) {
        prev.length = start - prev.start;
        const lengthToClear = oldLength - prev.length;
        for (let x = start; x < start + lengthToClear; x++)
          row[x] = null;
      }
    }

    // check overlap with next note
    if (i >= 0 && i < notes.length) {
      const next = notes[i];
      if (i == notes.length - 1)
        notes.pop();
      else
        notes.splice(i, 1);
      for (let x = next.start; x < next.start + next.length; x++)
        row[x] = null;
    }

    // add note
    const noteToAdd = new Note(note, start, length);
    if (i == notes.length)
      notes.push(noteToAdd)
    else
      notes.splice(i, 0, noteToAdd);
    const maxLength = this.#length;
    for (let x = start; x < start + length && x < maxLength; x++)
      row[x] = new GridEntry(noteToAdd, x == start);
    return true;
  }

  addChord(notes, start, length) {
    notes.forEach(note => this.addNote(note, start, length));
  }

  removeNote(note, start) {
    const notes = this.#notes[note];
    if (!notes) return;
    let i = 0;
    let length = 1;
    for (; i < notes.length; i++) {
      if (notes[i].start == start) {
        length = notes[i].length;
        break;
      }
    }
    if (i == notes.length) return;
    notes.splice(i, 1);
    const grid = this.#grid;
    for (let i = 0; i < length; i++)
      grid[note][start + i] = null;
  }

  removeChord(notes, start) {
    notes.forEach(note => this.removeNote(note, start));
  }

  get grid() {
    return this.#grid;
  }
}

class Note {
  note;
  start;
  length;

  constructor(note, start, length) {
    this.note = note;
    this.start = start;
    this.length = length;
  }
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
