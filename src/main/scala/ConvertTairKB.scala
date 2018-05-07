import java.io.{FileWriter, PrintWriter}

object ConvertTairKB {
  def main(args: Array[String]): Unit = {
    val tairLociFile = args(0)
    val goFile = args(1)

    val pw = new PrintWriter(new FileWriter("NER-Grounding-Override.tsv"))
    convertLociFile(pw, tairLociFile)
    convertGoFile(pw, goFile)
    pw.close()
  }

  def convertLociFile(pw: PrintWriter, fn: String): Unit = {
    println(s"Using loci file: $fn")
    var lineCount = 0
    var entCount = 0
    for(line <- io.Source.fromFile(fn).getLines()) {
      val tokens = line.trim.split("\\t+")
      if(tokens.length != 3)
        throw new RuntimeException(s"ERROR: invalid line: $line")
      lineCount += 1
      val name = tokens(0)
      val id = tokens(1)

      pw.println(s"""$name\ttair:$id\t\ttair\tLocus""")
      pw.println(s"""$id\ttair:$id\t\ttair\tLocus""")
      entCount += 2
    }

    println(s"Read $lineCount lines and created $entCount entities from the loci file.")
  }

  def convertGoFile(pw: PrintWriter, fn: String): Unit = {
    println(s"Using GO file: $fn")
    var lineCount = 0
    var entCount = 0
    for(line <- io.Source.fromFile(fn).getLines()) {
      val tokens = line.trim.split("\\t+")
      if(tokens.length != 3)
        throw new RuntimeException(s"ERROR: invalid line: $line")
      lineCount += 1
      val name = tokens(0)
      val id = tokens(1)
      val label = tokens(2)

      pw.println(s"""$name\t$id\t\tgo\t$label""")
      entCount += 1
    }

    println(s"Read $lineCount lines and created $entCount entities from the GO file.")

  }
}
