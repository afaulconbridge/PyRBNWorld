import subprocess
import datetime

def report(exe, scriptname, *args):
    pretime = datetime.datetime.now()
    cmd = (exe, scriptname)+args
    print " ".join(cmd),
    subprocess.check_call(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    posttime = datetime.datetime.now()
    dur = posttime-pretime
    print dur

if __name__ == "__main__":
    #run several scripts as benchmarks
    #test the timing of each
    #put the fastest one first so we get results sooner
    report("pypy",   "tst/bbucket.py", "cached")
    report("python", "tst/bbucket.py", "cached")
    #report("pypy",   "tst/bbucket.py")
    #report("python", "tst/bbucket.py")
