import sys
import re
from pybtex.database.input import bibtex
# from pybtex.database import parse_file as parse_bib_file, BibliographyData
from pybtex.database import parse_file as parse_bib_file
from pybtex.database import BibliographyData, BibliographyDataError

def replace_latex_ascii_codes(input_string):
    replacements = {
        '{\\o}': 'ø',
        '{\\aa}': 'å',
        '{\\ae}': 'æ',
        '{\\"a}': 'ä',
        '{\\`e}': 'è',
        '{\\\'e}': 'é',
        '{\\^e': 'ê',
        '{\\"e}': 'ë',
        '{\\c c}': 'ç',
        '{\\~n}': 'ñ',
        '{\\=o}': 'ō',
        '{\\"o}': 'ö',
        '{\\"u}': 'ü',
        '{\\u g}': 'ğ',
        '{\\.i}': 'i',
        '{\\ss}': 'ß',
        '{\'u}' : 'ú',
        '{\\v{s}}': 'š'
        # Add more replacements as needed
    }

    for latex_code, char in replacements.items():
        input_string = input_string.replace(latex_code, char)

    return input_string


def remove_duplicate_entries(bib_file_path):
    with open(bib_file_path, 'r') as f:
        bib_content = f.read()

    # Regex to match bib entries. Assumes entries start with @ and are separated by at least one blank line
    entry_pattern = re.compile(r'(@[a-zA-Z]+\{[^@]+,?)', re.DOTALL)
    entries = entry_pattern.findall(bib_content)

    # Create a dictionary to hold entries, using the citation key as the unique identifier
    unique_entries = {}
    for entry in entries:
        key_match = re.search(r'@[a-zA-Z]+\{([^,]+),', entry)
        if key_match:
            key = key_match.group(1)
            unique_entries[key] = entry  # This will overwrite duplicates

    # Concatenate unique entries back into a single string
    unique_content = '\n\n'.join(unique_entries.values())
    return unique_content

def parse_bib_file(bib_data):

    parser = bibtex.Parser()
    bib_structure = {}
    try:
        bib_data = parser.parse_string(bib_data)
        # bib_data = parse_bib_file(bib_file_path, check_duplicates=False)
    except BibliographyDataError as e:
        print(f"An error occurred while reading the BibTeX file: {e}")
        return bib_structure

    for cite_key, entry in bib_data.entries.items():
        authors = ' and '.join(str(person) for person in entry.persons['author'])
        year = entry.fields.get('year', '')
        title = entry.fields.get('title', '')
        publisher = entry.fields.get('publisher', '')
        journal = entry.fields.get('journal', '')
        bib_structure[cite_key] = {'authors': authors, 'year': year, 'title': title, 'journal': journal, 'publisher': publisher}
    return bib_structure

def convert_to_apa_authors(bibtex_authors):
    # Split authors by ' and ' and strip extra spaces
    authors_list = [author.strip() for author in bibtex_authors.split(' and ')]
    
    apa_authors = []
    for author in authors_list:
        # Check if the name contains a comma indicating Last, First format
        if ',' in author:
            last_name, first_names = author.split(',', 1)
        else:
            *first_names, last_name = author.split()
            first_names = ' '.join(first_names)
        
        # Convert first names to initials
        initials = '. '.join([name[0] for name in first_names.split()]) + '.'
        
        # Format to APA style: Lastname, F. M.
        apa_authors.append(f"{last_name.strip()}, {initials}")

    # Join with commas and insert '&amp;' before the last author
    if len(apa_authors) > 1:
        return ', '.join(apa_authors[:-1]) + ', &amp; ' + apa_authors[-1]
    else:
        return apa_authors[0]

# Example usage
#bibtex_authors = "John Doe and Jane Smith and Albert B. C. Einstein"
#print(convert_to_apa_authors(bibtex_authors))


def convert_citations(text, bib_structure):
    #with open(text_file_path, 'r') as f:
    #    text = f.read()

    cite_regex = re.compile(r'\\cite(p)?\{([^}]+)\}')
    used_citations = []

    '''
    def citation_replacement(match):
        prefix = "(" if match.group(1) else ""
        cite_key = match.group(2)
        # in text
        if cite_key in bib_structure:
            entry = bib_structure[cite_key]
            authors = entry['authors'].split(' and ')[0].split(',')[0]  # Assuming first author only
            year = entry['year']
            citation = f"{authors} et al., "
            citation+= f"{year}" if match.group(1) else f"({year})"
            used_citations.append(cite_key)
            return f"{prefix}{citation}{')' if prefix else ''}"
        # else:
        #     print('not found citekey: ' + cite_key)
        return match.group(0)
    '''
    def citation_replacement(match):
        prefix = "(" if match.group(1) else ""
        cite_keys = match.group(2).split(',')  # Split cite keys by comma
        citations = []

        for cite_key in cite_keys:
            cite_key = cite_key.strip()  # Remove leading/trailing whitespace
            if cite_key in bib_structure:
                entry = bib_structure[cite_key]
                authors = entry['authors'].split(' and ')[0].split(',')[0]  # Assuming first author only
                year = entry['year']
                citation = f"{authors} et al., "
                citation+= f"{year}" if match.group(1) else f"({year})"
                citations.append(citation)
                used_citations.append(cite_key)
            else:
                print('not found citekey: ' + cite_key)

        # Join multiple citations with a semicolon and space as per APA guidelines
        citation_text = '; '.join(citations)

        return f"{prefix}{citation_text}{')' if prefix else ''}"

    text = cite_regex.sub(citation_replacement, text)

    # Generate APA style citation list
    # TODO sort list
    citation_str = "==References==\n"
    citation_list = list()
    for cite_key in set(used_citations):  # Remove duplicates in used citations
        entry = bib_structure[cite_key]
        authors = convert_to_apa_authors( entry['authors'])
        year = entry['year']
        title = entry['title']
        journal = entry['journal']
        journal = "''" + journal + "'', " if len(journal) > 0 else ''
        publisher = entry['publisher']
        citation_list.append(f"# {authors} ({year}). {title}. {journal}{publisher}.\n")

    citation_list.sort()
    # Append citation list to text
    text += "\n\n" + citation_str + ''.join(citation_list)

    return text

if __name__ == '__main__':
    #text_file_path = sys.argv[1]
    # Read LaTeX content from stdin
    latex_content = sys.stdin.read()
    bib_file_path = sys.argv[1]
    bib_data = remove_duplicate_entries(bib_file_path)
    
    with open('refs_no_duplicates.bib', 'w') as f:
        f.write(bib_data)
    bib_structure = parse_bib_file(bib_data)
    converted_text = convert_citations(latex_content, bib_structure)
    converted_text = replace_latex_ascii_codes(converted_text)
    converted_text = re.sub('\n\n+', '\n\n', converted_text)
    with open('out_with_citations.txt', 'w') as f:
        f.write(converted_text)
    #print(converted_text)
