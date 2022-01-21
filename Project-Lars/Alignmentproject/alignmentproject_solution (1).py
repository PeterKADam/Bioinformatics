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


# Write your code below...


def empty_matrix(m, n):
    matrix = []
    for i in range(m):
        row = []
        for j in range(n):
            row.append(None)
        matrix.append(row)
    return matrix


def prepare_matrix(m, n, gap_score):

    matrix = empty_matrix(m, n)

    for i in range(len(matrix)):
        matrix[i][0] = gap_score * i

    for j in range(len(matrix[0])):
        matrix[0][j] = gap_score * j

    return matrix


def fill_matrix(seq1, seq2, score_matrix, gap_score):

    matrix = prepare_matrix(len(seq1) + 1, len(seq2) + 1, gap_score)

    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            base1 = seq1[i - 1]
            base2 = seq2[j - 1]
            diag = matrix[i - 1][j - 1] + score_matrix[base1][base2]
            left = matrix[i][j - 1] + gap_score
            up = matrix[i - 1][j] + gap_score
            matrix[i][j] = max(left, up, diag)

    return matrix


def get_traceback_arrow(matrix, row, col, match_score, gap_score):

    # yellow cells
    score_diagonal = matrix[row - 1][col - 1]
    score_left = matrix[row][col - 1]
    score_up = matrix[row - 1][col]

    # gree cell
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
            aligned1 = base1 + aligned1
            aligned2 = base2 + aligned2
            row -= 1
            col -= 1
        elif traceback_arrow == "up":
            aligned1 = base1 + aligned1
            aligned2 = "-" + aligned2
            row -= 1
        elif traceback_arrow == "left":
            aligned1 = "-" + aligned1
            aligned2 = base2 + aligned2
            col -= 1

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
    dp = fill_matrix(seq1, seq2, score_matrix, gap_score)
    return trace_back(seq1, seq2, dp, score_matrix, gap_score)


if __name__ == "__main__":

    score_matrix = {
        "A": {"A": 2, "T": 0, "G": 0, "C": 0},
        "T": {"A": 0, "T": 2, "G": 0, "C": 0},
        "G": {"A": 0, "T": 0, "G": 2, "C": 0},
        "C": {"A": 0, "T": 0, "G": 0, "C": 2},
    }

    gap_score = -2

    # a = "AT"
    # b = "GAT"

    # a = "GTC"
    # b = "GC"

    # a = "GC"
    # b = "GTC"

    a = "TGGTA"
    b = "TTTGT"

    for s in align(a, b, score_matrix, gap_score):
        print(s)

