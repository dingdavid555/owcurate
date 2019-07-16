library(png)
library(grid)

gridExtraExists <- require("gridExtra")
if(!gridExtraExists){
  install.packages("gridExtra")
}
library(gridExtra)

# ---------------------------------------------------------------------------------------------------------------
# ------------------------------------ CREATES VECTOR OF FILENAMES FROM FOLDER ----------------------------------
# ---------------------------------------------------------------------------------------------------------------

# FUNCTION DESCRIPTION
# Imports file names from folders containing .bin and .pdf files
# Creates object common.files for files contained in both folders

# ARGUMENTS
# data.folder: pathway to folder containing .bin files
# pdf.folder: pathway to folder containing .pdfs of previously-processed data

import.filenames <- function(data.folder, pdf.folder){
  
  # Creates vector of files in data.folder without file extension
  data.filenames <- list.files(data.folder)
  data.filenames <<- tools::file_path_sans_ext(basename(data.filenames))
  
  # Creates vector of files in pdf.folder without file extension
  pdf.filenames <- list.files(pdf.folder)
  pdf.filenames <<- tools::file_path_sans_ext(basename(pdf.filenames))
  
}


# ---------------------------------------------------------------------------------------------------------------
# --------------------------------------- READS IN RAW ACCELEROMETER DATA ---------------------------------------
# ---------------------------------------------------------------------------------------------------------------

# FUNCTION DESCRIPTION
# Function to read in .bin data with option to downsample
# Formats timestamps from unix time

# ARGUMENTS
# file: filename including .bin extension
# downsample.ratio: factor by which signal is downsampled; 1 = no downsampling

import.data <- function(file, downsample.ratio){
  
  print(sprintf("Importing %s.", file))
  print(" ")
  
  # Reads in raw binary file
  # Downsamples by downsample.ratio
  raw.data <<- owfiler::read_ga_bin(binfile=file, verbose=TRUE, do.temp=TRUE, downsample=downsample.ratio)
  
  # Formats timestamps from unix time
  datetime <<- as.POSIXct(raw.data$data.out[ , 1], origin="1970-01-01")
  
  # Data contained in each column: not used
  # timestamps <- raw.data$data.out[ ,1]
  # accel_x <- raw.data$data.out[ , 2]
  # accel_y <- raw.data$data.out[ , 3]
  # accel_z <- raw.data$data.out[ , 4]
  # lux <- raw.$data.out[ , 5]
  # button <- raw.data$data.out[ , 6]
  # temp_data <- raw.data$data.out[ , 7]
  
}

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------- PLOTTING DATA, CREATE PDF --------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

# FUNCTION DESCRIPTION
# Windows the data into window.len number of hours
# Creates a .png file with 4 plots for x, y, z accelerometer axes and temperature
# Creates a .pdf containing all the .png files
# Deletes .png files after .pdf is created

# ARGUMENTS
# window.len: integer, number of hours a window should be
# save.location: pathway to where the .pdf is saved
# file.id: filename (no extension) that is automatically passed in during loop when function is run

plot.data <- function(window.len, save.location, file.id){
  
  # ----------------------------------------------- PNG FILE PREP ----------------------------------------------
  print(" ")
  print(sprintf("Creating PNGs with window size of %s hours", window.len))
  
  # Converts window.size from hours to number of data points
  window.length.index <<- window.len * 60 * 60 * raw.data$freq
  
  # Creates a sequence to index plots by window.length
  window.sequence <<- seq(from=1, to=length(raw.data$data.out[,2]), by=window.length.index)
  
  # Window number counter. Displayed as plot title
  window.num <- 0
  
  # Creates empty object for png files
  png.files <<- c()
  
  # Creates a graph for each window in window.sequence
  for (start.index in window.sequence){
    
    # Tallies what window number is being viewed
    window.num <- window.num + 1
    
    # Sets end.index based on window.length
    end.index <- start.index + window.length.index
    
    # Changes the end.index of the last window to the last data point
    if (end.index >= length(raw.data$data.out[ , 2])){
      end.index <- length(raw.data$data.out[ , 2])
    }
    
    # Creates empty folder within save.location in which .png files are temporally created 
    dir.create(sprintf("%s/Temp_Folder", save.location))
    
    # Opens new PNG file for each graph
    png.file <- sprintf("%s/Temp_Folder/%s_%s.png", save.location, file.id, window.num)
    
    # Appends new png file to png.files object
    png.files[window.num] <- png.file
    
    # Starts creation of new png for current graph
    png(filename=png.file, width=800, height=800)
    
    # -------------------------------------------- PLOTTING ----------------------------------------------------
    
    # Sets up 2-row by 2-column graph
    # oma and mar adjust outer and inner margin sizes, respectively
    par(mfrow=c(2,2), oma = c(2, 0, 2, 0), mar=c(2,6,1,2))
    
    # Plots all 3 accelerometer axes and temperature data on separate graphs (2x2 configuration)
    # Accel ylim is set to accel range ± 1G (range is plotted with dashed lines)
    # Temp ylim set to range ± 1 found in current file
    
    # X-axis data
    plot(datetime[start.index:end.index], raw.data$data.out[start.index:end.index, 2], 
         type="l", col="purple", 
         ylim=c(-9, 9), ylab="X-axis (G)", 
         cex.axis=1.5, cex.lab=1.5)
    
    abline(h=c(-8, 8, 0), col="black", lty=2)
    
    # Y-axis data
    plot(datetime[start.index:end.index], raw.data$data.out[start.index:end.index, 3], 
         type="l", col="dodgerblue", 
         ylim=c(-9, 9), ylab="Y-axis (G)", 
         cex.axis=1.5, cex.lab=1.5)
    
    abline(h=c(-8, 8, 0), col="black", lty=2)
    
    # Z-axis data
    plot(datetime[start.index:end.index], raw.data$data.out[start.index:end.index, 4], 
         type="l", col="chartreuse4",
         ylim=c(-9, 9), ylab="Z-axis (G)", 
         cex.axis=1.5, cex.lab=1.5)
    
    abline(h=c(-8, 8, 0), col="black", lty=2)
    
    # Temperature data
    plot(datetime[start.index:end.index], raw.data$data.out[start.index:end.index, 7], 
         type="l", col="red", 
         ylim=c(min(raw.data$data.out[ , 7])-1, max(raw.data$data.out[ , 7])+1), ylab="Temperature (ºC)",  
         cex.axis=1.5, cex.lab=1.5)
    
    # Creates centered title and includes formatted start and end timestamps
    mtext(sprintf("Window #%s: %s to %s", window.num, 
                  strftime(datetime[start.index], "%a., %b %e at%l:%M %p"), 
                  strftime(datetime[end.index], "%a., %b %e at %l:%M %p")), 
          outer = TRUE, cex = 1.5)
    
    # Closes current PNG file
    dev.off()
    
  }
  
  # Prints how many PNGs were created once finished
  print(" ")
  print(sprintf("Created %s PNG files.", window.num))
  print(" ")
  
  # ------------------------------------------- PDF CREATION ----------------------------------------------------
  
  # Creates a .PDF 
  pdf(sprintf("%s/%s.pdf", save.location, file.id))
  
  # Adds header information as first 2 pages in .PDF
  grid.table(d=as.matrix(raw.data$header[1:23]))
  grid.newpage()
  grid.table(d=as.matrix(raw.data$header[24:45]))
  grid.newpage()
  #dev.off()
  
  # Sets length for loop based on number of created .PNG files
  n <- length(png.files)
  
  # Loads PNG files sequentially
  for (i in 1:n){
    
    # Loads PNG files
    png.file <- png.files[i]
    pngRaster <- readPNG(png.file)
    
    # Image formatting
    grid.raster(pngRaster, width=unit(0.8, "npc"), height=unit(0.75, "npc"))
    
    # Calls new plot while loop continues
    if (i < n) plot.new()
    
  }
  
  # Closes PDF
  dev.off()
  
  print(sprintf("Created PDF file as %s.pdf.", file.id))
  
  # Deletes the PNG files
  unlink(png.files)
  
}

# ---------------------------------------------------------------------------------------------------------------
# ----------------------------------------- RUNS FUNCTIONS ON NEW DATA FILES ------------------------------------
# ---------------------------------------------------------------------------------------------------------------

process.new.data <- function(){
  
  # Starts timer
  t0 <- Sys.time()
  
  # Checks for file names that are common to both data.folder and pdf.folder
  common.files <<- intersect(data.filenames, pdf.filenames)
  
  for (filename in data.filenames){
    
    # Functions not run on files that are found in common.files
    if (filename %in% common.files){
      print(" ")
      print(sprintf("Skipping file %s.bin since it has already been processed.", filename))
      
      # Runs functions if data has not already been processed
    } else {
      print(" ")
      import.data(file=sprintf("%s/%s.bin", bindir, filename), downsample.ratio=5)
    }
    
    plot.data(window.len=window.hours, save.location=pdfdir, file.id=filename)
    
    print("-----------------------------------------------------------------------------------------------")
    print(" ")
    
  }
  
  # Deletes temporary folder that was created to store .PNG files
  unlink(x=sprintf("%s/Temp_Folder", pdfdir), recursive=TRUE)
  
  # Ends timer
  t1 <- Sys.time()
  
  processing.time <- difftime(time1=t1, time2=t0, units="auto")
  print(sprintf("Total processing time is %s seconds.", round(as.numeric(processing.time, units="secs")), 1))
  
}

# ---------------------------------------------------------------------------------------------------------------
# -------------------------------------------- RUNS FUNCTIONS ---------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

# Window length in hours to view
window.hours = 4

# save location for .PDF output
pdfdir <- "~/Desktop/SamplePDFs"

# Location of .bin files
bindir <- "~/Desktop/SampleFiles"

import.filenames(data.folder=bindir, pdf.folder=pdfdir)

process.new.data()
