import time
import board
import audioio
import audiomixer
import adafruit_trellism4
from util import *
from kits import Kits
from screens import KitScreen

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
wav = kits[0][0]
print("%d channels, %d bits per sample, %d Hz sample rate " %
  (wav.channel_count, wav.bits_per_sample, wav.sample_rate))
if wav.channel_count == 1:
  audio = audioio.AudioOut(board.A1)
elif wav.channel_count == 2:
  audio = audioio.AudioOut(board.A1, right_channel = board.A0)
else:
  raise RuntimeError("wav files must be mono or stereo")
mixer = audiomixer.Mixer(
  voice_count = kits.total_samples,
  sample_rate = wav.sample_rate,
  channel_count = wav.channel_count,
  bits_per_sample = wav.bits_per_sample,
  samples_signed = True
)
audio.play(mixer)
kits.mixer = mixer
print("mixer started")
print("time: %f" % (time.monotonic() - timestamp))

# testing BEGIN
KIT_SELECTION_BUTTON = (3, 4)

sel_page = 0

trellis.pixels[KIT_SELECTION_BUTTON] = GREENH

kitScreen = KitScreen(trellis, kits)
kitScreen.draw()
# testing END

pressed = set()

while True:
  newpressed = set(trellis.pressed_keys)
  for down in newpressed - pressed:
    y = down[0]
    x = down[1]
    if x < 4:
      if KIT_SELECTION_BUTTON in pressed:
        kitScreen.select(ix4x4(y, x))
      else:
        sample_ix = ix4x4b(y, x)
        if kits.available(kitScreen.selected, sample_ix):
          kits.play(kitScreen.selected, sample_ix)
          trellis.pixels[down] = RED
    elif (y, x) == KIT_SELECTION_BUTTON:
      trellis.pixels[down] = GREEN
      kitScreen.drawSelection()
  for up in pressed - newpressed:
    y = up[0]
    x = up[1]
    if x < 4:
      if not (KIT_SELECTION_BUTTON in pressed):
        sample_ix = ix4x4b(y, x)
        if kits.available(kitScreen.selected, sample_ix):
          kits.stop(kitScreen.selected, sample_ix)
          trellis.pixels[up] = BLUEH
    elif (y, x) == KIT_SELECTION_BUTTON:
      trellis.pixels[down] = GREENH
      kitScreen.draw()
  pressed = newpressed
  time.sleep(0.01)
