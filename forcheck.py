import os
import shutil
def forcheck():
    dname='./Picture/'
    go='./testPicture/'
    dirs = os.listdir(dname)
    for d in dirs:
        #os.mkdir("./testPicture/"+d)
        files = os.listdir(dname + d)
        if len(files)==0:
            continue
        for i in xrange(10):
            shutil.move(dname+d+"/"+files[i], go+d+"/")
        print d

if __name__ == "__main__":
    forcheck()
