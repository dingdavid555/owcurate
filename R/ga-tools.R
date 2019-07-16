
read_ga_bin <- function(binfile = file.choose(), ...) {

  #read specified GENEActiv .bin file
  ga_bin <- GENEAread::read.bin(binfile = binfile, ...)

  #replace header with more complete custom header
  ga_bin$header <- read_ga_header(binfile)

  ga_bin

}

read_ga_header <- function(binfile = file.choose()) {
  
  #input: path to GENEActiv .bin file
  #
  #reads header as lines of text and parses into list of keys and values
  #
  #output: list of keys and corresponding values from header 
  #
  #
  
  #open connection to GENEActiv bin file
  con <- file(binfile, "r")
  
  #read header lines from file
  header_packet <- readLines(con, n = 59)

  #close file connection
  close(con)
  
  #parse header_packet, read in as lines of text, into a list of keys and values
  
  #find colon separating each key and value
  colon <- regexpr(":",header_packet)
  
  #get keys and values
  keys <- gsub(" ", "_", substring(header_packet,1,colon-1))
  values <- trimws(substring(header_packet,colon+1,nchar(header_packet)), which = "right")
  
  #create list of keys and values (after removing blanks) and return result
  header <- setNames(as.list(values[nchar(keys) > 0]), keys[nchar(keys) > 0])
  
}
