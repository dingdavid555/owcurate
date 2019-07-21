
# Is it necessary to create png files or can they be loaded into pdf directly?
# datetime variable: can it replace the date column?
# convert raw.data to some standard format? how do we accomaodate multiple file types (edf)
# front facing functino 

basename.diff <- function(indir, outdir){
  
  # FUNCTION DESCRIPTION
  # This function finds files that exist in indir and without a corresponding file basename in outdir.

  # ARGUMENTS
  # indir: pathway to folder containing input files
  # outdir: pathway to folder containing output files

  # Creates vector of files in indir
  infiles <- list.files(indir, full.names = TRUE)
  infiles <- infiles[file_test("-f", infiles)]
  
  # Creates vector of files in outdir
  outfiles <- list.files(outdir, full.names = TRUE)
  outfiles <- outfiles[file_test("-f", outfiles)]

  # remove path and file extension to compare file base names
  inbase <- tools::file_path_sans_ext(basename(infiles))
  outbase <- tools::file_path_sans_ext(basename(outfiles))

  # returns file base names that are not in outfiles
  infiles[which(!(inbase %in% outbase))]
  
}


pdfplot <- function(file, pdfdir, downsample, window.len) {

  # start timer
  t0 <- Sys.time()

  # if file is a folder, replace with a list of files that have not
  # already been processed.
  if (file_test("-d", file)) { file <- basename.diff(file, pdfdir) }

  # plot each file as a pdf
  for (f in file) { pdfplot_ga(f, pdfdir, downsample, window.len) }

  # End timer
  t1 <- Sys.time()
  
  processing.time <- difftime(time1=t1, time2=t0, units="auto")
  cat(sprintf("Total processing time was %s seconds.", round(as.numeric(processing.time, units="secs")), 1))

}

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------- PLOTTING DATA, CREATE PDF --------------------------------------------
# ---------------------------------------------------------------------------------------------------------------



pdfplot_ga <- function(file, pdfdir, downsample, window.len){
  
  # FUNCTION DESCRIPTION
  # Plots data from a single GENEActiv .bin file as a pdf.
  # Windows the data into window.len number of hours
  # Creates a .png file with 4 plots for x, y, z accelerometer axes and temperature
  # Creates a .pdf containing all the .png files
  # Deletes .png files after .pdf is created

  # ARGUMENTS
  # file: GENEActiv .bin file
  # pdfdir: output directory for pdf file
  # downsample: type of downsampling (see GENEAread:read.bin)
  # window.len: integer, number of hours a window should be

  # start timer
  t0 <- Sys.time()

  cat("===============================================================================")
  cat("===============================================================================")
  cat(" ")
  cat(sprintf("Importing %s.", file))

  
  # Reads in raw binary file
  # Downsamples by downsample.ratio
  raw.data <- owfiler::read_ga_bin(binfile=file, verbose=TRUE, do.temp=TRUE, downsample=downsample)
  
  # Formats timestamps from unix time
  datetime <- as.POSIXct(raw.data$data.out[ , 1], origin="1970-01-01")

  file.base <- tools::file_path_sans_ext(basename(file))
  # Data contained in each column: not used
  # timestamps <- raw.data$data.out[ ,1]
  # accel_x <- raw.data$data.out[ , 2]
  # accel_y <- raw.data$data.out[ , 3]
  # accel_z <- raw.data$data.out[ , 4]
  # lux <- raw.$data.out[ , 5]
  # button <- raw.data$data.out[ , 6]
  # temp_data <- raw.data$data.out[ , 7]

  # ----------------------------------------------- PNG FILE PREP ----------------------------------------------

  cat(sprintf("Creating PNGs with window size of %s hours", window.len))
  
  # Converts window.size from hours to number of data points
  window.length.index <- window.len * 60 * 60 * raw.data$freq
  
  # Creates a sequence to index plots by window.length
  window.sequence <- seq(from=1, to=length(raw.data$data.out[,2]), by=window.length.index)
  
  # Window number counter. Displayed as plot title
  window.num <- 0
  
  # Creates empty object for png files
  png.files <- c()
  
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
    dir.create(sprintf("%s/Temp_Folder", pdfdir))
    
    # Opens new PNG file for each graph
    png.file <- sprintf("%s/Temp_Folder/%s_%s.png", pdfdir, file.base, window.num)
    
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
  cat(sprintf("Created %s PNG files.", window.num))
  
  # ------------------------------------------- PDF CREATION ----------------------------------------------------
  
  # Creates a .PDF 
  pdf(sprintf("%s/%s.pdf", pdfdir, file.base))
  
  # Adds header information as first 2 pages in .PDF
  gridExtra::grid.table(d=as.matrix(raw.data$header[1:23]))
  grid::grid.newpage()
  gridExtra::grid.table(d=as.matrix(raw.data$header[24:45]))
  grid::grid.newpage()
  #dev.off()
  
  # Sets length for loop based on number of created .PNG files
  n <- length(png.files)
  
  # Loads PNG files sequentially
  for (i in 1:n){
    
    # Loads PNG files
    png.file <- png.files[i]
    pngRaster <- png::readPNG(png.file)
    
    # Image formatting
    grid::grid.raster(pngRaster, width=grid::unit(0.8, "npc"), height=grid::unit(0.75, "npc"))
    
    # Calls new plot while loop continues
    if (i < n) plot.new()
    
  }
  
  # Closes PDF
  dev.off()
  
  cat(sprintf("Created PDF file as %s.pdf.", file.base))
  
  # Deletes the PNG files
  unlink(png.files)

  # Deletes temporary folder that was created to store .PNG files
  unlink(x=sprintf("%s/Temp_Folder", pdfdir), recursive=TRUE)

  # Ends timer
  t1 <- Sys.time()
  
  processing.time <- difftime(time1=t1, time2=t0, units="auto")
  cat(sprintf("File processing time was %s seconds.", round(as.numeric(processing.time, units="secs")), 1))
  cat(" ")

  
}


