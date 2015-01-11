#!/usr/bin/python

"""
Description: Tool for performing benchmarking of programs

Copyright (c) 2015, Lucian Radu Teodorescu
"""

import os, sys, shutil, time, glob, subprocess, resource, struct, numpy
from collections import defaultdict

import config

testsDir = 'tests'
resultsDir = 'results'
tmpDir = resultsDir + '/tmp'

tests = []

def getFileContents(filename):
    with open(filename) as f:
        return f.read().rstrip();

def measureCommand(command, fout):
    resReadPipe, resWritePipe = os.pipe()
    pid = os.fork()
    if pid == 0:
        # Start executing the command
        p = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=fout)

        # Wait until the command is finished, or we reach the timeout
        timeout = config.testTimeout
        while p.poll() is None and timeout > 0:
            time.sleep(1)
            timeout -= 1
        isTimeout = False
        if not timeout > 0:
            p.terminate()
            isTimeout = True

        # Send back the results and quit
        rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
        ttime = rusage.ru_utime + rusage.ru_stime
        os.write(resWritePipe, struct.pack('?', isTimeout))
        os.write(resWritePipe, struct.pack('f', ttime))
        os.write(resWritePipe, struct.pack('L', rusage.ru_maxrss))
        sys.exit(0)

    # Read the results from the forked process
    isTimeout = struct.unpack('?', os.read(resReadPipe, struct.calcsize('?')))[0]
    ttime = struct.unpack('f', os.read(resReadPipe, struct.calcsize('f')))[0]
    maxrss = struct.unpack('L', os.read(resReadPipe, struct.calcsize('L')))[0]
    return (isTimeout, ttime, maxrss)


class Test:
    def __init__(self, dir):
        self.name = os.path.basename(dir)
        self.dir = dir
        self.runArgs = {}
        self.programs = []
        self.results = defaultdict(lambda: [])
        for f in glob.glob(dir+'/run/*'):
            if os.path.isfile(f):                
                runName = os.path.splitext(os.path.basename(f))[0]
                if runName.startswith('.'):
                    continue
                runArgs = getFileContents(f)
                self.runArgs[runName] = runArgs
        if ( not self.runArgs ):
            raise Exception("No run files found in %s" % (dir+'/run'))
        print "  run arguments for '%s': %s" % (self.name, self.runArgs.keys())

    def __repr__(self):
        return "Test(%s, args=%s, programs=%s)" % (self.name, self.runArgs, self.programs)

    def compile(self):
        print "  %-20s\t" % self.name,
        os.chdir(self.dir)
        logFilename = '%s/comp_%s.log' % (tmpDir, self.name)
        with open(logFilename, 'w') as f:
            if config.cleanBeforeBuild:
                res = subprocess.call(['make', 'clean'], stderr=subprocess.STDOUT, stdout=f)
                if res != 0:
                    raise Exception("Cannot execute 'make clean' on programs; check the log file: %s" % logFilename)
            res = subprocess.call(['make'], stderr=subprocess.STDOUT, stdout=f)
            if res != 0:
                raise Exception("Cannot compile the programs; check the log file: %s" % logFilename)
        # Gather executables
        for f in glob.glob(self.dir+'/*.out'):
            if not os.path.isfile(f):
                print
                raise Exception("Invalid program file: %s" % f)
            if not os.access(f, os.X_OK):
                print
                raise Exception("Program is not executable: %s" % f)
            if os.path.splitext(os.path.basename(f))[0].startswith('.'):
                continue
            self.programs.append(f)
        if len(self.programs) > 7:
            print '%d programs' % len(self.programs)
        else:
            print [os.path.basename(p) for p in self.programs]

    def run(self):
        # Run the programs
        resLogFilename = '%s/results_%s.log' % (resultsDir, self.name)
        with open(resLogFilename, 'w') as flog:
            for prog in sorted(self.programs):
                for argsName in sorted(self.runArgs):
                    for r in range(0, config.numRepeats):
                        args = self.runArgs[argsName]
                        progName = os.path.basename(prog)
                        progNameBase = os.path.splitext(progName)[0]
                        print "  %d: %s/%s %s:" % (r+1, self.name, progName, args)
                        print >>flog, "  %d: %s/%s %s:" % (r+1, self.name, progName, args)
                        logFilename = '%s/%s.%s.%s.%d.run.log' % (tmpDir, self.name, progName, argsName, r+1)
                        with open(logFilename, 'w') as fout:
                            os.chdir(self.dir)
                            isTimeout, time, mem = measureCommand([prog, args], fout)
                            if isTimeout:
                                print "      TIMEOUT - time: %f, mem: %gKB" % (time, mem/1024)
                                print >>flog, "      TIMEOUT - time: %f, mem: %gKB" % (time, mem/1024)
                                time = config.testTimeout + 1
                            else:
                                print "      time: %f, mem: %gKB" % (time, mem/1024)
                                print >>flog, "      time: %f, mem: %gKB" % (time, mem/1024)
                            self.results[(progName, args)].append((time, mem))

            # Average and print the results
            csvFilename = '%s/results_%s.csv' % (resultsDir, self.name)
            print "Results for '%s'" % self.name
            with open(csvFilename, 'w') as fout:
                print '# Program name, args, time (s), time deviation (s), memory (KB), memory deviation (KB)'
                print >>fout, '# Program name, args, time (s), time deviation (s), memory (KB), memory deviation (KB)'
                print >>flog, "Test results:"
                for k in sorted(self.results):
                    val = self.results[k]
                    print >>flog, "%s %s: %s" % (k[0], k[1], val)
                    if config.ignoreFirstRun:
                        val.pop(0)
                    times, mems = zip(*val)
                    timeAvg = numpy.mean(times)
                    timeStd = numpy.std(times)
                    memAvg = numpy.mean(mems) / 1024
                    memStd = numpy.std(mems) / 1024
                    print '%s, \t%s,\t %f, \t%f, \t%g, \t%g' % (k[0], k[1], timeAvg, timeStd, memAvg, memStd)
                    print >>fout, '%s, \t%s,\t %f, \t%f, \t%g, \t%g' % (k[0], k[1], timeAvg, timeStd, memAvg, memStd)
            

def ensureCleanDir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def checkDirectories():
    thisDir = os.path.dirname(os.path.realpath(__file__))
    global testsDir
    global resultsDir
    global tmpDir
    testsDir = thisDir + '/' + testsDir
    resultsDir = thisDir + '/' + resultsDir
    tmpDir = thisDir + '/' + tmpDir
    if not os.path.isdir(testsDir):
        print 'Cannot find tests directory: %s' % testsDir
        sys.exit(1)
    ensureCleanDir(resultsDir)
    ensureCleanDir(tmpDir)


def gatherTests():
    if os.path.isdir(testsDir+'/run'):
        # Don't consider the subdirs; all the data is in the tests folder
        tests.append(Test(testsDir))
    else:
        for d in glob.glob(testsDir+'/*'):
            if os.path.isdir(d):
                if os.path.splitext(os.path.basename(d))[0].startswith('.'):
                    continue
                tests.append(Test(d))
    # print '  available tests: %s' % [t.name for t in tests]


def main():
    print 'bench_tool, copyright (c) 2015 Lucian Radu Teodorescu'

    oldDir = os.getcwd()
    try:
        print 'Initializing...'
        checkDirectories()
        gatherTests()
        print 'Compiling programs...'
        for t in tests:
            t.compile()
        print 'Performing the benchmark...'
        for t in tests:
            t.run()

    except KeyboardInterrupt:
        print 'INTERRUPTED'
    except Exception as e:
        print 'ERROR: %s' % str(e)
    os.chdir(oldDir)
    print ''

if __name__ == "__main__":
    main()
