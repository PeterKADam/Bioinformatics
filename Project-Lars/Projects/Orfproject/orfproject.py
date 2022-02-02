codon_map = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

start_codon = "ATG"

stop_codons = ["TAG", "TGA", "TAA"]


#############################################################
# Write your functions definitions below.
# Do not write any other code here.


def find_start_positions(seq):
    start_positions = []
    for i in range(len(seq) - 2):
        if seq[i : i + 3] == start_codon:
            start_positions.append(i)
    return start_positions


def find_next_codon(seq, start, sele):
    for i in range(start, len(seq) - 2, 3):
        if seq[i : i + 3] == sele:
            return i
    return None


def find_next_stop_codon(seq, start):
    for i in range(start, len(seq) - 2, 3):
        if seq[i : i + 3] in stop_codons:
            return i
    return None


def find_orfs(seq):
    seq = seq.upper()
    list = []
    for start in find_start_positions(seq):
        if find_next_stop_codon(seq, start) != None:
            list.append([start, find_next_stop_codon(seq, start)])
    return list


def translate_codon(codon):
    return codon_map[codon] if codon in codon_map else "?"


def split_codons(orf):
    return [orf[x : x + 3] for x in range(0, len(orf), 3)]


def translate_orf(seq):
    return "".join([translate_codon(x) for x in split_codons(seq)])


def read_genome(file_name):
    f = open(file_name, "r")
    lines = f.readlines()
    substrings = []
    for line in lines:
        substrings.append(line.strip())
    genome = "".join(substrings)
    f.close()
    return genome


def find_candidate_proteins(seq):
    list = []
    for each in find_orfs(seq):
        list.append(translate_orf(seq[each[0] : each[1] + 3]))
    return list


#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...
genome = read_genome(r"Project-Lars\Orfproject\e_coli_O157_H157_str_Sakai.fasta")
first_1000_bases = genome
print(find_candidate_proteins(first_1000_bases))

