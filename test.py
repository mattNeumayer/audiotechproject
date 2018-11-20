import pyaudio
import wave
import sys
import time

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

# instantiate PyAudio (1)
print(pyaudio.paWASAPI)
p = pyaudio.PyAudio()

wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
print(wasapi_info)

for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))
input_device = p.get_device_info_by_index(wasapi_info['defaultInputDevice'])
output_device = p.get_device_info_by_index(wasapi_info['defaultOutputDevice'])

print(input_device)
print(output_device)

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    print(time_info)
    return (in_data, pyaudio.paContinue)


print(p.is_format_supported(int(output_device['defaultSampleRate']),
                            input_device=wasapi_info['defaultInputDevice'],
                            input_channels=3,
                            input_format=pyaudio.paInt16,
                            output_device=wasapi_info['defaultOutputDevice'],
                            output_channels=2,
                            output_format=pyaudio.paInt16))

# open stream using callback (3)
stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=int(output_device['defaultSampleRate']),
                output=True,
                input=True,
                input_device_index=wasapi_info['defaultInputDevice'],
                output_device_index= wasapi_info['defaultOutputDevice'],
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()

# close PyAudio (7)
p.terminate()