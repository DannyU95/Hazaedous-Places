import pandas as pd
# Separete file is used as a library of functions:
import functions as fun


mindate='1950-01-01'
maxdate='2022-12-01'
#1
# reorganize(Disaster first 3 letters): reorganizes the csv dataframe into useful
# geodataframe with danger stats calculated by the characteristics of each event.
#Read all the files in the folder and make useful list of disasters:
earthquakes = fun.reorganizeEar(pd.read_csv("earthquakes.csv"))
volcanoes = fun.reorganizeVol(pd.read_csv("GVP_Eruption_Results.csv"))
meteorites = fun.reorganizeMet(pd.read_csv("Meteorite-Landings.csv"))
storms = fun.reorganizeSto(pd.read_csv("Storms.csv"))
list_of_disasters = [earthquakes, volcanoes, meteorites]
# Now we can make 2 kinds of maps and read the lists:
#2
# Function which makes heat map in squares in the area and dates you want
# Also possible to decide if you want to scale the map to the area or add grid.
# You can decide which resolution you prefer
# and if you want the boundaries to be the area which data is available in.
# The danger of each event is summed in squared area.
fun.make_map_plot_areas(list_of_disasters,grid=False, scale=False, Min_date = mindate, Max_date =maxdate, res=50, boundaries=True, xmin=0, ymin=20, xmax=50, ymax=65)
#3
#Function which plots the the dots on a world map.
#You can choose the dates you want to show.
fun.make_map_plot(list_of_disasters, Min_date = mindate, Max_date =maxdate)

# Info of the functions used in the major functions is in the "functions" file.
print (list_of_disasters)
