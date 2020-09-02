# bioresources
Data resources from the biomedical domain

## Information for developers
The script [`ner_kb.sh`](ner_kb.sh) converts the KBs in `org.clulab.reach.kb` into the format expected by the BioNLPProcessor NER. Please re-run this script everytime a KB in the set above changes, or when the tokenization algorithm changes in BioNLPProcessor. 

If only a small number of KBs were modified, edit the [`ner_kb.config`](ner_kb.config) file and keep only the modified KBs to avoid re-generating *all* KBs.

To test changes in bioresourse in reach locally, run the following commands before starting reach:

```bash
cd bioresources; sbt publishLocal
cd reach; vi processors/build.sbt
```

Within build.sbt, change the bioresources version to the one published. It should look something like x.x.x-SNAPSHOT.