import os
import requests

# NOTE: this URL should be updated once the reach_export branch is merged
base_url = ('https://raw.githubusercontent.com/bgyori/famplex/reach_export/'
            'export/')
famplex_groundings = 'famplex_groundings.tsv'
famplex_overrides = 'famplex_grounding_overrides.tsv'


def get_real_lines(fname):
    with open(fname, 'r') as fh:
        lines = [l.strip() for l in fh.readlines() if l.strip() and
                 not l.startswith('#')]
    lines = [l.split('\t') for l in lines]
    return lines


def get_other_strings(fname):
    kb_files = [row[0] + '.tsv' for row in get_real_lines(fname)]
    strings = []
    for kb_fname in kb_files:
        # We skip famplex here to avoid redundancy
        if kb_fname == 'famplex.tsv':
            continue
        strings += [row[0] for row in
                    get_real_lines(os.path.join(kb_dir, kb_fname))]
    return set(strings)


def get_overrides(overrides_rows, other_strings, famplex_only=True):
    overrides = []
    for txt, db_id, db_ns, type in overrides_rows:
        # In famplex_only mode, skip and non-fplx groundings
        if famplex_only and db_ns != 'fplx':
            continue
        # If this is not an actual override, skip it
        if txt not in other_strings:
            continue
        overrides.append((txt, db_id, db_ns, type))
    return overrides


if __name__ == '__main__':
    # Basic positioning of folders
    here = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(here, os.pardir, 'src', 'main', 'resources', 'org',
                          'clulab', 'reach', 'kb')
    groundings_fname = os.path.join(kb_dir, 'famplex.tsv')

    # Download and write to groundings file
    with open(groundings_fname, 'w') as fh:
        fh.write(requests.get(base_url + famplex_groundings).text)

    # Now get all the "other" strings so we can figure out what to add
    # to the overrides file
    other_strings = get_other_strings(os.path.join(here, os.pardir,
                                      'ner_kb.config'))

    overrides_rows = \
        [row.split('\t') for row in
         requests.get(base_url + famplex_overrides).text.split('\n')]
    overrides = get_overrides(overrides_rows, other_strings, famplex_only=True)
