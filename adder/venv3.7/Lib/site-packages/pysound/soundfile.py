# Author:  Martin McBride
# Created: 2018-04-21
# Copyright (C) 2018, Martin McBride
# License: MIT

import wave
import array

def save(params, filename, source):
    '''
    Write a sequence of samples as a WAV file
    Currently a 16 bit mono file
    '''
    writer = wave.open(filename, 'wb');
    # Set the WAV file parameters, currently default values
    writer.setnchannels(1)
    writer.setsampwidth(2)
    writer.setframerate(params.sample_rate)
    data_out = array.array('h')
    for x in source:
        data_out.append(int(x * 32766))
    writer.writeframes(data_out.tostring())
    writer.close()
