#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################
from inspect import trace


MATCH_SCORES = {
    "A": {"A": 2, "T": 0, "G": 0, "C": 0},
    "T": {"A": 0, "T": 2, "G": 0, "C": 0},
    "G": {"A": 0, "T": 0, "G": 2, "C": 0},
    "C": {"A": 0, "T": 0, "G": 0, "C": 2},
}


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


# only your function definitions...
def empty_matrix(len_seq1: int, len_seq2: int):

    return [[None] * len_seq2 for _ in range(len_seq1)]


def prepare_matrix(len_seq1: int, len_seq2: int, gap_score: int):

    matrix = empty_matrix(len_seq1, len_seq2)

    for x in range(len_seq2):
        for y in range(len_seq1):
            if x == 0:
                matrix[y][x] = y * gap_score
            if y == 0:
                matrix[y][x] = x * gap_score
    return matrix


def fill_matrix(seq1, seq2, dictdict, gap_score):

    matrix = prepare_matrix(len(seq1) + 1, len(seq2) + 1, gap_score)

    for y in range(1, len(seq1) + 1):
        for x in range(1, len(seq2) + 1):
            matrix[y][x] = max(
                matrix[y][x - 1] + gap_score,
                matrix[y - 1][x] + gap_score,
                matrix[y - 1][x - 1] + dictdict[seq1[y - 1]][seq2[x - 1]],
            )

    return matrix


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


def trace_back(seq1, seq2, matrix, score_matrix, gap_score):

    # Strings to store the growing alignment strings:
    aligned1 = ""
    aligned2 = ""
    # continues...
    # The row and col index of the bottom right cell:
    row = len(seq1)
    col = len(seq2)
    # Keep stepping backwards through the matrix untill
    # we get to the top row or the left col:
    while row > 0 and col > 0:
        # The two bases we available to match:
        base1 = seq1[row - 1]
        base2 = seq2[col - 1]
        # The score for mathing those two bases:
        match_score = score_matrix[base1][base2]
        # Find out which cell the score in the current cell was derived from:
        traceback_arrow = get_traceback_arrow(matrix, row, col, match_score, gap_score)
        if traceback_arrow == "diagonal":
            # last column of the sub alignment is base1 over base2:
            aligned1 = base1 + aligned1
            aligned2 = base2 + aligned2
            # next cell is the diagonal cell:
            row -= 1
            col -= 1
        elif traceback_arrow == "up":
            # last column in the sub alignment is base1 over a gap:
            aligned1 = base1 + aligned1
            aligned2 = "-" + aligned2
            # next cell is the cell above:
            row -= 1
        elif traceback_arrow == "left":
            # last column in the sub alignment is a gap over base2:
            aligned1 = "-" + aligned1
            aligned2 = base2 + aligned2
            # next cell is the cell to the left:
            col -= 1
            # continues...
            # If row is not zero, step along the top row to the top left cell:
        while row > 0:
            base1 = seq1[row - 1]
            aligned1 = base1 + aligned1
            aligned2 = "-" + aligned2
            row -= 1
            # If col is not zero, step upwards in the left col to the top left cell:
        while col > 0:
            base2 = seq2[col - 1]
            aligned1 = "-" + aligned1
            aligned2 = base2 + aligned2
            col -= 1
        return [aligned1, aligned2]


def align(seq1, seq2, score_matrix, gap_score):

    matrix = fill_matrix(seq1, seq2, score_matrix, gap_score)

    return trace_back(seq1, seq2, matrix, score_matrix, gap_score)


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...


# print(fill_matrix("AT", "GAT", MATCH_SCORES, -2))
print(align("ATAT", "GATGAT", MATCH_SCORES, -2))
