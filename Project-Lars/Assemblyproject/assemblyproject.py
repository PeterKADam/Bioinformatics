#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...

# You get this one for free :-)
def pretty_print(d):
    print("      ", end="")
    for j in sorted(d):
        print("{: >6}".format(j), end="")
    print()

    for i in sorted(d):
        print("{: >6}".format(i), end="")
        for j in sorted(d):
            if i == j:
                s = "     -"
            else:
                s = "{: >6}".format(d[str(i)][str(j)])
            print(s, end="")
        print()


def read_data(filename):
    seq_dict = {}

    with open(filename) as f:
        data = f.read().splitlines()

    # for loop could prolly get refactored into list comprehension. but i wont, cause it looks bad

    for line in range(len(data)):
        i = data[line].split()
        seq_dict[i[0]] = i[1]
    return seq_dict


seqreads = read_data(r"Project-Lars\Assemblyproject\sequencing_reads.txt")


def mean_length(dict):
    return len("".join(dict.values())) / len(dict)


def get_overlap(left, right):
    max_overlap = min(len(left), len(right))
    for i in range(max_overlap):
        ovl = max_overlap - i
        if left[-ovl:] == right[:ovl]:
            return left[-ovl:]
    return ""


def get_all_overlaps(dict):
    dick = {}

    for i in dict:
        dick[i] = {}
        for y in dict:
            if i != y:
                dick[i][y] = len(get_overlap(dict[i], dict[y]))
    return dick


def get_left_overlaps(dict, read):
    return sorted([dict[x][read] for x in dict if dict[x] is not dict[read]])


def find_first_read(dict):
    for reads in dict.keys():
        if max(get_left_overlaps(dict, reads)) <= 2:
            return reads


def find_key_for_largest_value(dict):
    return max(dict, key=dict.get)


def find_order_of_reads(first, dict):
    seqreads = [first]
    for each in range(1, len(dict.keys())):
        seqreads.append(find_key_for_largest_value(dict[seqreads[each - 1]]))
        # dict[seqreads[0]]
        #     dict["Read4"]
    return seqreads


def reconstruct_sequence(order, reads, overlaps):
    sekvens = reads[order[0]]
    for i in range(1, len(order)):
        tempread = reads[order[i]]
        sekvens += tempread[overlaps[order[i - 1]][order[i]] :]
        # overlaps["før"]     ["nu"]

        #  {Read4: {Read2: 17,....}}
    return sekvens


def assemble_genome(path):
    return reconstruct_sequence(
        find_order_of_reads(
            find_first_read(get_all_overlaps(read_data(path))),
            get_all_overlaps(read_data(path)),
        ),
        read_data(path),
        get_all_overlaps(read_data(path)),
    )


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...

# pretty_print(get_all_overlaps(seqreads))

# print(find_order_of_reads("Read4", get_all_overlaps(seqreads)))

print(
    assemble_genome(r"Project-Lars\Assemblyproject\sequencing_reads.txt")
    == "TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTCGTCCAGACCCCTAGCTGGTACGTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGTCGTGAACACATCAGT"
)

