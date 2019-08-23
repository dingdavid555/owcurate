#Allan Liang
#This app plots the accelerometer (in 3 dimensions) and temperature data in given hour intervals from an input GeneActiv file
#The first plot controls the rest of the graphs by allowing you to zoom in and drag around the highlighted box, double click the first graph to exit the zoom
#Toggle between graphs by clicking next graph

#Install and load packages
#install.packages("ggplot2")
library("shiny")
library("ggplot2")
library("GENEAread")

#Constants that can be changed
freq <- 25.0
hourSampled <- 6.0
secToHours <- 3600.0
accelRange <- 9.0
plotLineSize = 0.07


# Load .bin GeneActiv file with a downsample of 3 on 75hz resulting in a frequency of 25hz
binFile = read.bin(file.choose(), downsample = 3)

# Define UI for application that draws a histogram
ui <- fluidPage(
    #Action buttons that toggle previous and next plot
    actionButton("PreviousPlot", "Previous Plot"),
    actionButton("NextPlot","Next Plot"),
    actionButton("ExitApp", "Exit App"),
    radioButtons("Toggle", "Pass/Fail", choices = list("Pass" = TRUE, "Fail" = FALSE), selected = TRUE),
    
    #Plot graphics
    fluidRow(
        column(width = 4, class = "well",
               #h4("Top plot controls the rest of the plots (Zoom)"),
               fluidRow(
                   column(width = 12,
                          plotOutput("zoom", height = 400,
                                     brush = brushOpts(
                                         id = "plot2_brush",
                                         resetOnNew = TRUE
                                     )
                          )
                   ),column(width = 12,
                            plotOutput("xplot", height = 400)
                   )
               )
        ),
        column(width = 4, class = "well", fluidRow(
            column(width = 12,
                   plotOutput("yplot", height = 400)
            ),
            column(width = 12,
                   plotOutput("zplot", height = 400)
            )
        )),
        column(width = 4, class = "well", fluidRow(
            column(width = 12,
                   plotOutput("tempPlot", height = 400)
            ),
            column(width = 12,
                   selectInput("timeWindow",
                               label = "Choose a time window to display",
                               choices = c(1 : ((24 * 7) / hourSampled)),
                               selected = 1))
        ))
    )
)


server <- function(input, output) {
    #ACTION BUTTON FUNCTION
    v <- reactiveValues(start = 0, end = hourSampled*secToHours)
    
    #Select timewindow with timeWindow widget will change the time window to the selected time window
    observeEvent(input$timeWindow,{
        v$start <- ((strtoi(input$timeWindow) - 1) * secToHours * hourSampled)
        v$end <- (strtoi(input$timeWindow) * secToHours * hourSampled)
    },
    ignoreInit = TRUE)
    
    #Getting the interval of the input GeneActiv file given start, end, and time format
    accelData <- reactive({
        get.intervals(binFile, start = v$start, end = v$end, time.format = "sec")
    })
    
    #Create a list of timepoints in sequence of start of time interval to end of time interval used as the x-axis for plotting all the plots
    #If plotting the first plot, requires one less data point then the rest of the plots in other intervals (because it does not plot anything when time = 0?)
    timestamps <- reactive(
        if(v$start == 0){
            seq((v$start / secToHours), (v$end / secToHours), ((v$end / secToHours) - (v$start / secToHours)) / ((hourSampled * secToHours * freq) -1))
        }
        else{
            seq((v$start / secToHours), (v$end / secToHours), ((v$end / secToHours) - (v$start / secToHours)) / (hourSampled * secToHours * freq))
        }
    )
    
    #Acceleration values in 3 dimensions from the interval given from input
    accel_x <- reactive(
        accelData()[,1]
    )
    accel_y <- reactive(
        accelData()[,2]
    )
    accel_z <- reactive(
        accelData()[,3]
    )
    
    # Temperature value extracted from the input file from given start time to end time (multiplied by frequency to get desired datapoints)
    temp <- reactive(
        #The first plot has (hours * secToHours * frequency) amount of time points
        if(v$start == 0){
            (binFile$data.out[, 7])[c((1 + (v$start * freq)):(v$end * freq))]
        }
        #All plots after the first have (hours * secToHours * frequency) + 1 amount of time points
        #The amount of time points must match in the dataframe
        else{
            (binFile$data.out[, 7])[c((v$start * freq):(v$end * freq))]
        }
    )
    
    #Create a dataframe used as input for plots
    reactiveDataFrame <- reactive(
        data.frame(timestamps(), accel_x(), accel_y(), accel_z(), temp()
        )
    )
    
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
    
    
    observeEvent(input$ExitApp, {
        #Write the dataframe into a CSV and then exit the app
        write.csv(values$df, file = "//files/students$/a33liang/Desktop/dataIntegrityCheck.csv", row.names = FALSE)
        stopApp()
    })
    
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
            ggplot(reactiveDataFrame(), aes(timestamps(), accel_x())) +
                geom_point(size = 0.1) +
                #xlim((v$start/secToHours), (v$end/secToHours)) +
                #ylim(-1 * accelRange, accelRange)
                scale_x_continuous(name = "Time (hours)") +
                scale_y_continuous(name = "X axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
        })
        
        output$xplot <- renderPlot({
            ggplot(reactiveDataFrame(), aes(timestamps(), accel_x())) +
                #geom_point(size = 0.003) +
                geom_line(size = plotLineSize) +
                coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
                scale_x_continuous(name = "Time (hours)") +
                scale_y_continuous(name = "X axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
        })
        
        output$yplot <- renderPlot({
            ggplot(reactiveDataFrame(), aes(timestamps(), accel_y())) +
                #geom_point(size = 0.003) +
                geom_line(size = plotLineSize) +
                coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
                scale_x_continuous(name = "Time (hours)") +
                scale_y_continuous(name = "Y axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
        })
        
        output$zplot <- renderPlot({
            ggplot(reactiveDataFrame(), aes(timestamps(), accel_z())) +
                #geom_point(size = 0.003) +
                geom_line(size = plotLineSize) +
                coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
                scale_x_continuous(name = "Time (hours)") +
                scale_y_continuous(name = "Z axis accelerometer (g)", breaks = c(-9:9), labels = c(-9:9), limits = c(-9, 9))
        })
        
        output$tempPlot <- renderPlot({
            ggplot(reactiveDataFrame(), aes(timestamps(), temp())) +
                #geom_point(size = 0.003) +
                geom_line(size = (plotLineSize * 3)) +
                # coord_cartesian(xlim = ranges2$x, ylim = ranges2$y, expand = FALSE) +
                scale_x_continuous(name = "Time (hours)") +
                scale_y_continuous(name = "Temperature (Celsius)")
            
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

shinyApp(ui, server)