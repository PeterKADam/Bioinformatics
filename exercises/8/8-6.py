def lucky_number():
    return 7
x = lucky_number()
y = lucky_number()

twice_as_lucky = x+y
print(twice_as_lucky)

twice_as_lucky = lucky_number()+lucky_number()
print(twice_as_lucky)

print(lucky_number()+lucky_number())
