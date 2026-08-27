import os

py_files = [f for f in os.listdir('.') if f.endswith('.py')]

for file_path in py_files:

    with open(file_path, 'r', encoding='utf-8') as f:

        lines = f.readlines()

    new_lines = [l for l in lines if l.strip() not in ('\"\"\"', 'u\"\"\"', "'''", "u'''")]

    with open(file_path, 'w', encoding='utf-8') as f:

        f.writelines(new_lines)

