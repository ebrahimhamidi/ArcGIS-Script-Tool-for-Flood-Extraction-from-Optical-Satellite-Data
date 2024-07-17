'''
Assignment - Final Project - Estimation of Flood Extent in Coastal Areas Using Remote Sensing Data
GY-539 GIS Programming
Department of Geology	
Instructor: Dr. Sagy Cohen
Prepared by: Ebrahim Hamidi
PhD Student at the Department of Civil, Construction and Environmental Engineering at the University of Alabama
Tuscaloosa, Alabama, USA
Email address: shamidi1@crimson.ua.edu
April 30, 2021

Random Forest Python code is based on the folowing publication:
Muñoz, D. F., Cissell, J. R., & Moftakhari, H. (2019).
Adjusting emergent herbaceous wetland elevation with object‐based image analysis, random forest and the 2016 NLCD.
Remote Sensing, 11(20), 2346. https://doi.org/10.3390/rs11202346
'''

# Import library
import pandas as pd
import numpy as np
import pickle
import shapefile
import arcpy
import os

# Setting arcpy workspace environment
arcpy.env.workspace = os.getcwd()

# Checking ArcGIS license
arcpy.CheckExtension("spatial")

# Read shapefiles
sfp = shapefile.Reader(arcpy.GetParameterAsText(0))
rp = sfp.records()
data1 = np.array(rp, dtype='float32')

# Read data from shape file
fields = [0]; fields.extend(range(3, 10))
heading = np.array(['OBJECT_ID', 'LENGTH', 'AREA', 'NDVI', 'NDWI', 'BI', 'NDBI', 'NIR', 'SWIR1', 'SWIR2'])
df1 = pd.DataFrame(data1, columns=heading)

# Creating Test and Train Data
variables = ['NDVI', 'NDWI', 'BI', 'NDBI', 'NIR', 'SWIR1', 'SWIR2']

# Generating Sample data
df = df1[variables]

# Load pre-trained RF model
rfc = pickle.load(open(arcpy.GetParameterAsText(1), 'rb'))

# Applying the trained Classifier to the test
prediction = rfc.predict(df1[variables])

# Output as dataframe
output = pd.DataFrame(prediction, columns=np.array(['Value']))
file = pd.concat([df1['OBJECT_ID'], output], axis=1)

# Creating process folder
path1 = os.path.dirname(arcpy.GetParameterAsText(0))
datapath = os.path.join(path1, 'ProcessFolder')
if os.path.exists(datapath) is not True:
    os.makedirs(datapath)

# Saving predicted results in a "newTextFile.txt" in the temporary "processfolder" 
newTextFile = os.path.join(datapath, 'newTextFile.txt')
numpy.savetxt(newTextFile, file, fmt='%i')

# Creating "newShapeFile.shp" in the temporary "processfolder" which is the copy of the original shapefile
newShapeFile = os.path.join(datapath, 'newShapeFile.shp')
arcpy.management.CopyFeatures(arcpy.GetParameterAsText(0), newShapeFile)

# Joining the predictioed results "newTextFile.txt" to the copy of the original shapefile "newShapeFile.shp"
arcpy.JoinField_management(newShapeFile, "OBJECTID", newTextFile, "Field1", "Field2")

# Defining pixel size
resterPxlSize = arcpy.GetParameterAsText(2)

# Creating a result raster
arcpy.PolygonToRaster_conversion(newShapeFile, "Field2", arcpy.GetParameterAsText(3), "CELL_CENTER", "NONE", resterPxlSize)
