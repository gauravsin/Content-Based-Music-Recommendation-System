import os
import pickle
SUMFILE = '/DataOne/MillionSongData/AdditionalFiles/msd_summary_file.h5'
msd_path = '/DataOne/MillionSongData'
msd_data_path = os.path.join(msd_path, 'data')
msd_addf_path = os.path.join(msd_path, 'AdditionalFiles')
# assert os.path.isdir(msd_path),'wrong path' # sanity check
msd_code_path = '/home/gaurav/MSongsDB-master'
USRPROF = '/home/gaurav/train_triplets.txt'


def mismatch_list():
    '''
    Used to Remove the songs which have a mismatch from the MSD.
        Basically, corrects an error on the MSD data.
    '''
    return_list = []
    file_ptr = open('sid_mismatches.txt', mode='r')
    for i in file_ptr.readlines():
        return_list.append(i.partition('<')[2].split()[0])
    return return_list


def create_usrsong(userfile):
    '''
    Stores user-song-playcount data in a dictionary.
    Format of dictionary: { UserID : { SongID : PlayCount } }
    '''
    usr100 = open("top_100_raters")
    usrprof = open(userfile)
    usrsong = open("top100usrsong.txt", "wb")
    usrsongdict = dict()
    mislist = mismatch_list()

    unqsngset = set()
    for line1 in usr100:
        usrid1 = line1.strip()
        for line2 in usrprof:
            usrid2 = line2.strip().split()[0]
            if usrid1 != usrid2:
                continue
            songid = line2.strip().split()[1]
            if songid not in mislist:
                playcnt = line2.strip().split()[2]
                if usrid1 in usrsongdict:
                    usrsongdict[usrid1][songid] = usrsongdict[
                        usrid1].get(songid, 0) + int(playcnt)
                    unqsngset.add(songid)
                else:
                    usrsongdict[usrid1] = dict()
                    usrsongdict[usrid1][songid] = usrsongdict[
                        usrid1].get(songid, 0) + int(playcnt)
                    unqsngset.add(songid)
        usrprof.seek(0)
        # print "User id",usrid1
    pickle.dump(unqsngset, open("unqsngfle.txt", "wb"))
    pickle.dump(usrsongdict, usrsong)
    usrsong.close()


def create_idix(h5, msd_path):
    '''
        Creates indices for the million songs.
        The reason is because songs are accessed as indices from 0
        to (the maximum number of songs - 1) and not SongIDs.
    '''
    import hdf5_getters
    totsng = hdf5_getters.get_num_songs(h5)
    idixdic = dict()
    for count in range(0, totsng):
        idixdic[hdf5_getters.get_song_id(h5, count)] = count
    idixfile = open("songidix.txt", "wb")
    pickle.dump(idixdic, idixfile)
    idixfile.close()


def create_songindex(idxfile, sngfile):
    '''
        Creates indices for only the required songs.
        The reason is because songs are accessed as indices from 0
        to (the maximum number of songs - 1) and not SongIDs.
        This is created so as to just possess the indices for the
        required songs.
    '''
    infile1 = open(sngfile, "rb")
    sngset = pickle.load(infile1)
    infile2 = open(idxfile, "rb")
    idxdic = pickle.load(infile2)
    usrindxdic = dict()
    for elem in sngset:
        usrindxdic[elem] = idxdic[elem]
    sngidxfile = open("songindex.txt", "wb")
    pickle.dump(usrindxdic, sngidxfile)
    sngidxfile.close()


def create_songdet(h5, sngidxfle):
    '''
    Collects song details for all unique songs heard by 100 raters.
    Format of dictionary: { SongID : [ Att_0, Att_1, Att_2 ] }
    '''
    import hdf5_getters
    sngdetfle = open("songdet.txt", "wb")
    sngdetdic = dict()
    sngidxfle = open(sngidxfle, "rb")
    sngidxdic = pickle.load(sngidxfle)
    for elem in sngidxdic:
        songidx = sngidxdic[elem]
        tempo = hdf5_getters.get_tempo(h5, songidx)
        loud = hdf5_getters.get_loudness(h5, songidx)
        year = hdf5_getters.get_year(h5, songidx)
        tmsig = hdf5_getters.get_time_signature(h5, songidx)
        key = hdf5_getters.get_key(h5, songidx)
        mode = hdf5_getters.get_mode(h5, songidx)
        duration = hdf5_getters.get_duration(h5, songidx)
        fadein = hdf5_getters.get_end_of_fade_in(h5, songidx)
        fadeout = hdf5_getters.get_start_of_fade_out(h5, songidx)
        artfam = hdf5_getters.get_artist_familiarity(h5, songidx)
        sngdetdic[elem] = [duration, tmsig, tempo,
                           key, mode, fadein, fadeout, year, loud, artfam]
    pickle.dump(sngdetdic, sngdetfle)
    sngdetfle.close()
