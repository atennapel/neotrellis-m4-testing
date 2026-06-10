// MIDI
const NOTE_ON = 144;
const NOTE_OFF = 128;

// scales
const MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11];

// colors
const OFF = 0
const RED = 1
const REDH = 2
const GREEN = 3
const GREENH = 4
const BLUE = 5
const BLUEH = 6
const YELLOW = 7
const YELLOWH = 8
const PURPLE = 9
const PURPLEH = 10
const CYAN = 11
const CYANH = 12
const WHITE = 13
const WHITEH = 14

// scales (must contain only the numbers 0-11 and be in ascending order)
const CHROMATIC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
const MAJOR = [0, 2, 4, 5, 7, 9, 11];
const MINOR = [0, 2, 3, 5, 7, 8, 10];
const MAJOR_PENTATONIC = [0, 2, 4, 7, 9];
const MINOR_PENTATONIC = [0, 3, 4, 5, 10];

// utility functions
function mod(a, b) {
  return ((a % b) + b) % b;
}

function clamp(min, max, v) {
  return v < min ? min : v > max ? max: v;
}
