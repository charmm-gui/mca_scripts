#!/usr/bin/env python3
import itertools as it
import os
import sys
from glob import glob
from contextlib import ExitStack

selections = []
with open('settings.str') as settings_file:
    for line in settings_file:
        line = line.lower().strip()
        if line.startswith('set '):
            selections.append(line.split()[-1])

pairs = it.combinations_with_replacement(selections, r=2)
for pair in pairs:
    pair = '_'.join(pair)
    if pair == 'memb_memb':
        continue
    infiles = glob(f'contact_{pair}.dat.*')
    outfile = f'contact_{pair}.dat'

    with ExitStack() as stack:
        infiles = [stack.enter_context(open(fname)) for fname in infiles]
        output = []

        # advance files past header
        file_times = []
        header = None
        next_file = None
        for infile in infiles:
            for line in infile:
                if line.startswith('#') and header is None:
                    header = line.strip()
                    break
                elif header is None:
                    print('no header in', infile.name, file=sys.stderr)
                    sys.exit(1)
                break

        # determine each file's start time
        first_time = {infile.name: None for infile in infiles}
        next_line  = first_time.copy()
        for infile in infiles:
            for line in infile:
                line = line.strip()
                next_line[infile.name] = line
                first_time[infile.name] = float(line.split()[0])
                break

        # sort infiles by start time
        infiles = sorted(infiles, key=lambda i: first_time[i.name])

        # concatenate the files
        for infile in infiles:
            line = next_line[infile.name]
            output.append(next_line[infile.name])
            last_time = float(line.split()[0])
            for line in infile:
                line = line.strip()
                time = float(line.split()[0])
                # time going backwards means write was interrupted
                if time < last_time:
                    break
                output.append(line)

    with open(outfile, 'w') as outfile:
        # write header
        print('writing', outfile.name)
        print(header, file=outfile)

        # check for duplicate times, write the *newest* version
        times = [float(line.split()[0]) for line in output]
        for index, time in enumerate(times):
            matches = [index for index,item in enumerate(times) if time == item]
            index = matches[-1]
            print(output[index], file=outfile)
