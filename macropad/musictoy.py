from adafruit_macropad import MacroPad
import board
import array
import math
import time

RED = (255, 0, 0)
OFF = 0

transpose = 0

def freq(note):
  return pow(2, (note - 69) / 12) * 440

MAJOR_MASK = [
  16, 17, 19,
  11, 12, 14,
  5, 7, 9,
  0, 2, 4
]
MINOR_MASK = [
  15, 17, 19,
  10, 12, 14,
  5, 7, 8,
  0, 2, 3
]
CHROMATIC_MASK = [
  9, 10, 11,
  6, 7, 8,
  3, 4, 5,
  0, 1, 2
]
MAJOR_MASK_H = [
  0, 7, 14,
  2, 9, 16,
  4, 11, 17,
  5, 12, 19
]
MINOR_MASK_H = [
  0, 7, 14,
  2, 8, 15,
  3, 10, 17,
  5, 12, 19
]
CHROMATIC_MASK_H = [
  0, 4, 8,
  1, 5, 9,
  2, 6, 10,
  3, 7, 11
]
masks = [MAJOR_MASK, MINOR_MASK, CHROMATIC_MASK, MAJOR_MASK_H, MINOR_MASK_H, CHROMATIC_MASK_H]
masks_len = len(masks)
mask_texts = ["major", "minor", "chromatic", "major h", "minor h", "chromatic h"]

mask_ix = 0
mask = masks[mask_ix]
mask_text = mask_texts[mask_ix]

def key2note(key):
  return mask[key] + 60 + transpose

def key2freq(key):
  return freq(key2note(key))

macropad = MacroPad()
text = macropad.display_text(title="  Music")

selection = 0
mode = 0
modes_len = 4
channel = 0

def selStr(s):
  return "> " if s == selection else "  "

def display():
  text[0].text = selStr(0) + "Transpose: " + str(transpose)
  text[1].text = selStr(1) + "Scale: " + mask_text
  text[2].text = selStr(2) + "Mode: " + ("speaker" if mode == 0 else "midi")
  text[3].text = selStr(3) + "Channel: " + str(channel)
  text.show()

display()

keys = []

def stop_all():
  if mode == 0:
    if keys:
      macropad.stop_tone()
  elif mode == 1:
    for k in keys:
      macropad.midi.send(macropad.NoteOff(key2note(k), channel = channel))

def retrigger():
  if mode == 0:
    if keys:
      macropad.start_tone(key2freq(keys[-1]))
  elif mode == 1:
    if keys:
      for k in keys:
        macropad.midi.send(macropad.NoteOn(key2note(k), channel = channel))

last_enc = 0
last_switch = False
while True:
  enc = macropad.encoder
  if enc != last_enc:
    if selection == 0:
      stop_all()
      transpose = enc
      retrigger()
    elif selection == 1:
      stop_all()
      mask_ix = enc % masks_len
      mask = masks[mask_ix]
      mask_text = mask_texts[mask_ix]
      retrigger()
    elif selection == 2:
      mode = enc % 2
      stop_all()
    elif selection == 3:
      stop_all()
      channel = enc % 16
      retrigger()
    display()
    last_enc = enc

  switch = macropad.encoder_switch
  if switch != last_switch:
    if switch:
      selection = (selection + 1) % modes_len
      display()
    last_switch = switch

  key_event = macropad.keys.events.get()
  if key_event:
    if key_event.pressed:
      key = key_event.key_number
      if mode == 0:
        macropad.stop_tone()
        macropad.start_tone(key2freq(key))
      else:
        macropad.midi.send(macropad.NoteOn(key2note(key), channel = channel))
      keys.append(key)
      macropad.pixels[key] = RED
    else:
      key = key_event.key_number
      keys.remove(key)
      if mode == 0:
        macropad.stop_tone()
        if keys:
          macropad.start_tone(key2freq(keys[-1]))
      else:
        macropad.midi.send(macropad.NoteOff(key2note(key), channel = channel))
      
      macropad.pixels[key] = OFF

  msg = macropad.midi.receive()
  if msg:
    print(msg)
