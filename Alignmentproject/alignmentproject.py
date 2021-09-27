#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################


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


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

