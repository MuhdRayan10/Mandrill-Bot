import os


i = os.listdir()
l = 0

def func(items, cog=''):
    global l
    for item in items:
        if item.endswith('.py'):
            with open(cog+item, 'r', encoding='utf-8') as f:
                x = len(f.readlines())
                l += x

        elif item == "cogs":
            func(os.listdir(item), './cogs/')



