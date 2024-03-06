from AIBP2 import *
import argparse
import os
import files
import time
from Bio import SeqIO

import sys

sys.setrecursionlimit(1500)


score_matrix = files.load_match_scores("matchscores.txt")


def generate_sequence(n):
    with open("TTN.fa", "r") as file:
        first_record = next(SeqIO.parse(file, "fasta"))
        seq = str(first_record.seq)
        return seq[:n]


def evaluate_time_complexity():
    # sequence_lengths = [100, 200, 300, 400, 500]  # Update with desired sequence lengths
    sequence_lengths = list(range(100, 2200, 100))
    affine_times = []
    linear_times = []

    for length in sequence_lengths:
        sequence = generate_sequence(length)  # Replace with your own sequence generation logic

        # Measure time for affine code
        start_time = time.time()
        AffineGlobalAlignment(sequence, sequence, score_matrix, 5, 5)
        end_time = time.time()
        affine_times.append(end_time - start_time)

        # Measure time for linear code
        start_time = time.time()
        LinearGlobalAlignment(sequence, sequence, score_matrix, 5)
        end_time = time.time()
        linear_times.append(end_time - start_time)

    return affine_times, linear_times


# Run the evaluation
affine_times, linear_times = evaluate_time_complexity()

# Print the results
print("Affine code times:", affine_times)
print("Linear code times:", linear_times)
