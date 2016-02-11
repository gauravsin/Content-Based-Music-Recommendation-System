import os
import glob
basedir = '/home/gaurav/PythonDir/ProjectWork/MillionSongSubset'
def count_all_files(basedir,ext='.h5') :
    cnt = 0
    for root, dirs, files in os.walk(basedir):
        files = glob.glob(os.path.join(root,'*'+ext))
        cnt += len(files)
    return cnt

print count_all_files(basedir)