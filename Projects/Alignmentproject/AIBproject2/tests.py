# CASE1
seq1 = "ACGTGTCAACGT"
seq2 = "ACGTCGTAGCTA"

print("CASE1: Linear Global Alignment: gapcost = 5")
# M = LinearGlobalAlignment(seq1, seq2, MATCH_SCORES_3, 5)
M_affine = AffineGlobalAlignment(seq1, seq2, MATCH_SCORES, 5, 5)
M_affine.print_finish_matrix()
# M.print_finish_matrix()


# CASE2
print("\nCASE2: Linear Global Alignment, UNEVEN: gapcost = 5")
seq3 = "AATAAT"
seq4 = "AAGG"
M2 = AffineGlobalAlignment(seq3, seq4, MATCH_SCORES, 5, 5)
M2.print_finish_matrix()

# CASE3
print("\nCASE3: Linear Global Alignment, UNEVEN: gapcost = 5")
seq5 = "TCCAGAGA"
seq6 = "TCGAT"
M3 = AffineGlobalAlignment(seq5, seq6, MATCH_SCORES, 5, 5)
M3.print_finish_matrix()

# CASE4 apparntly wrong?
print("\nCASE4: Linear Global Alignment: gapcost = 5")
seq7 = "ggcctaaaggcgccggtctttcgtaccccaaaatctcggcattttaagataagtgagtgttgcgttacactagcgatctaccgcgtcttatacttaagcgtatgcccagatctgactaatcgtgcccccggattagacgggcttgatgggaaagaacagctcgtctgtttacgtataaacagaatcgcctgggttcgc"
seq8 = "gggctaaaggttagggtctttcacactaaagagtggtgcgtatcgtggctaatgtaccgcttctggtatcgtggcttacggccagacctacaagtactagacctgagaactaatcttgtcgagccttccattgagggtaatgggagagaacatcgagtcagaagttattcttgtttacgtagaatcgcctgggtccgc"
M4 = AffineGlobalAlignment(seq7, seq8, MATCH_SCORES, 5, 5)
M4.print_finish_matrix()