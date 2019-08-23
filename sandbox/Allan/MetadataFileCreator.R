# Install and load packages
# install.packages("GENEAread")
library(GENEAread)

# Allan's function to check for file names in for the ReMiNDD study - change the constants and some of the header variables 
# when checking for file names for another study

# fileNameChecker
fileNameChecker_GA_ReMiNDD <- function(){
  # Preallocate vectors without bottlenecking from repeated calls of the dataframe
  # Create empty variables (must be global because they are filled in by another function)
  studyCodePF <<- character()
  sitePF <<- character()
  visitPF <<- character()
  sessionPF <<- character()
  platformPF <<- character()
  devicePF <<- character()
  IDPF <<- character()
  deviceLocationPF <<- character()
  frequencyPF <<- character()
  startDatePF <<- character()
  endDatePF <<- character()
  deviceIDPF <<- character()
  NumberOfChannelsPF <<- character()
  fileSizePF <<- character()
  ECGSampleRate <- "N/A" # Not applicable because GeneActiv's don't measure ECG data
  synchronizationPF <<- character()
  clippedDataPF <<- character()
  
  # Constants used for checking GeneActiv files for the ReMiNDD study
  # studyCode <<- "OND06"
  # site <<- "SBH"
  visit <<- 1
  session <<- "SE01"
  platform <<- "GABL"
  device <<- "GA"
  frequencyVar <<- "75 Hz"
  
  # File directory to store metadata files
  saveDirectory <- "//files/students$/a33liang/Desktop/GeneActivReadTest/Metadata"
  
  
  # Start period - compare it to information from Redcap
  # Input Redcap data
  setwd("N:/OBI/ONDRI@Home/ReMiNDD/Data curation/Sample REDCap tables")
  redcapData <<- read.csv("OND06_Sensor_Info_Baseline_DATA_2019-08-19_1146.csv")
  
  #Choose the directory location containing the files you want to check for and set it as the working directory
  directory <- choose.dir()
  setwd(directory)
  inputFiles <- list.files(directory)
  files <<- character()
  
  # Check if the folder of GeneActiv accelerometer files have filled columns in the eCRF tables
  # This inputs all the GeneActiv files with data in eCRF that can be compared into a new list to be compared to and checked with
  for(a in 1:length(inputFiles)){
    for(b in 1:length(redcapData$subject_id)){
      if(substring(inputFiles[a], 1, 14) == redcapData$subject_id[b] && redcapData$snsr_base_date[b] != "" && is.na(redcapData$snsr_base_l_wrist[b]) != TRUE){
        files <<- append(files, inputFiles[a])
      }
    }
  }
  
  #Loop for the amount of times there are GeneActiv files in the directory chosen
  for(i in 1:length(files)){
    header <<- readGENEActivHeader(files[i])
    binFile <<- read.bin(files[i])
    GAFileNameExtractor(files[i])
  }
  
  # Creating a dataframe
  setwd("//files/students$/a33liang/Desktop/GeneActivReadTest/ReMiNDD")
  metaDataFrame <<- data.frame(studyCode = studyCodePF, site = sitePF, visit = visitPF,
                               session = sessionPF, platform = platformPF, device = devicePF,
                               ID = IDPF, deviceLocation = deviceLocationPF, frequency = frequencyPF,
                               startDate = startDatePF, endDate = endDatePF, 
                               deviceID = deviceIDPF, ECGSampleRate, synchronization = synchronizationPF, 
                               clipping = clippedDataPF, NumberOfChannels = NumberOfChannelsPF, fileSize = fileSizePF,
                               stringsAsFactors = FALSE)
  
  # Output the dataframe - the file name of the data frame is the total amount of files in the save directory + one, to avoid overwriting files
  setwd(saveDirectory)
  write.csv(metaDataFrame, file = paste(saveDirectory, "/metadataTest", (length(list.files(saveDirectory)) + 1),".csv", sep = ""), row.names = FALSE)
}

#Kit's header script

#readGeneactivHeader
readGENEActivHeader <- function(file_path = file.choose()) {
  
  #input: path to GENEActiv .bin file
  #
  #reads header as lines of text and parses into list of keys and values
  #
  #output: list of keys and corresponding values from header 
  #
  #
  
  #open connection to GENEActiv bin file
  con <- file(file_path, "r")
  
  #read header lines from file
  header_packet <- readLines(con, n = 59)
  
  #close file connection
  close(con)
  
  #parse header_packet, read in as lines of text, into a list of keys and values
  
  #find colon separating each key and value
  colon <- regexpr(":",header_packet)
  
  #get keys and values
  keys <- substring(header_packet,1,colon-1)
  values <- trimws(substring(header_packet,colon+1,nchar(header_packet)), which = "right")
  
  #create list of keys and values (after removing blanks)
  header <- setNames(as.list(values[nchar(keys) > 0]), keys[nchar(keys) > 0])
}

#Allan's function to extract the proper naming from the file name, compare them with the constants
#used for the study and to the file header - print and report out whether the names are valid 
#or invalid and where they are valid or invalid
#Input is .bin file from the file directory chosen (not in AccData format which is the output from read.bin)

#GeneActivFileNameExctractor
GAFileNameExtractor <- function(x){
  
  #Check if the filename is the most bottom level directory and remove all top level directories
  #from the file name
  index <- nchar(x)
  for(i in index:1){
    if(substring(x, i, i) == "/"){
      print(substring(x, (i+1)))
      fileNameVar <- substring(x, (i+1))
      break
    }
    if(i == 1 && substring(x, i, i) != "/"){
      fileNameVar <- x
    }
  }
  
  #Counter variables
  index <- nchar(fileNameVar)
  counter <- 1
  i <- 1
  
  #Check the file name and extract components after the underscore
  while(i <= index){
    if(substring(fileNameVar, i, i) == "_"){
      switch(
        counter,
        if(substring(fileNameVar, 1, (i - 1)) == substring(redcapData$subject_id[i], 1, 5)){
          print("Study code ONDO6")
          studyCodePF <<- append(studyCodePF, "Pass")
          counter <- counter + 1
          fileNameVar <- substring(fileNameVar, (i + 1))
          i <- 1
          index <- nchar(fileNameVar)
        }
        else{
          print(substring(fileNameVar, 1, (i - 1)))
          print("Study code IS NOT ONDO6")
          studyCodePF <<- append(studyCodePF, "Fail")
          #break
        },
        if(substring(fileNameVar, 1, (i - 1)) == substring(redcapData$subject_id[i], 7, 9)){
          print ("Site is Sunnybrook Hospital")
          sitePF <<- append(sitePF, "Pass")
          counter <- counter + 1
          fileNameVar <- substring(fileNameVar, (i + 1))
          i <- 1
          index <- nchar(fileNameVar)
        }
        else{
          print(substring(fileNameVar, 1, (i - 1)))
          print("Site is not Sunnybrook Hospital")
          sitePF <<- append(sitePF, "Fail")
          #break
        },
        if (class(strtoi(substring(fileNameVar, 1, (i - 1)))) == "integer"){
          print("ID is valid")
          counter <- counter + 1
          i <- 1
        }
        else{
          print(substring(fileNameVar, 1, (i - 1)))
          print("ID is invalid")
          #break
        },
        
        
        # # Save the ID in the file name as a variable to compare with the ECRF data from Redcap
        # IDvar <- strtoi(substring(fileNameVar, 1, (i - 1))),
        
        if (substring(fileNameVar, 1, (i - 1)) == header$`Subject Code`){
          print("ID matches the file header")
          IDPF <<- append(IDPF, "Pass")
          counter <- counter + 1
          fileNameVar <- substring(fileNameVar, (i + 1))
          i <- 1
          index <- nchar(fileNameVar)
        }
        else{
          print("ID doesn't match the file header")
          IDPF <<- append(IDPF, "Fail")
          #break
        },
        if(strtoi(substring(fileNameVar, 1, (i - 1))) == visit){
          print("Visit number is valid")
          visitPF <<- append(visitPF, "Pass")
          counter <- counter + 1
          fileNameVar <- substring(fileNameVar, (i + 1))
          i <- 1
          index <- nchar(fileNameVar)
        }
        else{
          print(substring(fileNameVar, 1, (i - 1)))
          print("Visit number is invalid")
          visitPF <<- append(visitPF, "Fail")
          #break
        },
        if(substring(fileNameVar, 1, (i - 1)) == session){
          print ("Session is SE01")
          sessionPF <<- append(sessionPF, "Pass")
          counter <- counter + 1
          fileNameVar <- substring(fileNameVar, (i + 1))
          i <- 1
          index <- nchar(fileNameVar)
        }
        else{
          print(substring(fileNameVar, 1, (i - 1)))
          print("Session invalid")
          sessionPF <<- append(sessionPF, "Fail")
          #break
        },
        if(substring(fileNameVar, 1, (i - 1)) == platform){
          print ("Platform is GABL")
          platformPF <<- append(platformPF, "Pass")
          counter <- counter + 1
          fileNameVar <- substring(fileNameVar, (i + 1))
          i <- 1
          index <- nchar(fileNameVar)
        }
        else{
          print(substring(fileNameVar, 1, (i - 1)))
          print("Platform invalid")
          platformPF <<- append(platformPF, "Fail")
          #break
        },
        if(substring(fileNameVar, 1, (i - 1)) == device){
          print("Device is GeneActiv")
          devicePF <<- append(devicePF, "Pass")
          counter <- counter + 1
          i <- 1
          index <- nchar(fileNameVar)
          #print(fileNameVar)
        }
        else{
          print(substring(fileNameVar, 1, (i - 1)))
          print("Device is invalid")
          devicePF <<- append(devicePF, "Fail")
          #break
        },
        if((substring(fileNameVar, (i + 1), (i + 2)) == "LW") && (header$`Device Location Code` == "left wrist")){
          print("Body location is the left wrist and matches file header")
          deviceLocationPF <<- append(deviceLocationPF, "Pass")
        }
        else if((substring(fileNameVar, (i + 1), (i + 2)) == "LA") && (header$`Device Location Code` == "left ankle")){
          print("Body location is the left ankle and matches file header")
          deviceLocationPF <<- append(deviceLocationPF, "Pass")
        }
        else if((substring(fileNameVar, (i + 1), (i + 2)) == "RW") && (header$`Device Location Code` == "right wrist")){
          print("Body location is the right wrist and matches file header")
          deviceLocationPF <<- append(deviceLocationPF, "Pass")
        }
        else if((substring(fileNameVar, (i + 1), (i + 2)) == "RA") && (header$`Device Location Code` == "right ankle")){
          print("Body location is the right ankle and matches file header")
          deviceLocationPF <<- append(deviceLocationPF, "Pass")
        }
        else{
          print(paste("body location ", substring(fileNameVar, (i + 1), (i + 2)), " is invalid and doesn't match ", header$`Device Location Code`))
          deviceLocationPF <<- append(deviceLocationPF, "Fail")
        }
      )
    }
    #Iterate the while loop
    i = i + 1
  }
  
  
  # measurement frequency
  if (header$`Measurement Frequency` == frequencyVar){
    print("The measurement frequency is 75 Hz (Pass)")
    frequencyPF <<- append(frequencyPF, "Pass")
  }
  
  
  redcapIndex <<- NULL
  # for loop to search for the index in in the redcapData
  for(i in 1:(nrow(redcapData))){
    if(as.integer(substring(redcapData$subject_id[i], 11, 14)) == as.integer(header$`Subject Code`)){
      redcapIndex <<- i
    }
  }
  
  if(is.null(redcapIndex) == TRUE){
    print("Start date is invalid")
    startDatePF <<- append(startDatePF, "Fail")
  }
  
  if(is.null(redcapIndex) == FALSE){
    # Compare the start/base date between the file header and redcap base date
    if(redcapData$snsr_base_date[redcapIndex] == substring(header$`Start Time`, 1, 10)){
      print("Start date is valid")
      startDatePF <<- append(startDatePF, "Pass")
    }
    if(redcapData$snsr_base_date[redcapIndex] != substring(header$`Start Time`, 1, 10)){
      print("Start date is invalid")
      startDatePF <<- append(startDatePF, "Fail")
    }
    
    # Check for device ID by identifying device location
    if(header$`Device Location Code` == "left wrist"){
      if(redcapData$snsr_base_l_wrist[redcapIndex] == as.integer(header$`Device Unique Serial Code`)){
        print("Device serial code is valid")
        deviceIDPF <<- append(deviceIDPF, "Pass")
      }
      else{
        print("Device serial code is invalid")
        deviceIDPF <<- append(deviceIDPF, "Fail")
      }
    }
    
    if(header$`Device Location Code` == "right wrist"){
      if(redcapData$snsr_base_r_wrist[redcapIndex] == as.integer(header$`Device Unique Serial Code`)){
        print("Device serial code is valid")
        deviceIDPF <<- append(deviceIDPF, "Pass")
      }
      else{
        print("Device serial code is invalid")
        deviceIDPF <<- append(deviceIDPF, "Fail")
      }
    }
    
    if(header$`Device Location Code` == "left ankle"){
      if(redcapData$snsr_base_l_ankle[redcapIndex] == as.integer(header$`Device Unique Serial Code`)){
        print("Device serial code is valid")
        deviceIDPF <<- append(deviceIDPF, "Pass")
      }
      else{
        print("Device serial code is invalid")
        deviceIDPF <<- append(deviceIDPF, "Fail")
      }
    }
    
    if(header$`Device Location Code` == "right ankle" && redcapData$snsr_base_r_ankle[redcapIndex] == as.integer(header$`Device Unique Serial Code`)){
      print("Device serial code is valid")
      deviceIDPF <<- append(deviceIDPF, "Pass")
    }
    
    if(header$`Device Location Code` == "right ankle" && redcapData$snsr_base_r_ankle[redcapIndex] != as.integer(header$`Device Unique Serial Code`)){
      print("Device serial code is invalid")
      deviceIDPF <<- append(deviceIDPF, "Fail")
    }
    
    # Check if synchronization time recorded on Redcap data is inbetween the header start time and calculated end time
    # which is calculated by (start time plus hours recorded)
    if (as.Date(redcapData$snsr_base_sync_time[redcapIndex]) >= as.Date(header$`Start Time`) && as.Date(redcapData$snsr_base_sync_time[redcapIndex]) <= 
        as.Date(header$`Start Time`) + (floor((as.integer(substring(header$`Start Time`, 12, 13)) + as.integer(substring(header$`Measurement Period`, 1, 3))) / 24) - 1)){
      print("Synchronization time is between header start time and end time")
      synchronizationPF <<- append(synchronizationPF, "Pass")
    }
    
    if (as.Date(redcapData$snsr_base_sync_time[redcapIndex]) < as.Date(header$`Start Time`) || as.Date(redcapData$snsr_base_sync_time[redcapIndex]) > 
        as.Date(header$`Start Time`) + (floor((as.integer(substring(header$`Start Time`, 12, 13)) + as.integer(substring(header$`Measurement Period`, 1, 3))) / 24) - 1)){
      print("Synchronization time it NOT between header start time and end time")
      synchronizationPF <<- append(synchronizationPF, "Fail")
    }
  }
  
  ########################################## DON'T NEED ########################################## DON'T NEED ##########################################
  # redcapIndex2 <<- NULL
  # for(j in 1:(nrow(redcapData2))){
  #   if(as.integer(substring(redcapData2$subject_id[j], 11, 14)) == as.integer(header$`Subject Code`)){
  #     redcapIndex2 <<- j
  #   }
  # }
  # 
  # if(is.null(redcapIndex2) == TRUE){
  #   print("End date is invalid")
  #   endDatePF <<- append(endDatePF, "Fail")
  # }
  # 
  # if(is.null(redcapIndex2) == FALSE){
  #   # j is the row / index for the csv import object 
  #   # Compare the end time of collection from the file header to the redcap discharge date
  #   # end time of collection from the header file is calculated by adding the start time of collection to the amount of hours 
  #   # of the collection (rounded down to nearest hour)
  #   if(as.Date(header$`Start Time`) + (floor((as.integer(substring(header$`Start Time`, 12, 13)) + 
  #                                             as.integer(substring(header$`Measurement Period`, 1, 3))) / 24) - 1) == as.Date(redcapData2$snsr_dschrg_date[redcapIndex2])){
  #     print("End date is valid")
  #     endDatePF <<- append(endDatePF, "Pass")
  #   } 
  #   else{
  #     print("End date is invalid")
  #     endDatePF <<- append(endDatePF, "Fail")
  #   }
  # }
  
  # Duration check for the collection - see if measurement period from the header is >= 7 days (in hours)
  if(header$`Measurement Period` >= 168){
    endDatePF <<- append(endDatePF, "Pass")
  }
  
  if(header$`Measurement Period` < 168){
    endDatePF <<- append(endDatePF, "Fail")
  }
  
  
  
  # Check for number of channels by seeing if each of the 7 channels of the GENEActiv are non empty
  for (i in 1:7){
    if(length(binFile$data.out[,i]) == 0){
      NumberOfChannelsPF <<- append(NumberOfChannelsPF, "Fail")
      break
    }
    if(i == 7 && length(binFile$data.out[,i]) != 0){
      NumberOfChannelsPF <<- append(NumberOfChannelsPF, "Pass")
    }
  }
  
  # Clipping P/F check -> 15 minute windows, if any 15 minute window has 80% of the acceleration of 7.5g or higher
  # Constants and variables
  clippedData <<- NULL
  frequencyOfChannel <- 75
  windowTime <- 15
  clipped <- FALSE
  for(i in 1:(length(binFile$data.out[,1]) / (frequencyOfChannel * windowTime * 60))){
    baseIndex <- (frequencyOfChannel * 15 * (i - 1))
    for(dimension in 2:4){
      for(j in 1:(frequencyOfChannel * windowTime * 60)){
        if(binFile$data.out[(baseIndex + j), dimension] > 7.5){
          clippedData <<- append(clippedData, binFile$data.out[baseIndex + j])
        }
      }
      if(length(clippedData) >= (frequencyOfChannel * windowTime * 60 * 0.8)){
        clippedDataPF <<- append(clippedDataPF, "Fail")
        clipped <- TRUE
        break
      } 
    }
  }
  if(clipped == FALSE){
    clippedDataPF <<- append(clippedDataPF, "Pass")
  }
  
  # File size per hour = 900 pages/hour * (3,600 bytes/page + 217 bytes/page) 
  # = 3,435,300 bytes/hour
  # Compare if the real size of the file is within +/- 0.1% of the predicted file size using the predicted
  # file size constant of 3,435,300 bytes/hour
  byteHour <- 3435300
  if(file.size(x) >= as.integer(substring(header$`Measurement Period`, 1, 3)) * byteHour * 0.999 &&
     file.size(x) <= as.integer(substring(header$`Measurement Period`, 1, 3)) * byteHour * 1.001){
    fileSizePF <<- append(fileSizePF, "Pass")
  }
  
  if(file.size(x) < as.integer(substring(header$`Measurement Period`, 1, 3)) * byteHour * 0.999 ||
     file.size(x) > as.integer(substring(header$`Measurement Period`, 1, 3)) * byteHour * 1.001){
    fileSizePF <<- append(fileSizePF, "Fail")
  }
}




########################################## FUNCTIONS IN PROGRESS ##########################################




# # redcap is the i that is being iterated
# idSearch = function(redcap){
#   if(as.integer(substring(redcapData$subject_id[redcap], 11, 14)) == as.integer(header$`Subject Code`))
#   {
#     return(redcap)
#   }
# }