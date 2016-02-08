# bioresources
Data resources from the biomedical domain

## Information for developers
The script [blob/master/ner_kb.sh](`ner_kb.sh`) converts the KBs in `org.clulab.reach.kb` into the format expected by the BioNLPProcessor NER. Please re-run this script everytime a KB in the set above changes, or when the tokenization algorithm changes in BioNLPProcessor. 

If only a small number of KBs were modified, edit the [blob/master/ner_kb.config](`ner_kb.config`) file and keep only the modified KBs to avoid re-generating *all* KBs.
