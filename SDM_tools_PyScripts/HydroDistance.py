# ----------------------------------------------------------------------------------------
# HydroDistance.py
# Version:  Python 2.7.5
# Creation Date: 2016-07-15
# Last Edit: 2016-07-18
# Creator:  Kirsten Hazler
#
# Summary: 
# Generates Euclidean distance rasters from various hydrologic types in a classified hydro raster

# Syntax: 
# HydroDistance (inHydro, procMask, outGDB)
# ----------------------------------------------------------------------------------------

# Import arcpy and other modules
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system functionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
import gc # garbage collection 
from datetime import datetime # for time-stamping

# Script arguments to be input by user
inHydro = arcpy.GetParameterAsText(0) # Input classified hydro raster
procMask = arcpy.GetParameterAsText(1) # Mask to determine processing area
outGDB = arcpy.GetParameterAsText(2) # Output geodatabase to store final products

# Set processing mask
arcpy.env.mask = procMask

# Set up Remap tables for creating binary rasters
rmpMarEst = RemapValue([[1,'NODATA'],[2,'NODATA'],[3,1],[4,1]])
rmpMarine = RemapValue([[1,'NODATA'],[2,'NODATA'],[3,'NODATA'],[4,1]])
rmpEstuary = RemapValue([[1,'NODATA'],[2,'NODATA'],[3,1],[4,'NODATA']])
rmpInland = RemapValue([[1,1],[2,1],[3,'NODATA'],[4,'NODATA']])
rmpStreams = RemapValue([[1,1],[2,'NODATA'],[3,'NODATA'],[4,'NODATA']])
rmpLakesRivers = RemapValue([[1,'NODATA'],[2,1],[3,'NODATA'],[4,'NODATA']])

# Set up output names for euclidean distance rasters
edMarEst = outGDB + os.sep + 'edMarEst'
edMarine = outGDB + os.sep + 'edMarine'
edEstuary = outGDB + os.sep + 'edEstuary'
edInland = outGDB + os.sep + 'edInland'
edStreams = outGDB + os.sep + 'edStreams'
edLakesRivers = outGDB + os.sep + 'edLakesRivers'

# Define function to do binary reclassification followed by Euclidean distance
def BinEucl(Remap, outDistRaster):
   arcpy.AddMessage('Creating binary raster')
   outBinary = Reclassify(inHydro, "Value", Remap)
   arcpy.AddMessage('Creating Euclidean distance raster')
   outEucl = EucDistance (outBinary)
   outEucl.save(outDistRaster)
   arcpy.AddMessage('Saved final raster to %s' % outDistRaster)
   return outDistRaster
   
# Set up processing list
ProcList = [(rmpMarEst, edMarEst),
            (rmpMarine, edMarine),
            (rmpEstuary, edEstuary),
            (rmpInland, edInland),
            (rmpStreams, edStreams),
            (rmpLakesRivers, edLakesRivers)]

# Carry out the function for each hydro type
for item in ProcList:
   BinEucl(item[0], item[1])












