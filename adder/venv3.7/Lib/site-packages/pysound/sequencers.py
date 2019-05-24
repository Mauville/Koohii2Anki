# Author:  Martin McBride
# Created: 2018-09-20
# Copyright (C) 2018, Martin McBride
# License: MIT

from pysound import buffer
import numpy as np


def join(buffers):
    return np.concatenate(buffers)

class BasicSequence:

    def __init__(self, params, instrument, step):
        self.params = params
        self.instrument = instrument
        self.step = step
        self.buffer = buffer.create_buffer(params, 0)
        self.pos = 0

    def insert_next(self, frequency, duration=1, **extras):
        print(self.pos)
        params = buffer.BufferParams(self.params).set_length(self.step*duration)
        buf = self.instrument(params, frequency=frequency, **extras)
        buffer.insert_array(self.buffer, buf, self.pos)
        self.pos += params.length
        return self

    def insert_at(self, pos, frequency, duration=1, **extras):
        params = buffer.BufferParams(self.params).set_length(self.step*duration)
        buf = self.instrument(params, frequency=frequency, **extras)
        buffer.insert_array(self.buffer, buf, pos)
        self.pos = pos + params.length
        return self

    def insert_blank(self, duration=1):
        self.pos += self.params.b2s(self.step*duration)
        return self

    def get_buffer(self):
        return self.buffer
