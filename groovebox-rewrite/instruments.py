import os
import audiocore
import audiomixer
import synthio
from model import Kit, Sample, Synth

class Instruments:
  def __init__(self, kitsPath, model):
    self.voices = []
    self.notes = {}
    self.model = model
    self.initializeModel(kitsPath)
    self.mixer = self.initializeMixer()

  # initialization
  def initializeModel(self, path):
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
      self.model.instruments[i] = k

  def initializeKit(self, path, id):
    samplePaths = [path + "/" + f for f in os.listdir(path) if f.endswith(".wav")]
    samplePaths.sort()
    samples = []
    note = 0
    self.notes[id] = {}
    for samplePath in samplePaths[:16]:
      self.notes[id][note] = False
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
    self.notes[id] = {}
    modelSynth = Synth(id, voice)
    self.mixer.voice[voice].play(synth)
    return modelSynth

  # actions
  def isNoteOn(self, instrument, note):
    return self.notes[instrument.id].get(note, None)

  def noteOnInstrument(self, instrument, note):
    if isinstance(instrument, Kit):
      sample = instrument.samples[note]
      voice = sample.voice
      self.mixer.play(self.voices[voice], voice = voice, loop = sample.mode == Sample.MODE_LOOP)
      self.notes[instrument.id][note] = True
    elif isinstance(instrument, Synth):
      notes = self.notes[instrument.id]
      if notes.get(note) == None:
        noteObj = synthio.Note(frequency = synthio.midi_to_hz(note))
        self.voices[instrument.voice].press(noteObj)
        self.notes[instrument.id][note] = noteObj

  def noteOffInstrument(self, instrument, note):
    if isinstance(instrument, Kit):
      sample = instrument.samples[note]
      if sample.mode != Sample.MODE_ONESHOT:
        self.mixer.stop_voice(sample.voice)
      self.notes[instrument.id][note] = False
    elif isinstance(instrument, Synth):
      noteObj = self.notes[instrument.id].get(note)
      if noteObj:
        self.voices[instrument.voice].release(noteObj)
      self.notes[instrument.id][note] = None

  def noteOn(self, instrumentId, note):
    self.noteOnInstrument(self.model.instruments[instrumentId], note)

  def noteOff(self, instrumentId, note):
    self.noteOffInstrument(self.model.instruments[instrumentId], note)
