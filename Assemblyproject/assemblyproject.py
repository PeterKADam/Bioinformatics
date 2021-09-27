
#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...

# You get this one for free :-)
from os import read
from typing import Counter

RPATH = 'Assemblyproject\sequencing_reads.txt'
if __name__ != '__main__':
    RPATH = 'sequencing_reads.txt'

#useless function
def pretty_print(d):
    print('      ', end='')
    for j in sorted(d):
        print("{: >6}".format(j), end='')
    print()

    for i in sorted(d):
        print("{: >6}".format(i), end='')
        for j in sorted(d):
            if i == j:
                s = '     -'
            else:
                s = "{: >6}".format(d[str(i)][str(j)])
            print(s, end='')
        print()

#reads whole file, for every line, splits the line elements and assigns them as dict pairs. WILL BREAK FOR MORE THAN 2 ELEMENTS
def read_data(filename: str = RPATH):
    seq_dict = {}
    with open(filename) as f:
        data = f.read().splitlines()
    
    for line in range(len(data)):
        i = data[line].split()
        seq_dict[i[0]] = i[1]
    return seq_dict    

#join all values in one string and divides by nr of elements.
def mean_length(seqdict: dict =read_data()):
    return len(''.join(seqdict.values()))/len(seqdict.values())

'''
def get_overlap_deprecated(left, right): # old overlap function
    """
    @get_overlap_deprectared
    more or less black magic. takes right seq, checks if its in left
    if not, lop a bp off right, and check again.
    stops at 3 bp where the chance of random bp matches is too high.
    if no matches are found in the iterable, check the left edge of right seq with right edge of left seq for a one bp overlap.
    """
    for i in range(len(right)):
        if right[:len(right)-i-1] in left and len(right[:len(right)-i-1])>2:
            return right[:len(right)-i-1]
    if right[0]==left[len(left)-1]:
            return right[0]
    return ""
'''

def get_overlap(left: str,right: str):
    
    for current in range(min(len(right),len(left))):
        if left[current:] in right and left[current:].startswith(right[:len(left[current:])]):
            return left[current:]
    if right[0]==left[len(left)-1]:
        return right[0]
    return ""


def get_all_overlaps(readdata: dict = read_data()):
    overlapdict={}
    
    for each in readdata.keys():
        overlapdict[each]={}
        
        for every in readdata.keys():
            if not every == each:
                overlapdict[each][every]=len(get_overlap(readdata[each],readdata[every]))                     
    return overlapdict
 
def get_left_overlaps(*args):#overlaps:dict = get_all_overlaps(), read: str =None):
    #stupid arg handling to get over bad assignment parameters
    if type(args[0]) is str:
        overlaps = get_all_overlaps()
        read = args[0]
    elif type(args[0]) is dict:
        overlaps = args[0]
        read = args[1]
    else: print("u is retarded, pass good args, either (dict,'readX') or 'ReadX' for default dict from RPATH file")
    #func start ↓
    returnlist=[]

    for each in overlaps:
        if overlaps[each] is not overlaps[read]:
            returnlist.append(overlaps[each][read])
    return sorted(returnlist)

def find_first_read(overlaps: dict = get_all_overlaps()):

    sumdict={}

    for each in overlaps.keys():
        sumdict[each]=sum(get_left_overlaps(str(each)))
    return min(sumdict, key=sumdict.get)

def find_key_for_largest_values(overlaps:dict):
    return max(overlaps, key=overlaps.get)

def find_order_of_reads(first_read:str = find_first_read(), overlaps:dict=get_all_overlaps()):
    seq_list=[first_read]
    for each in range(1,len(overlaps.keys())-1):
        seq_list.append(find_key_for_largest_values(overlaps[str(seq_list[:len(seq_list)-1])]))        



    return seq_list

#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

Read1 ="GGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTCGTCCAGACCCCTAGC"
Read2 ="CTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGG"
Read4 ="TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGCG"
Read3 ="GTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGTCGTGAACACATCAGT"
Read5 ="CGATTCCAGGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTC"
Read6 ="TGACAGTAGATCTCGTCCAGACCCCTAGCTGGTACGTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGT"

print(find_order_of_reads())