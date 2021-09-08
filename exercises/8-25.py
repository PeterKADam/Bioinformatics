def is_uppercase_vowel(c):
    if c == 'A' or c == 'E' or c == 'I' or c == 'O' or c == 'U': return True
    else: return False

char = 'A'
if is_uppercase_vowel(char):
    print(char, "is an uppercase vowel")
else:
    print(char, "is NOT an uppercase vowel")