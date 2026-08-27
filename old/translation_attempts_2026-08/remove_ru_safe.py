import os

import tokenize

import io

import re



def remove_ru_from_code(source_code):

    ru_pattern = re.compile(r'[--]')

    cache = {

        'PASS': 'PASS',

        'FOUND': 'FOUND',

        'NA': 'NA',

        'SKIP': 'SKIP',

        'FAIL': 'FAIL'

    }

    

    tokens = list(tokenize.tokenize(io.BytesIO(source_code.encode('utf-8')).readline))

    output = []

    prev_end = (1, 0)

    

    for tok in tokens:

        if tok.type == tokenize.ENCODING:

            continue

            

        # Add whitespace between tokens

        start_line, start_col = tok.start

        prev_line, prev_col = prev_end

        if start_line > prev_line:

            output.append('\n' * (start_line - prev_line))

            output.append(' ' * start_col)

        elif start_col > prev_col:

            output.append(' ' * (start_col - prev_col))

            

        # Process the token

        tok_string = tok.string

        if tok.type == tokenize.COMMENT:

            if ru_pattern.search(tok_string):

                tok_string = ru_pattern.sub('', tok_string)

        elif tok.type == tokenize.STRING:

            if ru_pattern.search(tok_string):

                for ru, en in cache.items():

                    tok_string = tok_string.replace(ru, en)

                if ru_pattern.search(tok_string):

                    # Replace remaining Russian letters with empty string inside the string literal

                    tok_string = ru_pattern.sub('', tok_string)

                    

        output.append(tok_string)

        prev_end = tok.end

        

    return ''.join(output)



if __name__ == '__main__':

    for f in os.listdir('.'):

        if f.endswith('.py'):

            with open(f, 'r', encoding='utf-8', errors='ignore') as file:

                code = file.read()

            try:

                new_code = remove_ru_from_code(code)

                with open(f, 'w', encoding='utf-8') as file:

                    file.write(new_code)

                print(f"Processed {f}")

            except Exception as e:

                print(f"Failed to process {f}: {e}")

