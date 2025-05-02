import audiocore
import os

class Kit:
  def __init__(self, path):
    self.path = path
    samplePaths = [path + "/" + f for f in os.listdir(path) if f.endswith(".wav")]
    samplePaths.sort()
    samples = []
    self.samples = samples
    for samplePath in samplePaths[:16]:
      sample = audiocore.WaveFile(open(samplePath, "rb"))
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
    total_before = [0]
    self.kits = kits
    self.total_before = total_before
    for kitPath in kitPaths:
      kit = Kit(kitPath)
      if len(kit) > 0:
        kits.append(kit)
        total_before.append(total_before[-1] + len(kit))
        if len(kits) == 16:
          break
    if len(kits) == 0:
      raise RuntimeError("no kits found")
    self.total_samples = sum([len(k) for k in kits])

  def __len__(self):
    return len(self.kits)
  
  def __getitem__(self, i):
    return self.kits[i]
  
  def voice_index(self, kit, sample):
    return self.total_before[kit] + sample
  
  def play(self, kit, sample):
    self.mixer.play(self.kits[kit][sample], voice = self.voice_index(kit, sample))

  def stop(self, kit, sample):
    self.mixer.stop_voice(self.voice_index(kit, sample))

  def available(self, kit, sample):
    return kit < len(self) and sample < len(self[kit])

  def play_safe(self, kit, sample):
    if self.available(kit, sample):
      self.play(kit, sample)

  def stop_safe(self, kit, sample):
    if self.available(kit, sample):
      self.stop(kit, sample)
