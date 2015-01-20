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

memDiv = 1024.0*1024.0 if config.dumpMemAsMB else 1024.0
memUnit = 'MB' if config.dumpMemAsMB else 'KB'

def getFileContents(filename):
    with open(filename) as f:
        return f.read().rstrip()

def measureCommand(command, fout):
    resReadPipe, resWritePipe = os.pipe()
    pid = os.fork()
    if pid == 0:
        isTimeout = False
        try:
            # Start executing the command
            # print "Running: %s" % command
            command = command.split()
            p = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=fout)

            # Wait until the command is finished, or we reach the timeout
            timeout = config.testTimeout
            while p.poll() is None and timeout > 0:
                time.sleep(1)
                timeout -= 1
            if not timeout > 0:
                p.terminate()
                isTimeout = True
        except Exception as e:
            print 'RUN ERROR: %s' % str(e)
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
        self.programs = []
        self.runArgs = []
        self.results = defaultdict(lambda: [])

    def __repr__(self):
        return "Test(%s, programs=%s, args=%s)" % (self.name, self.programs, self.runArgs)

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

        # Gather programs; results a list of (name, executable)
        res = getFileContents('programs.in')
        progs = res.rstrip().split('\n')
        progs = filter(lambda p: not p.startswith('#'), progs)
        self.programs = []
        for p in progs:
            # Check if the line is of the form <name>:<executable>
            colon = p.find(':')
            if colon >= 0:
                self.programs.append( (p[0:colon].strip(), p[colon+1:].strip()) )
            else:
                name = p;
                if p.startswith('./'):
                    name = p[2:]
                name = name.replace('/', '_')

                self.programs.append( (name, p) )

        # Gather running arguments
        res = getFileContents('args.in')
        self.runArgs = res.rstrip().split('\n')
        self.runArgs = filter(lambda p: not p.startswith('#'), self.runArgs)

        if len(self.programs) > 5:
            print '%d programs' % len(self.programs),
        else:
            print [p[0] for p in self.programs],
        print " / ",
        if len(self.runArgs) > 7:
            print '%d args sets' % len(self.runArgs),
        else:
            print self.runArgs

    def run(self):
        # Run the programs
        resLogFilename = '%s/results_%s.log' % (resultsDir, self.name)
        with open(resLogFilename, 'w') as flog:
            for prog in self.programs:
                for args in self.runArgs:
                    for r in range(0, config.numRepeats):
                        progName = prog[0]
                        progExe = prog[1]
                        print "  %s: %s %s (%d)\t\t" % (self.name, progName, args, r+1),
                        print >>flog, "\n%s: %s %s (%d)" % (self.name, progName, args, r+1)
                        print >>flog, "  > %s %s" % (progExe, args)
                        sys.stdout.flush()
                        flog.flush()
                        logFilename = '%s/%s.%s %s.%d.run.log' % (tmpDir, self.name, progName, args, r+1)
                        with open(logFilename, 'w') as fout:
                            os.chdir(self.dir)
                            isTimeout, time, mem = measureCommand("%s %s" % (progExe, args), fout)
                            if isTimeout:
                                print "TIMEOUT - time: %f, mem: %f %s" % (time, mem/memDiv, memUnit)
                                print >>flog, "TIMEOUT - time: %f, mem: %f %s" % (time, mem/memDiv, memUnit)
                                time = config.testTimeout + 1
                            else:
                                print "time: %f, mem: %f %s" % (time, mem/memDiv, memUnit)
                                print >>flog, "time: %f, mem: %f %s" % (time, mem/memDiv, memUnit)
                            sys.stdout.flush()
                            flog.flush();
                            self.results[(progName, args)].append((time, mem))

            # Average and print the results
            csvFilename = '%s/results_%s.csv' % (resultsDir, self.name)
            print ""
            print "Results for '%s'" % self.name
            print >>flog, ""
            print >>flog, "Test results:"
            with open(csvFilename, 'w') as fout:
                print '# Program name, args, time (s), time deviation (s), memory (%s), memory deviation (%s)' % (memUnit, memUnit)
                print >>fout, '# Program name, args, time (s), time deviation (s), memory (%s), memory deviation (%s)' % (memUnit, memUnit)
                for k in sorted(self.results):
                    val = self.results[k]
                    print >>flog, "%s %s: %s" % (k[0], k[1], val),
                    if config.ignoreFirstRun:
                        val.pop(0)
                    times, mems = zip(*val)
                    timeAvg = numpy.mean(times)
                    timeStd = numpy.std(times)
                    memAvg = numpy.mean(mems) / memDiv
                    memStd = numpy.std(mems) / memDiv
                    print '%s, \t%s,\t %f, \t%f, \t%f, \t%f' % (k[0], k[1], timeAvg, timeStd, memAvg, memStd)
                    print >>fout, '%s, \t%s,\t %f, \t%f, \t%f, \t%f' % (k[0], k[1], timeAvg, timeStd, memAvg, memStd)
                    print >>flog, '\t=> (%f, %f)-(%f, %f)' % (timeAvg, timeStd, memAvg, memStd)
            print ""

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
    if os.path.isfile(testsDir+'/programs.in'):
        # Don't consider the subdirs; all the data is in the tests folder
        tests.append(Test(testsDir))
    else:
        for d in glob.glob(testsDir+'/*'):
            if os.path.isdir(d):
                if os.path.splitext(os.path.basename(d))[0].startswith('.'):
                    continue
                tests.append(Test(d))
    print '  available tests: %s' % [t.name for t in tests]


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
