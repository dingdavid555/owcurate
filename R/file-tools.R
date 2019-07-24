
# GENEActiv .bin ---------------------------------------------------------------------------

read_ga_bin <- function(binfile = file.choose(), ...) {

  #read specified GENEActiv .bin file
  ga_bin <- GENEAread::read.bin(binfile = binfile, ...)

  #replace header with more complete custom header
  ga_bin$header <- owcurate::read_ga_header(binfile)

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


# EDF ---------------------------------------------------------------------------------------------

# these functions are designed to read and write data files used in the collection of wearable device
# data in the ONDRI@Home program. They are designed for use within the constraints of this program and 
# may not fully comply with all data format specifications.


parse_edf_data <- function(data_packet, sig_labels, sig_record_samples, sig_phys_max, sig_phys_min, 
                           sig_dig_max, sig_dig_min) {

  # create record sample index table for each signal
  sig_record_indices <- cbind(cumsum(c(1, head(sig_record_samples, -1))), cumsum(sig_record_samples))

  # resphape data packet into a list of signals
  data <- apply(sig_record_indices, 1, function(x) c(t(data_packet[,x[1]:x[2]])))

  # calculate gains and offsets based on physical and digital mins and maxes
  gains <- (sig_phys_max - sig_phys_min) / (sig_dig_max - sig_dig_min)
  offsets <- sig_phys_max - (gains * sig_dig_max)
  gains <- as.list(gains)
  offsets <- as.list(offsets)

  # convert from digital to physical
  data <- mapply('*', data, gains)
  data <- mapply('+', data, offsets)

  names(data) <- sig_labels

  data

}

parse_edf_header <- function(header_packet) {

# NEED TO TEST THIS WITH DIFFERENT NUMBERS OF SIGNALS

  # initialize header data structure as a list
  header <- list()

  # parse and add values to the header structure keys
  header$version <- substr(header_packet, start = 1, stop = 8)
  header$patient_id <- substr(header_packet, start = 9, stop = 88)
  header$recording_id <- substr(header_packet, start = 89, stop = 168)
  header$start_date <- substr(header_packet, start = 169, stop = 176)
  header$start_time <- substr(header_packet, start = 177, stop = 184)
  header$num_bytes <- substr(header_packet, start = 185, stop = 192)
  header$reserved <- substr(header_packet, start = 193, stop = 236)
  header$num_records <- substr(header_packet, start = 237, stop = 244)
  header$dur_record <- substr(header_packet, start = 245, stop = 252)
  header$num_signals <- substr(header_packet, start = 253, stop = 256)

  # parse number of signals from header
  ns <- as.numeric(header$num_signals)

  # parse and add signal header values as vector containing a value for each signal
  header$sig_labels <- substring(header_packet, 
                                 first = seq(257, 256 + (ns * 16), 16),
                                 last = seq(272, 257 + (ns * 16), 16))
  header$sig_type <- substring(header_packet, 
                               first = seq(257 + (ns * 16), 256 + (ns * 96), 80),
                               last = seq(336 + (ns * 16), 257 + (ns * 96), 80))
  header$sig_phys_dim <- substring(header_packet, 
                                   first = seq(257 + (ns * 96), 256 + (ns * 104), 8),
                                   last = seq(264 + (ns * 96), 257 + (ns * 104), 8))
  header$sig_phys_min <- substring(header_packet, 
                                   first = seq(257 + (ns * 104), 256 + (ns * 112), 8),
                                   last = seq(264 + (ns * 104), 257 + (ns * 112), 8))
  header$sig_phys_max <- substring(header_packet, 
                                   first = seq(257 + (ns * 112), 256 + (ns * 120), 8),
                                   last = seq(264 + (ns * 112), 257 + (ns * 120), 8))
  header$sig_dig_min <- substring(header_packet, 
                                  first = seq(257 + (ns * 120), 256 + (ns * 128), 8),
                                  last = seq(264 + (ns * 120), 257 + (ns * 128), 8))
  header$sig_dig_max <- substring(header_packet, 
                                  first = seq(257 + (ns * 128), 256 + (ns * 136), 8),
                                  last = seq(264 + (ns * 128), 257 + (ns * 136), 8))
  header$sig_prefilt <- substring(header_packet, 
                                  first = seq(257 + (ns * 136), 256 + (ns * 216), 80),
                                  last = seq(336 + (ns * 136), 257 + (ns * 216), 80))
  header$sig_record_samples <- substring(header_packet, 
                                         first = seq(257 + (ns * 216), 256 + (ns * 224), 8),
                                         last = seq(264 + (ns * 216), 257 + (ns * 224), 8))
  header$sig_reserved <- substring(header_packet, 
                                   first = seq(257 + (ns * 224), 256 + (ns * 256), 32),
                                   last = seq(288 + (ns * 224), 257 + (ns * 256), 32))

  #return header
  header

}


read_edf <- function(infile = file.choose()) {

  # much code copied from edfReader::readEdfHeader

  # if file exists then open a connection, otherwise return a message
  if (file.exists(infile)) { # infile exists


    cat("Reading ", infile, "...\n", sep = "")
    
    cat("Reading header...\n", sep = "")

    # read header
    header_packet <- read_edf_header(infile)

    cat("Parsing header...\n", sep = "")

    # parse header packet into keys and values 
    header <- c(list(filename = infile), parse_edf_header(header_packet))

    cat("Reading data...\n", sep = "")

    # read data
    data_packet <- read_edf_data(infile, 
                                 num_records = as.numeric(header$num_records),
                                 num_signals = as.numeric(header$num_signals),
                                 sig_record_samples = as.numeric(header$sig_record_samples))

    cat("Parsing data...\n", sep = "")

    # parse data packet into signal data
    data <- parse_edf_data(data_packet,
                           sig_labels = trimws(header$sig_labels), 
                           sig_record_samples = as.numeric(header$sig_record_samples),
                           sig_phys_max = as.numeric(header$sig_phys_max),
                           sig_phys_min = as.numeric(header$sig_phys_min),
                           sig_dig_max = as.numeric(header$sig_dig_max),
                           sig_dig_min = as.numeric(header$sig_dig_min))

    list(header = header, data = data)

  } else { # infile doesn't exist

    cat("File '", infile, "' doesn't exists.", sep = "")

  }    

}

read_edf_data <- function(infile, num_records, num_signals, sig_record_samples) {

  # calculate number of total samples per record
  record_samples <- sum(sig_record_samples)

  # initialize data packet matrix
  data_packet <- matrix(NA, record_samples, num_records)

  # open connection to file
  con <- file(infile, "rb")

  # move pointer to start of data
  seek(con, 256 + (num_signals * 256), "start") 

  # read data records into a data packet matrix
  data_packet <- t(apply(data_packet, 2, function(x) {
                                           x <- readBin(con, integer(), n = record_samples, 
                                                        size = 2, signed = TRUE, endian = "little")
                                         }))
  
  # close file connection
  close(con)

  # return data packet
  data_packet

}

read_edf_header <- function(infile) {

  # open connection to file
  con <- file(infile, "rb")

  # read header as character vector
  header_packet <- readChar(con, 256, TRUE)

  # parse number of signals from header
  ns <- as.numeric(substr(header_packet, start = 253, stop = 256))

  # read signal headers as character vector
  header_packet <- paste0(header_packet, readChar(con, 256 * ns, TRUE))

  # close connection to file
  close(con)

  # return header_packet
  header_packet

}
