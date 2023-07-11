# fastasplit
Split fasta files

Josh Tompkin, 2023

## Installation and usage

Install with pip:
```bash
    pip3 install fastasplit
```

Usage:
```bash
    fastasplit [-h] [--version] [-d dir] [-p prefix] [-e] [-f] -n int [-s] [-q] [-v] fasta
```

Specify number of files with `-n <int>`, numer of sequences per file with `-n <int> -s`, or put every sequence into its own file with `-e`. Run with `-h` to print help.

## Examples

Split a fasta file named 'sequences.fa' into 20 fasta files with equal number of sequences in each:
```bash
    fastasplit -n 20 sequences.fa
```
Split a fasta file named 'sequences.fa' into files with 10 sequences each:
```bash
    fastasplit -n 10 -s sequences.fa
```
Split each sequence in 'sequences.fa' into a separate file:
```bash
    fastasplit -e sequences.fa
```
