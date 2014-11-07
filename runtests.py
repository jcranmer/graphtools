#!/usr/bin/env python

import os
import subprocess
import sys

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %0 xunit.xml" % sys.argv[0]
    sys.exit(1)

# This is the directory of runtests.py
directory = os.path.dirname(os.path.realpath(__file__))

graphmaker = os.path.join(directory, "graphmaker.py")
testdir = os.path.join(directory, "tests")
tests = filter(lambda f : f.endswith('.png'), os.listdir(testdir))

def runTest(test, xunitfile):
    testscript = os.path.join(testdir, os.path.splitext(test)[0] + ".py")
    gold = os.path.join(testdir, test)
    if not os.path.exists(testscript):
        raise Exception("Cannot find file %s" % os.path.basename(testscript))
    output = os.tmpfile()
    stderr = os.tmpfile()
    try:
        subprocess.check_call([graphmaker, testscript], stdout=output,
            stderr=stderr, cwd=testdir)
        output.seek(0)
        subprocess.check_call(["cmp", gold], stdin=output, stderr=stderr)
    finally:
        stderr.seek(0)
        rawstderr = stderr.read()
        if rawstderr:
            import xml.sax.saxutils
            xunitfile.write('<system-err>\n')
            xunitfile.write(xml.sax.saxutils.quoteattr(rawstderr))
            xunitfile.write('</system-err>\n')

with open(sys.argv[1], 'w') as xunitfile:
    xunitfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    xunitfile.write('<testsuite name="graphtools" tests="%d">\n' % len(tests))
    for test in tests:
        xunitfile.write('<testcase name="%s">\n' % test)
        try:
            runTest(test, xunitfile)
        except:
            print "Test", test, "failed:", sys.exc_info()[1]
            xunitfile.write('<failure type="Unknown">%s</failure>\n'
                % sys.exc_info()[1])
        xunitfile.write('</testcase>\n')
    xunitfile.write('</testsuite>\n')
