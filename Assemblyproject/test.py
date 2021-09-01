

with open('sequencing_reads.txt','r') as file:
        input_file = file.read()
f = open('sequencing_reads.txt','r')
#for line in input_file:
print(input_file.split()[0])

f.close