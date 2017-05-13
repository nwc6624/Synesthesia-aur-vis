intro
Thank you for downloading Synesthesia:aur-vis, a visualizer for the rare disease. To start it, run Synesthesia.py in a Python environment on either Windows or Linux. Email nocaulfield <at> gmail.com for more assistance, or search for it on the Internet. A succesfully run program should have two windows—a screen displaying the camera's video, and a separate window with options labeled "Synesthesia:aur-vis Interface"

Synesthesia.py is in the Synesthesia,aur-vis directory


shortcomings
"Errors should never pass silently." wrote Tim Peters in the Zen of Python—an authoritative twenty lines of text for Pythonistas.
Our team needs to test .wav support, as of now, support for external audio files is defunct; only the microphone can be used. As for the GUI, it is mostly disconnected from the actual program. To modify any settings, the user will have to dive into the .py files. Large parts of the program's configuration cannot be modified through the graphical interface at this time, settings will have to be changed in the python code if the user wishes to change how the program reacts to audio. 

The current settings should work for most users, inquiries or problems should be reported to nocaulfield <at> gmail.com. These errors can be fixed in time for the Supercomputing Challenge Finals. Some areas of the code have been marked as they "will[soon] be modifiable through the graphical interface." Also, at the bottom of Synesthesia.py(line 265) is "s = SynesthesiaVisualizer(video_device=0, audio_device=0, get_audio=True, get_motion=True, get_contours=True, syn_overlay=True, grayscale=False, binary_image=False)" This snippet of code can be changed easily.

video_device can be changed to a video filename to fetch video from a files. In this example, the video is in the same location as Synesthesia.py: video_device='video.mp4'
Try different numbers from 0 to 20 as device indexes for both audio and video, if 0 does not work. 0 is the Windows default.
See freq_to_color() at line 63 for the conversion of sound frequencies to color. Varying the multiplier to a larger number should cause more intense visual artifacts.


epilepsy
WARNING: READ BEFORE RUNNING THIS PROGRAM!

A very small percentage of individuals may experience epileptic seizures when exposed to certain light patterns or flashing lights. Exposure to certain patterns or backgrounds on a computer screen, or while playing video games, may induce an epileptic seizure in these individuals. Certain conditions may induce previously undetected epileptic symptoms even in persons who have no history of prior seizures or epilepsy.

If you, or anyone in your family, have an epileptic condition, consult your physician prior to using this program. If you experience any of the following symptoms while playing a video or computer game -- dizziness, altered vision, eye or muscle twitches, loss of awareness, disorientation, any involuntary movement, or convulsions -- IMMEDIATELY discontinue use and consult your physician before resuming.


install
See INSTALL.txt




possible settings
A user can control application of visual artifacts according to motion contours of recent video and the contours of current frame, the color and intensity of which can depend on several aspects of input audio; namely, volume, frequency range, and loudest frequencies. Some example uses: high motion scenarios and high sound volume could result in severe obstruction of a person's sight; a low pitched sound could create a consistent blanket of a certain color; only a specific frequency range causes a certain color; and any other scenarios envisioned or experienced by the user. 
