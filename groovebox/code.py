import time
import board
import audioio
import adafruit_trellism4
import synthio
import adafruit_wave
import os
from state import State
from ui import UI

BRIGHTNESS = 0.05
KITS_PATH = "/samples"
WAVEFORMS_PATH = KITS_PATH + "/waveforms"

# initialization
trellis = adafruit_trellism4.TrellisM4Express(rotation = 90)
pixels = trellis.pixels
pixels.brightness = BRIGHTNESS
pixels.fill(0)

timestamp = time.monotonic()
print("initializing...")
ui = UI()
state = State(ui, KITS_PATH)
model = state.model
print("total samples: %d" % len(state.voices))

if state.mixer.channel_count == 1:
  audio = audioio.AudioOut(board.A1)
elif state.mixer.channel_count == 2:
  audio = audioio.AudioOut(board.A1, right_channel = board.A0)
else:
  raise RuntimeError("wav files must be mono or stereo")
audio.play(state.mixer)

# Note: synthio.Synthesizer has to be called from code.py, or else it does not seem to play any sound
# and the synths have to be created after the call to audio.play above.
def loadWaveform(file):
  with adafruit_wave.open(file) as w:
    return memoryview(w.readframes(w.getnframes())).cast('h')
waveformsPaths = [WAVEFORMS_PATH + "/" + f for f in os.listdir(WAVEFORMS_PATH) if f.endswith(".wav")][:8]
synths = []
for waveformPath in waveformsPaths:
  waveform = loadWaveform(waveformPath)
  synth = synthio.Synthesizer(channel_count = state.mixer.channel_count, sample_rate = state.mixer.sample_rate, waveform = waveform)
  synths.append(synth)
state.initializeSynths(synths)
print("initialization done, time: %f" % (time.monotonic() - timestamp))

ui.init(trellis.pixels, state)
ui.draw()

# main loop
pressed = set()
while True:
  stamp = time.monotonic()

  state.tick()

  while time.monotonic() - stamp < 60 / (model.bpm * 4):
    newpressed = set(trellis.pressed_keys)
    downs = newpressed - pressed
    ups = pressed - newpressed
    state.input(newpressed, downs, ups)
    pressed = newpressed
