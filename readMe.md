# AIR POLLUTION ESTIMATION MODEL
This code is based on my MS thesis, aimed at estimating real-time individual exposure to air pollution using GPS trajectory data and air pollution data obtained from the PurpleAir network.

# BIG IDEA
The model relies on two primary datasets:
GPS Trajectory Data: This dataset comprises the GPS logs of individuals, documenting the various places or microenvironments they visited over three days i.e., two weekdays and one weekend. The data is recorded every minute and contains four main columns: timestamp, longitude, latitude, and identification (ID).

Air Pollution Dataset: Collected at one-minute intervals from the PurpleAir network, this dataset corresponds to the date and time of the GPS trajectory data acquisition.

# How it works
The model iterates through the timestamps in the air pollution dataset, filtering the air pollution data points for a specific minute. During each iteration, the selected air pollution data points are dynamically converted into a shapefile. Geostatistical analysis, specifically Kriging, is employed to predict the air pollution surface for that minute. Simultaneously, the GPS trajectory data for the same time frame is dynamically overlaid, allowing extraction of individuals' air pollution exposure values for that minute. This process is carried out iteratively across the entire dataset.

This methodology enables the estimation of real-time air pollution exposure for individuals based on their GPS trajectories, allowing for a comprehensive analysis of their exposure levels during the recorded time.

# Things to do fix if this code is not working on your computer
This code should work perfectly for anyone who has previously used the arcpy and geopandas libraries on their computer. However, if errors arise due to importing some libraries:
import arcpy and import geopandas Errors: If you encounter errors related to these imports, it's recommended to use Jupyter Notebook. You can resolve the geopandas issue by executing pip install geopandas. However, resolving the arcpy issue with pip install arcpy might not work. In such cases, refer to this video tutorial https://bit.ly/Arcpy_Anaconda for guidance on resolving the arcpy library installation issue specifically within an Anaconda environment.
By following these steps, one should be able to address any library-related issues encountered while running this code. Adjustments or additional troubleshooting steps may be necessary based on the specific errors or configurations on your system.

# Further Work
This code can be further enhanced by implementing functionalities to convert its input datasets from csv into shapefiles. Additionally, it can be developed into an ArcGIS toolbox, allowing other researchers to utilize and benefit from its functionalities for their respective studies.

By expanding the code's capabilities to seamlessly convert input datasets to shapefiles and packaging it into an ArcGIS toolbox, it can become a more accessible and versatile tool for broader usage in research endeavors related to air pollution estimation and individual exposure analysis.


#
Credit: Abdulahi Opejin