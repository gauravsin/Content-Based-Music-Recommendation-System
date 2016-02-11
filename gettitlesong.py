import os
import glob
import sys
sys.path.append('/home/gaurav/PythonDir/ProjectWork/MSongsDB-master/PythonSrc')
import hdf5_getters
basedir = '/home/gaurav/PythonDir/ProjectWork/MillionSongSubset'
def get_all_titles(basedir,ext='.h5') :
    titles = []
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        for f in files:
            h5 = hdf5_getters.open_h5_file_read(f)
            titles.append( hdf5_getters.get_title(h5) )
            h5.close()
    return titles

print get_all_titles(basedir)