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
                                  plotOutput("zoom", 
                                             height = 400, 
                                             brush = brushOpts(id = "plot2_brush", resetOnNew = TRUE)
                                            )
                           ),
                           column(width = 12, plotOutput("xplot", height = 400))
                  )
           ),
           column(width = 4, class = "well", 
                  fluidRow(column(width = 12, plotOutput("yplot", height = 400)),
                           column(width = 12, plotOutput("zplot", height = 400))
                  )
           ),
           column(width = 4, class = "well", 
                  fluidRow(column(width = 12, plotOutput("tempPlot", height = 400)))
           )
  )
)
