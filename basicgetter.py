#!/usr/bin/env python3.4

import sys
sys.path.append('/home/gaurav/PythonDir/ProjectWork/MSongsDB-master/PythonSrc')

import hdf5_getters

h5 = hdf5_getters.open_h5_file_read('/home/gaurav/PythonDir/ProjectWork/MillionSongSubset/data/A/A/A/TRAAAAW128F429D538.h5')
title = hdf5_getters.get_title(h5)
print(title.decode())

print(list(filter(lambda x: x[:3] == 'get',hdf5_getters.__dict__.keys())))

h5.close()
