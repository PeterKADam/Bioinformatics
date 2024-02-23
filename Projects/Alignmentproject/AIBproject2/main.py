from AIBP2 import *

# these are not the matchscores youre looking for
MATCH_SCORES = {
    "A": {"A": 10, "T": 2, "G": 5, "C": 2},
    "T": {"A": 2, "T": 10, "G": 2, "C": 5},
    "G": {"A": 5, "T": 2, "G": 10, "C": 2},
    "C": {"A": 2, "T": 5, "G": 2, "C": 10},
}
# move along
MATCH_SCORES_2 = {
    "A": {"A": 2, "T": 0, "G": 0, "C": 0},
    "T": {"A": 0, "T": 2, "G": 0, "C": 0},
    "G": {"A": 0, "T": 0, "G": 2, "C": 0},
    "C": {"A": 0, "T": 0, "G": 0, "C": 2},
}


MATCH_SCORES_3 = {
    "A": {"A": 0, "C": 5, "G": 2, "T": 5},
    "C": {"A": 5, "C": 0, "G": 5, "T": 2},
    "G": {"A": 2, "C": 5, "G": 0, "T": 5},
    "T": {"A": 5, "C": 2, "G": 5, "T": 0},
}


# CASE1
seq1 = "ACGTGTCAACGT"
seq2 = "ACGTCGTAGCTA"

print("CASE1: Linear Global Alignment: gapcost = 5")
M = LinearGlobalAlignment(seq1, seq2, MATCH_SCORES_3, 5)
M_affine = AffineGlobalAlignment(seq1, seq2, MATCH_SCORES_3, 5, 5)

M_affine.prepare_matrixes()
M_affine.fill_matrixes()
M_affine.print_matrix_set()
M.print_finish_matrix()


# CASE2
print("\nCASE2: Linear Global Alignment, UNEVEN: gapcost = 5")
seq3 = "AATAAT"
seq4 = "AAGG"
M2 = LinearGlobalAlignment(seq3, seq4, MATCH_SCORES_3, 5)
M2.print_finish_matrix()

# CASE3
print("\nCASE3: Linear Global Alignment, UNEVEN: gapcost = 5")
seq5 = "TCCAGAGA"
seq6 = "TCGAT"
M3 = LinearGlobalAlignment(seq5, seq6, MATCH_SCORES_3, 5)
M3.print_finish_matrix()

# CASE4 apparntly wrong?
print("\nCASE4: Linear Global Alignment: gapcost = 5")
seq7 = "ggcctaaaggcgccggtctttcgtaccccaaaatctcggcattttaagataagtgagtgttgcgttacactagcgatctaccgcgtcttatacttaagcgtatgcccagatctgactaatcgtgcccccggattagacgggcttgatgggaaagaacagctcgtctgtttacgtataaacagaatcgcctgggttcgc"
seq8 = "gggctaaaggttagggtctttcacactaaagagtggtgcgtatcgtggctaatgtaccgcttctggtatcgtggcttacggccagacctacaagtactagacctgagaactaatcttgtcgagccttccattgagggtaatgggagagaacatcgagtcagaagttattcttgtttacgtagaatcgcctgggtccgc"
M4 = LinearGlobalAlignment(seq7, seq8, MATCH_SCORES_3, 5)
M4.print_finish_matrix()
