
from scipy.io import wavfile
import numpy as np

def load_wave(wave_filename):
    try :
        frame_rate, data = wavfile.read(wave_filename)
        if data.dtype == np.uint8 :
            data = (data.astype(np.int16)-128)*256
        elif data.dtype != np.int16 : 
            raise Exception('Unhandeled sample width')
        if len(data.shape) == 1 :
            data = np.repeat(data,2)
            data = data.reshape((int(len(data)/2),2))
        elif len(data.shape) == 2 and data.shape[1] > 2:
            data= data[:,0:2]
        data_list = data.tolist()
        return frame_rate, \
               data_list
    except KeyboardInterrupt:
        raise
    except :
        return -1

def save_wave(frame_rate, audio_data, wave_filename):
    try :
        data = np.asarray(audio_data)
        mask = np.mod(data,1)
        if audio_data and (sum(mask == 0 )[0] < data.shape[0] or sum(mask == 0 )[1] < data.shape[0]):
            raise Exception('Invalid audio data')
        wavfile.write(wave_filename, frame_rate, data.astype(np.int16))
        return 0
    except KeyboardInterrupt:
        raise
    except :
        return -1

