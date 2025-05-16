import time
import board
import audiocore
import audioio
import audiomixer
import adafruit_trellism4
import synthio
import adafruit_wave
import os

from input import Input
from logic import Logic
from painter import *

BRIGHTNESS = 0.05

# TEMP BEGIN
files = ["/samples/" + f for f in os.listdir("/samples") if f.endswith(".wav")]
files.sort()
print(files)
with open(files[0], "rb") as f:
  wav = audiocore.WaveFile(f)
  print("%d channels, %d bits per sample, %d Hz sample rate " %
        (wav.channel_count, wav.bits_per_sample, wav.sample_rate))
  if wav.channel_count == 1:
    audio = audioio.AudioOut(board.A1)
  elif wav.channel_count == 2:
    audio = audioio.AudioOut(board.A1, right_channel=board.A0)
  else:
    raise RuntimeError("Must be mono or stereo waves!")
  mixer = audiomixer.Mixer(
    voice_count=8,
    sample_rate=wav.sample_rate,
    channel_count=wav.channel_count,
    bits_per_sample=wav.bits_per_sample,
    samples_signed=True
  )
  audio.play(mixer)
samples = []
for f in files:
  wave_file = open(f, "rb")
  sample = audiocore.WaveFile(wave_file)
  samples.append(sample)
class Player:
  def __init__(self, mixer, samples):
    self.mixer = mixer
    self.samples = samples

  def play(self, i):
    self.mixer.play(self.samples[i], voice = i)

  def setVolume(self, v):
    for i in range(8):
      self.mixer.voice[i].level = v
# TEMP END

# initialization
trellis = adafruit_trellism4.TrellisM4Express()
pixels = trellis.pixels
pixels.auto_write = True
pixels.brightness = BRIGHTNESS
pixels.fill(0)
pixels.show()

# main loop
input = Input(trellis)
painter = Painter(trellis.pixels)
logic = Logic(input, painter, Player(mixer, samples))

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
