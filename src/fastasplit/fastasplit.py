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

from importlib.metadata import version
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

def splite(fasta: str, prefix: str | None, full: bool, quiet: bool, directory: str, verbose: int, force: bool) -> None:
    """Split each sequence in fasta file into a separate file

    Args:
        fasta (str): Path to fasta file
        prefix (str | None): Prefix to give split files. `None` if using header
        full (bool): Use full sequence header for prefix
        quiet (bool): Print progress messages
        directory (str): Directory to place split files
        verbose (int): Verbosity level
    """
    seqnum = getseqn(fasta, quiet)
    if not force:
        if seqnum > 100:
            flag = True
            while flag:
                cont = input(f"This command will create {seqnum} output files. Are you sure you want to proceed? (y/n) ").lower()
                if cont == 'n':
                    flag = False
                    sys.exit()
                elif cont == 'y':
                    flag = False

    ndigits = len(str(seqnum))

    with open(fasta, 'r', encoding="UTF-8") as fastafile:

        nsplit = 1
        for line in fastafile:

            if line[0] == '>':
                if prefix is not None:
                    name = f"{prefix}.{nsplit:0{ndigits}d}.fa"
                    if not quiet:
                        if verbose > 0:
                            print(f"Creating split file {nsplit}/{seqnum}...")
                        elif verbose > 1:
                            print(f"Creating split file {nsplit}/{seqnum} for sequence: {line.strip()[1:]}")
                elif full:
                    name = line.strip()[1:]
                else:
                    words = line.strip().split()
                    name = f"{words[0][1:] if len(words[0]) > 1 else words[1]}.fa"

                splitfile = open(f"{directory}/{name}", 'w', encoding="UTF-8")
                nsplit += 1

            splitfile.write(line)

def splits(num: int, fasta: str, prefix: str, quiet: bool, directory: str, verbose: int, force: bool) -> None:
    """Split fasta file by number of sequences

    Args:
        num (int): Number of sequences to place in each file
        fasta (str): Path to fasta file
        prefix (str): Prefix to give split files
        quiet (bool): Print progress messages
        directory (str): Directory to place split files
        verbose (int): Verbosity level
    """
    nseq = getseqn(fasta, quiet)
    nfile = (nseq // num) + (nseq % num > 0)
    ndigit = len(str(nfile))
    if not force:
        if nfile > 100:
            flag = True
            while flag:
                cont = input(f"This command will create {nfile} output files. Are you sure you want to proceed? (y/n) ").lower()
                if cont == 'n':
                    flag = False
                    quit()
                elif cont == 'y':
                    flag = False

    with open(fasta, 'r', encoding="UTF-8") as fastafile:
        splitnum = 1
        splitfile = open(f"{directory}/{prefix}.{splitnum:0{ndigit}d}.fa", 'w', encoding="UTF-8")
        if not quiet:
            print (f"Creating split file {splitnum}/{nfile}...")
            if verbose > 0:
                print (f"   Split file {splitnum} will contain {num} sequences")
        seqcount = 0
        for line in fastafile:
            if line[0] == '>':
                seqcount += 1
                if seqcount > num:
                    splitfile.close()
                    splitnum += 1
                    splitfile = open(f"{directory}/{prefix}.{splitnum:0{ndigit}d}.fa", 'w', encoding="UTF-8")
                    if not quiet:
                        print (f"Creating split file {splitnum}/{nfile}...")
                        if verbose > 0:
                            print (f"   Split file {splitnum} will contain {num} sequences")
                    seqcount = 1
            splitfile.write(line)

def splitn(num: int, fasta: str, prefix: str, quiet: bool, directory: str, verbose: int, force: bool) -> None:
    """Split fasta file into a number of files with equal number of sequences

    Args:
        num (int): Number of files to split fasta file into
        fasta (str): Path to fasta file
        prefix (str): Prefix to give split files
        quiet (bool): Print progress messages
        directory (str): Directory to place split files
        verbose (int): Verbosity level
    """
    if not force:
        if num > 100:
            flag = True
            while flag:
                cont = input(f"This command will create {num} output files. Are you sure you want to proceed? (y/n) ").lower()
                if cont == 'n':
                    flag = False
                    sys.exit()
                elif cont == 'y':
                    flag = False

    ndigits = len(str(num))
    splitnum = getseqn(fasta, quiet)
    perfile, remain = (splitnum // num, splitnum % num)

    with open(fasta, 'r', encoding='UTF-8') as fastafile:
        splitnum = 1
        splitfile = open(f'{directory}/{prefix}.{splitnum:0{ndigits}d}.fa', 'w', encoding='UTF-8')
        if remain > 0:
            perthisfile = perfile + 1
        else:
            perthisfile = perfile
        remain -= 1
        if not quiet:
            print (f"Creating split file {splitnum}/{num}...")
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
                    splitfile = open(f'{directory}/{prefix}.{splitnum:0{ndigits}d}.fa', 'w', encoding='UTF-8')
                    if not quiet:
                        print (f"Creating split file {splitnum}/{num}...")
                    if remain > 0:
                        perthisfile = perfile + 1
                    else:
                        perthisfile = perfile
                    remain -= 1
                    if verbose > 0:
                        print (f"   Split file {splitnum} will contain {perthisfile} sequences")
                    seqcount = 1
            splitfile.write(line)

def pos_int(num) -> int:
    """Helper function for argparser"""
    try:
        num = int(num)
    except ValueError as exc:
        raise argparse.ArgumentError(None, f"argument -n/--number: Invalid positive integer value: {num}") from exc
    if num <= 0:
        raise argparse.ArgumentError(None, f"argument -n/--number: Invalid positive integer value: {num}")
    return num

def main():
    """Main script wrapper. Parses arguments and calls appropriate function"""
    parser = argparse.ArgumentParser(
        description="Split a fasta file into smaller files with an equal number of sequences.")

    parser.add_argument('--version', action='version', version=f"{'%(prog)s'} {version('fastasplit')}",
                        help='Show version information and exit')

    parser.add_argument('-d', '--directory', metavar='dir', dest='dir', default='.',
                        help='Specify directory to place split files in. Default is \'.\'',)

    parser.add_argument('-p', '--prefix', metavar='prefix', dest='prefix', default='split',
                        help='Prefix to use for naming all split files. Default is \'split\', or first word of sequence header if `-e`.')

    parser.add_argument('-e', '--every', dest='every', action='store_true',
                        help='Split each sequence into its own file. Do not provide `-n`')

    parser.add_argument('-f', '--fullhead', dest='full', action='store_true',
                        help='Use with `-e`. Use full sequence header as prefix instead of just the first word.')

    parser.add_argument('-n', '--number', metavar='int', dest='num', type=pos_int,
                        required=not ('-e' in sys.argv or '--every' in sys.argv), help='Number of files to split fasta into. Required if not `-e`')

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

    args.dir = args.dir.rstrip('/')
    if not os.path.isdir(args.dir):
        os.mkdir(args.dir)

    if args.every:
        if ('-p' in sys.argv or '--prefix' in sys.argv):
            splite(args.fasta, args.prefix, args.full, args.quiet, args.dir, args.verbose, args.force)
        else:
            splite(args.fasta, None, args.full, args.quiet, args.dir, args.verbose, args.force)
    elif args.seqnum:
        splits(args.num, args.fasta, args.prefix, args.quiet, args.dir, args.verbose, args.force)
    else:
        splitn(args.num, args.fasta, args.prefix, args.quiet, args.dir, args.verbose, args.force)

if __name__ == '__main__':
    main()
