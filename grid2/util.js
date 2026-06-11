// colors
const WHITE = 0;
const BLACK = 1;
const RED = 2;
const PINK = 3;
const GREEN = 4;
const BLUE = 5;
const YELLOW = 6;
const PURPLE = 7;
const CYAN = 8;
const GREY = 9;
const DARKBLUE = 10;

const COLORS = ["white", "black", "red", "pink", "green", "blue", "yellow", "purple", "cyan", "grey", "darkblue"];

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
  return v < min ? min : v > max ? max : v;
}

// kits
const KITS = [
  "4OP-FM",
  "Bongos",
  "CR78",
  "KPR77",
  "Kit3",
  "Kit8",
  "LINN",
  "R8",
  "Stark",
  "Techno",
  "TheCheebacabra1",
  "TheCheebacabra2",
  "acoustic-kit",
  "breakbeat13",
  "breakbeat8",
  "breakbeat9",
];
