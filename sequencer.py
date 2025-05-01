# Simple sequencer for 8 samples (taken from the /samples dir)
# This started from the code from https://learn.adafruit.com/trellis-m4-beat-sequencer/eight-step-simple-sequencer

import time
import board
import audioio
import audiocore
import audiomixer
import adafruit_trellism4
import os

tempo = 120

DRUM_COLOR = ((0, 255, 255),
              (0, 255, 0),
              (255, 255, 0),
              (255, 0, 0))
WHITE = (255, 255, 255)

trellis = adafruit_trellism4.TrellisM4Express(rotation = 90)

trellis.pixels.brightness = 0.05

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

print("READY")

trellis.pixels.fill(0)

current_press = set()

NOT_SELECTED = 0
SELECTED = (0, 0, 255)
STEP = (0, 255, 0)
STEP_SEL = (0, 255 // 2, 0)
PLAYING = (255, 0, 0)

trellis.pixels[(1, 0)] = SELECTED
trellis.pixels[(1, 1)] = NOT_SELECTED
trellis.pixels[(1, 2)] = NOT_SELECTED
trellis.pixels[(1, 3)] = NOT_SELECTED
trellis.pixels[(0, 0)] = NOT_SELECTED
trellis.pixels[(0, 1)] = NOT_SELECTED
trellis.pixels[(0, 2)] = NOT_SELECTED
trellis.pixels[(0, 3)] = NOT_SELECTED

cursel = 0
curselpos = (1, 0)
playing = False
curstep = 15
tempo = 120
recording = False
solo = -1

pats = [
    [False] * 16, [False] * 16, [False] * 16, [False] * 16,
    [False] * 16, [False] * 16, [False] * 16, [False] * 16
]
mutes = [False] * 8

volume = [10] * 8

while True:
    stamp = time.monotonic()

    if playing:
        sx = curstep % 8
        sy = (1 - curstep // 8) + 2
        step = pats[cursel][curstep]
        trellis.pixels[(sy, sx)] = STEP if step else 0

    curstep = (curstep + 1) % 16

    if playing:
        sx = curstep % 8
        sy = (1 - curstep // 8) + 2
        step = pats[cursel][curstep]
        trellis.pixels[(sy, sx)] = STEP_SEL if step else WHITE
        for i in range(8):
            if pats[i][curstep] and not mutes[i] and (solo == -1 or solo == i):
                mixer.play(samples[i], voice = i)

    while time.monotonic() - stamp < 60 / (tempo * 4):
        pressed = set(trellis.pressed_keys)
        for down in pressed - current_press:
            y = down[0]
            x = down[1]

            # sample selection
            if (x >= 0 and x < 4) and (y == 0 or y == 1):
                i = (1 - y) * 4 + x
                if not mutes[i] and (solo == -1 or solo == i):
                    mixer.play(samples[i], voice = i)

                if cursel != i:
                    trellis.pixels[curselpos] = NOT_SELECTED
                    cursel = i
                    curselpos = (y, x)
                    trellis.pixels[curselpos] = SELECTED
                    trellis.pixels[(1, 4)] = PLAYING if mutes[cursel] else 0
                    trellis.pixels[(0, 4)] = STEP if solo == cursel else 0

                    pattern = pats[cursel]
                    for s in range(16):
                        step = pattern[s]
                        sx = s % 8
                        sy = (1 - s // 8) + 2
                        trellis.pixels[(sy, sx)] = STEP if step else 0

                if playing and recording:
                    pattern = pats[cursel]
                    pattern[curstep] = True

            # mute
            if y == 1 and x == 4:
                newmute = not mutes[cursel]
                mutes[cursel] = newmute
                trellis.pixels[(y, x)] = PLAYING if newmute else 0

            # solo
            if y == 0 and x == 4:
                solo = -1 if solo == cursel else cursel
                trellis.pixels[(y, x)] = 0 if solo == -1 else STEP

            # step
            elif (y == 2 or y == 3):
                i = (1 - (y - 2)) * 8 + x
                pattern = pats[cursel]
                newstep = not pattern[i]
                pattern[i] = newstep
                trellis.pixels[(y, x)] = STEP if newstep else 0

            # start/stop
            elif y == 0 and x == 7:
                playing = not playing
                if not playing:
                    sx = curstep % 8
                    sy = (1 - curstep // 8) + 2
                    step = pats[cursel][curstep]
                    trellis.pixels[(sy, sx)] = STEP if step else 0
                curstep = 15
                trellis.pixels[(y, x)] = PLAYING if playing else 0

            # record switch
            elif y == 1 and x == 7:
                recording = not recording
                trellis.pixels[(y, x)] = PLAYING if recording else 0

            # volume up
            elif y == 1 and x == 5:
                cur = volume[cursel]
                if cur < 10:
                    trellis.pixels[(y, x)] = WHITE
                    cur = cur + 1
                    volume[cursel] = cur
                    mixer.voice[cursel].level = cur / 10
                    trellis.pixels[(y, x)] = 0

            # volume down
            elif y == 0 and x == 5:
                cur = volume[cursel]
                if cur > 0:
                    trellis.pixels[(y, x)] = WHITE
                    cur = cur - 1
                    volume[cursel] = cur
                    mixer.voice[cursel].level = cur / 10
                    trellis.pixels[(y, x)] = 0

            # tempo up
            elif y == 1 and x == 6:
                if tempo < 300:
                    trellis.pixels[(y, x)] = WHITE
                    tempo = tempo + 10
                    trellis.pixels[(y, x)] = 0

            # tempo down
            elif y == 0 and x == 6:
                if tempo > 10:
                    trellis.pixels[(y, x)] = WHITE
                    tempo = tempo - 10
                    trellis.pixels[(y, x)] = 0

        current_press = pressed
        time.sleep(0.01)
