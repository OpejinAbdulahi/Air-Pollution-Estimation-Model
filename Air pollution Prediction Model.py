import pandas as pd
import os
import geopandas as gpd
from shapely.geometry import Point
import arcpy
import csv
from arcpy.sa import *

# Set the workspace // Global workspace
arcpy.env.workspace = r"C:\Users\OPEJINA22\OneDrive - East Carolina University\Desktop\Air Pollution Estimation Model"
arcpy.env.overwriteOutput = True

# CSV files (Data) of the datasets for the analysis
purpleAir = "PurpleAir_Air_Pollution_Data.csv"    # One minute purpleair data goes here
geoAir = "Participants_Trajectory_Data.csv"  # GPS Trajecyory data goes here

# Create folder for the output files generated after Executed operations for the two datasets
new_folder_names = ["One Minute Air-Pollution Surfaces", "One minute exposure values", "People_Exposure_estimates"]

# List to store the directory paths of the created folders
created_folder_paths = []

# Loop through the list of folder names and create each folder
for folder_name in new_folder_names:
    new_folder_path = os.path.join(arcpy.env.workspace, folder_name)

    # Check if the folder already exists before creating it
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
        created_folder_paths.append(new_folder_path)
    else:
        created_folder_paths.append(new_folder_path)

# Directories of output/exported files for the two datasets
purple_path = created_folder_paths[0]
geoair_path = created_folder_paths[1]
participant_output = created_folder_paths[2]

# Datasets Locations and dull directory paths
PurpleAir = os.path.join(arcpy.env.workspace, purpleAir)
GeoAir = os.path.join(arcpy.env.workspace, geoAir)

# Eastern North Carolina Boundary Shapefile
boundary = os.path.join(arcpy.env.workspace, "boundary.shp")

# IMPORTING DATAFRAME FOR PURPLEAIR DATA
df = pd.read_csv(purpleAir)
# Selecting the columns of interest from dataframe
df_purple = df[['Eastern', 'pm2.5_atm', 'Latitude', 'Longitude']]

# IMPORTING DATAFRAME FOR GEOAIR DATA
df_geoair = pd.read_csv(GeoAir)
df_geoair = df_geoair[['datetime', 'new_lat', 'new_lon', 'ID.1']]

# Filter uniques timestamp's column of Geoair based on the date and time/minute in which GeoAir data were collected by research participants
filter_ = df_geoair['datetime'].unique()  # Mapping unique dates in minutes

# Loop through the unique timestamps in GeoAir data
for filt in filter_:
    # Definition of condition for sub-dataframe selection for the two DataFrames (PurpleAir and Geoair)
    geo_condition = df_geoair['datetime'] == filt
    purp_condition = df_purple['Eastern'] == filt

    # Apply condition
    purp_sub_df = df_purple[purp_condition]
    geo_sub_df = df_geoair[geo_condition]

    # Create a GeoDataFrame for purpleAir sub-dataframe
    gdf_purple = gpd.GeoDataFrame(purp_sub_df, crs="EPSG:4326", geometry=gpd.points_from_xy(purp_sub_df['Longitude'], purp_sub_df['Latitude']))

    # Create a GeoDataFrame for purpleAir sub-dataframe
    gdf_geo = gpd.GeoDataFrame(geo_sub_df, crs="EPSG:4326", geometry=gpd.points_from_xy(geo_sub_df['new_lon'], geo_sub_df['new_lat']))

    # Save the GeoDataFrame as a shapefile
    gdf_geo.to_file(f'{geoair_path}/points{filt}.shp', driver='ESRI Shapefile')

    # Save the GeoDataFrame as a shapefile
    gdf_purple.to_file(f'{purple_path}/points{filt}.shp', driver='ESRI Shapefile')

    # KRIGING OPERATION STARTS HERE
    # Shapefiles for the Kriging
    fc = [f"{purple_path}\\points{filt}.shp", f"{geoair_path}\\points{filt}.shp", boundary]

    # Shapefiles for the Kriging
    z_field = "pm2.5_atm"  # input the field to interpolate

    # Define the spatial relationship and selection type for the input point feature for kriging
    spatial_relationship = "WITHIN_A_DISTANCE"
    selection_type = "NEW_SELECTION"
    search_distance = "60 miles"

    # Make a selection for air pollution within a distance of 30 miles of study area for kriging analysis
    select = arcpy.SelectLayerByLocation_management(fc[0], spatial_relationship, fc[2], search_distance, selection_type)

    # Count the selected points
    num_selected_points = int(arcpy.GetCount_management(select)[0]) # Important piece that helps check feature with no data in there

    # This if statement capture shapefile or kriging input feature that has no data (i.e., empty input shapefile) and allow for contuinuty of the code, otherwise the code would keep crashing at the stage when input feature is empty.
    if num_selected_points == 0:
        print(f"No points within the boundary for minute {filt}. Skipping Kriging.")
        continue  # Skip Kriging for this minute and continue with the next minute

    # Setting extent
    extent = arcpy.Extent(-80.408403, 32.962868, -73.869617, 37.352792)
    arcpy.env.extent = extent

    # arcpy.env.extent = extent
    #extent_layer = "boundary.shp"
    #arcpy.env.extent = extent_layer

    #Kriging model
    kriging_model = arcpy.sa.KrigingModelOrdinary()   # define kriging model/parameter to use

    # Perform simple kriging
    kriging_result = Kriging(select, z_field, kriging_model)

    # Save the output kriged raster in every minute
    original_kriging = f"{purple_path}\\{filt}_kr_output.tif"
    kriging_result.save(original_kriging)

    # Clip the kriging surface using the boundary shapefile
    output_clipped_raster = ExtractByMask(original_kriging, fc[2])

    # Here's a simple example using FocalStatistics to fill nodata areas with nearby cell values
    neighborhood = arcpy.sa.NbrRectangle(3, 3, "CELL")
    filled_raster = arcpy.sa.FocalStatistics(output_clipped_raster, neighborhood, "MEAN")

    # Save the filled raster
    output_filled_raster = f"{purple_path}\\{filt}_filled_raster.tif"
    filled_raster.save(output_filled_raster)

    # Collective GPS Traject in every minute
    out_table = f"{geoair_path}\\{filt}_Interpolated_value.dbf"

    # Extract raster values to points
    arcpy.gp.ExtractValuesToPoints_sa(fc[1], output_filled_raster, out_table, "INTERPOLATE", "VALUE_ONLY")

    def delete_file(file_path):
        try:
            # Check if the file exists
            if os.path.exists(file_path):
                # Use arcpy's Delete_management function to delete the file
                arcpy.Delete_management(file_path)
                #print(f"File '{file_path}' deleted successfully.")
            else:
                print(f"File '{file_path}' does not exist.")
        except Exception as e:
            print(f"Error deleting the file: {str(e)}")

    # deleting kriged outcome, kriging shapefiles, and gps trajectory shapefiles :
    # delete_file(original_kriging)
    delete_file(fc[0])
    delete_file(fc[1])

# Seting folder for final result
arcpy.env.workspace = geoair_path

# Get a list of all shapefiles in the workspace
shapefiles = arcpy.ListFeatureClasses()

# Check if there are shapefiles to merge
if len(shapefiles) < 2:
    print("There are not enough shapefiles to merge.")
else:
    output_shapefile = os.path.join(participant_output, "ParticipantDataInOneMinute.shp")

    # Use the Merge tool to combine all shapefiles into one
    arcpy.Merge_management(shapefiles, output_shapefile)

    print(f"Successfully merged {len(shapefiles)} shapefiles into {output_shapefile}")

    # Specify the name of the input shapefile
    input_shapefile = f'{participant_output}\\ParticipantDataInOneMinute.shp'

    # Specify the name of the output CSV file
    output_csv = f'{participant_output}\\OneMinute_ParticipantData.csv'

    # Use the arcpy.da.SearchCursor to read the attributes from the shapefile
    with arcpy.da.SearchCursor(input_shapefile, ["*"]) as cursor:
        # Get the field names (header) from the shapefile
        field_names = [field.name for field in arcpy.ListFields(input_shapefile)]

        # Open the CSV file for writing
        with open(output_csv, 'w', newline='') as csv_file:
            # Create a CSV writer
            csv_writer = csv.writer(csv_file)

            # Write the header row to the CSV file
            csv_writer.writerow(field_names)

            # Iterate through the rows in the shapefile and write them to the CSV file
            for row in cursor:
                csv_writer.writerow(row)

# Deleting initially created geoair_path folder
#if arcpy.Exists(geoair_path):
    #arcpy.Delete_management(geoair_path)

# Deleting initially created purpleair_path folder
#if arcpy.Exists(purple_path):
    #arcpy.Delete_management(purple_path)

print("Air Pollution Estimation Operations were successfully completed")