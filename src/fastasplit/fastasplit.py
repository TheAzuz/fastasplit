#! /usr/bin/env python3
"""
split fasta files

==============
= fastasplit =
==============

author: Josh Tompkin
contact: jtompkin-dev@proton.me
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


def confirm_continue(file_number: int, force: bool, limit: int = 100) -> bool:
    """Check if there are too many output files and ask for confirmation to continue."""
    if force:
        return True
    if file_number <= limit:
        return True
    while True:
        continue_choice = input(f"This command will create {file_number} output files. "+
                                "Are you sure you want to proceed? (y/n) ").lower()
        if continue_choice == 'n':
            return False
        if continue_choice == 'y':
            return True


def get_fasta_file(file_path: str) -> TextIO:
    """Return file object from `path`."""
    if file_path == '-':
        return sys.stdin
    return open(file_path, 'rt', encoding='UTF-8')


def get_sequence_number(fasta_file: TextIO, quiet: bool) -> int:
    """Return number of sequences in fasta file."""
    if not quiet:
        print('Counting total sequences in fasta file...')

    with fasta_file:
        sequence_count = 0
        for line in fasta_file:
            if line[0] == '>':  # Line is a sequence header
                sequence_count += 1
    if not quiet:
        print (f"Found {sequence_count} sequences in fasta file")
    return sequence_count


def split_each(args) -> None:
    """Split each sequence in fasta file into a separate file"""
    if args.fasta != '-':
        sequence_number = get_sequence_number(get_fasta_file(args.fasta), args.quiet)
        if not confirm_continue(sequence_number, args.force, 100):
            sys.exit(2)
        digit_number = len(str(sequence_number))
    else:
        sequence_number = 'unknown'
        digit_number = 3

    fasta_file = get_fasta_file(args.fasta)
    with fasta_file:
        split_count = 1
        for line in fasta_file:
            if line[0] == '>':
                if args.prefix is not None:
                    name = f"{args.prefix}.{split_count:0{digit_number}d}.fa"
                    if not args.quiet:
                        if args.verbose > 0:
                            print(f"Creating split file {split_count}/{sequence_number}...")
                        elif args.verbose > 1:
                            print(f"Creating split file {split_count}/{sequence_number} "+
                                  f"for sequence: {line.strip()[1:]}")
                elif args.full:
                    name = line.strip()[1:]
                else:
                    words = line.strip().split()
                    name = f"{words[0][1:] if len(words[0]) > 1 else words[1]}.fa"
                splitfile = open(f"{args.directory}/{name}", 'w', encoding="UTF-8")
                split_count += 1
            splitfile.write(line)


def split_sequence(args) -> None:
    """Split fasta file by number of sequences"""
    if args.fasta != '-':
        nseq = get_sequence_number(get_fasta_file(args.fasta), args.quiet)
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


def split_number(args) -> None:
    """Split fasta file into a number of files with equal number of sequences"""

    if confirm_continue(args.num, args.force, 100) is False:
        sys.exit(2)

    seqnum = get_sequence_number(get_fasta_file(args.fasta), args.quiet)
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


def pos_int(argument) -> int:
    """Test if `argument` is a positive integer."""
    try:
        argument = int(argument)
    except ValueError as exc:
        raise argparse.ArgumentError(
            None, f"argument -n/--number: Invalid positive integer value: {argument}") from exc
    if argument <= 0:
        raise argparse.ArgumentError(
            None, f"argument -n/--number: Invalid positive integer value: {argument}")
    return argument


def main():
    """Main script wrapper. Parse arguments and call appropriate function."""
    parser = argparse.ArgumentParser(prog='fastasplit',
                                     description="Split a fasta file into smaller fasta files.")

    program_version = f"{parser.prog} {__version__ if _VERSION_GOOD else 'standalone'}"
    parser.add_argument('--version', action='version',
                        version=program_version,
                        help='Show version information and exit')

    split_options = parser.add_argument_group('split options')
    split_options.add_argument('-n', '--number', metavar='int', dest='num', type=pos_int,
                               required=not('-e' in sys.argv or '--every' in sys.argv),
                               help="""Number of files to split fasta into, or number of sequences
                               per file if `-s` is provided. `-s` must be provided to
                               use stdin for input. Required if `-e` is not provided""")
    split_options.add_argument('-s', '--seqnum', dest='seqnum', action='store_true',
                               help='`-n` represents number of sequences to put in each file')
    split_options.add_argument('-e', '--every', dest='every', action='store_true',
                               help='Split each sequence into its own file. Do not provide `-n`')

    naming_options = parser.add_argument_group('naming options')
    naming_options.add_argument('-d', '--directory', metavar='dir', dest='directory', default='.',
                                help="Specify directory to place split files in. Default is '.'")
    naming_options.add_argument('-p', '--prefix', metavar='prefix', dest='prefix', default='split',
                                help="""Prefix to use for naming all split files.
                                Default is 'split', or first word of sequence header if `-e`""")
    naming_options.add_argument('-f', '--fullhead', dest='full', action='store_true',
                                help="""Use with `-e`. Use full sequence header
                                as prefix instead of just the first word""")

    message_options = parser.add_argument_group('message options')
    message_options.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                                 help='Suppress progress messages')
    message_options.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                                 help='Increases verbosity level. Can be invoked up to 3 times')
    message_options.add_argument('--force', dest='force', action='store_true',
                                 help="""Do not prompt for comfirmation
                                 when creating a large number of files""")

    parser.add_argument('fasta',
                        help="""Path to fasta file. Read from stdin if '-' is given.
                        Some features will not work if '-' is given""")

    args = parser.parse_args()

    if args.fasta == '-' and (args.num is not None and args.seqnum is False):
        raise argparse.ArgumentError(None, "Fasta cannot be read from stdin "+
                                     "if -s is not provided along with -n")
    # Create given directory if it does not exist.
    args.directory = args.directory.rstrip('/')
    if not os.path.isdir(args.directory):
        os.mkdir(args.directory)

    if args.every:
        split_each(args)
    elif args.seqnum:
        split_sequence(args)
    else:
        split_number(args)

if __name__ == '__main__':
    main()
