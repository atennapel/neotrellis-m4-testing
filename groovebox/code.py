import time
import board
import audioio
import adafruit_trellism4
import synthio
from state import State
from ui import UI

BRIGHTNESS = 0.05

# initialization
trellis = adafruit_trellism4.TrellisM4Express(rotation = 90)
pixels = trellis.pixels
pixels.brightness = BRIGHTNESS
pixels.fill(0)

timestamp = time.monotonic()
print("initializing...")
ui = UI()
state = State(ui, "/samples")
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
synths = []
for _ in range(8):
  synth = synthio.Synthesizer(channel_count = state.mixer.channel_count, sample_rate = state.mixer.sample_rate)
  synths.append(synth)
state.initializeSynths(synths)
print("initialization done, time: %f" % (time.monotonic() - timestamp))

ui.draw(pixels, state)

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
