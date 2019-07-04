server <- function(input, output) {
  
  # Constants that can be changed
  freq <- 25.0
  hourSampled <- 4.0
  secToHours <- 3600.0
  accelRange <- 9.0
  plotLineSize = 0.07

  # Load .bin GeneActiv file with a downsample of 3 on 75hz resulting in a frequency of 25hz
  binFile = GENEAread::read.bin(file.choose(), downsample = 3)

  # ACTION BUTTON FUNCTION
  v <- reactiveValues(start = 0, end = hourSampled*secToHours)
  
  # Getting the interval of the input GeneActiv file given start, end, and time format
  accelData <- reactive({GENEAread::get.intervals(binFile, start = v$start, end = v$end, time.format = "sec")}) 
  
  # Create a list of timepoints in sequence of start of time interval to end of time interval used as 
  # the x-axis for plotting all the plots. If plotting the first plot, requires one less data point then the 
  #mrest of the plots in other intervals (because it does not plot anything when time = 0?)
  timestamps <- reactive(
    if (v$start == 0) {
      seq((v$start / secToHours), 
          (v$end / secToHours), 
          ((v$end / secToHours) - (v$start / secToHours)) / ((hourSampled * secToHours * freq) -1))
    } else {
      seq((v$start / secToHours), 
          (v$end / secToHours), 
          ((v$end / secToHours) - (v$start / secToHours)) / (hourSampled * secToHours * freq))
    }
  ) 
  
  #Acceleration values in 3 dimensions from the interval given from input
  accel_x <- reactive(accelData()[,1]) 
  accel_y <- reactive(accelData()[,2]) 
  accel_z <- reactive(accelData()[,3]) 
  
  # Temperature value extracted from the input file from given start time to end time 
  # (multiplied by frequency to get desired datapoints)
  temp <- reactive(
    # The first plot has (hours * secToHours * frequency) amount of time points.
    # All plots after the first have (hours * secToHours * frequency) + 1 amount of time points
    # The amount of time points must match in the dataframe
    if (v$start == 0) {
      (binFile$data.out[, 7])[c((1 + (v$start * freq)):(v$end * freq))]
    } else {
      (binFile$data.out[, 7])[c((v$start * freq):(v$end * freq))]
    }
  )
  
  #Create a dataframe used as input for plots
  reactiveDataFrame <- reactive(data.frame(timestamps(), accel_x(), accel_y(), accel_z(), temp()))
  
  #Create the dataframe used to track the start and end time of plots with pass/fail for each plot
  values <- reactiveValues()
  values$df <- data.frame(timeStart = integer(), timeEnd = integer(), plotpf = logical(), stringsAsFactors = FALSE)
  
  
  #Setting up the variable that changes when previous or next plot is toggled - increases or decreases the variables by x hours
  #Gets interval from the next x amount of hours
  observeEvent(input$NextPlot, {
    
    #Add a row into the dataframe including start time, end time, and pass/fail
    newLine <- c(timeStart = v$start, timeEnd = v$end, plotpf = input$Toggle)
    values$df[((v$start / (hourSampled * secToHours)) + 1), ] <- newLine
    
    #TROUBLESHOOTING AND DEBUGGING
    print(values$df)
    
    v$start <- v$start + (hourSampled * secToHours)
    v$end <- v$end + (hourSampled * secToHours)
  })
  
  #Gets interval from the previous x amount of hours only if the current plot isn't the first plot
  observeEvent(input$PreviousPlot, {
    if(v$start != 0){
      #Remove the last row of the dataframe pf
      values$df <- values$df[-nrow(values$df),]
      
      #Decrease the start time and end time for the plots
      v$start <- v$start - (hourSampled * secToHours)
      v$end <- v$end - (hourSampled * secToHours)
    }
  })
  

  #Write the dataframe into a CSV and then exit the app --> I have hard coded my file directory to save in my desktop
  #write.csv(values$df, file = "//files/students$/a33liang/Desktop/dataIntegrityCheck.csv", row.names = FALSE)
   
  observeEvent(input$ExitApp, {stopApp()})
  
  # When a double-click happens, check if there's a brush on the plot.
  # If so, zoom to the brush bounds; if not, reset the zoom.
  observeEvent(input$plot1_dblclick, {
    brush <- input$plot1_brush
    if (!is.null(brush)) {
      ranges$x <- c(brush$xmin, brush$xmax)
      ranges$y <- c(brush$ymin, brush$ymax)    
    } else {
      ranges$x <- NULL
      ranges$y <- NULL
    }
  })
  
  # -------------------------------------------------------------------
  # Linked plots (acceleration (x, y, z) and temperature)
  ranges2 <- reactiveValues(x = NULL, y = NULL)
  
  observe({
    output$zoom <- renderPlot({
      ggplot2::ggplot(reactiveDataFrame(), ggplot2::aes(timestamps(), accel_x())) +
        ggplot2::geom_point(size = 0.1) +
        #xlim((v$start/secToHours), (v$end/secToHours)) +
        #ylim(-1 * accelRange, accelRange)
        ggplot2::scale_x_continuous(name = "Time (hours)") +
        ggplot2::scale_y_continuous(name = "X axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
    }) 
    
    output$xplot <- renderPlot({
      ggplot2::ggplot(reactiveDataFrame(), ggplot2::aes(timestamps(), accel_x())) +
        #ggplot2::geom_point(size = 0.003) + 
        ggplot2::geom_line(size = plotLineSize) +
        ggplot2::coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
        ggplot2::scale_x_continuous(name = "Time (hours)") +
        ggplot2::scale_y_continuous(name = "X axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
    }) 
    
    output$yplot <- renderPlot({
      ggplot2::ggplot(reactiveDataFrame(), ggplot2::aes(timestamps(), accel_y())) +
        #ggplot2::geom_point(size = 0.003) + 
        ggplot2::geom_line(size = plotLineSize) +
        ggplot2::coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
        ggplot2::scale_x_continuous(name = "Time (hours)") +
        ggplot2::scale_y_continuous(name = "Y axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
    }) 
    
    output$zplot <- renderPlot({
      ggplot2::ggplot(reactiveDataFrame(), ggplot2::aes(timestamps(), accel_z())) +
        #ggplot2::geom_point(size = 0.003) + 
        ggplot2::geom_line(size = plotLineSize) +
        ggplot2::coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
        ggplot2::scale_x_continuous(name = "Time (hours)") +
        ggplot2::scale_y_continuous(name = "Z axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
    }) 
    
    output$tempPlot <- renderPlot({
      ggplot2::ggplot(reactiveDataFrame(), ggplot2::aes(timestamps(), temp())) +
        #ggplot2::geom_point(size = 0.003) +
        ggplot2::geom_line(size = (plotLineSize * 3)) +
      # coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
      ggplot2::scale_x_continuous(name = "Time (hours)") +
      ggplot2::scale_y_continuous(name = "Temperature (Celsius)")
      
    })
  })
  
  
  # When a double-click happens, check if there's a brush on the plot.
  # If so, zoom to the brush bounds; if not, reset the zoom.
  observe({
    brush <- input$plot2_brush
    if (!is.null(brush)) {
      ranges2$x <- c(brush$xmin, brush$xmax)
      ranges2$y <- c(brush$ymin, brush$ymax)
      
    } else {
      ranges2$x <- NULL
      ranges2$y <- NULL
    }
  })
}
