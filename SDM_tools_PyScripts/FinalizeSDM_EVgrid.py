# -------------------------------------------------------------------------------------------------------
# FinalizeSDM_EVgrid.py
# Version:  Python 2.7.5 / ArcGIS 10.2.2
# Creation Date: 2015-10-30
# Last Edit: 2015-10-30
# Creator:  Kirsten R. Hazler
#
# Summary:
#     Multiplies input raster by a specified multiplier, and outputs to an integer format. This script
# is used to finalize environmental variables (EV) rasters in preparation for input to Random Forest 
# Species Distribution Models (SDM).
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
inRaster = arcpy.GetParameterAsText(0) # Input raster
Multiplier = arcpy.GetParameter(1) # Multiplier used to preserve precision in integer output
outRaster = arcpy.GetParameterAsText(2) # Output raster

# Additional script parameters and environment settings
arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten

try:
   if Multiplier == 1:
      # Simply convert to integer
      outRast = Int(0.5 + Raster(inRaster))
   else:
      # Multiply before converting to integer
      outRast = Int(0.5 + (Multiplier * Raster(inRaster)))
   
   outRast.save(outRaster)
   

except:
   # Error handling code swiped from "A Python Primer for ArcGIS"
   tb = sys.exc_info()[2]
   tbinfo = traceback.format_tb(tb)[0]
   pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
   msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

   arcpy.AddError(msgs)
   arcpy.AddError(pymsg)
   arcpy.AddError(arcpy.GetMessages(1))
      







