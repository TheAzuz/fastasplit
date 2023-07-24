#! /usr/bin/env python3

"""
==============
= fastasplit =
==============
split fasta files
main script

author: Josh Tompkin
contact: jtompkindev@gmail.com
github: https://github.com/jtompkin/fastasplit
"""

from importlib.metadata import version, PackageNotFoundError
import argparse
import sys
import os


def getseqn(fasta: str, quiet: bool) -> int:
    """Reutns number of sequences in given fasta file

    Args:
        fasta (str): Path to fasta file
        quiet (bool): Whether to print progress messages

    Returns:
        int: Number of sequences in fasta file
    """
    if not quiet:
        print ('Counting total sequences in fasta file...')
    with open(fasta, 'r', encoding='UTF-8') as fastafile:
        nseq = 0
        for line in fastafile:
            if line[0] == '>':  # Line is a sequence header
                nseq += 1
    if not quiet:
        print (f"Found {nseq} sequences in fasta file")
    return nseq


def splite(args) -> None:
    """Split each sequence in fasta file into a separate file"""
    seqnum = getseqn(args.fasta, args.quiet)
    if not args.force:
        if seqnum > 100:
            flag = True
            while flag:
                cont = input(f"""This command will create {seqnum} output files.
                             Are you sure you want to proceed? (y/n) """).lower()
                if cont == 'n':
                    flag = False
                    sys.exit()
                elif cont == 'y':
                    flag = False

    ndigits = len(str(seqnum))
    with open(args.fasta, 'r', encoding="UTF-8") as fastafile:
        nsplit = 1
        for line in fastafile:
            if line[0] == '>':
                if args.prefix is not None:
                    name = f"{args.prefix}.{nsplit:0{ndigits}d}.fa"
                    if not args.quiet:
                        if args.verbose > 0:
                            print(f"Creating split file {nsplit}/{seqnum}...")
                        elif args.verbose > 1:
                            print(f"""Creating split file {nsplit}/{seqnum}
                                  for sequence: {line.strip()[1:]}""")
                elif args.full:
                    name = line.strip()[1:]
                else:
                    words = line.strip().split()
                    name = f"{words[0][1:] if len(words[0]) > 1 else words[1]}.fa"
                splitfile = open(f"{args.directory}/{name}", 'w', encoding="UTF-8")
                nsplit += 1
            splitfile.write(line)


def splits(args) -> None:
    """Split fasta file by number of sequences"""

    nseq = getseqn(args.fasta, args.quiet)
    nfile = (nseq // args.num) + (nseq % args.num > 0)
    ndigit = len(str(nfile))
    if not args.force:
        if nfile > 100:
            flag = True
            while flag:
                cont = input(f"""This command will create {nfile} output files.
                             Are you sure you want to proceed? (y/n) """).lower()
                if cont == 'n':
                    flag = False
                    quit()
                elif cont == 'y':
                    flag = False

    with open(args.fasta, 'r', encoding="UTF-8") as fastafile:
        splitnum = 1
        splitfile = open(f"{args.directory}/{args.prefix}.{splitnum:0{ndigit}d}.fa", 'w', encoding="UTF-8")
        if not args.quiet:
            print (f"Creating split file {splitnum}/{nfile}...")
            if args.verbose > 0:
                print (f"   Split file {splitnum} will contain {args.num} sequences")
        seqcount = 0
        for line in fastafile:
            if line[0] == '>':
                seqcount += 1
                if seqcount > args.num:
                    splitfile.close()
                    splitnum += 1
                    splitfile = open(f"{args.directory}/{args.prefix}.{splitnum:0{ndigit}d}.fa", 'w', encoding="UTF-8")
                    if not args.quiet:
                        print (f"Creating split file {splitnum}/{nfile}...")
                        if args.verbose > 0:
                            print (f"   Split file {splitnum} will contain {args.num} sequences")
                    seqcount = 1
            splitfile.write(line)


def splitn(args) -> None:
    """Split fasta file into a number of files with equal number of sequences"""

    if not args.force:
        if args.num > 100:
            flag = True
            while flag:
                cont = input(f"""This command will create {args.num} output files.
                             Are you sure you want to proceed? (y/n) """).lower()
                if cont == 'n':
                    flag = False
                    sys.exit(2)
                elif cont == 'y':
                    flag = False

    ndigits = len(str(args.num))
    splitnum = getseqn(args.fasta, args.quiet)
    perfile, remain = (splitnum // args.num, splitnum % args.num)

    with open(args.fasta, 'r', encoding='UTF-8') as fastafile:
        splitnum = 1
        splitfile = open(f'{args.directory}/{args.prefix}.{splitnum:0{ndigits}d}.fa', 'w', encoding='UTF-8')
        if remain > 0:
            perthisfile = perfile + 1
        else:
            perthisfile = perfile
        remain -= 1
        if not args.quiet:
            print (f"Creating split file {splitnum}/{args.num}...")
            if args.verbose > 0:
                print (f"   Split file {splitnum+1} will contain {perthisfile} sequences")

        seqcount = 0
        for line in fastafile:
            if line[0] == '>':  # Line is a sequence header
                if args.verbose > 2:
                    print (f"Adding sequence: {line[1:].strip()}")
                seqcount += 1
                if seqcount > perthisfile:  # Need to open new split file
                    splitfile.close()
                    splitnum += 1
                    splitfile = open(f'{args.directory}/{args.prefix}.{splitnum:0{ndigits}d}.fa', 'w', encoding='UTF-8')
                    if not args.quiet:
                        print (f"Creating split file {splitnum}/{args.num}...")
                    if remain > 0:
                        perthisfile = perfile + 1
                    else:
                        perthisfile = perfile
                    remain -= 1
                    if args.verbose > 0:
                        print (f"   Split file {splitnum} will contain {perthisfile} sequences")
                    seqcount = 1
            splitfile.write(line)


def pos_int(num) -> int:
    """Helper function for argparser"""
    try:
        num = int(num)
    except ValueError as exc:
        raise argparse.ArgumentError(
            None, f"argument -n/--number: Invalid positive integer value: {num}") from exc
    if num <= 0:
        raise argparse.ArgumentError(
            None, f"argument -n/--number: Invalid positive integer value: {num}")
    return num


def _main():
    """Main script wrapper. Parse arguments and call appropriate function."""
    parser = argparse.ArgumentParser(
        description="Split a fasta file into smaller files with an equal number of sequences.")
    try:
        parser.add_argument('--version', action='version',
                            version=f"{'%(prog)s'} {version('fastasplit')}",
                            help='Show version information and exit')
    except PackageNotFoundError:
        parser.add_argument('--version', action='version', version='Standalone',
                            help='Show version information and exit')
    parser.add_argument('-d', '--directory', metavar='dir', dest='directory', default='.',
                        help="Specify directory to place split files in. Default is '.'",)
    parser.add_argument('-p', '--prefix', metavar='prefix', dest='prefix', default='split',
                        help="""Prefix to use for naming all split files.
                        Default is 'split', or first word of sequence header if `-e`""")
    parser.add_argument('-e', '--every', dest='every', action='store_true',
                        help='Split each sequence into its own file. Do not provide `-n`')
    parser.add_argument('-f', '--fullhead', dest='full', action='store_true',
                        help="""Use with `-e`. Use full sequence header
                        as prefix instead of just the first word""")
    parser.add_argument('-n', '--number', metavar='int', dest='num', type=pos_int,
                        required=not ('-e' in sys.argv or '--every' in sys.argv),
                        help="""Number of files to split fasta into.
                        Required if `-e` is not provided""")
    parser.add_argument('-s', '--seqnum', dest='seqnum', action='store_true',
                        help='`-n` represents number of sequences to put in each file')
    parser.add_argument('--force', dest='force', action='store_true',
                        help='Do not prompt for comfirmation when creating a large number of files')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='Suppress printing progress messages to the screen')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                        help='Increases verbosity level. Can be invoked up to 3 times')
    parser.add_argument('fasta', help='Path to fasta file')

    args = parser.parse_args()
    # Create given directory if it does not exist.
    args.directory = args.directory.rstrip('/')
    if not os.path.isdir(args.directory):
        os.mkdir(args.directory)

    if args.every:
        splite(args)
    elif args.seqnum:
        splits(args)
    else:
        splitn(args)

if __name__ == '__main__':
    _main()
