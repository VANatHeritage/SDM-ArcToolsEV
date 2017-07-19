# -------------------------------------------------------------------------------------------------------
# ReplaceRasterWithUpdate.py
# Version:  Python 2.7.5 / ArcGIS 10.2.2
# Creation Date: 2015-07-31
# Last Edit: 2015-07-31
# Creator:  Kirsten R. Hazler
#
# Summary:
#     For each input raster, deletes the data set of the same name in the target geodatabase, and 
# replaces it with the input.
#
# -------------------------------------------------------------------------------------------------------

# Import required modules
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system functionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
import gc # garbage collection
from datetime import datetime # for time-stamping

# Script arguments to be input by user
inRaster = arcpy.GetParameterAsText(0) # Input raster(s)
outGDB = arcpy.GetParameterAsText(1) # Geodatabase containing raster(s) to be replaced
ProcLogFile = arcpy.GetParameterAsText(2) # Text file to contain processing results

# Additional script parameters and environment settings
arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten
FailList = list() # List to keep track of units where processing failed

# Create and open a log file.
# If this log file already exists, it will be overwritten.  If it does not exist, it will be created.
Log = open(ProcLogFile, 'w+') 
FORMAT = '%Y-%m-%d %H:%M:%S'
timestamp = datetime.now().strftime(FORMAT)
Log.write("Process logging started %s \n" % timestamp)

for raster in inRaster.split(';'):
   rName = os.path.basename(raster)
   outRaster = outGDB + os.sep + rName
   arcpy.AddMessage('Raster to be replaced is %s' % outRaster)
   
   try:
      if arcpy.Exists(outRaster):
         arcpy.AddMessage('Deleting old version of %s.' % rName)
         arcpy.Delete_management (outRaster)
      arcpy.Copy_management (raster, outRaster)
      arcpy.AddMessage('Copying new version of %s to output geodatabase.' % rName)
      Log.write('\nCopied new version of %s to output geodatabase.' % rName)
      
   except:
      # Error handling code swiped from "A Python Primer for ArcGIS"
      tb = sys.exc_info()[2]
      tbinfo = traceback.format_tb(tb)[0]
      pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
      msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

      arcpy.AddWarning('Unable to process raster rdBeers_%s' % rName)
      FailList.append(rName)
      arcpy.AddWarning(msgs)
      arcpy.AddWarning(pymsg)
      arcpy.AddMessage(arcpy.GetMessages(1))
      
# List the units where processing failed
if FailList:
   msg = '\nProcessing failed for some rasters: \n'
   Log.write(msg)
   arcpy.AddMessage('%s See the processing log, %s' % (msg, ProcLogFile))
   for unit in FailList:
      Log.write('\n   -%s' % unit)
      arcpy.AddMessage(unit)
         
timestamp = datetime.now().strftime(FORMAT)
Log.write("\nProcess logging ended %s" % timestamp)   
Log.close()







