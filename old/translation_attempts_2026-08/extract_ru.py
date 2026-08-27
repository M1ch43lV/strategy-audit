import os, re, json



def extract():

    ru_pattern = re.compile(r'[A-Yaa-yoyo]')

    files = [f for f in os.listdir('.') if f.endswith('.py')]

    strings = set()

    

    for f in files:

        with open(f, encoding='utf-8', errors='ignore') as file:

            for line in file:

                if ru_pattern.search(line):

                    # Extract string literals and comments

                    # This is simple: just extract the whole line to translate it, or extract quotes/comments

                    strings.add(line.strip())

                    

    with open('ru_strings.json', 'w', encoding='utf-8') as out:

        json.dump(list(strings), out, ensure_ascii=False, indent=2)

        

if __name__ == '__main__':

    extract()

