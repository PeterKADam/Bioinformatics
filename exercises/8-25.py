def is_uppercase_vowel(c):
    if c in 'AEIOU':
        print(c, "is an uppercase vowel")
        return True
    else:
        print(c, "is NOT an uppercase vowel")
        return False

is_uppercase_vowel('A')