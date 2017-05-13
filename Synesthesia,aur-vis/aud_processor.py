 	# This program is free software: you can redistribute it and/or modify
	# it under the terms of the GNU General Public License as published by
	# the Free Software Foundation, either version 3 of the License, or
	# (at your option) any later version.

	# This program is distributed in the hope that it will be useful,
	# but WITHOUT ANY WARRANTY; without even the implied warranty of
	# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	# GNU General Public License for more details.

	# You should have received a copy of the GNU General Public License
	# along with this program.  If not, see <http://www.gnu.org/licenses/>.

	#Contact the author at nocaulfield <AT> gmail

import pyaudio, wave, struct, sys
import numpy as np, threading

class AudioProcessor(object):
	'''Container for composite audio based functions using pyaudio.'''
	def __init__(self, parent, audio_device):
		'''Create pyaudio variables, mostly generic audio variables like sample rate'''
		#Audio data
		self.a_stream = None
		self.parent = parent
		self.quit = False

		#Devices
		self.audio_device = audio_device
		self.audio_dev_out = None
		self.timer = 0
		if isinstance(self.audio_device, str):
			self.from_device = False
		else:
			self.from_device = True

		#Audio rates
		self.sample_rate = 44100
		self.sample_size = 2
		self.channels = 2
		self.frame_rate = 1024
		self.nfft = 1024 #FFT resolution
		self.buf_size = self.nfft * 4

		self.freq = np.ndarray(0)

	def to_decibels(self, freqs):
		'''Turn set of frequencies into decibels'''
		try:
			y = 10.0*np.log10(freqs)
		except:
			print sys.exc_info()[0]
			print sys.exc_info()[1]
			y = None
		return y

	def prepare_audio(self, wavfile=None):
		'''Get audio, accepts device number or .wav file.'''
		pa = pyaudio.PyAudio()

		if self.from_device == True:
			self.a_stream = pa.open(format=pyaudio.paInt16,
				channels=self.channels,
				rate=self.sample_rate,
				input=True,
				frames_per_buffer=self.buf_size,
				input_device_index = self.audio_device)

		if self.from_device == False:
			self.timer = 0
			self.a_stream = wave.open(self.audio_device, 'rb')
			#CHANGE THIS SO IT LOADS SETTINGS AUTOMATICALLY, or fails
			# assert self.a_stream.getnchannels() == self.channels
			# assert self.a_stream.getsampwidth() == self.sample_size
			# assert self.a_stream.getframerate() == self.sample_rate

		self.pipe_audio()

	def start_thread(self):
		t = threading.Thread(target=self.prepare_audio)
		t.daemon = True
		t.start()

	def pipe_audio(self):
		'''Get and return audio. Can detect frequency, volume, and beats per minute.'''
		while self.quit == False:
			if self.parent.get_audio:
				# Read n*nFFT frames from stream, n > 0
				if self.from_device == True:
					self.N = max(self.a_stream.get_read_available() / self.nfft, 1) * self.nfft
				else:
					self.N = (int((self.timer + 1) * self.sample_rate / 25.0) - self.a_stream.tell()) / self.nfft

				if not self.N:
					return 0

				try:
					if self.from_device == True:
						data = self.a_stream.read(self.N)
					else:
						data = self.a_stream.readframes(self.N)
				except:
					print sys.exc_info()[0]
					print sys.exc_info()[1]
					data = None

				#Backup frequencies. If current data is bad, show previous sound.
				if not isinstance(self.freq, int):
					bak = self.freq

				self.freq = self.get_frequencies(data)

				if isinstance(self.freq, int):
						if bak.any():
							self.freq = bak

				self.parent.frequencies = self.freq

	def get_frequencies(self, data, MAX_y=2**32):
		'''Returns frequencies of audio stream and decibel levels'''
		freqs, y = 0, 0
		if not data == None and self.from_device == True:
			# Unpack data, LRLRLR...
			try:
				y = np.array(struct.unpack("%dh" % (self.N * self.channels), data)) / MAX_y
			except:
				print sys.exc_info()[0]
				print sys.exc_info()[1]
				return 0
			y_L = y[::2]
			y_R = y[1::2]

			Y_L = np.fft.fft(y_L, self.nfft)
			Y_R = np.fft.fft(y_R, self.nfft)

			# Sewing FFT of two channels together, DC part uses right channel's
			freqs = abs(np.hstack((Y_L[-self.nfft / 2:-1], Y_R[:self.nfft / 2])))

		if not data == None and self.from_device == False:
			y = np.array(struct.unpack("%dh" % (len(data) / self.sample_size), data)) / MAX_y
			y_L = y[::2]
			y_R = y[1::2]

			Y_L = np.fft.fft(y_L, self.nfft)
			Y_R = np.fft.fft(y_R, self.nfft)

			#Sewing FFT of two channels together, DC part uses right channel's
			freqs = abs(np.hstack((Y_L[self.nfft / 2:-1], Y_R[:self.nfft / 2])))

		return freqs

	def close(self):
		self.quit = True
		if self.from_device == True:
			self.a_stream.stop_stream()
			self.a_stream.close()
		if self.from_device == False:
			self.a_stream.close()
