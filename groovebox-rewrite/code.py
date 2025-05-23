import time
import board
import audiocore
import audioio
import audiomixer
import adafruit_trellism4
import synthio
import adafruit_wave
import os
from adafruit_seesaw import digitalio, neopixel, rotaryio, seesaw

from model import Model
from instruments import Instruments
from input import Input
from logic import Logic
from painter import *

SEESAW_ADDR = 0x36
ENCODER_PRODUCT = 4991
ENCODER_BUTTON_PIN = 24
BRIGHTNESS = 0.05
KITS_PATH = "/samples"
WAVEFORMS_PATH = KITS_PATH + "/waveforms"

# initialization
trellis = adafruit_trellism4.TrellisM4Express()
pixels = trellis.pixels
pixels.auto_write = True
pixels.brightness = BRIGHTNESS
pixels.fill(0)
pixels.show()

i2c = board.STEMMA_I2C()
seesaw = seesaw.Seesaw(i2c, addr = SEESAW_ADDR)
if (seesaw.get_version() >> 16) & 0xFFFF != ENCODER_PRODUCT:
  print("Failed to load seesaw, wrong product")
seesaw.pin_mode(ENCODER_BUTTON_PIN, seesaw.INPUT_PULLUP)
encoder_button = digitalio.DigitalIO(seesaw, ENCODER_BUTTON_PIN)
encoder = rotaryio.IncrementalEncoder(seesaw)
encoder_pixel = neopixel.NeoPixel(seesaw, 6, 1)
encoder_pixel.brightness = BRIGHTNESS

# loading instruments
timestamp = time.monotonic()
print("initializing...")
model = Model()
instruments = Instruments(KITS_PATH, model)
print("total samples: %d" % len(instruments.voices))

if instruments.mixer.channel_count == 1:
  audio = audioio.AudioOut(board.A1)
elif instruments.mixer.channel_count == 2:
  audio = audioio.AudioOut(board.A1, right_channel = board.A0)
else:
  raise RuntimeError("wav files must be mono or stereo")
audio.play(instruments.mixer)

# Note: synthio.Synthesizer has to be called from code.py, or else it does not seem to play any sound
# and the synths have to be created after the call to audio.play above.
def loadWaveform(file):
  with adafruit_wave.open(file) as w:
    return memoryview(w.readframes(w.getnframes())).cast('h')
waveformsPaths = [WAVEFORMS_PATH + "/" + f for f in os.listdir(WAVEFORMS_PATH) if f.endswith(".wav")][:8]
synths = []
for waveformPath in waveformsPaths:
  waveform = loadWaveform(waveformPath)
  synth = synthio.Synthesizer(channel_count = instruments.mixer.channel_count, sample_rate = instruments.mixer.sample_rate, waveform = waveform)
  synths.append(synth)
instruments.initializeSynths(synths)
print("initialization done, time: %f" % (time.monotonic() - timestamp))

# main loop
input = Input(trellis, encoder, encoder_button)
painter = Painter(trellis.pixels, encoder_pixel)
logic = Logic(input, painter, model, instruments)

prevtime = time.monotonic_ns()
while True:
  # calculate delta
  curtime = time.monotonic_ns()
  delta = curtime - prevtime
  prevtime = curtime
  
  # update
  input.update()
  logic.update(delta)

  # draw
  logic.draw()
  painter.show()
