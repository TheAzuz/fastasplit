# fastasplit
Split fasta files

Josh Tompkin, 2023

## Installation and usage

Download fastasplit.py and run with python3.

Specify number of files with `-n <int>`, numer of sequences per file with `-n <int> -s`, or put every sequence into its own file with `-e`.

Example to split a fasta file named 'sequences.fa' into 20 fasta files with equal number of sequences in each.
```bash
    python3 fastasplit.py -n 20 sequences.fa
```

Run with `-h` to see other options.
