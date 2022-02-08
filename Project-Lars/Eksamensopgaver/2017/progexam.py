# Write your Python functions in this file. Do not rename it.

# Problem 1


def get_number_of_bases(seq):
    return len(seq)


# Problem 2


def count_bases(seq):
    dict = {"A": 0, "T": 0, "G": 0, "C": 0}
    for i in seq:
        dict[i] += 1
    return dict


# Problem 3


def reverse_complement(seq):
    reversedseq = ""
    for base in range(len(seq) - 1, -1, -1):
        if seq[base] == "A":
            reversedseq += "T"
        if seq[base] == "T":
            reversedseq += "A"
        if seq[base] == "G":
            reversedseq += "C"
        if seq[base] == "C":
            reversedseq += "G"
    return reversedseq


# Problem 4
def count_cpg(seq):
    count = 0
    for base in range(0, len(seq) - 1):
        if seq[base : base + 2] == "CG":
            count += 1
    return count


# Problem 5
def melting_temp(seq):
    i = count_bases(seq)
    if len(seq) < 14:
        return (i["A"] + i["T"]) * 2 + (i["C"] + i["G"]) * 4
    return 64.9 + 41 * (i["G"] + i["C"] - 16.4) / (len(seq))


# Problem 6
def count_kmers(seq, int):
    dict = {}
    for base in range(len(seq) - int + 1):
        if seq[base : base + int] not in dict:
            dict[seq[base : base + int]] = 0
        dict[seq[base : base + int]] += 1
    return dict


# Problem 7
def kmer_profile(seq, int):
    dict = {}
    for length in range(2, int + 1):
        dict[length] = count_kmers(seq, length)
    return dict


# Problem 8
def has_hairpin(seq, minimum_bases):
    looplen = 4
    for i in range(len(seq) - minimum_bases + 1):
        substring = seq[i : i + minimum_bases]
        right = seq[i + minimum_bases :]
        revcl = reverse_complement(substring)
        if revcl in right[looplen:]:
            return True
        return False


# Problem 9
def substitutions(seq1, seq2):
    version = 0
    sistion = 0
    for base in range(len(seq1)):
        if (
            (seq1[base] == "A" and seq2[base] == "G")
            or (seq1[base] == "G" and seq2[base] == "A")
            or (seq1[base] == "C" and seq2[base] == "T")
            or (seq1[base] == "T" and seq2[base] == "C")
        ):
            sistion += 1
        elif seq1[base] != seq2[base]:
            version += 1
    return [sistion, version]


# Problem 10
def self_comparison(seq):
    matrix = []
    for every in range(len(seq)):
        matrix.append([None] * len(seq))

    for i in range(len(seq)):
        for j in range(len(seq)):
            if seq[i] == seq[j]:
                matrix[i][j] = 1
            else:
                matrix[i][j] = 0
    return matrix


# Problem 11
def better_self_comparison(seq, int):
    matrix = []
    for every in range(len(seq)):
        matrix.append([NONE] * len(seq))

    for i in range(len(seq)):
        for j in range(len(seq)):
            if seq[i] == seq[j]:
                if (
                    seq[i - int : i + int + 1] == seq[j - int : j + int + 1]
                    and j >= int
                    and j <= len(seq) - int - 1
                ):
                    matrix[i][j] = 1
                else:
                    matrix[i][j] = 0
            else:
                matrix[i][j] = 0
    return matrix

