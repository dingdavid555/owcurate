#Allan Liang 
#This app plots the accelerometer (in 3 dimensions) and temperature data in given hour intervals from an input GeneActiv file 
#The first plot controls the rest of the graphs by allowing you to zoom in and drag around the highlighted box, double click the first graph to exit the zoom
#Toggle between graphs by clicking next graph

vis_ga <- function() {

  # get app directory for ga-vis shiny app
  app_dir <- system.file("vis-ga", package = "owcurate")

  # run ga-vis shiny app
  shiny::runApp(app_dir, display.mode = "normal")
	
}

