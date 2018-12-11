# Audio Project: Python (pyaudio) and VST Support

We will send the actual source code via email.

The program can be started by executing the controller.py file.

### Task A
1. Play a given soundfile in its entirety, using a single high-level function call.
2. Play user-selected portions of a given soundfile, with user-selectable sampling rate. The program should display level meters in decibels that move appropriately during playback. 
3. Play a long soundfile, with continuous event-driven double-buffering of the disk I/O.
4. Display real-time dB meters of two live inputs. 
5. Record a short soundfile in its entirety.
6. Record a long soundfile, with continuous event-driven double-buffering of the disk I/O. The program must check for available disk space. The program must ask the user to confirm overwrite of any existing file.

Our program can do all of this except displaying 2 dB-graphs at the same time. Due to our VST support implementation it is difficult to display other meters than the output dB. We'd like to emphasize that our program is using PortAudio as backend and therefore is cross-platform and supports plenty of different sound API.
We also didn't implement user-selectable sampling rates for wav file because playing wav at the wrong sampling rate has no use in our opinion. But the sample rate of the input/output device can be selected by the user.

### Task B
We can load some VST plugins, display their control interface and pipe the input from both an input device and a wav file to the plugin and play/record the result.
We will show and explain more details in the presentation.



