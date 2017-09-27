# -------------------------------------------------------------------------------------------------------
# BeersAspect.py
# Version:  Python 2.7.5 / ArcGIS 10.2.2
# Creation Date: 2015-06-04
# Last Edit: 2015-09-23
# Creator:  Kirsten R. Hazler
#
# Summary:
#     Uses an input Digital Elevation Model (DEM) to derive aspect, and then the Beers transformation
# of aspect, which ranges from 0 (most exposed) to 2 (most sheltered). A neutral value of 1 is applied 
# to all cells where slope is less than 3 degrees.  

# Reference:
#     Beers, Thomas W., Peter E. Dress, and Lee C. Wensel.  1966.  Notes and observations.  Aspect 
# transformation in site productivity research.  Journal of Forestry 64:691-692.
#
#
# -------------------------------------------------------------------------------------------------------

# Import required modules
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system functionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
from datetime import datetime # for time-stamping

# Script arguments to be input by user
inDEM = arcpy.GetParameterAsText(0) # Input DEM
   # Default: N:\SDM\ProcessedData\NED_Products\NED_mosaics.gdb\rd_NED30m
inSlope = arcpy.GetParameterAsText(1) # Raster representing slope in degrees
   # Default: E:\Testing\SlopeAndCurve.gdb\rd_Slope
outAspect = arcpy.GetParameterAsText(2) # Output aspect raster
outBeers = arcpy.GetParameterAsText(3) # Output Beers aspect raster
ProcLogFile = arcpy.GetParameterAsText(4) # Text file to contain processing results

# Additional script parameters and environment settings
arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten
arcpy.env.snapRaster = inDEM
#CellSize = int(arcpy.GetRasterProperties_management (inDEM, 'CELLSIZEX').getOutput(0))
deg2rad = math.pi/180.0 # needed for conversion from degrees to radians for input to Cos function

# Create and write to a log file.
# If this log file already exists, it will be overwritten.  If it does not exist, it will be created.
Log = open(ProcLogFile, 'w+') 
FORMAT = '%Y-%m-%d %H:%M:%S'
timestamp = datetime.now().strftime(FORMAT)
Log.write("Process logging started %s \n\n" % timestamp)
Log.write('Input parameters are...\n')
Log.write('Input DEM: %s\n' % inDEM)
Log.write('Input slope raster: %s\n' % inSlope)
Log.write('Output aspect raster: %s\n' % outAspect)
Log.write('Output Beers aspect raster: %s\n' % outBeers)

try:
   # Create Aspect in degrees
   rdAspect = Aspect(inDEM)
   rdAspect.save(outAspect)
   arcpy.AddMessage('Created aspect raster')

   # Create Beers Aspect
   # Set to 1 if Slope < 3 (flat slope)
   rdBeers = Con (Raster(inSlope) < 3, 1, (Cos((45 - rdAspect)*deg2rad) + 1))
   rdBeers.save(outBeers)
   arcpy.AddMessage('Created Beers Aspect raster.')
   arcpy.AddMessage('Processing log is %s ' % ProcLogFile)

except:
   # Error handling code swiped from "A Python Primer for ArcGIS"
   tb = sys.exc_info()[2]
   tbinfo = traceback.format_tb(tb)[0]
   pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
   msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

   arcpy.AddError(msgs)
   arcpy.AddError(pymsg)
   arcpy.AddError(arcpy.GetMessages(1))
      
timestamp = datetime.now().strftime(FORMAT)
Log.write("\n\nProcess logging ended %s" % timestamp)   
Log.close()

















