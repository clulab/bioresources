import os
import re
import csv
import obonet
from indra.statements.resources import amino_acids

from collections import Counter


def get_synonyms(syns_entry):
    synonyms = []
    for synonym in syns_entry:
        match = re.match(r'^\"(.+)\" (EXACT|RELATED|NARROW|BROAD)',
                         synonym)
        syn, status = match.groups()
        if status in allowed_synonyms:
            synonyms.append(syn)
    return synonyms


def length_filter(txt):
    # We filter out single-character names and names that are very long
    # and so are unlikely to be ever found in text
    return 2 <= len(txt) <= 50


def character_filter(txt):
    cnt = Counter([c for c in txt])
    special_chars = {'(', ')', '[', ']', '{', '}', ','}
    num_special_chars = sum(cnt.get(c, 0) for c in special_chars)
    return num_special_chars < 6


def ambig_aa_filter(name, txt):
    if is_aa_sequence(name) and re.match(r'(^[A-Z-]+$)', txt):
        return False
    return True


def mod_filter(txt):
    return "MOD:" not in txt


aa_abbrevs = {aa['short_name'].capitalize() for aa in amino_acids.values()}


def is_aa_sequence(txt):

    # Return True if the given text is a sequence of amino acids like Tyr-Glu.
    return ('-' in txt) and (all(part in aa_abbrevs
                                 for part in txt.split('-')))


def is_derived_from(pro_id, data):

    relationship = data.get('relationship')

    if relationship is None:
        return False

    if isinstance(relationship, list):
        relationship = relationship[0]

    return re.match(r'PR:', pro_id) and re.match(r'derives\_from PR:', relationship)


def is_cleavage_and_modification(data):

    comments = data.get('comment')
    definition = data.get('def')

    if comments is None or definition is None:
        return False

    return re.match(r'Category\=modification', comments) and ('cleavage' in definition)


def accept_entry(name, synonym, pro_id, data):

    # Sanity check filters
    if not (length_filter(synonym) and character_filter(synonym) and \
            ambig_aa_filter(name, synonym) and mod_filter(synonym)):
        return False

    # Finds guaranteed protein cleavages from relationship tag
    if is_derived_from(pro_id, data):
        return True

    # Experimental Filter for finding additional cleavages
    if is_cleavage_and_modification(data):
        return True

    return False


if __name__ == '__main__':

    # Basic positioning
    here = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(here, os.pardir, 'src', 'main', 'resources', 'org',
                          'clulab', 'reach', 'kb')
    resource_fname = os.path.join(kb_dir, 'protein-ontology-fragments.tsv')

    # Download Protein Ontology resource file
    url = 'https://proconsortium.org/download/current/pro_reasoned.obo'
    g = obonet.read_obo(url)
    allowed_synonyms = {'EXACT', 'RELATED'}
    entries = []

    for node, data in g.nodes(data=True):
        name = data['name']
        pro_id = node
        raw_synonyms = data.get('synonym', [])

        synonyms = get_synonyms(raw_synonyms)

        # Format of the output defined here
        entries += [(txt, pro_id) for txt in ([name] + synonyms)
                    if accept_entry(name, txt, pro_id, data)]

    # We sort the entries first by the synonym but in a way that special
    # characters and capitalization is ignored, then sort by ID
    entries = sorted(entries, key=(lambda x:
                                   (re.sub('[^A-Za-z0-9]', '', x[0]).lower(),
                                    x[1])))

    # Now dump the entries into an updated TSV file
    with open(resource_fname, 'w', newline='') as fh:
        writer = csv.writer(fh, delimiter="\t")
        for entry in entries:
            writer.writerow(entry)
