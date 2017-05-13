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


#A visual_artifact will have its own color and frequency band. It will be drawn in a sperate buffer in SYnesthesia.py
#Update variables

import threading, sys, Queue

import Tkinter as tk
import ttk as ttk


class gui34(threading.Thread):
	'''Species of Arctic Iguana, thrives on audio data and is somewhat approachable. Very specific to Synesthesia.py but can be used to demonstrate Tkinter's many uses as a GUI toolkit'''
	def __init__(self, parent=None):
		'''A thread. Runs tkinter GUI: tkinter is not fully thread-safe, thus some precautions have been taken.'''
		threading.Thread.__init__(self)
		self.daemon = True
		self.parent = parent
		self.start()

	def tk_init(self):
		'''Create tkinter tabs, widgets, buttons, and a matplotlib graph.'''
		self.quit = False
		self.app = tk.Tk()
		self.app.title("Synesthesia:aur-vis Interface")

		#Queues to synchronize necessary variables across threads
		self.settings_qe = Queue.LifoQueue()
		self.stats_qe = Queue.LifoQueue()
		self.rec_qe = Queue.LifoQueue()

		self.config = {'audio':True, 'motion':True, 'contours':True, 'syn_on':True, 'gray':False, 'binary':False}
		self.s_audio = self.config['audio']
		self.s_motion = self.config['motion']
		self.s_contours = self.config['contours']
		self.s_syn_on = self.config['syn_on']

		self.s_gray = self.config['gray']
		self.s_binary = self.config['binary']

		#Global look
		ttk.Style().configure(("TNotebook", "TFrame"), background="#ffffff")

		#Main area, navigated by tabs
		self.n = ttk.Notebook(height="384", width="621", padding="2")

		#Tabs for:
		#Settings
		self.s_n = ttk.Notebook(padding="0 16 0 32")
		#Data
		self.d_n = ttk.Notebook(padding="0 16 0 16")
		#About
		self.a_n = ttk.Notebook(padding="0 16 0 16")

		self.n.add(self.s_n, text='Settings')
		self.n.add(self.d_n, text="Data")
		self.n.add(self.a_n, text='About')
		self.settings_content()
		self.data_content()
		self.about_content()

		self.n.select(self.d_n)
		self.n.pack(fill=tk.BOTH, expand=True)

		self.app.protocol("WM_DELETE_WINDOW", self._quit)
		self.app.bind("<Escape>", self._quit)

	def refresh(self):
		'''Fetch needed variables; then update according tkinter structures.'''
		try:
			stats = self.stats_qe.get()
			self.max_freq.set(stats['freq'])
			self.vid_res.set(stats['v_res'])

		except Queue.Empty:
			self.max_freq.set('?')
		except:
			print 'gui34 refresh error'
		#Must loop
		self.app.after(100, self.refresh)


	def run(self):
		self.tk_init()
		if self.quit == False:
			self.app.after(50, self.refresh)
			self.app.mainloop()
		else:
			self._quit()

	def callback(self):
		self._quit()

	def _quit(self, *args):
		self.app.quit()
		self.app.destroy()
		#On Windows prevents Fatal Python Error: PyEval_RestoreThread: NULL tstate
		self.quit = True #Broadcast status
		sys.exit()

	def settings_content(self):
		'''Add content to settings tab'''
		#Apply settings, undo settings to previously loaded, load/save preset. Apply and revert are greyed out until changes are made to settings

		#Buffer for aligning and centering buttons on bottom edge. grid() usage was unsuccesful.
		self.s_n_b = ttk.Frame(self.s_n)
		self.s_n_b.pack(side=tk.BOTTOM)

		self.b_apply = ttk.Button(self.s_n_b, text='Apply', command=self.apply_config)

		self.b_revert = ttk.Button(self.s_n_b, text='Revert Changes')

		self.b_load	= ttk.Button(self.s_n_b, text='Load')
	#	self.b_load['command'] = print ('apply settings()')

		self.b_save = ttk.Button(self.s_n_b, text='Save Settings')
	#	self.b_save['command'] = print ('apply settings()')

		for i in (self.b_apply, self.b_revert, self.b_load, self.b_save):
			i.pack(side=tk.LEFT)#j.grid(column=i, row=1, sticky=tk.S)


		self.s_load = ttk.Frame(self.s_n)
		self.s_syn = ttk.Frame(self.s_n)
		self.s_cus = ttk.Frame(self.s_n)
		self.s_spd = ttk.Frame(self.s_n)
		self.s_dbg = ttk.Frame(self.s_n)

		self.s_n.add(self.s_load, text="Load data")
		self.s_n.add(self.s_syn, text="Synesthesia types")
		self.s_n.add(self.s_cus, text="Custom type")
		self.s_n.add(self.s_spd, text="Processing quality")
		self.s_n.add(self.s_dbg, text="Debugging")



		#Load file or select device for either audio or video, then reset parent's a/v/ processors
		self.s_vin = ttk.Button(self.s_load, text='Load video', command=self.select_video).grid(row=0, column=0, pady=16, padx=16)
		self.s_ain = ttk.Button(self.s_load, text='Load audio', command=self.select_audio).grid(row=1, column=0)

		self.s_av = ttk.Label(self.s_load, text='Fetch data from a device to use the microphone or camera').grid(row=2, column=0, pady=16, padx=16)

		self.use_vid_dev = True
		self.use_snd_dev = True
		self.s_vcheck = ttk.Checkbutton(self.s_load, text="Use video device", variable=self.use_vid_dev).grid(row=0, column=1)
		self.s_acheck = ttk.Checkbutton(self.s_load, text="Use audio device", variable=self.use_snd_dev).grid(row=1, column=1)





		#Synesthesia types. Default presets and recently saved presets
		#show current settings in label


		#show preset names, load them from file using Radio Buttons
		#show most recently saved preset

		#Align all elements in Synesthesia Types tab



		#Custom types: a lot of options. use FRAME LABELS, and scrolling
		#Select current visual artifact to edit
		# self.s_artifact =

		#canvas for current color
		#Check Button, overlay, contours, contour lines or filled, line width

		#add another audio band selector and color, canvas, check buttons

		#sensitivity Scale

		#Check Button motion detection?

		#Menu additive, subtractive, average compositing

		#Align all elements in Custom Types tab




		#Speed vs quality selectors
		#video resize factor
		#audio rates

		#Align all elements in Speed tab

		#Debug toggles
		self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Fetch audio", variable=self.s_audio).pack(pady=16)

		self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Detect motion", variable=self.s_motion).pack(pady=8)

		self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Calculate contours", variable=self.s_contours).pack(pady=8)

		self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Synesthesia overlay?", variable=self.s_syn_on).pack(pady=8)

		self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Show binary image", variable=self.s_binary).pack(pady=8)

		self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Show grayscale image", variable=self.s_gray).pack(pady=8)
		# self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Fetch audio", variable=self.parent.get_audio).pack()
		# self.s_d_aud = ttk.Checkbutton(self.s_dbg, text="Fetch audio", variable=self.parent.get_audio).pack()

	def data_content(self):
		'''Add content to data tab'''
		self.d_st= ttk.Frame(self.d_n)
		self.d_gr= ttk.Frame(self.d_n)
		self.d_re= ttk.Frame(self.d_n)

		self.d_n.add(self.d_st, text="Statistics")
		self.d_n.add(self.d_gr, text="Graph")
		self.d_n.add(self.d_re, text="Record")



		#Statistics tab. _r denotes usage of tk.StringVar
		#Initialize dynamically updated variables
		self.max_freq = tk.StringVar()
		self.vid_res = tk.StringVar()
		self.fps = tk.StringVar()

		self.aud_res = [0, 0, 0]
		self.aud_res[0] = tk.StringVar()
		self.aud_res[1] = tk.StringVar()

		self.d_mxfr = ttk.Label(self.d_st, text="'Loudest' frequencies").pack(padx=16, pady=16)
		self.d_mxfr_r = ttk.Label(self.d_st, textvariable=self.max_freq).pack()

		self.d_vf = ttk.Label(self.d_st, text='Video resolution').pack(padx=16, pady=16)
		self.d_vf_r = ttk.Label(self.d_st, textvariable=self.vid_res).pack()
		# self.d_af = ttk.Label(self.d_st, text='Audio sampling size').pack()
		# self.d_af_r = ttk.Label(self.d_st, textvariable=self.aud_res[0]).pack()
		# self.d_af2 = ttk.Label(self.d_st, text='Audio sampling rate').pack()
		# self.d_af2_r = ttk.Label(self.d_st, textvariable=self.aud_res[1]).pack()

		# self.d_fps = ttk.Label(self.d_st, text='FPS for visualizer').pack()
		# self.d_fps_r = ttk.Label(self.d_st, textvariable=self.fps).pack()


		#Record tab
		#Take screenshots every x ms
		self.rec_interval = 0

		self.d_sht_start = ttk.Button(self.d_re, text='Take screenshots', command=lambda: self.take_shots(self.parent, 10)).pack(pady=16)
		self.d_sht_stop = ttk.Button(self.d_re, text='Stop screenshot capture', command=lambda: self.take_shots(self.parent, -1)).pack()
		# self.d_sht_label = ttk.Label(self.d_re, text='Set screenshot interval').pack(pady=16)

		# self.d_sht_int = ttk.Scale(self.d_re, orient='horizontal', length=300, from_=10, to_=1000).pack()

		#Graph
		self.g_label = ttk.Label(self.d_gr, text='Audio frequency graph is being renovated.\nWill use matplotlib to display audio data from a numpy array').pack(pady=16, padx=16)


	def about_content(self):
		'''Add content to about tab'''
		self.a_abt= ttk.Frame(self.a_n)
		self.a_cred= ttk.Frame(self.a_n)
		self.a_li= ttk.Frame(self.a_n)

		self.a_n.add(self.a_abt, text="About")
		self.a_n.add(self.a_cred, text="Credits")
		self.a_n.add(self.a_li, text="License")

		#Text within About's About screen
		self.a_abttxt = tk.Text(self.a_abt, relief=tk.SUNKEN, bd=2, setgrid=1, height=35, pady=32, padx=32)
		self.a_abtbar = tk.Scrollbar(self.a_abt)
		self.tk_extern_txt(self.a_abttxt, self.a_abtbar, "About.txt")

		#Text within About Credits
		self.a_credtxt = tk.Text(self.a_cred, relief=tk.SUNKEN, bd=2, setgrid=1, height=35, pady=32, padx=32)
		self.a_credbar = tk.Scrollbar(self.a_cred)
		self.tk_extern_txt(self.a_credtxt, self.a_credbar, "Credits.txt")

		#Text within About License
		self.a_litxt = tk.Text(self.a_li, relief=tk.SUNKEN, bd=2, setgrid=1, height=35, pady=32, padx=32)
		self.a_libar = tk.Scrollbar(self.a_li)
		self.tk_extern_txt(self.a_litxt, self.a_libar, "gpl.txt")

	def tk_extern_txt(self, txtname, barname, filenym):
		'''Fill a Text field with data from a .txt file'''
		txtname.pack(side = tk.LEFT, expand = tk.Y, fill = tk.BOTH)
		barname.pack(side = tk.LEFT, fill=tk.Y)
		txtname['yscrollcommand'] = barname.set
		barname['command'] = txtname.yview
		#Get text from external file: easier to manage
		txtfile = open(filenym, "r")
		txt = txtfile.read()
		txtname.insert('0.0', txt )
		#Make widget read-only and close current txt file
		txtname.config(state = tk.DISABLED)
		txtfile.close()


	def apply_config(self):
		'''Update queue'''
		self.config['audio'] = self.s_audio
		self.config['motion'] = self.s_motion
		self.config['contours'] = self.s_contours
		self.config['syn_on'] = self.s_syn_on

		self.config['gray'] = self.s_gray
		self.config['binary'] = self.s_binary

		self.settings_qe.put(self.config)

	def select_video(self, parent):
		'''Callback to get video device index or a supported file for cv2 use'''
		pass

	def select_audio(self, parent):
		'''Callback to get audio device index or a .wav file'''
        # f = tkFileDialog.askopenasfilename()
		pass

	def artifact_band(self, artifact, band, parent):
		'''Callback for changing active audio band of current visual_artifact'''
		# rgb, hx = ttk.tkColorChooser.askcolor()
		pass

	def artifact_color(self, artifact, color, parent):
		'''Callback for changing color of current visual_artifact'''
		# rgb, hx = ttk.tkColorChooser.askcolor()
		pass

	def take_shots(self, parent, interval):
		'''Take screenshots @ interval ms, disable and enable appropriate buttons'''
		# if interval > 0:
			# self.d_sht_stop.configure(state=tk.NORMAL)
			# self.d_sht_start.configure(state=tk.DISABLED)
			# interval = self.d_sht_int.get() get() not working
		# else:
			# self.d_sht_start.configure(state='normal')
			# self.d_sht_stop.configure(state='disabled')
		self.rec_qe.put(interval)

	def input_audio(self, parent_pyaudio):
			#Need to contact parent's pyaudio object
		ndev = parent_pyaudio.get_device_count()

		n = 0
		ins = ""
		outs = ""
		while n < ndev:
			s = parent_pyaudio.get_device_info_by_index(n)
			print n, s
			if s['maxInputChannels'] > 0:
				ins = ins + str(s['index']) + ": " + s['name'] + "\n"
			if s['maxOutputChannels'] > 0:
				outs = outs + str(s['index']) + ": " + s['name'] + "\n"
			n = n + 1


		self.audio_device = None

		s = ttk.tkSimpleDialog.askstring("Device", "Type audio input device's index:\nPress Cancel for Windows Default\n\n" + ins + "\n\nNumber: ")
		if (s != None):         # If Cancel pressed, then None
			try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
				v = int(s)
			except:
				s = "error"

			if s != "error":
				if v < 0 or v > ndev:
					v = 0
				self.audio_device = v
