import audiocore
import audiomixer
import os
from util import *

SAMPLEMODE_HOLD = 0
SAMPLEMODE_ONESHOT = 1
SAMPLEMODE_LOOP = 2

class Sample:
  def __init__(self, path, voice):
    self.path = path
    self.voice = voice
    self.wavefile = audiocore.WaveFile(open(path, "rb"))
    self.mode = SAMPLEMODE_HOLD

  def play(self):
    self.mixer.play(self.wavefile, voice = self.voice, loop = self.mode == SAMPLEMODE_LOOP)

  def stop(self):
    if self.mode != SAMPLEMODE_ONESHOT:
      self.mixer.stop_voice(self.voice)

  def nextMode(self):
    self.mode = (self.mode + 1) % 3

  def modeColor(self):
    color = BLUEH
    if self.mode == SAMPLEMODE_ONESHOT:
      color = GREENH
    elif self.mode == SAMPLEMODE_LOOP:
      color = WHITEH
    return color

class Kit:
  def __init__(self, path, voice):
    self.path = path
    samplePaths = [path + "/" + f for f in os.listdir(path) if f.endswith(".wav")]
    samplePaths.sort()
    samples = []
    self.samples = samples
    for samplePath in samplePaths[:16]:
      sample = Sample(samplePath, voice)
      voice = voice + 1
      samples.append(sample)

  def __len__(self):
    return len(self.samples)
  
  def __getitem__(self, i):
    return self.samples[i]

class Kits:
  def __init__(self, path):
    self.path = path
    kitPaths = [path + "/" + k for k in os.listdir(path) if k.startswith("kit")]
    kitPaths.sort()
    kits = []
    self.kits = kits
    voice = 0
    for kitPath in kitPaths:
      kit = Kit(kitPath, voice)
      kitlen = len(kit)
      if kitlen > 0:
        voice = voice + kitlen
        kits.append(kit)
        if len(kits) == 16:
          break
    if len(kits) == 0:
      raise RuntimeError("no kits found")
    self.total_samples = sum([len(k) for k in kits])

  def initMixer(self):
    wav = self[0][0].wavefile
    print("%d channels, %d bits per sample, %d Hz sample rate " %
      (wav.channel_count, wav.bits_per_sample, wav.sample_rate))
    self.channel_count = wav.channel_count
    if wav.channel_count != 1 and wav.channel_count != 2:
      raise RuntimeError("wav files must be mono or stereo")
    mixer = audiomixer.Mixer(
      voice_count = self.total_samples,
      sample_rate = wav.sample_rate,
      channel_count = wav.channel_count,
      bits_per_sample = wav.bits_per_sample,
      samples_signed = True
    )
    self.mixer = mixer
    for k in range(len(self)):
      kit = self[k]
      for s in range(len(kit)):
        sample = kit[s]
        sample.mixer = mixer
    return mixer

  def __len__(self):
    return len(self.kits)
  
  def __getitem__(self, i):
    return self.kits[i]
  
  def play(self, kit, sample):
    self.kits[kit][sample].play()

  def stop(self, kit, sample):
    self.kits[kit][sample].stop()

  def available(self, kit, sample):
    return kit < len(self) and sample < len(self[kit])

  def play_safe(self, kit, sample):
    if self.available(kit, sample):
      self.play(kit, sample)

  def stop_safe(self, kit, sample):
    if self.available(kit, sample):
      self.stop(kit, sample)
