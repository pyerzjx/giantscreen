a = ['n', 'tg', 'df']
b = "afasd[n]azv[tg]xv[n] [df]"
for i in a:
    b = b.replace("[%s]"%i,"1")

print(b)
