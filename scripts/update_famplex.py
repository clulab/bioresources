import os
import requests

# NOTE: this URL should be updated once the reach_export branch is merged
base_url = ('https://raw.githubusercontent.com/bgyori/famplex/reach_export/'
            'export/')
famplex_groundings = 'famplex_groundings.tsv'
famplex_overrides = 'famplex_groundings_override.tsv'


if __name__ == '__main__':
    # Basic positioning of folders
    here = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(here, os.pardir, 'src', 'main', 'resources', 'org',
                          'clulab', 'reach', 'kb')
    groundings_fname = os.path.join(kb_dir, 'hgnc.tsv')

    # Download and write to groundings file
    with open(groundings_fname, 'w') as fh:
        fh.write(requests.get(base_url + famplex_groundings).text)

