#include <math.h>

#include <SPI.h>
#include <SdFat_Adafruit_Fork.h>
#include <Adafruit_InternalFlash.h>
#include <Adafruit_TinyUSB.h>
#include <Adafruit_NeoTrellisM4.h>
#include <Audio.h>
#include <Wire.h>


Adafruit_NeoTrellisM4 trellis = Adafruit_NeoTrellisM4();

// GUItool: begin automatically generated code
AudioSynthWaveform       waveform1;      //xy=254,296
AudioSynthWaveform       waveform2;      //xy=256,342
AudioSynthWaveform       waveform3;      //xy=257,383
AudioPlayMemory          playMem4;       //xy=256,635
AudioPlayMemory          playMem1;       //xy=258,502
AudioSynthWaveform       waveform4;      //xy=259,432
AudioPlayMemory          playMem2;       //xy=261,553
AudioPlayMemory          playMem3;       //xy=268,591
AudioMixer4              mixer1;         //xy=505,317
AudioMixer4              mixer2;         //xy=516,498
AudioMixer4              mixer3;         //xy=681,391
AudioOutputAnalogStereo  dacs1;          //xy=944,342
AudioConnection          patchCord1(waveform1, 0, mixer1, 0);
AudioConnection          patchCord2(waveform2, 0, mixer1, 1);
AudioConnection          patchCord3(waveform3, 0, mixer1, 2);
AudioConnection          patchCord4(playMem4, 0, mixer2, 3);
AudioConnection          patchCord5(playMem1, 0, mixer2, 0);
AudioConnection          patchCord6(waveform4, 0, mixer1, 3);
AudioConnection          patchCord7(playMem2, 0, mixer2, 1);
AudioConnection          patchCord8(playMem3, 0, mixer2, 2);
AudioConnection          patchCord9(mixer1, 0, mixer3, 0);
AudioConnection          patchCord10(mixer2, 0, mixer3, 1);
AudioConnection          patchCord11(mixer3, 0, dacs1, 0);
AudioConnection          patchCord12(mixer3, 0, dacs1, 1);
// GUItool: end automatically generated code

#include "AudioSampleBd01.h"
#include "AudioSampleBd05.h"
#include "AudioSampleCp02.h"
#include "AudioSampleCr01.h"
#include "AudioSampleHh01.h"
#include "AudioSampleOh03.h"
#include "AudioSampleRs01.h"
#include "AudioSampleSd01.h"
const unsigned int* soundData[8] =  {
  AudioSampleBd01, AudioSampleBd05, AudioSampleCp02, AudioSampleCr01,
  AudioSampleHh01, AudioSampleOh03, AudioSampleRs01, AudioSampleSd01
};

// painter BEGIN
int front[32] = {0x0};
int back[32] = {0x0};
void setColor(int pos, int color) {
  // back[pos] = color;
  trellis.setPixelColor(pos, color);
}
void flip() {
  for (int i = 0; i < 32; i++) {
    int f = front[i];
    int b = back[i];
    if (f != b) {
      trellis.setPixelColor(i, b);
      front[i] = b;
    }
  }
  trellis.show();
}
// painter END

int key2note(int key) {
  int x = key % 8;
  int y = key / 8;
  return (3 - y) * 5 + x + 60;
}
float note2freq(int note) {
  return powf(2.0, ((float) note - 69.0) / 12.0) * 440.0;
}
float key2freq(int key) {
  return note2freq(key2note(key));
}

float freqs[32];
void initFreqs() {
  for (int i = 0; i < 32; i++)
    freqs[i] = key2freq(i);
}

bool keys[32] = {false};
int keyWaveforms[32] = {0};

int lastWaveformIx = 0;

AudioSynthWaveform* waveFormIx(int ix) {
  switch (ix) {
    case 0: return &waveform1;
    case 1: return &waveform2;
    case 2: return &waveform3;
    default: return &waveform4;
  }
}

int getNextWaveForm() {
  int ix = lastWaveformIx;
  lastWaveformIx = (ix + 1) % 4;
  return ix;
}

void setup() {
  Serial.begin(115200);
  Serial.println("initializing");

  initFreqs();

  trellis.begin();
  trellis.setBrightness(60);
  trellis.autoUpdateNeoPixels(false);
  trellis.fill(0x0);
  trellis.show();

  AudioMemory(10);
  AudioProcessorUsageMaxReset();
  AudioMemoryUsageMaxReset();

  waveform1.begin(WAVEFORM_SAWTOOTH);
  waveform2.begin(WAVEFORM_SAWTOOTH);
  waveform3.begin(WAVEFORM_SAWTOOTH);
  waveform4.begin(WAVEFORM_SAWTOOTH);

  mixer1.gain(0, 0.25);
  mixer1.gain(1, 0.25);
  mixer1.gain(2, 0.25);
  mixer1.gain(3, 0.25);

  mixer2.gain(0, 0.25);
  mixer2.gain(1, 0.25);
  mixer2.gain(2, 0.25);
  mixer2.gain(3, 0.25);

  mixer3.gain(0, 0.5);
  mixer3.gain(1, 0.5);

  Serial.println("initialization done");
}

unsigned long currentMillis = 0;
int bpm = 120;
int bpmDiff = 60000 / (bpm * 4);
int step = 31;
bool playing = true;
int steps[32] = {0};
int lastStepAdded = 1;
void loop() {
  if (playing) {
    unsigned long nextMillis = millis();
    if (nextMillis - currentMillis >= bpmDiff) {
      step = (step + 1) % 32;
      takeStep(step);
      currentMillis = nextMillis;
    }
  }

  trellis.tick();
  while (trellis.available()) {
    keypadEvent e = trellis.read();
    int key = e.bit.KEY;
    if (e.bit.EVENT == KEY_JUST_PRESSED) {
      int cur = steps[key];
      if (cur == 0) steps[key] = lastStepAdded;
      else {
        int newval = (cur + 1) % 9;
        steps[key] = newval;
        lastStepAdded = newval == 0 ? 1 : newval;
      }
    }
    /*
    if (e.bit.EVENT == KEY_JUST_PRESSED) {
      int wfIx = getNextWaveForm();
      AudioSynthWaveform* wf = waveFormIx(wfIx);
      wf->frequency(freqs[key]);
      wf->amplitude(1);
      keys[key] = true;
      keyWaveforms[key] = wfIx;
    } else if (e.bit.EVENT == KEY_JUST_RELEASED) {
      AudioSynthWaveform* wf = waveFormIx(keyWaveforms[key]);
      wf->amplitude(0);
      keys[key] = false;
    }
    */
  }
  draw();
  // flip();
  trellis.show();
}

void takeStep(int step) {
  int value = steps[step];
  if (value > 0) {
    playMem1.play(soundData[value]);
  }
}

void draw() {
  for (int i = 0; i < 32; i++) {
    int color = 0x0;
    if (keys[i])
      color = 0x0000ff;
    else if (playing && step == i)
      color = 0xff0000;
    else if (steps[i] > 0) {
      switch (steps[i]) {
        case 1: color = 0x00ff00; break;
        case 2: color = 0x00ff00; break;
        case 3: color = 0x0000ff; break;
        case 4: color = 0xffff00; break;
        case 5: color = 0xff00ff; break;
        case 6: color = 0x00ffff; break;
        case 7: color = 0x004400; break;
        case 8: color = 0x000044; break;
      }
    }
    setColor(i, color);
  }
}
