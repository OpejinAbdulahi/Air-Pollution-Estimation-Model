# AIR POLLUTION ESTIMATION MODEL
This code is based on my MS thesis, aimed at estimating real-time individual exposure to air pollution using GPS trajectory data and air pollution data obtained from the PurpleAir network.

# BIG IDEA
The model relies on two primary datasets:
GPS Trajectory Data: This dataset comprises the GPS logs of individuals, documenting the various places or microenvironments they visited over three days—two weekdays and one weekend. The data is recorded every minute and contains four main columns: timestamp, longitude, latitude, and identification (ID).

Air Pollution Dataset: Collected at one-minute intervals from the PurpleAir network, this dataset corresponds to the date and time of the GPS trajectory data acquisition.

# How it works
    The model iterates through the timestamps in the air pollution dataset, filtering the air pollution data points for a specific minute. During each iteration, the selected air pollution data points are dynamically converted into a shapefile. Geostatistical analysis, specifically Kriging, is employed to predict the air pollution surface for that minute. Simultaneously, the GPS trajectory data for the same time frame is dynamically overlaid, allowing extraction of individuals' air pollution exposure values for that minute. This process is carried out iteratively across the entire dataset.

    This methodology enables the estimation of real-time air pollution exposure for individuals based on their GPS trajectories, allowing for a comprehensive analysis of their exposure levels during the recorded time.

# Things to do fix if this code is not working on your computer
Honestly, this code should work for anyone who have been using arcpy and geopandas libraries on their computer. 
Otherwise, "import arcpy" and "import geopandas" migh be throwing error. in this case, I recommend using jupyter notebook. "pip install geopandas" should resolve the issue with geopandas, however "pip install arcpy" might seem not to resolve the issue with arcpy. Hence, this video " https://bit.ly/Arcpy_Anaconda "could help resolve it in anaconda. 


#
Credit: Abdulahi Opejin