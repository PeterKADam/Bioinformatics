# from Bio import SeqIO


class alignment_matrix:
    def __init__(self, sequence1, sequence2, score_matrix, gap_cost):
        self.sequence1 = sequence1.upper()
        self.sequence2 = sequence2.upper()
        self.score_matrix = score_matrix
        self.gap_cost = gap_cost
        self.matrix = self.empty_matrix()
        self.alignments = []

    def empty_matrix(self):
        return [
            [None] * (len(self.sequence1) + 1) for _ in range(len(self.sequence2) + 1)
        ]

    def print_dp_matrix(self, matrix_object):
        if len(matrix_object) > 20:
            return print("Matrix too large to print")

        max_len = max(len(str(cell)) for row in matrix_object for cell in row)
        fmt = "{{:>{}}}".format(max_len + 1)
        row_fmt = fmt * (len(matrix_object[0]) + 1) + "\n"
        mat_fmt = row_fmt * (len(matrix_object) + 1)
        seq1, seq2 = self.sequence1, self.sequence2
        seq1 = " " + seq1
        seq2 = " " + seq2
        lst = [" "] + list(seq1)
        for i in range(len(seq2)):
            lst.extend([seq2[i]] + list(map(repr, matrix_object[i])))
        print(mat_fmt.format(*lst))

    def niceprint_alignments(self):
        if len(self.alignments) == 0:
            print("No alignments found")
        elif len(self.alignments) <= 5:
            for i, a in enumerate(self.alignments, start=1):
                print(f"Pair {i}:\n\t{a[0]}\n\t{a[1]}\n")
        else:
            print(
                f"Too many alignments to print, there are: {len(self.alignments)} alignments\n"
                f"the start of one of the alignments is:\n\t{self.alignments[0][0][:100]}\n\t{self.alignments[0][1][:100]}\n"
            )


class LinearGlobalAlignment(alignment_matrix):
    def __init__(self, sequence1, sequence2, score_matrix, gap_cost):
        super().__init__(sequence1, sequence2, score_matrix, gap_cost)

    def prepare_matrix(self):
        for col in range(len(self.sequence1) + 1):
            self.matrix[0][col] = col * self.gap_cost

        for row in range(len(self.sequence2) + 1):
            self.matrix[row][0] = row * self.gap_cost

    def fill_matrix(self):

        for col in range(1, len(self.sequence1) + 1):  # j
            for row in range(1, len(self.sequence2) + 1):  # i

                self.matrix[row][col] = min(
                    # C(i-1, j-1) + match
                    self.matrix[row - 1][col - 1]
                    + self.score_matrix[self.sequence1[col - 1]][
                        self.sequence2[row - 1]
                    ],
                    # c(i, j-1) + gapcost
                    self.matrix[row][col - 1] + self.gap_cost,
                    # c(i-1, j) + gapcost
                    self.matrix[row - 1][col] + self.gap_cost,
                )

    def get_traceback_arrows(self, row, col, match_score, gap_score):
        score_diagonal = self.matrix[row - 1][col - 1]
        score_left = self.matrix[row][col - 1]
        score_up = self.matrix[row - 1][col]

        score_current = self.matrix[row][col]

        arrows = []

        if score_current == score_diagonal + match_score:
            arrows.append("diagonal")
        if score_current == score_left + gap_score:
            arrows.append("left")
        if score_current == score_up + gap_score:
            arrows.append("up")

        return arrows

    def traceback_recursive(self, row, col):
        if row == 0 and col == 0:
            return [("", "")]
        elif row == 0:
            return [(col * "-", self.sequence1[:col])]
        elif col == 0:
            return [(self.sequence2[:row], row * "-")]

        arrows = self.get_traceback_arrows(
            row,
            col,
            self.score_matrix[self.sequence2[row - 1]][self.sequence1[col - 1]],
            self.gap_cost,
        )

        alignments = []
        for arrow in arrows:
            if arrow == "diagonal":
                sub_alignments = self.traceback_recursive(row - 1, col - 1)
                alignments.extend(
                    [
                        (self.sequence2[row - 1] + a1, self.sequence1[col - 1] + a2)
                        for a1, a2 in sub_alignments
                    ]
                )
            elif arrow == "up":
                sub_alignments = self.traceback_recursive(row - 1, col)
                alignments.extend(
                    [
                        (self.sequence2[row - 1] + a1, "-" + a2)
                        for a1, a2 in sub_alignments
                    ]
                )
            elif arrow == "left":
                sub_alignments = self.traceback_recursive(row, col - 1)
                alignments.extend(
                    [
                        ("-" + a1, self.sequence1[col - 1] + a2)
                        for a1, a2 in sub_alignments
                    ]
                )

        return alignments

    def get_alignments(self):
        alignments = self.traceback_recursive(len(self.sequence2), len(self.sequence1))
        # Reverse the completed strings
        self.alignments = [(a1[::-1], a2[::-1]) for a1, a2 in alignments]

    def print_finish_matrix(self):
        self.prepare_matrix()
        self.fill_matrix()
        self.print_dp_matrix(self.matrix)
        print(f"maximum is : {self.matrix[-1][-1]}")
        self.get_alignments()
        self.niceprint_alignments()


class AffineGlobalAlignment(alignment_matrix):
    def __init__(self, sequence1, sequence2, score_matrix, gap_cost, gap_open):
        super().__init__(sequence1, sequence2, score_matrix, gap_cost)
        self.gap_open = gap_open
        self.matrixI = self.empty_matrix()
        self.matrixD = self.empty_matrix()

    def prepare_matrixes(self):
        self.matrix[0][0] = self.matrixI[0][0] = self.matrixD[0][0] = 0
        for col in range(1, len(self.sequence1) + 1):
            self.matrix[0][col] = (col * self.gap_cost) + self.gap_open
            self.matrixI[0][col] = (col * self.gap_cost) + self.gap_open

        for row in range(1, len(self.sequence2) + 1):
            self.matrix[row][0] = (row * self.gap_cost) + self.gap_open
            self.matrixD[row][0] = (row * self.gap_cost) + self.gap_open

    def print_matrix_set(self):
        print("Matrix M")
        self.print_dp_matrix(self.matrix)
        print("Matrix I")
        self.print_dp_matrix(self.matrixI)
        print("Matrix D")
        self.print_dp_matrix(self.matrixD)

    def fill_matrixes(self):
        for col in range(1, len(self.sequence1) + 1):  # j
            for row in range(1, len(self.sequence2) + 1):  # i

                # Matrix I
                self.matrixI[row][col] = min(
                    # open new
                    self.gap_open + self.gap_cost + self.matrix[row - 1][col],
                    # extend
                    (
                        self.gap_cost + self.matrixI[row - 1][col]
                        if self.matrixI[row - 1][col] is not None
                        else float("inf")
                    ),
                )
                # Matrix D
                self.matrixD[row][col] = min(
                    # open new
                    self.gap_open + self.gap_cost + self.matrix[row][col - 1],
                    # extend
                    (
                        self.gap_cost + self.matrixD[row][col - 1]
                        if self.matrixD[row][col - 1] is not None
                        else float("inf")
                    ),
                )
                # Matrix M
                self.matrix[row][col] = min(
                    # match
                    self.matrix[row - 1][col - 1]
                    + self.score_matrix[self.sequence1[col - 1]][
                        self.sequence2[row - 1]
                    ],
                    # insert
                    self.matrixI[row][col],
                    # del
                    self.matrixD[row][col],
                )
