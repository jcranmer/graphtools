#!/usr/bin/env python

import os
import subprocess
import sys

# This is the directory of runtests.py
directory = os.path.dirname(os.path.realpath(__file__))

graphmaker = os.path.join(directory, "graphmaker.py")
testdir = os.path.join(directory, "tests")
tests = filter(lambda f : f.endswith('.png'), os.listdir(testdir))

def runTest(test):
    testscript = os.path.join(testdir, os.path.splitext(test)[0] + ".py")
    gold = os.path.join(testdir, test)
    if not os.path.exists(testscript):
        raise Exception("Cannot find file %s" % os.path.basename(testscript))
    output = os.tmpfile()
    subprocess.check_call([graphmaker, testscript], stdout=output, cwd=testdir)
    output.seek(0)
    subprocess.check_call(["cmp", gold], stdin=output)

for test in tests:
    try:
        runTest(test)
    except:
        print "Test", test, "failed:", sys.exc_info()[1]
