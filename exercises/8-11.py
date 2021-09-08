def assess_number(x):
    if x < 3:
        return 'quite a few'
    if x < 100:
        return 'a lot'
    return 'a whole lot'

nr_apples = 200
print(nr_apples, "apples is", assess_number(nr_apples))