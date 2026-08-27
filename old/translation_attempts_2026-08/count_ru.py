import os, re

files = [f for f in os.listdir('.') if f.endswith('.py')]

for f in files:

    with open(f, encoding='utf-8', errors='ignore') as file:

        c = sum(bool(re.search('[A-Yaa-yoyo]', l)) for l in file)

        if c > 0:

            print(f"{f}: {c} lines")

