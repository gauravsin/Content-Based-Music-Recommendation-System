import sys
sys.path.append('/home/gaurav/PythonDir/ProjectWork/MSongsDB-master/PythonSrc')
import hdf5_getters
sumfile = '/home/gaurav/PythonDir/ProjectWork/MillionSongSubset/AdditionalFiles/subset_msd_summary_file.h5'

h5 = hdf5_getters.open_h5_file_read(sumfile)
for k in range(10000):
    #a_name = hdf5_getters.get_artist_name(h5,k)
    hot1 = hdf5_getters.get_song_hotttnesss(h5,k)
    #if a_name == 'Radiohead':
    if hot1:
        print hdf5_getters.get_track_id(h5,k), hot1

#Faster
#h5 = hdf5_getters.open_h5_file_read(sumfile)
#idxs = h5.root.metadata.songs.getWhereList('artist_name=="Radiohead"')
#for idx in idxs:
#    print h5.root.analysis.songs.cols.track_id[idx]