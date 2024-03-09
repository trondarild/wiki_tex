import sys
import re
from pybtex.database.input import bibtex
# from pybtex.database import parse_file as parse_bib_file, BibliographyData
from pybtex.database import parse_file as parse_bib_file
from pybtex.database import BibliographyData, BibliographyDataError

def remove_duplicate_entries(bib_file_path):
    with open(bib_file_path, 'r') as f:
        bib_content = f.read()

    # Regex to match bib entries. Assumes entries start with @ and are separated by at least one blank line
    # TODO remove all comments; collapse entries to one line; remove duplicates    
    entry_pattern = re.compile(r'(@[a-zA-Z]+\{[^@]+?\}\n\n?)', re.DOTALL)
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
        bib_structure[cite_key] = {'authors': authors, 'year': year, 'title': title, 'publisher': publisher}
    return bib_structure

def convert_citations(text, bib_structure):
    #with open(text_file_path, 'r') as f:
    #    text = f.read()

    cite_regex = re.compile(r'\\cite(p)?\{(.+?)\}')
    used_citations = []

    def citation_replacement(match):
        prefix = "(" if match.group(1) else ""
        cite_key = match.group(2)
        if cite_key in bib_structure:
            entry = bib_structure[cite_key]
            authors = entry['authors'].split(' and ')[0].split(',')[0]  # Assuming first author only
            year = entry['year']
            citation = f"{authors} et al., ({year})"
            used_citations.append(cite_key)
            return f"{prefix}{citation}{')' if prefix else ''}"
        return match.group(0)

    text = cite_regex.sub(citation_replacement, text)

    # Generate APA style citation list
    citation_list = "==References==\n"
    for cite_key in set(used_citations):  # Remove duplicates in used citations
        entry = bib_structure[cite_key]
        authors = entry['authors']
        year = entry['year']
        title = entry['title']
        publisher = entry['publisher']
        citation_list += f"# {authors} ({year}). {title}. {publisher}.\n"

    # Append citation list to text
    text += "\n\n" + citation_list

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
    #with open(text_file_path.replace('.txt', '_with_citations.txt'), 'w') as f:
    #    f.write(converted_text)
    print(converted_text)
