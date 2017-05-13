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

import cv2, cPickle
import numpy as np

class VideoProcessor(object):
	'''Container for composite opencv video processing functions.'''
	def __init__(self, parent, input_device, reduce_frame):
		'''Setup necessary values'''
		#Resize image when finding contours, efficiency.
		self.resize_factor = reduce_frame
		#For motion detection, how many frames does it remember?
		self.past_frames = 10.0

		self.moving_average = None
		self.diff = None

		#0 is usually the camera, also takes video files
		self.input = input_device

		self.parent = parent


	def prepare_video(self):
		'''Get video from desired input.'''
		try:
			self.vid = cv2.VideoCapture(self.input)
		except:
			#print error message
			easy_error("Video failed to load")

	def prepare_frame(self, frame, gray=True, resize=True, blur_=5):
		'''Prepare image for processing by reducing false positives'''
		#Equalize each channel of a color image, but finding median value of grayscale image is more efficient
		# arr = cv2.split(frame)
		# arr[0] = cv2.equalizeHist(arr[0])
		# arr[1] = cv2.equalizeHist(arr[1])
		# arr[2] = cv2.equalizeHist(arr[2])
		# frame = cv2.merge(arr)

		if gray == True:
			try:
				frame = cv2.cvtColor(frame, cv2.cv.CV_RGB2GRAY)
			except:
				frame = cv2.cvtColor(frame, cv2.cv.CV_RGBA2GRAY)
				easy_error()

			#Make the pixel values range from 0 to 255
			frame = cv2.equalizeHist(frame)

		frame = cv2.blur(frame, (blur_, blur_))


		#Finally, reduce image size
		y = frame.shape[0]
		x = frame.shape[1]
		f = cv2.resize(frame, (int(x / self.resize_factor), int(y / self.resize_factor)))

		return f


	def snap_video(self):
		'''Get and return video. May return moving areas and significant areas.'''
		ret, frame = self.vid.read()
		return frame

	def motion_detection(self, stream):
		'''Takes video and returns rectangles indicating moving areas'''
		#Convert to grayscale and smooth to reduce errors
		gray = self.prepare_frame(stream)

		#messy way of converting image depth to 32f, needed for cv2.accumulateWeighted
		gray = cv2.filter2D(gray, cv2.CV_32F, np.array(1.0))

		contours = None

		#Gets average, takes difference between current frame and average frames, (might turn into binary image) then finds contours
		if self.moving_average == None:
			self.moving_average = gray
		if self.diff == None:
			self.diff = gray

		#Averages many frames. As an explanation, it is like primitive long exposure cameras that captured empty streets though crowds bustled by.
		#alpha, 1, the current image is all, 0.5 the current + the previous, 0.3333 the current + previous 2
		cv2.accumulateWeighted(gray, self.moving_average, (1 / float(self.past_frames)) )

		self.diff = cv2.absdiff(gray, self.moving_average)

		thresh = np.median(gray)
		retval, self.diff = cv2.threshold(self.diff, thresh, 255, cv2.THRESH_BINARY)

 		#Teh-Chin contour detection
 		self.diff = cv2.convertScaleAbs(self.diff)

		contours, hierarchy = cv2.findContours(self.diff, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

		#Prepare frame reduces image size by 4, reverse that
		for i in contours:
			i *= self.resize_factor

		return contours

	def contour_detection(self, stream):
		'''Find contours of a single frame'''
		streams = cv2.split(stream)

		for i in range(3):
			gray = self.prepare_frame(streams[i],gray=False)

			thresh = np.median(gray)
			retval, gray = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)

			#Teh-Chin contour detection
			gray = cv2.convertScaleAbs(gray)

			if i == 0:
				contoura, hierarchy = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
			if i == 1:
				contourb, hierarchy = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
			if i == 2:
				contourc, hierarchy = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

			#Preparing the frame reduces image size by some factor, reverse that.
		for k in contoura:
			k *= self.resize_factor
		for k in contourb:
			k *= self.resize_factor
		for k in contourc:
			k *= self.resize_factor

		c = contoura + contourb + contourc
		#cv2.drawContours(stream, c, -1, (50, 50, 50), -1)
		return c

	def draw_detection(self, frame, color, contours=True, motion=True, plain=True, outline_size=1):
		'''Draw transparent, colored shapes'''
		#Get frame and import contours to draw
		#frame = cv2.cvtColor(frame, cv2.cv.CV_RGB2RGBA)
		if motion:
			m_contours = self.parent.motion_contours
		else:
			m_contours = None
		if contours:
			contours = self.parent.contours
		else:
			contours = None

		#Receive equal sized empty array
		frame_t = frame * 0

		if m_contours:
			# for i in m_contours:
				# bound_rect = cv2.boundingRect(i)
				# cv2.rectangle(frames[0], (bound_rect[0], bound_rect[1]), (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3]), color, 10)
			# Must pickle and depickle to fix a windows bug
			tmp = cPickle.dumps(m_contours)
			m_contours = cPickle.loads(tmp)
			cv2.drawContours(frame_t, m_contours, -1, color, outline_size)

		if contours:
			# for i in contours:
				# bound_rect = cv2.boundingRect(i)
				# cv2.rectangle(frames[1], (bound_rect[0], bound_rect[1]), (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3]), color 10)
			tmp = cPickle.dumps(contours)
			contours = cPickle.loads(tmp)
			cv2.drawContours(frame_t, contours, -1, color, outline_size)

		if plain:
			frame_t += color

		return frame_t
