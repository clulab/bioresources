import os
import re
import csv
import sys
import gzip
import tqdm
import requests
import itertools
from collections import defaultdict
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


def make_organism_mappings(taxonomy_ids):
    import obonet
    import networkx
    # Note the path can be changed here
    obo_path = '/Users/ben/Downloads/ncbitaxon.obo'
    print('Loading %s' % obo_path)
    g = obonet.read_obo(obo_path)
    # This dict maps specific taxonomy names to the name of one or more
    # parent terms that will be included as organisms for it in the resource
    # file
    mappings = defaultdict(list)
    for taxonomy_id in taxonomy_ids:
        term_name = g.nodes['NCBITaxon:%s' % taxonomy_id]['name']
        # We get all the ancestors that point to this term directly or
        # indirectly
        sub_terms = networkx.ancestors(g, 'NCBITaxon:%s' % taxonomy_id)
        # We then map the name of the sub term to the name of the parent entry
        for sub_term in sub_terms:
            sub_taxonomy_name = g.nodes[sub_term]['name']
            mappings[sub_taxonomy_name].append(term_name)
    return dict(mappings)


def get_extra_organism_synonyms(organism_synonyms, extra_organism_mappings):
    if not extra_organism_mappings:
        return []
    extra_organism_names = set()
    for syn in organism_synonyms:
        extra_organism_names |= set(extra_organism_mappings.get(syn, set()))
    return sorted(list(extra_organism_names))


def process_row(row, extra_organism_mappings=None):
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

    # Here we add any additional organism names from parent taxonomy terms as
    # defned by extra_organism_mappings
    organism_synonyms += get_extra_organism_synonyms(organism_synonyms,
                                                     extra_organism_mappings)

    # We now take each gene synonym and each organism synonym and create all
    # combinations of these as entries.
    entries = []
    for gene, organism in itertools.product(gene_synonyms + protein_synonyms,
                                            organism_synonyms):
        # We skip synonyms that are more than 5 words in length (consistent
        # with original KB construction).
        if len(gene.split(' ')) > 5:
            continue
        # We also skip single letter synonyms like M, S, etc. since they become
        # problematic in NER (pick up lots of unrelated words). These can still
        # be picked up when mentioned more explicitly, like "M protein" in text.
        if len(gene) == 1:
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
    if len(sys.argv) > 1:
        extra_organisms = sys.argv[1:]
        print('Adding extra organism mappings for: %s' % str(extra_organisms))
        extra_organism_mappings = make_organism_mappings(extra_organisms)
    else:
        extra_organism_mappings = {}
    # Basic positioning of folders
    here = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(here, os.pardir, 'src', 'main', 'resources', 'org',
                          'clulab', 'reach', 'kb')
    resource_fname = os.path.join(kb_dir, 'uniprot-proteins.tsv')

    # Download the custom UniProt resource file
    '''
    print('Downloading from %s' % uniprot_url)
    res = requests.get(uniprot_url, params=params)
    res.raise_for_status()

    print('Saving downloaded entries')
    with open('uniprot_entries.tsv', 'w') as fh:
        fh.write(res.text)
    '''
    # Process the resource file into appropriate entries
    processed_entries = []
    print('Processing downloaded entries')
    with open('uniprot_entries.tsv', 'r') as fh:
        reader = csv.reader(fh, delimiter='\t')
        next(reader)
        for row in tqdm.tqdm(reader):
            processed_entries += \
                process_row(row,
                            extra_organism_mappings=extra_organism_mappings)
    # We sort the entries first by the synonym but in a way that special
    # characters and capitalization is ignored, then sort by ID and then
    # by organism.
    processed_entries = sorted(processed_entries,
                               key=lambda x: (re.sub('[^A-Za-z0-9]', '',
                                                     x[0]).lower(), x[1],
                                                     x[2]))
    # Now dump the entries into an updated TSV file
    print('Saving processed entries')
    with open(resource_fname, 'w') as fh:
        writer = csv.writer(fh, delimiter='\t')
        for entry in processed_entries:
            writer.writerow(entry)
    # And then into a GZ file
    with open(resource_fname, 'rb') as f1, \
            gzip.open(resource_fname + '.gz', 'wb') as f2:
        f2.writelines(f1)
