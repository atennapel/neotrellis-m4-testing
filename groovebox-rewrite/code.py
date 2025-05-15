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
from sequencer import Sequencer
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
    mixer = audiomixer.Mixer(voice_count=8,
                          sample_rate=wav.sample_rate,
                          channel_count=wav.channel_count,
                          bits_per_sample=wav.bits_per_sample,
                          samples_signed=True)
    audio.play(mixer)
samples = []
for f in files:
    wave_file = open(f, "rb")
    sample = audiocore.WaveFile(wave_file)
    samples.append(sample)
def play(i):
   mixer.play(samples[i], voice = i)
# TEMP END

# initialization
trellis = adafruit_trellism4.TrellisM4Express()
pixels = trellis.pixels
pixels.auto_write = True
pixels.brightness = BRIGHTNESS
pixels.fill(0)
pixels.show()

# logic
class Logic:
  def __init__(self, input, painter):
    self.input = input
    self.painter = painter
    self.state = [False] * 32

  def update(self, delta):
    input = self.input
    for button in input.pressed:
      x, y = button
      self.state[x + y * 8] = True
      if x == 7 and y == 3:
        if sequencer.playing:
          sequencer.stop()
        else:
          sequencer.start()

    for button in input.released:
      x, y = button
      self.state[x + y * 8] = False

  def draw(self):
    painter = self.painter
    for i, pressed in enumerate(self.state):
      if sequencer.playing and i == sequencer.step:
        painter.setIndex(i, BLUE)
      else:
        painter.setIndex(i, RED if pressed else OFF)

  def trigger(self, step):
    if step % 4 == 0:
      play(0)
    elif (step + 2) % 4 == 0:
      play(1)

# main loop
input = Input(trellis)
painter = Painter(trellis.pixels)
logic = Logic(input, painter)
sequencer = Sequencer(32, 120, logic)

prevtime = time.monotonic_ns()
while True:
  # calculate delta
  curtime = time.monotonic_ns()
  delta = curtime - prevtime
  prevtime = curtime
  
  # update
  input.update()
  sequencer.update(delta)
  logic.update(delta)
  
  # draw
  logic.draw()
  painter.show()
