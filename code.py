import time
import board
import audioio
import adafruit_trellism4
from util import *
from kits import Kits
from screens import MainScreen

trellis = adafruit_trellism4.TrellisM4Express(rotation = 90)
trellis.pixels.brightness = 0.05
trellis.pixels.fill(0)

timestamp = time.monotonic()
print("load kits...")
kits = Kits("/samples")
print("%d kit(s) loaded" % len(kits))
print("total samples: %d" % kits.total_samples)
print("time: %f" % (time.monotonic() - timestamp))

timestamp = time.monotonic()
print("start mixer...")
mixer = kits.initMixer()
if kits.channel_count == 1:
  audio = audioio.AudioOut(board.A1)
elif kits.channel_count == 2:
  audio = audioio.AudioOut(board.A1, right_channel = board.A0)
else:
  raise RuntimeError("wav files must be mono or stereo")
audio.play(mixer)
print("mixer started")
print("time: %f" % (time.monotonic() - timestamp))

screen = MainScreen(trellis, kits)
screen.draw()

pressed = set()

while True:
  newpressed = set(trellis.pressed_keys)
  downs = newpressed - pressed
  ups = pressed - newpressed
  screen.input(newpressed, downs, ups)
  pressed = newpressed
  time.sleep(0.01)
