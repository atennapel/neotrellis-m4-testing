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
const PINK = 9
const PINKH = 10
const CYAN = 11
const CYANH = 12
const WHITE = 13
const WHITEH = 14

// utility functions
function mod(a, b) {
  return ((a % b) + b) % b;
}

function clamp(min, max, v) {
  return v < min ? min : v > max ? max: v;
}
