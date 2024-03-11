import re
import sys
'''
Puts bib file into standard format, one ref per line
'''

def regex_replacements(source):
    replacements = {
        r'\%.+': '',  # Remove \index{} entries
        r',\n': ', ',
        r'\}\n\}': '}}',
        r'([0-9])\n\}': '\\1}',
        r'\{\n': '{',
        r'\n+': '\n'
        # Add more regex patterns and their replacements as needed
    }
    retval = source
    for pattern, replacement in replacements.items():
        #print(pattern)
        retval = re.sub(pattern, replacement, retval)
        # print (retval)
    return retval



if __name__ == '__main__':
    text = sys.stdin.read()
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines]
    text = '\n'.join(cleaned_lines)
    text = regex_replacements(text)
    #to_file(text)
    print(text)
