import pickle
import numpy as np
import time
from scipy.cluster.vq import kmeans2


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def get_eucldist(list1, list2):
    '''
    returns the euclidean distance between two vectors of equal length
    '''
    arr1 = np.array(list1)
    arr2 = np.array(list2)
    eucdist = np.linalg.norm(arr1 - arr2)
    return eucdist


def create_setply():
    '''
    Computes the training set, testing set, likeness set for clustering
    Takes every user's song bunch and divides them into a ground dictionary,
    a validation dictionary and a likeness dictionary.
    The likeness is computed using another function (create_likecluster(songs))
    '''
    import random
    usrsngfile = open("top100usrsong.txt", "rb")
    usrsngdict = pickle.load(usrsngfile)
    traindict = dict()
    testdict = dict()
    likedict = dict()
    for userid in usrsngdict.keys():
        likeval = create_likecluster(usrsngdict[userid])
        index = 0
        trainlen = len(usrsngdict[userid]) * 0.2
        while bool(usrsngdict[userid]):
            songid = random.choice(usrsngdict[userid].keys())
            plycnt = usrsngdict[userid].pop(songid)
            if index < trainlen:
                index += 1
                if plycnt >= likeval:
                    if userid in traindict:
                        traindict[userid][songid] = traindict[
                            userid].get(songid, 0) + int(plycnt)
                    else:
                        traindict[userid] = dict()
                        traindict[userid][songid] = traindict[
                            userid].get(songid, 0) + int(plycnt)
            else:
                if userid in testdict:
                    testdict[userid][songid] = testdict[
                        userid].get(songid, 0) + int(plycnt)
                else:
                    testdict[userid] = dict()
                    testdict[userid][songid] = testdict[
                        userid].get(songid, 0) + int(plycnt)
        likedict[userid] = likeval
    pickle.dump(traindict, open("trainfile.txt", "wb"))
    pickle.dump(testdict, open("testfile.txt", "wb"))
    pickle.dump(likedict, open("likefile.txt", "wb"))


def create_likecluster(usersongdict):
    '''
    Creates 4 clusters for every users playcounts.
    Selects 2 largest clusters considering the number of playcounts.
    Selects the one with the highest average playcount .
    Selects the minimum playcount value from this cluster.
    Returns the Minimum Playcount = Likness barrier.
    '''
    import operator
    k = 4
    plycntlis = []
    songlist = []
    dummylis = []
    for songid in usersongdict:
        songlist.append(songid)
        dummylis.append(1)
        plycntlis.append(usersongdict[songid])
    twodarr = list(zip(plycntlis, dummylis))
    plycntarr = np.array(normalize(twodarr))
    res, idx = kmeans2(plycntarr, k, 100, minit='points')
    cluslist = list(idx)
    plycntdic = dict(zip(songlist, cluslist))  # {S01:2,S02:1,S03:0}
    clusdict = {clus: cluslist.count(clus) for clus in range(k)}
    sortclus = sorted(clusdict.items(), key=operator.itemgetter(
        1), reverse=True)  # ((1:35),(3:25),(2:15))
    maxcls = sortclus[0][0]
    seccls = sortclus[1][0]
    maxsum, maxcnt, maxavg = 0, 0, 0
    secsum, seccnt, secavg = 0, 0, 0
    needavg = 0
    for songid in plycntdic.keys():
        if plycntdic[songid] == maxcls:
            maxsum += usersongdict[songid]
            maxcnt += 1
        elif plycntdic[songid] == seccls:
            secsum += usersongdict[songid]
            seccnt += 1
    maxavg = maxsum / float(maxcnt)
    secavg = secsum / float(seccnt)
    needavg = max(maxavg, secavg)
    needcls = -1
    if needavg == maxavg:
        needcls = maxcls
    else:
        needcls = seccls
    minplycnt = 999999
    for songid in plycntdic.keys():
        if needcls == plycntdic[songid]:
            if usersongdict[songid] < minplycnt:
                minplycnt = usersongdict[songid]
    return minplycnt


def create_userkmeans():
    '''
    Creates 15 clusters for every user's songs under ground set.

    '''
    k = 15
    userkmeandict = dict()
    trainfile = open("trainfile.txt", "rb")
    traindict = pickle.load(trainfile)
    songfile = open("songdet.txt", "rb")
    songdict = pickle.load(songfile)
    sngclsdict = dict()
    for user in traindict.keys():
        usersongattlist = []
        snglist = []
        for usersong in traindict[user].keys():
            snglist.append(usersong)
            usersongattlist.append(
                normalize([songdict[usersong][0], songdict[usersong][1], songdict[usersong][3], songdict[usersong][6], songdict[usersong][8]]))
        usersongattarray = np.array(usersongattlist)
        res, idx = kmeans2(usersongattarray, k, 100, minit='points')
        lis1 = list(idx)
        sngclsdict = dict(zip(snglist, idx))
        userkmeandict[user] = [res, sngclsdict]
        sngclsdict = dict()
    pickle.dump(userkmeandict, open("userclusters.txt", "wb"))


def generate_threshold():
    '''
    generates a dictionary with key = userid, value = [[Centers],[threshold1,threshold2...]]
    and returns dictionary name
    For every users cluster set, a threshold distance was computed.
    Distance was measured as Euclidean distance.
    The farthest song in every cluster marked the threshold.
    The distance of the song from the center = Cluster threshold
    '''
    usrclsfile = open("userclusters.txt", "rb")
    usrclsdict = pickle.load(usrclsfile)
    usrsngfile = open("top100usrsong.txt", "rb")
    usrsngdict = pickle.load(usrsngfile)
    sngdetfile = open("songdet.txt", "rb")
    sngdetdict = pickle.load(sngdetfile)
    usrclsthresh = dict()
    for userid in usrclsdict.keys():
        clscentarr = list(usrclsdict[userid][0])
        clsidxdic = usrclsdict[userid][1]
        threshold = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        index = 0
        for clusng in clsidxdic.keys():
            for elem in range(15):
                if clsidxdic[clusng] == elem:
                    attlist = [sngdetdict[clusng][0], sngdetdict[clusng][1], sngdetdict[
                        clusng][3], sngdetdict[clusng][6], sngdetdict[clusng][8]]
                    attdist = get_eucldist(clscentarr[elem], attlist)
                    if (threshold[elem] < attdist):
                        threshold[elem] = attdist
                    break
        usrclsthresh[userid] = [clscentarr, threshold]
    pickle.dump(usrclsthresh, open("userclusterthresh.txt", "wb"))
    return usrclsthresh


def create_actlikes():
    '''
    Selects each song from the testing set for each user.
    The songs playcount is compared with the users likeness boundary.
    If it crosses this boundary, it is marked as being likeable.
    The dictionary is dumped in to a file and the format is:
    { UserID : { SongID : 1/0 } }
    1 represents the user liking the song.
    0 represents the users dislike.
    Creates dictionary actlikfile.txt
    '''
    testdict = pickle.load(open("testfile.txt", "rb"))
    likedict = pickle.load(open("likefile.txt", "rb"))
    detdict = pickle.load(open("songdet.txt", "rb"))
    actlikdic = dict()
    for userid in testdict.keys():
        for songid in testdict[userid].keys():
            if testdict[userid][songid] >= likedict[userid]:
                if userid in actlikdic.keys():
                    actlikdic[userid][songid] = actlikdic[
                        userid].get(songid, 0) + 1
                else:
                    actlikdic[userid] = dict()
                    actlikdic[userid][songid] = actlikdic[
                        userid].get(songid, 0) + 1
            else:
                if userid in actlikdic.keys():
                    actlikdic[userid][songid] = actlikdic[
                        userid].get(songid, 0) + 0
                else:
                    actlikdic[userid] = dict()
                    actlikdic[userid][songid] = actlikdic[
                        userid].get(songid, 0) + 0
    pickle.dump(actlikdic, open("actlikfile.txt", "wb"))


def create_predlikes():
    '''
    Selects each song from the testing set for each user.
    The song is plotted on the training space.
    The nearest cluster is obtained.
    The song is marked as likeable if it lies within cluster threshold.
    These make up the prediction file and the dictionary format is:
    { UserID : { SongID : 1/0 } }
    1 represents the user liking the song
    0 represents the users dislike
    Creates dictionary predlikfile.txt
    '''
    testdict = pickle.load(open("testfile.txt", "rb"))
    detdict = pickle.load(open("songdet.txt", "rb"))
    threshdict = pickle.load(open("userclusterthresh.txt", "rb"))
    predlikdic = dict()
    for userid in testdict.keys():
        for songid in testdict[userid].keys():
            songatts = [detdict[songid][0], detdict[songid][1], detdict[
                songid][3], detdict[songid][6], detdict[songid][8]]
            close = 9999999999.99
            closecent = -1
            for cluster in range(15):
                centatts = threshdict[userid][0][cluster]
                songdist = get_eucldist(songatts, centatts)
                if songdist <= close:
                    closecent = cluster
                    close = songdist
            threshdist = threshdict[userid][1][closecent]
            if close <= threshdist:
                if userid in predlikdic.keys():
                    predlikdic[userid][songid] = predlikdic[
                        userid].get(songid, 0) + 1
                else:
                    predlikdic[userid] = dict()
                    predlikdic[userid][songid] = predlikdic[
                        userid].get(songid, 0) + 1
            else:
                if userid in predlikdic.keys():
                    predlikdic[userid][songid] = predlikdic[
                        userid].get(songid, 0) + 0
                else:
                    predlikdic[userid] = dict()
                    predlikdic[userid][songid] = predlikdic[
                        userid].get(songid, 0) + 0
    pickle.dump(predlikdic, open("predlikfile.txt", "wb"))


def check_accuracy():
    '''
    Accuracy is displayed in the following format for every user:
                    Predictions  Like    Dislike
    Actual        Like            a             b
    Actual        Dislike       c             d
    a + b + c + d = Total number of songs in test set for the user.
    The data is stored in a file.
    '''
    actlikdic = pickle.load(open("actlikfile.txt", "rb"))
    predlikdic = pickle.load(open("predlikfile.txt", "rb"))
    testdict = pickle.load(open("testfile.txt", "rb"))
    curtime = time.time()
    confile = open("confile_" + str(curtime) + ".txt", "w")
    usraccdic = dict()
    totres = 0
    totsng = 0
    maxres = 0
    maxrat = 0
    minrat = 1
    maxtot = 0
    minres = 999999
    mintot = 999999
    for userid in testdict.keys():
        llcnt = 0
        ddcnt = 0
        ldcnt = 0
        dlcnt = 0
        for songid in testdict[userid].keys():
            if (actlikdic[userid][songid] > 0 and predlikdic[userid][songid] > 0):
                llcnt += 1
            elif (actlikdic[userid][songid] == 0 and predlikdic[userid][songid] == 0):
                ddcnt += 1
            elif (actlikdic[userid][songid] > 0 and predlikdic[userid][songid] == 0):
                ldcnt += 1
            elif (actlikdic[userid][songid] == 0 and predlikdic[userid][songid] > 0):
                dlcnt += 1
        confile.write(userid + "\n")
        confile.write(" " * 8 + " Predictions\n")
        confile.write(" " * 8 + " L " + "D\n")
        confile.write("Actual " + "L " + str(llcnt) + " " + str(ldcnt) + "\n")
        confile.write("Actual " + "D " + str(dlcnt) + " " + str(ddcnt) + "\n")
        confile.write("*" * 80 + "\n")
        usraccdic[userid] = [llcnt, ddcnt, ldcnt, dlcnt]
        totres = totres + llcnt + ddcnt
        totsng = totsng + llcnt + ddcnt + ldcnt + dlcnt
        if maxrat < (llcnt + ddcnt) / float(llcnt + ddcnt + ldcnt + dlcnt):
            maxrat = (llcnt + ddcnt) / float(llcnt + ddcnt + ldcnt + dlcnt)
        if minrat > (llcnt + ddcnt) / float(llcnt + ddcnt + ldcnt + dlcnt):
            minrat = (llcnt + ddcnt) / float(llcnt + ddcnt + ldcnt + dlcnt)
    accr = totres / float(totsng)
    accu = accr * 100
    maxu = maxrat * 100
    minu = minrat * 100

    print "Average accuracy:", accu
    print "Max accuracy:", maxu
    print "Min accuracy:", minu

    confile.close()
    pickle.dump(usraccdic, open("accuracy.txt", "wb"))
