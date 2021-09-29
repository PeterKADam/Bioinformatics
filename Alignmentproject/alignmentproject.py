#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################
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

    matrix = []

    for each in range(len_seq1):
        matrix.append([None] * len_seq2)
    return matrix


def prepare_matrix(len_seq1: int, len_seq2: int, gap_score: int):

    matrix = empty_matrix(len_seq1, len_seq2)

    for x in range(len_seq2):
        for y in range(len_seq1):
            if x == 0:
                matrix[y][x] = y * gap_score
            if y == 0:
                matrix[y][x] = x * gap_score
    return matrix


def fill_matrix():

    return


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

print(prepare_matrix(3, 4, -2))

