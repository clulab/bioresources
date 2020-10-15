@ECHO OFF

REM
REM Converts the Reach KBs into a LexiconNER, serializes, and compresses it.
REM Re-run this script whenever a Reach KB changes _and_ that KB has been run
REM through new_kb.sh, locally published, and accessed as a dependent resource
REM by reach.  This generally means that bioresources needs to be published
REM locally and then reach's processors/build.sbt file changed to access the
REM local version of bioresources before this script gets run.  This is because
REM reach needs access to the KBs as resources rather than files.
REM

cd ../reach

REM generate the serialized LexiconNER model now
sbt "runMain org.clulab.processors.bionlp.ner.KBLoader ../bioresources/src/main/resources/org/clulab/reach/kb/ner/model.ser.gz"

cd ../bioresources
