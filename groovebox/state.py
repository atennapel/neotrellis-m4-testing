import os
import audiocore
import audiomixer
from model import Model, Kit, Sample, Synth

class State:
  def __init__(self, ui, kitsPath):
    self.ui = ui

    self.voices = []
    self.model = self.initializeModel(kitsPath)
    self.mixer = self.initializeMixer()

    self.step = 15
    self.playing = False

    self.currentInstrument = self.model.instrument[0]

  # initialization
  def initializeModel(self, path):
    model = Model()
    kitPaths = [path + "/" + k for k in os.listdir(path) if k.startswith("kit")]
    kitPaths.sort()
    kits = []
    id = 0
    for kitPath in kitPaths:
      kit = self.initializeKit(kitPath, id)
      sampleCount = len(kit)
      if sampleCount > 0:
        id = id + 1
        kits.append(kit)
        if len(kits) == 8:
          break
    if len(kits) == 0:
      raise RuntimeError("no kits found")
    for i, k in enumerate(kits):
      model.instruments[i] = k
    return model

  def initializeKit(self, path, id):
    samplePaths = [path + "/" + f for f in os.listdir(path) if f.endswith(".wav")]
    samplePaths.sort()
    samples = []
    note = 0
    for samplePath in samplePaths[:16]:
      sample = self.initializeSample(samplePath, id, note)
      note = note + 1
      samples.append(sample)
    return Kit(path, id, samples)

  def initializeSample(self, path, id, note):
    voice = len(self.voices)
    self.voices.append(audiocore.WaveFile(open(path, "rb")))
    return Sample(path, id, note, voice)

  def initializeMixer(self):
    wav = self.voices[0]
    print("%d channels, %d bits per sample, %d hz sample rate " %
      (wav.channel_count, wav.bits_per_sample, wav.sample_rate))
    mixer = audiomixer.Mixer(
      voice_count = len(self.voices) + 8, # 8 synth voices added
      sample_rate = wav.sample_rate,
      channel_count = wav.channel_count,
      bits_per_sample = wav.bits_per_sample,
      samples_signed = True,
      buffer_size = 2048,
    )
    return mixer
  
  def initializeSynths(self, synths):
    for i, synth in enumerate(synths[:8]):
      id = i + 8
      self.model.instruments[id] = self.initializeSynth(id, synth)

  def initializeSynth(self, id, synth):
    voice = len(self.voices)
    self.voices.append(synth)
    modelSynth = Synth(id, voice)
    self.mixer.voice[voice].play(synth)
    return modelSynth

  # actions
  def noteOn(self, instrumentId, note):
    instrument = self.model.instruments[instrumentId]
    if isinstance(instrument, Kit):
      sample = instrument.samples[note]
      voice = sample.voice
      self.mixer.play(self.voices[voice], voice = voice, loop = sample.mode == Sample.MODE_LOOP)
    elif isinstance(instrument, Synth):
      self.voices[instrument.voice].press(note)

  def noteOff(self, instrumentId, note):
    instrument = self.model.instruments[instrumentId]
    if isinstance(instrument, Kit):
      sample = instrument.samples[note]
      if sample.mode != Sample.MODE_ONESHOT:
        self.mixer.stop_voice(sample.voice)
    elif isinstance(instrument, Synth):
      self.voices[instrument.voice].release(note)

  # update
  def tick(self):
    if self.playing:
      self.ui.beforeStep(self)
    self.step = (self.step + 1) % 16
    if self.playing:
      self.ui.step(self)

  def input(self, pressed, downs, ups):
    pass
