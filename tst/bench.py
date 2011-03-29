import subprocess
import datetime

def report(exe, scriptname, *args):
    cmd = (exe, scriptname)+args
    print " ".join(cmd),
    pretime = datetime.datetime.now()
    #subprocess.check_call(cmd)
    retcode = subprocess.call(cmd)
    if retcode == 0:
        posttime = datetime.datetime.now()
        dur = posttime-pretime
        print dur
    else:
        print "FAILED"

if __name__ == "__main__":
    #run several scripts as benchmarks
    #test the timing of each
    #put the fastest one first so we get results sooner
    report("pypy",   "tst/bbucket.py", "cached")
    report("python", "tst/bbucket.py", "cached")
    report("pypy",   "tst/bbucket.py")
    report("python", "tst/bbucket.py")
