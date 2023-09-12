import numpy as np
import shapely
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

# Minor functions
#----------------------
# Danger calculation for earthquakes.
def danger_calc_ear(value1, value2):
    return (value1 / 10) - (value2 / 700)
# Danger calculation for meteorites.
def danger_calc_met(value1):
    return (((value1['mass (g)']-10000000)/value1['mass (g)'].max())+(10/23))**0.5
# Convert 3 columns with Year Month Day to Number 'YMD', Capitals.
def con_date(disas, name="",cap=False):
    if cap:
        return (disas[name + 'Day']) + (disas[name + 'Month'] * 100) + (disas[name + 'Year'] * 10000)
    else:
        return (disas[name + 'day']) + (disas[name + 'month'] * 100) + (disas[name + 'year'] * 10000)
#merge list of geodatafremes, returns 'geometry' and 'danger'.
def mer_gdf(list,Min_date,Max_date):
    df = pd.DataFrame()
    for i in list:
        i = i.loc[:,('Danger','geometry')]
        df = pd.concat([i.loc[Min_date:Max_date],df])
    return df
# Plot a map with the locations in the list of data frames.
def make_map_plot(list_of_disasters, Min_date = 0, Max_date =3000):
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    df = pd.DataFrame({'geometry': [pd.NA]})
    for i in list_of_disasters:
        i = i.loc[:, ('title', 'geometry')]
        # i['geometry'] = i['geometry'].buffer(2)
        df = pd.concat([i[Min_date:Max_date], df])
    ax = df.plot(column='title',legend=True, cmap='viridis')
    ax.set_aspect('equal')
    world.plot(ax=ax, color='white', edgecolor='black')
    ax.set_title("Dangerous points", fontsize=25)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()

# Major functions
#-------------------------
# Plot a map with the areas in which disasters are located.
# Parameters: scale:scale to area, Min_date, Max_date, res: division of the are to n squares,
# boundaries of the geometries avalible, use xmin,xmax,ymin,ymax(longitude and latitude) for specific area .
def make_map_plot_areas(list_of_disasters,grid=False, scale=False, Min_date = 0, Max_date =3000, res=30,boundaries=False,xmin=-190, ymin=-190, xmax=190, ymax=190):
    df = mer_gdf(list_of_disasters,Min_date,Max_date)
    if boundaries:
        xmin, ymin, xmax, ymax = df.total_bounds
    cell_size = (max(xmax,ymax) - min(xmin, ymin)) / res
    grid_cells = []
    for x0 in np.arange(xmin, xmax + cell_size, cell_size):
        for y0 in np.arange(ymin, ymax + cell_size, cell_size):
            x1 = x0 - cell_size
            y1 = y0 + cell_size
            grid_cells.append(shapely.geometry.box(x0, y0, x1, y1))
    cell = gpd.GeoDataFrame(grid_cells, columns=['geometry'])
    merged = gpd.sjoin(df, cell, how='left', predicate='within')
    dissolve = merged.dissolve(by="index_right", aggfunc="sum")
    max_danger = dissolve.Danger.max()
    most_d_area = dissolve[dissolve['Danger']==max_danger]['geometry']
    print (f'The max Danger is: {max_danger} and it is in: {most_d_area}')
    cell.loc[dissolve.index, 'Danger'] = dissolve.Danger.values
    ax = cell.plot(column='Danger', figsize=(12, 8), cmap='viridis', vmax=dissolve.Danger.max(), edgecolor="grey",legend=True)
    plt.autoscale(not scale)
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world.plot(ax=ax, color='none', edgecolor='black')
    if grid:
        cell.plot(ax=ax, facecolor="none", edgecolor='grey')
    ax.set_title("Dangerous Areas", fontsize=50)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()
# Reorganizes Earthquakes CSV table to 3 columns: (Day of the week, Danger, geometry). Date is the index.
def reorganizeEar(earthquake):
    paramV = ['Date', 'Longitude', 'Latitude', 'Depth', 'Magnitude']
    earthquake = earthquake.loc[:, paramV]
    earthquake['title'] = 'earthquakes'
    earthquake['Date'] = pd.to_datetime(earthquake['Date'],format="%d/%m/%Y",errors='coerce')
    earthquake.dropna(subset=['Date'], inplace=True)
    earthquake['Day of the week'] = earthquake['Date'].dt.day_name()
    earthquake['Danger'] = danger_calc_ear(earthquake['Magnitude'], earthquake['Depth'])
    earthquake.loc[earthquake.Danger < 0, 'Danger'] = 0
    earthquake.set_index('Date', inplace=True)
    earthquake = gpd.GeoDataFrame(
        earthquake, geometry=gpd.points_from_xy(earthquake.Longitude, earthquake.Latitude))
    earthquake = earthquake.drop(columns=['Latitude', 'Longitude', 'Depth', 'Magnitude'])
    return earthquake.sort_index()
# Reorganizes CSV table to 3 columns: (Duration [Days], geometry). Date is the index.
def reorganizeVol(volcano,MinDuration=0):
    paramV = ['Start Year', 'Start Month', 'Start Day', 'End Year', 'End Month', 'End Day', 'Latitude', 'Longitude']
    paramVX = ['Start Year', 'Start Month', 'Start Day', 'End Year', 'End Month', 'End Day', 'End Date']
    volcano = volcano.loc[:, paramV]
    volcano['title'] = 'volcanoes'
    volcano = volcano[volcano['Start Year'] > 0]
    volcano['Date'] = con_date(volcano, name="Start ",cap=True)
    volcano['End Date'] = con_date(volcano, name="End ",cap=True)
    volcano.dropna(subset=['Date', 'End Date'], inplace=True)
    volcano = volcano.astype({'Date':int,'End Date':int})
    volcano['Date'] = pd.to_datetime(volcano['Date'], format='%Y%m%d',yearfirst = True, errors='coerce')
    volcano['End Date'] = pd.to_datetime(volcano['End Date'], format='%Y%m%d', yearfirst=True, errors='coerce')
    volcano['Duration [Days]'] = volcano['End Date'] - volcano['Date']
    volcano['Day of the week'] = volcano['Date'].dt.day_name()
    volcano['Danger'] = 1
    volcano.dropna(subset=['Duration [Days]'], inplace=True)
    volcano['Duration [Days]'].replace('0 days','1 days',inplace = True)
    volcano = volcano[volcano['Duration [Days]'] > f'{MinDuration} days']
    volcano.drop(paramVX, inplace=True, axis=1)
    volcano.set_index('Date', inplace=True)
    volcano = gpd.GeoDataFrame(
        volcano, geometry=gpd.points_from_xy(volcano.Longitude, volcano.Latitude))
    volcano = volcano.drop(columns=['Latitude', 'Longitude'])
    return volcano.sort_index()
# Reorganizes CSV table to 3 columns: (Day of the week, Danger, geometry). Date is the index.
def reorganizeMet(meteorite):
    paramV = ['year', 'reclong', 'reclat', 'mass (g)']
    meteorite = meteorite.loc[:, paramV]
    meteorite['title'] = 'meteorites'
    meteorite['Date'] = pd.to_datetime(meteorite['year'],errors='coerce')
    meteorite.dropna(subset=['Date'], inplace=True)
    meteorite['Day of the week'] = meteorite['Date'].dt.day_name()
    meteorite['Danger'] = danger_calc_met(meteorite)
    meteorite['Danger'].replace(np.nan,0, inplace=True)
    meteorite.set_index('Date', inplace=True)
    meteorite = gpd.GeoDataFrame(
        meteorite, geometry=gpd.points_from_xy(meteorite.reclong, meteorite.reclat))
    meteorite = meteorite.drop(columns=['mass (g)' , 'reclong', 'reclat', 'year'])
    return meteorite.sort_index()
# Reorganizes CSV table to 3 columns: (Day of the week, Danger, geometry). Date is the index.
def reorganizeSto(storm):
    paramV = ['name', 'year', 'month', 'day','long','lat','category']
    storm = storm.loc[:, paramV]
    storm['title'] = 'storms'
    storm['Date'] = con_date(storm, name="")
    storm.dropna(subset=['Date'], inplace=True)
    storm = storm.astype({'Date': int})
    storm['Date'] = pd.to_datetime(storm['Date'], format='%Y%m%d', yearfirst=True, errors='coerce')
    storm['Day of the week'] = storm['Date'].dt.day_name()
    storm['Danger'] = storm['category']/5
    storm.loc[storm.Danger < 0, 'Danger'] = 0
    storm.set_index('Date', inplace=True)
    storm = gpd.GeoDataFrame(
        storm, geometry=gpd.points_from_xy(storm.long, storm.lat))
    storm = storm.drop(columns=['long', 'lat', 'year', 'month', 'day','category'])
    return storm.sort_index()