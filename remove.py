def remove(name):
    import os
    f = open(name)
    f2 = open("tmpfile", 'w')
    for row in f:
        if(os.path.exists(row[0:-3])):
            f2.write(row)
    f.close()
    f2.close()
    os.rename("tmpfile", name)



if __name__ == "__main__":
    remove("train.txt")
    remove("test.txt")
