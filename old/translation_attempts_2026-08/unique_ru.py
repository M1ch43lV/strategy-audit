import os, re



ru_pattern = re.compile(r'[A-Yaa-yoyo]')

files = [f for f in os.listdir('.') if f.endswith('.py')]

lines = []



for f in files:

    with open(f, encoding='utf-8', errors='ignore') as file:

        for line in file:

            if ru_pattern.search(line):

                lines.append(line.strip())



comments = [l for l in lines if l.startswith('#')]

docstrings = [l for l in lines if l.startswith('u\"\"\"') or l.startswith('\"\"\"') or l.startswith("u'''") or l.startswith("'''") or l.endswith('\"\"\"') or l.endswith("'''")]

others = [l for l in lines if l not in comments and l not in docstrings]

unique_others = list(set(others))



print(f'Unique other lines: {len(unique_others)}')

