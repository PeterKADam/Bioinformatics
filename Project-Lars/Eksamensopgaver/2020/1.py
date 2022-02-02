def count_stuff(iterable):
    dict = {}
    for i in iterable:
		if str(i) in dict:
            dict[i] = 0
        dict[i] = +1
    return dict