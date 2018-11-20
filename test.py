import pyaudio
import wave
import sys
import time

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')
wfout = wave.open("out.wav", 'wb')
wfout.setnchannels(2)
wfout.setsampwidth(2)
wfout.setframerate(44100)

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    #data = wf.readframes(frame_count)
    #print(time_info)
    wfout.writeframes(in_data)
    #print(len(in_data))
    return (in_data, pyaudio.paContinue)



# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=44100,
                output=True,
                input=True,
                stream_callback=callback)
#print(p.get_default_input_device_info())
#print(p.get_sample_size(p.get_default_input_device_info()))


# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()
wfout.close()

# close PyAudio (7)
p.terminate()