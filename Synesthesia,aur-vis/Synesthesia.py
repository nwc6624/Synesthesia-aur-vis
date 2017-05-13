	# This program is free software: you can redistribute it and/or modify
	# it under the terms of the GNU General Public License as published by
	# the Free Software Foundation, either version 3 of the License, or
	# (at your option) any later version.

	# This program is distributed in the hope that it will be useful,
	# but WITHOUT ANY WARRANTY; without even the implied warranty of
	# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	# GNU General Public License for more details.

	# You should have received a copy of the GNU General Public License
	# along with this program.  If not, see <http://wws.gnu.org/licenses/>.

	#Contact the author at nocaulfield <AT> gmail

# Created for the 2012-2013 Supercomputing Challenge, a type of science
# fair for middle school and high school students that blends science,
# computational modeling and math. Based in New Mexico, USA

# by  Hugo Rivera, Noah Caulfield

# Allows user to simulate aural to visual Synesthesia in a modifiable way.

import colorsys, sys, random
import cv2; import numpy as np
import vid_processor, aud_processor, gui34


class SynesthesiaVisualizer(object):
	'''Ties audio and video together and forms visual artifacts: a modifiable model of synesthesia.'''
	def __init__(self, video_device=0, audio_device=0, get_audio=True, get_motion=True, get_contours=True, syn_overlay=True, grayscale=False, binary_image=False):
		'''Load settings.'''
		self.video_device = video_device
		self.audio_device = audio_device

		#Empty variables used to store motion, bpm, etc
		self.motion_contours = None
		self.contours = None
		self.frequencies = np.ndarray(0) #Empty array

		#Processing types
		self.get_audio = get_audio
		self.get_motion = get_motion
		self.get_contours = get_contours
		self.synesthesia = syn_overlay

		self.show_grayscale = grayscale
		self.show_binary = binary_image

		self.mx = [[0, 0], [0, 0], [0, 0]]

		self.window_name = 'Synesthesia:aur-vis'
		self.timer_int = -1

		#Create a log file, or open an existing one.
		self.log = open("log", 'w')
		self.log.write("New log file created for Synesthesia model.\n")
		self.log.flush()

		#Processors
		self.p = None
		self.a = None
		self.v = None

	def freq_to_color(self, type_=1, multiplier=1):
		#Will be modifiable through the graphical interface
		if type_ == 0:
			#random colors
			b = random.random()
			g = random.random()
			r = random.random()

		if type_ == 1:
			b = 50 / float(self.freqs[self.mx[0][1]]) * 10 + 60
			g, r = b * 2, b

		if type_ == 2:
			b = 50 / float(self.freqs[self.mx[0][1]]) * 10 + 60
			g = 0
			r = 200 / float(self.freqs[self.mx[2][1]]) * 10 + 150

		if type_ == 3:
			self.freqs = self.frequencies
			self.mx = n_max(self.freqs, 3)

			b = 100 / float(self.freqs[self.mx[0][1]]) * 128
			g = 100 / float(self.freqs[self.mx[1][1]]) * 128
			r = 100 / float(self.freqs[self.mx[2][1]]) * 128

		bf = (b + 0.0000001) * multiplier
		gf = (g + 0.0000001) * multiplier
		rf = (r + 0.0000001) * multiplier
		color = (rf, bf, gf)

		return color

	def setup_processors(self, reset=True):
		if reset:
			if self.get_audio:
				self.a.close()
				self.p.terminate()
			self.p = None
			self.a = None
			self.v = None

		if self.get_audio:
			self.a = aud_processor.AudioProcessor(self, self.audio_device)
			self.a.start_thread()
		#Variable reduce_frame should be below 1 to shrink the image and process it faster
		self.v = vid_processor.VideoProcessor(self, self.video_device, reduce_frame=3)
		self.v.prepare_video()

	def main(self):
		'''Run according to settings. Show video, make tkinter GUI for settings and help, and possibly retrieve audio'''
		self.quit = False
		#Get settings, video, & audio(if it is needed)
		self.setup_processors(reset=False)
		self.timer = 0

		#Tkinter window
		self.gui = gui34.gui34(self)

		while self.quit == False:
			self.run()


	def run(self):
		self.timer += 1

		#Fetch video
		self.frame = self.v.snap_video()
		self.v_resx = self.frame.shape[1]
		self.v_resy = self.frame.shape[0]
		display = self.frame

		if self.show_binary or self.show_grayscale:
			display = self.v.prepare_frame(self.frame, gray=True)

			#Restore original size, frames are reduced for more rapid processing
			display = cv2.resize(display, (int(self.v_resx * self.v.resize_factor), int(self.v_resy * self.v.resize_factor)))


		if self.show_binary:
			display = self.v.prepare_frame(self.frame, gray=True)
			thresh = np.median(display)
			retval, display = cv2.threshold(self.frame, thresh, 255, cv2.THRESH_BINARY)

		if self.get_motion: #Retrieve motion contours
			self.motion_contours = self.v.motion_detection(self.frame)

		if self.get_contours: #Retrieve contours
			self.contours = self.v.contour_detection(self.frame)

		#Will be modifiable through the graphical interface
		color = (0, 0, 0)

		self.freqs = self.frequencies
		if self.get_audio:
			self.freqs = self.frequencies
			self.mx = n_max(self.freqs, 10)


			try:
				color = self.freq_to_color(type_=1, multiplier=1)
			except:
				color = (0, 0, 0)
				easy_error("Frequency to color conversion error")


		if self.synesthesia:
			display = self.create_overlay(self.frame, colors=color, intensity = 50)

		cv2.imshow(self.window_name, display)

		#Screenshot utility, saves .png of current image to current folder at every self.timer_int frames.
		#Will be modifiable through the graphical interface
		if self.timer_int > 0 and self.timer % self.timer_int == 0:
			cv2.imwrite("s-" + str(self.timer) + ".png", display)


		#Check for escape keys or check for tkinter closing
		if 0xFF & cv2.waitKey(5) == 27 or self.quit or self.gui.quit:
			#Close tkinter after cv windows closes
			try:
				self.quit = True
				self.gui.quit = True

				self.a.close()
				self.p.terminate()
				cv2.destroyAllWindows()

				self.gui._quit()

				self.log.close()
				sys.exit()
			except:
				#Catch exit errors
				easy_error("Tkinter is not completely thread-safe.")

		if self.timer % 5 == 0:
			self.update_threaded_vars()

	def create_overlay(self, frame, colors, intensity=50, outline_size=-1):
		''''''
		one = self.v.draw_detection(frame, colors, contours=True, motion=True, plain=False, outline_size=outline_size)
		two = self.v.draw_detection(frame, colors, contours=False, motion=False, plain=True, outline_size=outline_size)

		#Combine overlays and add them to final frame.
		#Will be modifiable through the graphical interface
		return (two + one) / 2 + (frame / 2)

	def update_threaded_vars(self):
		'''Two synchronization of several variables'''
		self.gui.stats_qe.put(
		{'freq' : (self.mx[0][0], self.mx[1][0], self.mx[2][0]),
		'v_res' : (self.v_resx, self.v_resy)}
		)
		try:
			self.timer_int = self.gui.rec_qe.get(False)
			self.gui.rec_qe.task_done()
		except:
			pass

		try:
			config = self.gui.settings_qe.get(False)
			self.get_audio = config['audio']
			self.get_motion = config['motion']
			self.get_contours = config['contours']
			self.synesthesia = config['syn_on']

			self.show_grayscale = config['gray']
			self.show_binary = config['binary']
		except:
			pass

def easy_error(extra=None):
	'''Convenience, writes errors from an 'except' statement to a log and to stdout'''
	if extra:
		a = str(extra) + "\n"
		s.log.write(a); s.log.flush()
		print a
	b = str(sys.exc_info()[0]) + "\n"
	s.log.write(b); s.log.flush()
	print b
	c = str(sys.exc_info()[1]) + "\n"
	s.log.write(c); s.log.flush()
	print c

def n_max(arr, n):
	'''Find n-most biggest points in a numpy array'''
	if arr.shape[0] >=2:
		indices = arr.ravel().argsort()[-n:]
		indices = (np.unravel_index(i, arr.shape) for i in indices)
		return [(arr[i], i) for i in indices]
	else:
		return arr

if __name__ == '__main__':
	#0 - just show video
	#6-5 - grayscale or black and white
	#10 - motion detection
	#20 - contour detection
	#100 - total detection & audio input
	#101 - same as 100, only show colors
	print """Synesthesia,aur-vis  Copyright (C) 2013 Hugo Rivera\nThis program comes with ABSOLUTELY NO WARRANTY\nThis is free software, and you are welcome to redistribute it\nunder certain conditions; see the License(gpl)."""
	cv2.setUseOptimized(True)
	#Devices set to Windows defaults
	s = SynesthesiaVisualizer(video_device=0, audio_device=0, get_audio=True, get_motion=True, get_contours=True, syn_overlay=True, grayscale=False, binary_image=False)
	s.main()
