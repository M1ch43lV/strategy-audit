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

print(f'Total: {len(lines)}, Comments: {len(comments)}, Docstrings: {len(docstrings)}, Other: {len(lines) - len(comments) - len(docstrings)}')

for l in [l for l in lines if l not in comments and l not in docstrings][:20]:

    print(l)

