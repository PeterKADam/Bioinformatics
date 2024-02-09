#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################
from Bio import SeqIO


MATCH_SCORES = {
	"A": {"A": 10, "T": 2, "G": 5, "C": 2},
	"T": {"A": 2, "T": 10, "G": 2, "C": 5},
	"G": {"A": 5, "T": 2, "G": 10, "C": 2},
	"C": {"A": 2, "T": 5, "G": 2, "C": 10},
}


#Making the matrix beautiful
def print_dp_matrix(seq1, seq2, matrix):
	max_len = max(len(str(cell)) for row in matrix for cell in row)
	fmt = "{{:>{}}}".format(max_len + 1)
	row_fmt = fmt * (len(matrix[0]) + 1) + "\n"
	mat_fmt = row_fmt * (len(matrix) + 1)
	seq1 = " " + seq1
	seq2 = " " + seq2
	lst = [" "] + list(seq2)
	for i in range(len(seq1)):
		lst.extend([seq1[i]] + list(map(repr, matrix[i])))
	print(mat_fmt.format(*lst))


#Making an empty matrix the right size
def empty_matrix(len_seq1: int, len_seq2: int):

	return [[None] * len_seq2 for _ in range(len_seq1)]


#Inserting the first colomn and row with gap score in empty matrix
def prepare_matrix(len_seq1: int, len_seq2: int, gap_score: int):

	matrix = empty_matrix(len_seq1, len_seq2)

	for x in range(len_seq2):
		for y in range(len_seq1):
			if x == 0:
				matrix[y][x] = y * gap_score
			if y == 0:
				matrix[y][x] = x * gap_score
	return matrix


#Filling in the rest of the alignment matrix
def fill_matrix(seq1, seq2, match_score, gap_score):

	matrix = prepare_matrix(len(seq1) + 1, len(seq2) + 1, gap_score)

	for y in range(1, len(seq1) + 1):
		for x in range(1, len(seq2) + 1):
			matrix[y][x] = max(
				matrix[y][x - 1] + gap_score,
				matrix[y - 1][x] + gap_score,
				matrix[y - 1][x - 1] + match_score[seq1[y - 1]][seq2[x - 1]],
			)

	return matrix


#Finding out from which cell we can come to this one
def get_traceback_arrow(matrix, row, col, match_score, gap_score):
	# yellow
	score_diagonal = matrix[row - 1][col - 1]
	score_left = matrix[row][col - 1]
	score_up = matrix[row - 1][col]

	# green
	score_current = matrix[row][col]

	if score_current == score_diagonal + match_score:
		return "diagonal"
	elif score_current == score_left + gap_score:
		return "left"
	elif score_current == score_up + gap_score:
		return "up"


#Tracing back the arrows to find an alignment
def trace_back(seq1, seq2, matrix, score_matrix, gap_score):

	# Strings to store the growing alignment strings:
	aligned1 = ''
	aligned2 = ''

	# The row and col index of the bottom right cell:
	row = len(seq1)
	col = len(seq2)

	# Keep stepping backwards through the matrix untill
	# we get to the top row or the left col:
	while row > 0 and col > 0:

		# The two bases we available to match:
		base1 = seq1[row-1]
		base2 = seq2[col-1]

		# The score for mathing those two bases:
		match_score = score_matrix[base1][base2]

		# Find out which cell the score in the current cell was derived from:
		traceback_arrow = get_traceback_arrow(matrix, row, col, match_score, gap_score)

		if traceback_arrow == 'diagonal':
			aligned1 = base1 + aligned1
			aligned2 = base2 + aligned2
			row -= 1
			col -= 1
		elif traceback_arrow == 'up':
			aligned1 = base1 + aligned1
			aligned2 = '-' + aligned2
			row -= 1
		elif traceback_arrow == 'left':
			aligned1 = '-' + aligned1
			aligned2 = base2 + aligned2
			col -= 1

	# If row is not zero, step along the top row to the top left cell:
	while row > 0:
		base1 = seq1[row-1]
		aligned1 = base1 + aligned1
		aligned2 = '-' + aligned2
		row -= 1

	# If col is not zero, step upwards in the left col to the top left cell:
	while col > 0:
		base2 = seq2[col-1]
		aligned1 = '-' + aligned1
		aligned2 = base2 + aligned2
		col -= 1

	return [aligned1, aligned2]


#Print the alignment and the max score for optimal alignment
def align(seq1, seq2, score_matrix, gap_score):

	matrix = fill_matrix(seq1, seq2, score_matrix, gap_score)
	print(trace_back(seq1, seq2, matrix, score_matrix, gap_score))
	max_score=matrix[-1][-1]
	print("max: {max_score}",max_score) #hopefully
	return print(print_dp_matrix(seq1, seq2, matrix))
	#return



### GET ALL OPTIMAL ALIGNMENTS ##


#Finding out from which cells we can come to this one
def get_traceback_arrows(matrix, row, col, match_score, gap_score):
	# yellow
	score_diagonal = matrix[row - 1][col - 1]
	score_left = matrix[row][col - 1]
	score_up = matrix[row - 1][col]

	# green
	score_current = matrix[row][col]

	arrows = []

	if score_current == score_diagonal + match_score:
		arrows.append("diagonal")
	if score_current == score_left + gap_score:
		arrows.append("left")
	if score_current == score_up + gap_score:
		arrows.append("up")
	
	return arrows


#Recursion of tracing back the arrows to find an alignment
def traceback_recursive(seq1, seq2, matrix, score_matrix, gap_score, row, col):
    if row == 0 and col == 0:
        return [("", "")]

    arrows = get_traceback_arrows(matrix, row, col, score_matrix[seq1[row-1]][seq2[col-1]], gap_score)

    alignments = []
    for arrow in arrows:
        if arrow == 'diagonal':
            sub_alignments = traceback_recursive(seq1, seq2, matrix, score_matrix, gap_score, row - 1, col - 1)
            alignments.extend([(seq1[row - 1] + a1, seq2[col - 1] + a2) for a1, a2 in sub_alignments])
        elif arrow == 'up':
            sub_alignments = traceback_recursive(seq1, seq2, matrix, score_matrix, gap_score, row - 1, col)
            alignments.extend([(seq1[row - 1] + a1, '-' + a2) for a1, a2 in sub_alignments])
        elif arrow == 'left':
            sub_alignments = traceback_recursive(seq1, seq2, matrix, score_matrix, gap_score, row, col - 1)
            alignments.extend([('-' + a1, seq2[col - 1] + a2) for a1, a2 in sub_alignments])

    return alignments


#Tracing back to find all optimal alignments
def trace_back2(seq1, seq2, matrix, score_matrix, gap_score):
	row = len(seq1)
	col = len(seq2)
	
	alignments = traceback_recursive(seq1, seq2, matrix, score_matrix, gap_score, row, col)
	
	print(alignments)
	print("Number of optimal alignments: ",len(alignments))
	return


def load_fasta(filename):
	return SeqIO.read(filename, "fasta").seq


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

seq1=load_fasta("seq1.fasta")
seq2=load_fasta("seq2.fasta")
len_seq1=len(seq1)
len_seq2=len(seq2)
score_matrix=MATCH_SCORES
gap_score=-5
matrix=fill_matrix(seq1, seq2, score_matrix, gap_score)

# seq1="TCCAGAGA"
# seq2="TCGAT"
# len_seq1=len(seq1)
# len_seq2=len(seq2)
# score_matrix=MATCH_SCORES
# gap_score=-5
# matrix=fill_matrix(seq1, seq2, score_matrix, gap_score)

# seq1="CGTGTCAAGTCT"
# seq2="ACGTCGTAGCTAGG"
# len_seq1=len(seq1)
# len_seq2=len(seq2)
# score_matrix=MATCH_SCORES
# gap_score=-5
# matrix=fill_matrix(seq1, seq2, score_matrix, gap_score)

#print(empty_matrix(len_seq1, len_seq2))
#print(prepare_matrix(len_seq1, len_seq2, gap_score))
#print(fill_matrix(seq1, seq2, score_matrix, gap_score))
#print(trace_back(seq1, seq2, matrix, score_matrix, gap_score))
#print(align(seq1, seq2, score_matrix, gap_score))
print(align(seq1, seq2, score_matrix, gap_score))
print(trace_back2(seq1, seq2, matrix, score_matrix, gap_score))

# print(fill_matrix("AT", "GAT", MATCH_SCORES, -2))
#align("AATAAT", "AAGG", MATCH_SCORES, -5)
#align(load_fasta("seq1.fasta"), load_fasta("seq2.fasta"), MATCH_SCORES, -5)