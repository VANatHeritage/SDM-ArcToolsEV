# -------------------------------------------------------------------------------------------------------
# BatchExtractZipfiles.py
# Version:  Python 2.7.5
# Creation Date: 2015-04-15
# Last Edit: 2015-04-15
# Creator:  Kirsten R. Hazler
#
# Summary:
#     Extracts all zip files within a specified directory, and saves the output to another specified directory.
#
# Usage Tips:
#     This is intended to be run as an ArcGIS tool.
#
# Required Arguments (input by user):
#  ZipDir:  The directory containing the zip files to be extracted
#  OutDir:  The directory in which extracted files will be stored
# -------------------------------------------------------------------------------------------------------

# Import required modules
import arcpy # to get ArcGIS functionality
import zipfile # for handling zipfiles
import os # provides access to operating system funtionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
import gc # garbage collection

# Script arguments to be input by user
ZipDir = arcpy.GetParameterAsText(0) # input directory containing zip files to be extracted
OutDir = arcpy.GetParameterAsText(1) # output directory to store extracted files

# If the output directory does not already exist, create it
if not os.path.exists(OutDir):
   os.makedirs(OutDir)
                                   
# Set up the processing log                                   
ProcLog = OutDir + os.sep + "ZipLog.txt"
log = open(ProcLog, 'w+')

try:
   flist = os.listdir (ZipDir) # Get a list of all items in the input directory
   zfiles = [f for f in flist if '.zip' in f] # This limits the list to zip files
   for zfile in zfiles:
      if zipfile.is_zipfile (ZipDir + os.sep + zfile):
         arcpy.AddMessage('Extracting %s' % zfile)
         try:
            zf = zipfile.ZipFile(ZipDir + os.sep + zfile)
            zf.extractall(OutDir)
            arcpy.AddMessage(zfile + ' extracted')
            log.write('\n' + zfile + ' extracted')

         except:
            arcpy.AddWarning('Failed to extract %s' % zfile)
            log.write('\nWarning: Failed to extract %s' % zfile)
            # Error handling code swiped from "A Python Primer for ArcGIS"
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
            msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

            arcpy.AddWarning(msgs)
            arcpy.AddWarning(pymsg)
            arcpy.AddMessage(arcpy.GetMessages(1))
      else: 
         arcpy.AddWarning('%s is not a valid zip file' % zfile)
         log.write('\nWarning: %s is not a valid zip file' % zfile)
   arcpy.AddMessage('Your files have been extracted to %s.' % OutDir)
         
except:
   # Error handling code swiped from "A Python Primer for ArcGIS"
   tb = sys.exc_info()[2]
   tbinfo = traceback.format_tb(tb)[0]
   pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
   msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

   arcpy.AddError(msgs)
   arcpy.AddError(pymsg)
   arcpy.AddMessage(arcpy.GetMessages(1))
   
finally:
   log.close()
   


