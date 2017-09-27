# -----------------------------------------------------------------------------------------
# Roughness.py
# Version:  Python 2.7.5 / ArcGIS 10.2.2
# Creation Date: 2015-07-25
# Last Edit: 2015-07-25
# Creator:  Kirsten R. Hazler
#
# Summary:
#     Uses an input Digital Elevation Model (DEM) to derive terrain roughness indices at three different scales. "Roughness" is defined as the standard deviation of elevation values within a specified neighborhood.  Scale is determined by the neighborhood radii (in units of raster cells) input by the user. Each neighborhood is defined as a circle with radius r, unless r = 1, in which case a square 3x3 neighborhood is used.

# Processing is done by USGS quads or by other units defined by a polygon feature class. Thus, the output for each defined scale (neighborhood) is a set of rasters which will need to be mosaicked together later.
# -----------------------------------------------------------------------------------------

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
inDEM = arcpy.GetParameterAsText(0) # Input DEM
   # Default: N:\SDM\ProcessedData\NED_Products\NED_mosaics.gdb\rd_NED30m
inProcUnits = arcpy.GetParameterAsText(1) # Polygon feature class determining units to be processed
   # Default : N:\SDM\ProcessedData\SDM_ReferenceLayers.gdb\fc_ned_1arcsec_g
inFld = arcpy.GetParameterAsText(2) # Field containing the unit ID
   # Default: FILE_ID
R1 = arcpy.GetParameter(3) # Radius 1 (in raster cells)
   # Default:  1
R2 = arcpy.GetParameter(4) # Radius 2 (in raster cells)
   # Default: 10
R3 = arcpy.GetParameter(5) # Radius 3 (in raster cells)   
   # Default: 100
outGDB1 = arcpy.GetParameterAsText(6) # Geodatabase to hold final products for neighborhood 1
outGDB2 = arcpy.GetParameterAsText(7) # Geodatabase to hold final products for neighborhood 2
outGDB3 = arcpy.GetParameterAsText(8) # Geodatabase to hold final products for neighborhood 3
scratchGDB = arcpy.GetParameterAsText(9) # Geodatabase to hold intermediate products
ProcLogFile = arcpy.GetParameterAsText(10) # Text file to contain processing results

# Additional script parameters and environment settings
arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten
arcpy.env.snapRaster = inDEM
CellSize = int(arcpy.GetRasterProperties_management (inDEM, 'CELLSIZEX').getOutput(0))
FailList = list() # List to keep track of units where processing failed
maxRad = max(R1, R2, R3)

# Create and open a log file.
# If this log file already exists, it will be overwritten.  If it does not exist, it will be created.
Log = open(ProcLogFile, 'w+') 
FORMAT = '%Y-%m-%d %H:%M:%S'
timestamp = datetime.now().strftime(FORMAT)
Log.write("Process logging started %s \n" % timestamp)

ProcUnits = arcpy.da.SearchCursor(inProcUnits, [inFld])

for Unit in ProcUnits:
   try:
      UnitID = Unit[0]
      arcpy.AddMessage('Working on unit %s...' % UnitID)
        
      # Make a feature class with the single unit's shape, then buffer it
      # arcpy.AddMessage('Selecting feature...')
      where_clause = "%s = '%s'" %(inFld, UnitID) # Create the feature selection expression
      arcpy.MakeFeatureLayer_management (inProcUnits, 'selectFC', where_clause) 
      
      # arcpy.AddMessage('Buffering feature...')
      buffFC = scratchGDB + os.sep + 'buffFC' + UnitID
      buffDist = CellSize * maxRad
      arcpy.Buffer_analysis ('selectFC', buffFC, buffDist)
      
      # Clip the DEM to the above feature
      # arcpy.AddMessage('Clipping DEM to feature...')
      clipDEM = scratchGDB + os.sep + 'clipDEM'
      extent = arcpy.Describe(buffFC).extent
      XMin = extent.XMin
      YMin = extent.YMin
      XMax = extent.XMax
      YMax = extent.YMax
      rectangle = '%s %s %s %s' %(XMin, YMin, XMax, YMax) 
      arcpy.Clip_management (inDEM, rectangle, clipDEM, buffFC, '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
      
      # Set processing mask
      arcpy.env.mask = clipDEM 
   
      # Loop through the focal statistics process for each radius
      r = 1
      for item in ((R1, outGDB1), (R2, outGDB2), (R3, outGDB3)):
         # Define neighborhood
         radius = item[0]
         if radius == 1:
            neighborhood = NbrRectangle(3, 3, "CELL")
         else:
            neighborhood = NbrCircle(radius, "CELL")
            
         # Specify output
         gdb = item[1]
         outRoughness = gdb + os.sep + "rough_" + UnitID + "_" + str(r)
         
         # Run focal statistics
         arcpy.AddMessage('Calculating roughness for radius %s...' % r)
         roughness = FocalStatistics (clipDEM, neighborhood, "STD", "DATA")
         
         # Clip to original unit shape
         extent = arcpy.Describe('selectFC').extent
         XMin = extent.XMin
         YMin = extent.YMin
         XMax = extent.XMax
         YMax = extent.YMax
         rectangle = '%s %s %s %s' %(XMin, YMin, XMax, YMax) 
         arcpy.AddMessage('Clipping output for radius %s...' % r)
         arcpy.Clip_management (roughness, rectangle, outRoughness, 'selectFC', '', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
         r += 1
      
   except:
      # Error handling code swiped from "A Python Primer for ArcGIS"
      tb = sys.exc_info()[2]
      tbinfo = traceback.format_tb(tb)[0]
      pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
      msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

      arcpy.AddWarning('Unable to process unit %s' % UnitID)
      FailList.append(UnitID)
      arcpy.AddWarning(msgs)
      arcpy.AddWarning(pymsg)
      arcpy.AddMessage(arcpy.GetMessages(1))
      
# List the units where processing failed
if FailList:
   msg = '\nProcessing failed for some units: \n'
   Log.write(msg)
   arcpy.AddMessage('%s See the processing log, %s' % (msg, ProcLogFile))
   for unit in FailList:
      Log.write('\n   -%s' % unit)
      arcpy.AddMessage(unit) 
      
timestamp = datetime.now().strftime(FORMAT)
Log.write("\nProcess logging ended %s" % timestamp)   
Log.close()



















