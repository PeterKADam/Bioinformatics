from Bio import SeqIO
from Bio.Seq import Seq
import os
from datetime import datetime


def load_match_scores(path):
    MATCH_SCORES = {}

    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                values = line.split()
                key = values.pop(0)
                MATCH_SCORES[key] = {
                    k: int(v) for k, v in zip(["A", "C", "G", "T"], values)
                }
    return MATCH_SCORES


def load_sequences(filepath):
    sequences = []
    for record in SeqIO.parse(filepath, "fasta"):
        sequences.append(str(record.seq))
    return sequences


def SaveAlignments(Alignments, strategy):

    SeqAligns = [
        SeqIO.SeqRecord(Seq(Alignments[0][0]), id="seq1", description=""),
        SeqIO.SeqRecord(Seq(Alignments[0][1]), id="seq2", description=""),
    ]

    SeqIO.write(
        SeqAligns,
        f"{datetime.now().strftime('%H:%M:%S')}-{strategy}-alignment.fasta",
        "fasta",
    )
    return
