
#############################################################
# Write your functions definitions below.
# Do not write any other code here.
#############################################################

# only your function definitions...

# You get this one for free :-)
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

def read_data(filename):
    input_file = open(filename)
    seq_dict = {}
    for line in input_file:
        print(line)

    return
read_data(seque)







#############################################################
# Code for calling and testing your functions should be below
# here. If you separate function definitions from the rest of
# your script in this way, you are less likely to make mistakes.
#############################################################

# any other code ...





