# Author:  Martin McBride
# Created: 2018-09-25
# Copyright (C) 2018, Martin McBride
# License: MIT

import math
import numpy as np
from pysound.buffer import create_buffer


def echo(params, source, delay, strength):
    '''
    Create an echo
    :param params:
    :param source:
    :param delay:
    :param strength:
    :return:
    '''
    source = create_buffer(params, source)
    delay = create_buffer(params, delay)
    strength = create_buffer(params, strength)
    output = source[:]
    for i in range(params.length):
        d = int(i - delay[i])
        if 0 <= d < params.length:
            output[i] += source[d]*strength[i]
    return output
