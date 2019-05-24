# Author:  Martin McBride
# Created: 2018-04-22
# Copyright (C) 2018, Martin McBride
# License: MIT

# Numpy array is used to store sound data

import numpy as np

class BufferParams:
    '''
    Length and sample rate of a buffer
    '''
    
    def __init__(self, value=None):
        '''
        Create parameters
        :param value: sample rate to use, defaults to 11025
        If value is a BufferParams, copy its parameters
        If value is a number, set the sample rate to that value and set the length to the same value
        (giving a one second timeframe)
        If no value, set to 1 second at 44100 smaple rate
        '''
        if isinstance(value, BufferParams):
            self.sample_rate = value.sample_rate
            self.length = value.length
            self.tempo = value.tempo
        elif value == None:
            self.sample_rate = 44100
            self.length = self.sample_rate
            self.tempo = 60
        else:
            self.sample_rate = int(value)
            self.length = self.sample_rate
            self.tempo = 60

    def set_time(self, time):
        '''
        Update the length of the buffer in seconds
        :param time: number of seconds
        :return: self
        '''
        self.length = int(time*self.sample_rate)
        return self

    def set_length(self, length):
        '''
        Update the length of the buffer in samples
        :param length: number of samples
        :return: self
        '''
        self.length = length
        return self

    def set_tempo(self, tempo):
        '''
        Update the length of the buffer in samples
        :param tempo: beats per minute
        :return: self
        '''
        self.tempo = tempo
        return self

    def t2s(self, time):
        '''
        Converts a unit of time (in seconds) to a sample count
        '''
        return int(time*self.sample_rate)

    def b2s(self, beats):
        '''
        Converts a number of beats to a sample count
        '''
        return int(beats*60*self.sample_rate/self.tempo)

def create_buffer(params, value):
    '''
    If the value is a float, create a numpy array of the required length, filled with value
    If the value is a numpy array, check its length
    Otherwise throw a type error
    '''
    try:
        fv = float(value)
        return np.full(params.length, fv, np.float)
    except TypeError:
        if isinstance(value, np.ndarray):
            if (len(value)>=params.length):
                return value
        raise TypeError('Value must be a float or a numpy array ofthe required length')

'''
Mix an array into another at a certain point
dest - the main buffer
src - the data to be inserted
at - position (in samples) to insert the data
'''
def insert_array(dest, src, at):
    destlen = dest.size
    srclen = src.size
    if at < 0:                   #Before start
        return
    if at > destlen:             #After end
        return
    length = srclen
    if at + srclen > destlen:
        length -= at + srctlen - destlen
    if length <= 0:
        return
    dest[at:at+length] = np.add(dest[at:at+length], src[:length])
            
