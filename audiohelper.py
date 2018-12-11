import numpy as np


def rms_func(data):
    """Avoids using Audioop"""
    rms = np.sqrt(np.mean(data**2))
    return rms


def convert_frame_from_bytes_to_numpy(frames, channels, bytes_type=np.int16, numpy_type=np.float64):
    frames_np = np.fromstring(frames, np.int16).astype(np.float64) / 32768.0
    deinterleaved = np.vstack([frames_np[idx::channels] for idx in range(channels)])
    return deinterleaved


def convert_frame_from_numpy_to_bytes(frames, bytes_type=np.int16):
    frames_out = (frames * 32768.0).astype(np.int16)
    interleaved = frames_out.reshape((-1,), order='F')
    return interleaved.tostring()


def _max_value(bytes_type):
    if bytes_type == np.int8:
        max_value = np.power(2, 7)
        print("WARNING: Using different byte type!")
    elif bytes_type == np.int16:
        max_value = np.power(2, 15)
    elif bytes_type == np.int32:
        max_value = np.power(2, 31)
        print("WARNING: Using different byte type!")
    elif bytes_type == np.float32:
        max_value = 1
        print("WARNING: Using different byte type!")
    elif bytes_type == np.float64:
        max_value = 1
        print("WARNING: Using different byte type!")
    else:
        raise ValueError('Unsupported bytes_type %s.' % str(bytes_type))
    return max_value
