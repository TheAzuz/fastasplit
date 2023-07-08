#!/bin/python3

import _version
import argparse
import sys, os

def getseqn(fasta: str, quiet: bool) -> int:
    if not quiet:
        print ('Counting total sequences in fasta file...')
    with open(fasta, 'r') as fastafile:
        seqn = 0
        for line in fastafile:
            if line[0] == '>':
                seqn += 1
    if not quiet:
        print (f"Found {seqn} sequences in fasta file")
    return seqn

def splite(fasta: str, prefix: str | None, full: bool, quiet: bool, dir: str, verbose: int):
    
    seqnum = getseqn(fasta, quiet)
    if seqnum > 100:
        flag = True
        while flag:
            cont = input(f"This command will create {seqnum} output files. Are you sure you want to proceed? (y/n) ").lower()
            if cont == 'n':
                flag = False
                quit()
            elif cont == 'y':
                flag = False

    ndigits = len(str(seqnum))

    with open(fasta, 'r') as fastafile:

        splitn = 1
        for line in fastafile:

            if line[0] == '>':
                
                if prefix != None:
                    name = f"{prefix}.{splitn:0{ndigits}d}.fa"
                    if not quiet:
                        if verbose > 0:
                            print(f"Creating split file {splitn}/{seqnum}...")
                        elif verbose > 1:
                            print(f"Creating split file {splitn}/{seqnum} for sequence: {line.strip()[1:]}")
                elif full:
                    name = line.strip()[1:]
                else:
                    words = line.strip().split()
                    name = f"{words[0][1:] if len(words[0]) > 1 else words[1]}.fa"
                    

                splitfile = open(f"{dir}/{name}", 'w')
                splitn += 1

            splitfile.write(line)


def splits(n: int, fasta: str, prefix: str, quiet: bool, dir: str, verbose: int):
    
    seqn = getseqn(fasta, quiet)

    filen = (seqn // n) + (seqn % n > 0)
    ndigits = len(str(filen))

    if filen > 100:
        flag = True
        while flag:
            cont = input(f"This command will create {filen} output files. Are you sure you want to proceed? (y/n) ").lower()
            if cont == 'n':
                flag = False
                quit()
            elif cont == 'y':
                flag = False

    with open(fasta, 'r') as fastafile:

        splitnum = 1
        splitfile = open(f"{dir}/{prefix}.{splitnum:0{ndigits}d}.fa", 'w')
        if not quiet:
            print (f"Creating split file {splitnum}/{filen}...")
        
        seqcount = 0
        for line in fastafile:
            
            if line[0] == '>':
                seqcount += 1
                if seqcount > n:
                    splitfile.close()
                    splitnum += 1
                    splitfile = open(f"{dir}/{prefix}.{splitnum:0{ndigits}d}.fa", 'w')
                    if not quiet:
                        print (f"Creating split file {splitnum}/{filen}...")
                    seqcount = 1

            splitfile.write(line)

def splitn(n: int, fasta: str, prefix: str, quiet: bool, dir: str, verbose: int):

    if n > 100:
        flag = True
        while flag:
            cont = input(f"This command will create {n} output files. Are you sure you want to proceed? (y/n) ").lower()
            if cont == 'n':
                flag = False
                quit()
            elif cont == 'y':
                flag = False

    ndigits = len(str(n))
    splitnum = getseqn(fasta, quiet)
    perfile, remain = (splitnum // n, splitnum % n)

    with open(fasta, 'r') as fastafile:

        splitnum = 1
        splitfile = open(f'{dir}/{prefix}.{splitnum:0{ndigits}d}.fa', 'w')
        if not quiet:
            print (f"Creating split file {splitnum}/{n}...")

        if remain > 0:
            perthisfile = perfile + 1
        else:
            perthisfile = perfile
        remain -= 1
        if verbose > 0:
            print (f"   Split file {splitnum+1} will contain {perthisfile} sequences")

        seqcount = 0
        for line in fastafile:

            if line[0] == '>':  # Line is a sequence header
                if verbose > 2:
                    print (f"Adding sequence: {line[1:].strip()}")
                seqcount += 1
                if seqcount > perthisfile:  # Need to open new split file
                    splitfile.close()
                    splitnum += 1
                    splitfile = open(f'{dir}/{prefix}.{splitnum:0{ndigits}d}.fa', 'w')
                    if not quiet:
                        print (f"Creating split file {splitnum}/{n}...")
                    if remain > 0: 
                        perthisfile = perfile + 1
                    else:
                        perthisfile = perfile
                    remain -= 1
                    if verbose > 0:
                        print (f"   Split file {splitnum} will contain {perthisfile} sequences")
                    seqcount = 1
            
            splitfile.write(line)

def pos_int(x):
    try:
        x = int(x)
    except ValueError:
        raise argparse.ArgumentError(None, f"argument -n/--number: Invalid positive integer value: {x}")
    if x <= 0:
        raise argparse.ArgumentError(None, f"argument -n/--number: Invalid positive integer value: {x}")
    return x

def main():
    parser = argparse.ArgumentParser(description="Split a fasta file into smaller files with an equal number of sequences.")

    parser.add_argument('--version', action='version', version="%(prog)s {}".format(_version.__version__), help='Show version information and exit')

    parser.add_argument('-d', '--directory', metavar='dir', dest='dir', default='.', help='Specify directory to place split files in. Default is \'.\'',)

    parser.add_argument('-p', '--prefix', metavar='prefix', dest='prefix', default='split', help='Prefix to use for naming all split files. Default is \'split\', or first word of sequence header if `-e`.')
    
    parser.add_argument('-e', '--every', dest='every', action='store_true', help='Split each sequence into its own file. Do not provide `-n`')

    parser.add_argument('-f', '--fullhead', dest='full', action='store_true', help='Use with `-e`. Use full sequence header as prefix instead of just the first word.')

    parser.add_argument('-n', '--number', metavar='int', dest='num', type=pos_int, required=not ('-e' in sys.argv or '--every' in sys.argv), help='Number of files to split fasta into')
    
    parser.add_argument('-s', '--seqnum', dest='seqnum', action='store_true', help='`-n` represents number of sequences to put in each file. Default is number of files NO EFFECT YET')
    
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='Suppress printing progress messages to the screen')

    parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, help='Increases verbosity level. Can be invoked up to 3 times to increase level further')

    parser.add_argument('fasta', help='Path to fasta file')

    args = parser.parse_args()
    
    args.dir = args.dir.rstrip('/')
    if not os.path.isdir(args.dir):
        os.mkdir(args.dir)

    if args.every:
        if ('-p' in sys.argv or '--prefix' in sys.argv):
            splite(args.fasta, args.prefix, args.full, args.quiet, args.dir, args.verbose)
        else:
            splite(args.fasta, None, args.full, args.quiet, args.dir, args.verbose)
    elif args.seqnum:
        splits(args.num, args.fasta, args.prefix, args.quiet, args.dir, args.verbose)
    else:
        splitn(args.num, args.fasta, args.prefix, args.quiet, args.dir, args.verbose)

if __name__ == '__main__':
    main()