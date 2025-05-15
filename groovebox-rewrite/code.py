import time
import board
import audioio
import adafruit_trellism4
import synthio
import adafruit_wave
import os

from input import Input
from painter import *

BRIGHTNESS = 0.05

# initialization
trellis = adafruit_trellism4.TrellisM4Express()
pixels = trellis.pixels
pixels.auto_write = True
pixels.brightness = BRIGHTNESS
pixels.fill(0)
pixels.show()

# logic
state = [False] * 32

def update(input, delta):
  for button in input.pressed:
    state[button[0] + button[1] * 8] = True
  for button in input.released:
    state[button[0] + button[1] * 8] = False

def draw(painter):
  for i, pressed in enumerate(state):
    painter.setIndex(i, RED if pressed else OFF)

# main loop
input = Input(trellis)
painter = Painter(trellis.pixels)
prevtime = time.monotonic_ns()
while True:
  # calculate delta
  curtime = time.monotonic_ns()
  delta = curtime - prevtime
  prevtime = curtime
  
  # update
  input.update()
  update(input, delta)
  
  # draw
  draw(painter)
  painter.draw()
