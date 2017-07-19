# ----------------------------------------------------------------------------------------
# BatchSolarRad.py
# Version:  Python 2.7.5
# Creation Date: 2015-04-24
# Last Edit: 2016-04-06
# Creator:  Kirsten R. Hazler
#
# Summary:
#     Derives solar radiation from a DEM, for a specified set of footprints polygons.
#     These polygons should already be in the desired format and projected coordinate 
#     system to match the DEM.
#
# Usage Tips:
#
# Syntax:
# ----------------------------------------------------------------------------------------

# Import required modules
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import xml.etree.ElementTree as ET # enables manipulation of XML metadata files
import os # provides access to operating system funtionality such as file and directory paths
from os import listdir
from os.path import isfile, join
import sys # provides access to Python system functions
import traceback # used for error handling
import gc # garbage collection
from datetime import datetime # for time-stamping

# Script arguments to be input by user
in_DEM = arcpy.GetParameterAsText(0) # Input digital elevation model
z_factor = arcpy.GetParameter(1) # The number of ground x,y units in one surface z unit.
   # Default:  1
in_Tiles = arcpy.GetParameterAsText(2) 
   # Polygon feature class outlining footprints of tiles to be processed
   # Typically this would be the NED tile outlines, but can use smaller tiles for testing.
fld_ID = arcpy.GetParameterAsText(3)
   # A field to use as unique ID for each tile
out_GDB = arcpy.GetParameter(4) # File geodatabase to store the output solar radiation tiles
ProcLog = arcpy.GetParameterAsText(5) # Text file to record processing record

# Hard-coded parameters required by Area Solar Radiation tool
# Roy, generally you should use defaults for the various solar parameters
# Use the option to do solar radiation for "special dates", i.e. equinoxes and solstices
# I think this should yield 4 outputs, but it may be that one of the seasons is omitted,
# in which case you'll need to code it to also run the missing one.

# in_surface_raster 
   # Not needed here; use raster extracted in loop
latitude = '' 
   # No value given, so the average latitude for the extracted raster will be used
sky_size = 200 
   # Square side length, in cells, for the viewshed, sky map, and sun map grids
time_configuration = 'TimeWholeYear(2015)' 
   # Specifies the time configuration (period) used for calculating solar radiation.
day_interval = ''
   # Use default
hour_interval = ''
   # Use default
each_interval = 'INTERVAL'
   # For a whole year with monthly intervals, results in 12 output radiation values for each location. 
# z_factor
   # Not needed here; entered by user
slope_aspect_input_type = 'FROM_DEM'
   # The slope and aspect grids are calculated from the input surface raster. 
calculation_directions = 32
   # Number of azimuth directions used when calculating the viewshed.  Default is 32.
zenith_divisions = 16
   # Number of divisions, relative to zenith, used to create sky sectors in the sky map.  Default is 8.
azimuth_divisions = 16
   # Number of divisions, relative to north, used to create sky sectors in the sky map.  Default is 8.
diffuse_model_type = 'UNIFORM_SKY'
   # Uniform diffuse model. The incoming diffuse radiation is the same from all sky directions. 
diffuse_proportion = 0.3 
   # This is the default value for generally clear sky conditions.
transmittivity = 0.5 
   # This is the default for a generally clear sky.
# out_direct_radiation_raster
   # Not needed here; use raster naming convention in loop
# out_diffuse_radiation_raster
   # Not needed here; use raster naming convention in loop
# out_direct_duration_raster
   # Not needed here; use raster naming convention in loop

# Geoprocessing environment settings
arcpy.env.snapRaster = SnapRast # Set the snap raster for alignment of outputs
arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten
scratch = arcpy.env.scratchGDB # Scratch workspace

# Get the set of NED footprints to process, along with relevant attributes
myFields = ['SHAPE@', 'bname']
nedList = arcpy.da.SearchCursor(nedFC, myFields)

# Initialize a list for processing records, and start processing log
myProcList = list()
Log = open(ProcLog, 'w+') 
timeStamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
Log.write('Solar radiation processing started %s.' % timeStamp)
### Add records of tool parameters to the log, here

myProcList = [] # Empty list to keep track of features processed.

Footprints = ### Set up the search cursor from in_Tiles here.

for fp in Footprints:
   try:
      fp_ID = tile[0]
      arcpy.AddMessage('Working on %s...' % fp_ID)
      
      # Make a temp feature class from the single footprint
      
      # Buffer the footprint by the sky_size
      
      # Extract the DEM for the buffered footprint
      
      # Run solar radiation
      
      # Clip output solar radiation rasters to original footprint
      
      arcpy.AddMessage('Completed %s' % fp_ID)
      myProcList.append('\nCompleted %s' % fp_ID)
      
   except:
      arcpy.AddMessage('Failed to process %s' % fp_ID)
      myProcList.append('\nFailed to process %s' % fp_ID)
      # Error handling code swiped from "A Python Primer for ArcGIS"
      tb = sys.exc_info()[2]
      tbinfo = traceback.format_tb(tb)[0]
      pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
      msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

      arcpy.AddWarning(msgs)
      arcpy.AddWarning(pymsg)
      arcpy.AddMessage(arcpy.GetMessages(1))

# Write processing results to a log file.
# If this log file already exists, it will be overwritten.  If it does not exist, it will be created.

timeStamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
Log.write('Solar radiation processing completed %s.  Results below.\n' % timeStamp)
for item in myProcList:
   Log.write("%s\n" % item)
Log.close()
arcpy.AddMessage('Processing results can be viewed in %s' % myLogFile)

