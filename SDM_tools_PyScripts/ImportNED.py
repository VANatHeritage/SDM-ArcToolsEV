# -------------------------------------------------------------------------------------------------------
# ImportNED.py
# Version:  Python 2.7.5
# Creation Date: 2015-04-15
# Last Edit: 2015-05-04
# Creator:  Kirsten R. Hazler
#
# Summary:
#     Imports GRID-format National Elevation Dataset (NED) into a file geodatabase, in preparation for 
#     adding them to a mosaic dataset.   
#     The following processes are performed:
#     - Gets the list of GRID format rasters in the NED directory.  This is the list to process.
#     - Imports the rasters to the specified geodatabase.
#     - Deletes the source data after successful import of each raster
#     - Write processing results to a log file.
#
# Usage Tips:
#     This tool is intended for use with NED grids that have already been extracted from downloaded zipfiles.
#     If this tool does not function as expected, it may be that NED file structure and/or naming conventions
#     have changed since this script was written.
#
# Required Arguments:
# nedDir: Directory in which the original NED grids reside
# nedGDB: File geodatabase to store NED data
# -------------------------------------------------------------------------------------------------------

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
nedDir = arcpy.GetParameterAsText(0) # Directory in which the original NED grids reside
nedGDB = arcpy.GetParameterAsText(1) # File geodatabase to store processed NED data

# Additional script parameters
scratch = arcpy.env.scratchGDB
myLogFile = nedDir + os.sep + 'ProcLog.txt'

arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten

# Get the list of GRID-format rasters in the NED directory
arcpy.env.workspace = nedDir
nedGRIDs = arcpy.ListRasters("*", "GRID")

# Initialize a list for processing records
myProcList = list()

for gname in nedGRIDs:
   try:
      arcpy.AddMessage('Working on %s...' % gname)
      
      inNED = nedDir + os.sep + gname
      outNED = nedGDB + os.sep + gname
      nedTag = gname[3:]
      
      arcpy.CopyRaster_management (inNED, outNED)
      arcpy.AddMessage('- Added %s to geodatabase' % gname)
      myProcList.append('\nAdded %s to geodatabase' % gname)
            
      # Delete the source data
      try: 
         arcpy.AddMessage('- Deleting source NED for %s' % gname)
         arcpy.Delete_management(inNED)
      except:
         arcpy.AddMessage('Unable to delete source NED for %s' % gname)
         myProcList.append('Unable to delete source NED for %s' % gname)
      
      # Get the list of files remaining
      flist = os.listdir (nedDir) # Get a list of all items in the input directory
      dfiles = [nedDir + os.sep + f for f in flist if nedTag in f] # This limits the list to related files
      arcpy.AddMessage('Files to delete: %s' % dfiles)
      delfails = 0
      for d in dfiles:
         try:
            os.remove(d)
         except:
            delfails += 1
      if delfails == 0:
         arcpy.AddMessage('Successfully cleaned up ancillary files for %s' % gname)
         myProcList.append('Successfully cleaned up ancillary files for %s' % gname)
      else:
         arcpy.AddMessage('Unable to delete all ancillary files for %s' % gname)
         myProcList.append('Unable to delete all ancillary files for %s' % gname)
         
   except:
      arcpy.AddMessage('Failed to process %s' % gname)
      myProcList.append('\nFailed to process %s' % gname)
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
Log = open(myLogFile, 'w+') 
timeStamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
Log.write('NED processing completed %s.  Results below.\n' % timeStamp)
for item in myProcList:
   Log.write("%s\n" % item)
Log.close()
arcpy.AddMessage('Processing results can be viewed in %s' % myLogFile)




