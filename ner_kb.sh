#!/bin/sh

#
# Converts the Reach KBs into the format expected by BioNLPProcessor
# Re-run this script whenever a Reach KB changes
# To avoid rugenerating *all* KBs edit the ner_kb.config file and keep only the modified KBs
#

cd ../processors

# generete the NER KBs here
sbt 'run-main org.clulab.processors.bionlp.ner.KBGenerator ../bioresources/ner_kb.config ../bioresources/src/main/resources/org/clulab/reach/kb/ ../bioresources/src/main/resources/org/clulab/reach/kb/ner'

# generate the serialized LexiconNER model now
sbt 'run-main org.clulab.processors.bionlp.ner.KBLoader ../bioresources/src/main/resources/org/clulab/reach/kb/ner/model.ser.gz'

cd ../bioresources


