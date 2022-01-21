# This serve to make the log function available:
from math import log

#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...


def sequence_difference(seq1, seq2):
    diff = 0
    for i in range(len(seq1)):
        if seq1[i] != seq2[i]:
            diff += 1
    return diff / len(seq1)


def jukes_cantor(diff):
    return -(3 / 4) * log(1 - (4 / 3) * diff)


def lower_trian_matrix(seqlist):
    list = []
    for y in range(len(seqlist)):
        sublist = []
        for x in range(y):
            if not y == x:
                sublist.append(
                    jukes_cantor(sequence_difference(seqlist[y], seqlist[x]))
                )
        list.append(sublist)
    return list


def find_lowest_cell(matrix):
    x = 1
    y = 0
    min_val = matrix[x][y]
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] < min_val:
                min_val = matrix[i][j]
                x, y = i, j
    return [x, y]


def link(x, y):
    return (x + y) / 2


def update_table(table, a, b):
    # For the lower index, reconstruct the entire row (ORANGE)
    for i in range(0, b):
        table[b][i] = link(table[b][i], table[a][i])
        # Link cells to update the column above the min cell (BLUE)
    for i in range(b + 1, a):
        table[i][b] = link(table[i][b], table[a][i])
        # Link cells to update the column below the min cell (RED)
    for i in range(a + 1, len(table)):
        table[i][b] = link(table[i][b], table[i][a])
    # Delete cells we no longer need (lighter colors)
    for i in range(a + 1, len(table)):
        # Remove the (now redundant) first index column entry
        del table[i][a]
    # Remove the (now redundant) first index row
    del table[a]


def update_labels(labels, i, j):
    # turn the label at first index into a combination of both labels
    labels[j] = "({},{})".format(labels[j], labels[i])
    # Remove the (now redundant) label in the first index
    del labels[i]


def cluster(sequences, names):

    table = lower_trian_matrix(sequences)
    labels = names[:]

    # Until all labels have been joined...
    while len(labels) > 1:
        # Locate lowest cell in the table
        i, j = find_lowest_cell(table)

        # Join the table on the cell co-ordinates
        update_table(table, i, j)

        # Update the labels accordingly
        update_labels(labels, i, j)

    # Return the final label
    return labels[0]


def read_fasta(filename):

    f = open(filename, "r")

    record_list = []
    header = ""
    sequence = ""
    for line in f:
        line = line.strip()  ## get rid of whitespace and newline
        if line.startswith(">"):
            if header != "":  ## if it is the first header
                record_list.append([header, sequence])
                sequence = ""
            header = line[1:]
        else:
            sequence += line
    record_list.append([header, sequence])

    return record_list


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

# liste = [1, 0, 3, 4, 5, 2, 4]
# print(liste.index(min(liste)))
# print(find_lowest_cell(lower_trian_matrix(sequences)))

names = ["A", "B", "C", "D"]
sequences = ["TAAAAAAAAAAA", "TTAAAAAAAAAA", "AAAAAAAAAAGG", "AAAAAAAAGGGG"]
tree = cluster(sequences, names)
print(tree)
