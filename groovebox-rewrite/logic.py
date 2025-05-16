from sequencer import Sequencer
from painter import *

class Logic:
  def __init__(self, input, painter, player):
    self.input = input
    self.painter = painter
    self.state = [False] * 32
    self.sequencer = Sequencer(64, 120, self)
    self.player = player
    self.value = 8
    self.barShowing = False
    self.pattern = [False] * 64
    self.page = 0

  def update(self, delta):
    self.sequencer.update(delta)

    input = self.input
    for button in input.pressed:
      x, y = button
      self.state[x + y * 8] = True
      if x == 7 and y == 3:
        if self.sequencer.playing:
          self.sequencer.stop()
        else:
          self.sequencer.start()
      elif x == 0 and y == 3:
        self.barShowing = True
      elif y == 2 and x < 4:
        self.page = x
      elif y == 0 and self.barShowing:
        self.value = 0 if x == 0 and self.value == 1 else x + 1
        self.player.setVolume(self.value / 8)
      elif y == 0 or y == 1:
        i = y * 8 + x + self.page * 16
        self.pattern[i] = not self.pattern[i]

    for button in input.released:
      x, y = button
      self.state[x + y * 8] = False
      if x == 0 and y == 3:
        self.barShowing = False

  def draw(self):
    painter = self.painter
    for i, pressed in enumerate(self.state):
      if self.barShowing and i < 8:
        painter.setIndex(i, BLUE if i < self.value else OFF)
      elif self.sequencer.playing and i < 16 and i + self.page * 16 == self.sequencer.step:
        painter.setIndex(i, BLUE)
      elif i < 16 and self.pattern[i + self.page * 16]:
        painter.setIndex(i, GREEN)
      elif i == 16 and self.page == 0:
        painter.setIndex(i, PURPLE)
      elif i == 17 and self.page == 1:
        painter.setIndex(i, PURPLE)
      elif i == 18 and self.page == 2:
        painter.setIndex(i, PURPLE)
      elif i == 19 and self.page == 3:
        painter.setIndex(i, PURPLE)
      else:
        painter.setIndex(i, RED if pressed else OFF)

  def trigger(self, step):
    if self.pattern[step]:
      self.player.play(0)
