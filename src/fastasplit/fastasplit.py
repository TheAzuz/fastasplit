#! /usr/bin/env python3

"""
==============
= fastasplit =
==============

split fasta files

author: Josh Tompkin
contact: jtompkindev@gmail.com
github: https://github.com/jtompkin/fastasplit
"""

from typing import TextIO
import argparse
import sys
import os

try:
    from .version import __version__
    _VERSION_GOOD = True
except ImportError:
    _VERSION_GOOD = False

def confirm_continue(nfiles: int, force: bool, limit: int = 100) -> bool:
    """Check if there are too many output files and ask for confirmation to continue.
    
    Args:
        nfiles (int): Number of files that will be created
        force (bool): Will not ask for confirmation if `True`
        limit (int): Max number of files before confirmation is needed

    Returns:
        bool: `True` if user wants to continue, else `False`
    """
    if force is not True:
        if nfiles > limit:
            while True:
                cont = input(f"This command will create {nfiles} output files. "+
                              "Are you sure you want to proceed? (y/n) ").lower()
                if cont == 'n':
                    return False
                if cont == 'y':
                    return True
    return True


def get_fasta_file(path: str) -> TextIO:
    """Return file object from `path`."""
    if path == '-':
        return sys.stdin
    return open(path, 'rt', encoding='UTF-8')


def get_seq_num(fastafile: TextIO, quiet: bool) -> int:
    """Return number of sequences in fasta file."""
    if not quiet:
        print ('Counting total sequences in fasta file...')

    with fastafile:
        nseq = 0
        for line in fastafile:
            if line[0] == '>':  # Line is a sequence header
                nseq += 1
        if not quiet:
            print (f"Found {nseq} sequences in fasta file")
    return nseq


def splite(args) -> None:
    """Split each sequence in fasta file into a separate file"""
    if args.fasta != '-':
        seqnum = get_seq_num(get_fasta_file(args.fasta), args.quiet)
        if confirm_continue(seqnum, args.force, 100) is False:
            sys.exit(2)
        ndigits = len(str(seqnum))
    else:
        seqnum = 'unknown'
        ndigits = 3

    fastafile = get_fasta_file(args.fasta)
    with fastafile:
        nsplit = 1
        for line in fastafile:
            if line[0] == '>':
                if args.prefix is not None:
                    name = f"{args.prefix}.{nsplit:0{ndigits}d}.fa"
                    if not args.quiet:
                        if args.verbose > 0:
                            print(f"Creating split file {nsplit}/{seqnum}...")
                        elif args.verbose > 1:
                            print(f"Creating split file {nsplit}/{seqnum} "+
                                  f"for sequence: {line.strip()[1:]}")
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
    if args.fasta != '-':
        nseq = get_seq_num(get_fasta_file(args.fasta), args.quiet)
        nfile = (nseq // args.num) + (nseq % args.num > 0)
        if confirm_continue(nfile, args.force, 100) is False:
            sys.exit(2)
        ndigit = len(str(nfile))
    else:
        nfile = 'unknown'
        ndigit = 3

    fastafile = get_fasta_file(args.fasta)

    with fastafile:
        splitnum = 1
        splitfile = open(f"{args.directory}/{args.prefix}.{splitnum:0{ndigit}d}.fa",
                         'w', encoding="UTF-8")
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
                    splitfile = open(f"{args.directory}/{args.prefix}.{splitnum:0{ndigit}d}.fa",
                                     'w', encoding="UTF-8")
                    if not args.quiet:
                        print (f"Creating split file {splitnum}/{nfile}...")
                        if args.verbose > 0:
                            print (f"   Split file {splitnum} will contain {args.num} sequences")
                    seqcount = 1
            splitfile.write(line)


def splitn(args) -> None:
    """Split fasta file into a number of files with equal number of sequences"""

    if confirm_continue(args.num, args.force, 100) is False:
        sys.exit(2)

    seqnum = get_seq_num(get_fasta_file(args.fasta), args.quiet)
    perfile, remain = (seqnum // args.num, seqnum % args.num)

    ndigits = len(str(args.num))

    fastafile = get_fasta_file(args.fasta)

    with fastafile:

        splitnum = 1
        splitfile = open(f'{args.directory}/{args.prefix}.{splitnum:0{ndigits}d}.fa',
                         'w', encoding='UTF-8')
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
            # Line is a sequence header
            if line[0] == '>':
                if args.verbose > 2:
                    print (f"Adding sequence: {line[1:].strip()}")
                seqcount += 1
                # Need to open new split file
                if seqcount > perthisfile:
                    splitfile.close()
                    splitnum += 1
                    splitfile = open(f'{args.directory}/{args.prefix}.{splitnum:0{ndigits}d}.fa',
                                     'w', encoding='UTF-8')
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
    parser = argparse.ArgumentParser(prog='fastasplit',
                                     description="Split a fasta file into smaller fasta files.")

    if _VERSION_GOOD is True:
        parser.add_argument('--version', action='version',
                            version=f"{'%(prog)s'} {__version__}",
                            help='Show version information and exit')
    else:
        parser.add_argument('--version', action='version',
                            version=f"{'%(prog)s'} standalone",
                            help='Show version information and exit')
    parser.add_argument('--force', dest='force', action='store_true',
                        help='Do not prompt for comfirmation when creating a large number of files')

    split_opts = parser.add_argument_group('Split options')
    split_opts.add_argument('-n', '--number', metavar='int', dest='num', type=pos_int,
                            required=not('-e' in sys.argv or '--every' in sys.argv),
                            help="""Number of files to split fasta into, or number of sequences
                            per file if `-s` is provided. `-s` must be provided to
                            use stdin for input. Required if `-e` is not provided""")
    split_opts.add_argument('-s', '--seqnum', dest='seqnum', action='store_true',
                            help='`-n` represents number of sequences to put in each file')
    split_opts.add_argument('-e', '--every', dest='every', action='store_true',
                            help='Split each sequence into its own file. Do not provide `-n`')

    naming_opts = parser.add_argument_group('Naming options')
    naming_opts.add_argument('-d', '--directory', metavar='dir', dest='directory', default='.',
                             help="Specify directory to place split files in. Default is '.'")
    naming_opts.add_argument('-p', '--prefix', metavar='prefix', dest='prefix', default='split',
                             help="""Prefix to use for naming all split files.
                             Default is 'split', or first word of sequence header if `-e`""")
    naming_opts.add_argument('-f', '--fullhead', dest='full', action='store_true',
                             help="""Use with `-e`. Use full sequence header
                             as prefix instead of just the first word""")

    message_opts = parser.add_argument_group('Message options')
    message_opts.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                              help='Suppress progress messages')
    message_opts.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                              help='Increases verbosity level. Can be invoked up to 3 times')

    parser.add_argument('fasta',
                        help="""Path to fasta file. Read from stdin if '-' is given.
                        Some features will not work if '-' is given""")

    args = parser.parse_args()
    print(args.fasta, args.num, args.seqnum)

    if args.fasta == '-' and (args.num is not None and args.seqnum is False):
        raise argparse.ArgumentError(None, "Fasta cannot be read from stdin "+
                                     "if -s is not provided along with -n")
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
