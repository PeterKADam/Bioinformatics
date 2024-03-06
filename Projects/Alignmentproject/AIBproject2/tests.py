from AIBP2 import *
import argparse
import os
import files


def main():

    gapcost = 5
    gap_open = 5
    # gapopen = args.gapopen

    caseseq1 = "acgtgtcaacgt"
    caseseq2 = "acgtcgtagcta"
    caseseq3 = "aataat"
    caseseq4 = "aagg"

    matchscore = files.load_match_scores("matchscores.txt")

    #     print(
    print(
        f"""case1 linear : {LinearGlobalAlignment(caseseq1, caseseq2, matchscore, gapcost).get_max() == 22}
	case1 affine : {AffineGlobalAlignment(caseseq1, caseseq2, matchscore, gapcost, gap_open).get_max() == 24}
	"""
    )

    print(
        f"""case2 linear : {LinearGlobalAlignment(caseseq3, caseseq4, matchscore, gapcost).get_max() == 14}
	case2 affine : {AffineGlobalAlignment(caseseq3, caseseq4, matchscore, gapcost, gap_open).get_max() == 22}
	"""
    )

    seq1 = "tatggagagaataaaagaactgagagatctaatgtcgcagtcccgcactcgcgagatactcactaagaccactgtggaccatatggccataatcaaaaag"
    seq2 = "atggatgtcaatccgactctacttttcctaaaaattccagcgcaaaatgccataagcaccacattcccttatactggagatcctccatacagccatggaa"
    seq3 = "tccaaaatggaagactttgtgcgacaatgcttcaatccaatgatcgtcgagcttgcggaaaaggcaatgaaagaatatggggaagatccgaaaatcgaaa"
    seq4 = "aaaagcaacaaaaatgaaggcaatactagtagttctgctatatacatttgcaaccgcaaatgcagacacattatgtataggttatcatgcgaacaattca"
    seq5 = "atgagtgacatcgaagccatggcgtctcaaggcaccaaacgatcatatgaacaaatggagactggtggggagcgccaggatgccacagaaatcagagcat"
    seqlist = [seq1, seq2, seq3, seq4, seq5]
    matchscore = files.load_match_scores("matchscores.txt")

    q1 = LinearGlobalAlignment(seq1, seq2, matchscore, gapcost)
    print(f"q1\nalignment:\t{q1.alignments[0][0]}\n\t\t{q1.alignments[0][1]}\n\t\tscore: {q1.get_max()}\n")

    q2 = AffineGlobalAlignment(seq1, seq2, matchscore, gapcost, gap_open)
    print(f"q2:\nalignment:\t{q2.alignments[0][0]}\n\t\t{q2.alignments[0][1]}\n\t\tScore: {q2.get_max()}\n")

    # q3 & q4 #probably shouldnt recalculate the scores, but it's easier than passing them around
    scoresLinear = [[0 for _ in range(5)] for _ in range(5)]
    scoresAffine = [[0 for _ in range(5)] for _ in range(5)]
    for i, seq_i in enumerate(seqlist):
        for j, seq_j in enumerate(seqlist):
            scoresLinear[i][j] = LinearGlobalAlignment(seq_i, seq_j, matchscore, gapcost).get_max()
            scoresAffine[i][j] = AffineGlobalAlignment(seq_i, seq_j, matchscore, gapcost, gap_open).get_max()
    # q3
    print("Optimal linear alignment scores:")
    for i in range(5):
        for j in range(5):
            print(f"{scoresLinear[i][j]:10}", end="")
        print()

    # q4

    print("Optimal alignment scores:")
    for i in range(5):
        for j in range(5):
            print(f"{scoresAffine[i][j]:10}", end="")
        print()


if __name__ == "__main__":
    main()
