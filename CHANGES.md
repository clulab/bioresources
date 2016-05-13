#Changes
=======
+ **1.1.7** - Replace local cell type KB with Cell Ontology KB.
+ **1.1.6** - Activate Uniprot Tissue type KB, ordered before Organs. Order Proteins before Protein Families.
+ **1.1.5** - Replace ChEBI and HMDB with PubChem subset.
+ **1.1.4** - Added PFAM protein family KB, prioritize/use in NER.
+ **1.1.3** - Added 3 new cancer terms to bio process KB. The Cell_Lines KB was renamed to CellLine.
+ **1.1.2** - Added plural forms for the celullar location KB. Removed some entries (Mum) from the Species KB, because they were introducing too many false positives.
+ **1.1.1** - Reduced species KB to most common species names. Removed tissue-type KB from the NER.
+ **1.1.0** - Added KBs in the format expected by the BioNLPProcessor NER.
+ **1.0.0** - Initial release. Copied KB resources from Reach 1.2.3-SNAPSHOT. These are used both by reach and processors (for BioNLPProcessor).
