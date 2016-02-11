from msdpackage import create_idix, create_songdet, create_songindex, create_usrsong, mismatch_list
from kmeanspkg import check_accuracy, create_actlikes, create_likecluster, create_predlikes, create_setply, create_userkmeans, generate_threshold


def setup(file):
    import os
    import re
    configdict = dict()
    matchpat = r"\'(.+?)\'"
    filepath = os.getcwd() + '/' + file + ".txt"
    if os.path.isfile(filepath):
        print "Found the config file... Reading contents..."
        for line in open(filepath, "rb").readlines():
            print line
            if len(re.findall(matchpat, line)) != 0:
                if line.find("SUMFILE") == 0:
                    configdict["SUMFILE"] = re.findall(matchpat, line)[0]
                elif line.find("msd_path") == 0:
                    configdict["msd_path"] = re.findall(matchpat, line)[0]
                elif line.find("msd_code_path") == 0:
                    configdict["msd_code_path"] = re.findall(matchpat, line)[0]
                elif line.find("USRPROF") == 0:
                    configdict["USRPROF"] = re.findall(matchpat, line)[0]
    else:
        print "Cannot find any config file named " + file + ".txt in your current folder" + os.getcwd()
        print "Please try again"
        main()
    print configdict.keys()
    return configdict


def main():
    import os
    import sys
    sys.path.append('/home/gaurav/MSongsDB-master/PythonSrc')
    import hdf5_getters
    configfile = raw_input(
        "Please enter the name of the configuration file:\n")
    msd_var_dict = setup(configfile)
    SUMFILE = msd_var_dict["SUMFILE"]
    msd_path = msd_var_dict["msd_path"]
    msd_data_path = os.path.join(msd_path, 'data')
    msd_addf_path = os.path.join(msd_path, 'AdditionalFiles')
    msd_code_path = msd_var_dict["msd_code_path"]
    USRPROF = msd_var_dict["USRPROF"]

    H5 = hdf5_getters.open_h5_file_read(SUMFILE)

    if not os.path.exists("top100usrsong.txt"):
        create_usrsong(USRPROF)
        print ("top100usrsong.txt created")

    if not os.path.exists("songidix.txt"):
        create_idix(H5, msd_data_path)
        print "songidix.txt created"

    if not os.path.exists("songindex.txt"):
        create_songindex("songidix.txt", "unqsngfle.txt")
        print "songindex.txt created"

    if not os.path.exists("songdet.txt"):
        create_songdet(H5, "songindex.txt")
        print "songindex.txt created"

    if not os.path.exists("trainfile.txt") or not os.path.exists("testfile.txt") or not os.path.exists("likefile.txt"):
        create_setply()
        print "train,test and like files created."
    if not os.path.exists("userclusters.txt"):
        create_userkmeans()
        print "userclusters.txt created."
    if not os.path.exists("userclusterthresh.txt"):
        generate_threshold()
        print "userclusterthresh.txt created."
    if not os.path.exists("actlikfile.txt"):
        create_actlikes()
        print "actlikfile.txt created."
    if not os.path.exists("predlikfile.txt"):
        create_predlikes()
        print "predlikfile.txt created."
    if not os.path.exists("accuracy.txt"):
        check_accuracy()

if __name__ == "__main__":
    main()
