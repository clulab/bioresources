import os
import re
import csv
import requests
import itertools
from protmapper.resources import _process_feature


# Base URL for UniProt
uniprot_url = 'http://www.uniprot.org/uniprot'
# Get protein names, gene names and the organism
columns = ['id', 'protein%20names', 'genes', 'organism',
           'feature(CHAIN)', 'feature(PEPTIDE)']
# Only get reviewed entries and use TSV format
params = {
    'sort': 'id',
    'desc': 'no',
    'compress': 'no',
    'query': 'reviewed:yes',
    'format': 'tab',
    'columns': ','.join(columns)
}


def process_row(row):
    entry, protein_names, genes, organisms, chains, peptides = row
    # Gene names are space separated
    gene_synonyms = genes.split(' ') if genes else []
    # We use a more complex function to parse protein synonyms which appear
    # as "first synonym (second synonym) (third synonym) ...".
    protein_synonyms = parse_uniprot_synonyms(protein_names) \
        if protein_names else []
    # We remove EC codes as synonyms because they always refer to higher-level
    # enzyme categories shared across species
    protein_synonyms = [p for p in protein_synonyms
                        if not p.startswith('EC ')]
    # Organisms and their synonyms also appear in the format that protein
    # synonyms do
    organism_synonyms = parse_uniprot_synonyms(organisms)
    # ... except we need to deal with a special case in which the first
    # organism name has a strain name in parantheses after it, and make sure
    # that the strain name becomes part of the first synonym.
    if len(organism_synonyms) >= 2 and \
            organism_synonyms[1].startswith('strain'):
        organism_synonyms[0] = '%s (%s)' % (organism_synonyms[0],
                                            organism_synonyms[1])
        organism_synonyms = [organism_synonyms[0]] + organism_synonyms[2:]
    # We now take each gene synonym and each organism synonym and create all
    # combinations of these as entries.
    entries = []
    for gene, organism in itertools.product(gene_synonyms + protein_synonyms,
                                            organism_synonyms):
        # We skip synonyms that are more than 5 words in length (consistent
        # with original KB construction).
        if len(gene.split(' ')) > 5:
            continue
        entries.append((gene, entry, organism))

    chains = _process_feature('CHAIN', chains)
    peptides = _process_feature('PEPTIDE', peptides)
    for feature in chains + peptides:
        # Skip fragments with no name or the same name as an entry name/synonym
        if not feature.name or feature.name in {entry[0] for entry in entries}:
            continue
        # We skip synonyms that are more than 5 words in length (consistent
        # with original KB construction).
        if len(feature.name.split(' ')) > 5:
            continue
        feature_entry = '%s#%s' % (entry, feature.id)
        for organism in organism_synonyms:
            entries.append((feature.name, feature_entry, organism))

    return entries


def parse_uniprot_synonyms(synonyms_str):
    synonyms_str = re.sub(r'\[Includes: ([^]])+\]',
                          '', synonyms_str).strip()
    synonyms_str = re.sub(r'\[Cleaved into: ([^]])+\]',
                          '', synonyms_str).strip()

    def find_block_from_right(s):
        parentheses_depth = 0
        assert s.endswith(')')
        s = s[:-1]
        block = ''
        for c in s[::-1]:
            if c == ')':
                parentheses_depth += 1
            elif c == '(':
                if parentheses_depth > 0:
                    parentheses_depth -= 1
                else:
                    return block
            block = c + block
        return block

    syns = []
    while True:
        if not synonyms_str:
            return syns
        if not synonyms_str.endswith(')'):
            return [synonyms_str] + syns

        syn = find_block_from_right(synonyms_str)
        syns = [syn] + syns
        synonyms_str = synonyms_str[:-len(syn)-3]


if __name__ == '__main__':
    # Basic positioning of folders
    here = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(here, os.pardir, 'src', 'main', 'resources', 'org',
                          'clulab', 'reach', 'kb')
    resource_fname = os.path.join(kb_dir, 'uniprot-proteins.tsv')

    # Download the custom UniProt resource file
    res = requests.get(uniprot_url, params=params)
    res.raise_for_status()
    with open('uniprot_entries.tsv', 'w') as fh:
        fh.write(res.text)
    # Process the resource file into appropriate entries
    processed_entries = []
    with open('uniprot_entries.tsv', 'r') as fh:
        reader = csv.reader(fh, delimiter='\t')
        next(reader)
        for row in reader:
            processed_entries += process_row(row)
    # We sort the entries first by the synonym but in a way that special
    # characters and capitalization is ignored, then sort by ID and then
    # by organism.
    processed_entries = sorted(processed_entries,
                               key=lambda x: (re.sub('[^A-Za-z0-9]', '',
                                                     x[0]).lower(), x[1],
                                                     x[2]))
    # Now dump the entries into an updated TSV file
    with open(resource_fname, 'w') as fh:
        writer = csv.writer(fh, delimiter='\t')
        for entry in processed_entries:
            writer.writerow(entry)
