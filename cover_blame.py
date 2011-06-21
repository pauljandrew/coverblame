import sys
import collections
import os
from subprocess import Popen, PIPE, STDOUT
import re

culprits = {}
culpritcount = {}

def main():
    argv = sys.argv
    coverout = argv[1]
    if not os.path.exists(coverout):
        print "No such file"
    for line in open(coverout,'r').readlines(): 
        parse_line(line)
    for dude in culprits:
        print dude, "-", culpritcount[dude]
        for key, val in culprits[dude].items():
            print "---", key, val

def get_filename(module):
    return "%s.py" % module.replace(".", "/")

def parse_line(line):
        parts = line.split()
        module = get_filename(parts[0])
        percent = parts[3]
        if percent == "100%":
            return
        uncovered = parts[-1]
        if uncovered.find("-") != -1:
            start, end = [int(i) for i in uncovered.split("-")]
            for i in range(start, end):
                blame(module, i)
        else:
            blame(module, int(uncovered))

def update_counts(culprit, module, lineno):
    if culprit not in culprits.keys():
        culprits[culprit] = {}
        culpritcount[culprit] = 0
    culpritcount[culprit] += 1
    if module not in culprits[culprit].keys():
        culprits[culprit][module] = [lineno]
    else:
        culprits[culprit][module].append(lineno)

def blame(module, lineno):
    cmd = "git blame {file} -L {line},{line}".format(file=module, line=lineno)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    culprit = output.split('(')[1].split(' 20')[0]
    update_counts(culprit, module, lineno)


if __name__ == '__main__':
    main()
