def hej(a, b):
    return max(len(a), len(b))


print(hej("AAAAAAAAAA", "BBBBBBBBBB"))


gcfreq =gc_frequency(sequence)
if gcfreq >=0 and gcfreq < 2:
    return [0,0.2]
if gcfreq >=2 and gcfreq < 4:
    return [0.2,0.4]