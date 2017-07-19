# ----------------------------------------------------------------------------------------
# nhdSwampMarshToRaster.py
# Version:  Python 2.7.5
# Creation Date: 2015-07-22
# Last Edit: 2016-08-24
# Creator:  Kirsten R. Hazler/Roy Gilb
#
# Summary:
# For a set of National Hydrography Dataset geodatabases, converts Swamp/Marsh features (from NHDWaterbody)to rasters based on a table of FCodes.  Creates final output rasters in which Swamp/Marsh features are coded 0.
#
# Usage Notes:
# A set of 46 geodatabases needed for an SDM project required about ?? hours to run.
#
# Syntax:
# nhdToRaster(inGDB, inFCodes, inSnap, outGDB, scratchGDB)
# ----------------------------------------------------------------------------------------

# Import required modules
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system functionality 
import sys # provides access to Python system functions
import traceback # used for error handling
import gc # garbage collection
from datetime import datetime # for time-stamping

# Script arguments to be input by user
inGDB = arcpy.GetParameterAsText(0) # Input set of NHD geodatabases to process
inFCodes = arcpy.GetParameterAsText(1) # Input table containing FCodes to include in burn
   # Default:  tb_nhdFCodes
inSnap = arcpy.GetParameterAsText(2) # Raster to set cell size and alignment
   # Default: nlcd_2011_lc_sdm
outGDB = arcpy.GetParameterAsText(3) # Geodatabase to hold final products
scratchGDB = arcpy.GetParameterAsText(4) # Geodatabase to hold intermediate products

# Additional script parameters and environment settings
arcpy.env.overwriteOutput = True # Existing data may be overwritten
arcpy.env.snapRaster = inSnap # Make sure outputs align with snap raster
arcpy.env.extent = 'MAXOF' # Make sure outputs are not truncated
outCS = arcpy.Describe(inSnap).SpatialReference
arcpy.env.outputCoordinateSystem = outCS

# Validate that snap raster has NAD83 datum
if outCS.GCS.Name != 'GCS_North_American_1983':
   arcpy.AddWarning('NHD data use the NAD83 datum, but your snap raster has a different datum.')
   arcpy.AddWarning('Proceeding, but the resulting raster may be suspect.')

# Define function to create swamp/marsh subset, add burn field, and dissolve features (to flatten overlaps)
def Subset(inFeats, outName, outVal):
   outName = scratchGDB + os.sep + outName + huc4
   tmpName = outName + '_tmp'
   where_clause = '"FCode" in (46600, 46601, 46602)' #Selection expression for Swamp/Marsh
   arcpy.arcpy.Select_analysis (inFeats, tmpName, where_clause)
   arcpy.AddField_management (tmpName, 'Burn', 'SHORT')
   arcpy.CalculateField_management (tmpName, 'Burn', outVal, 'PYTHON')
   arcpy.Dissolve_management (tmpName, outName, ['Burn'], '', 'SINGLE_PART', 'DISSOLVE_LINES')
   return outName

for gdb in inGDB.split(';'):
   try:
      # Set up some variables
      huc4 = os.path.basename(gdb)[4:8]
      nhdWB = gdb + os.sep + 'Hydrography' + os.sep + 'NHDWaterbody'
      
      arcpy.AddMessage('Working on watershed %s...' % huc4)
      
      # Project polygons to match the snap raster's coordinate system
      arcpy.AddMessage('Projecting polygon features...')
      prjPFC = scratchGDB + os.sep + 'prjPFC' + huc4
      arcpy.CopyFeatures_management (nhdWB, prjPFC)
      
      # Create subset of Swamp/Marsh features based on FCodes, and add a 'Burn' field  
      arcpy.AddMessage('Subsetting swamp/marsh polygons...')
      Wetlands = Subset(prjPFC, 'Wetlands', 0)
      
      # Rasterize the wetland features
      arcpy.AddMessage('Rasterizing wetlands...')
      rd_Wetlands = outGDB + os.sep + 'rdWetlands' + huc4
      try:
         arcpy.PolygonToRaster_conversion (Wetlands, 'Burn', rd_Wetlands, "MAXIMUM_COMBINED_AREA", 'None', inSnap)
         arcpy.AddMessage('Completed watershed %s.' %huc4)
         arcpy.AddMessage('The output wetland raster is %s.' %rd_Wetlands)
      except:
         arcpy.AddMessage('There are no wetland polygons to rasterize')
      
   except:
      arcpy.AddWarning('Failed to process watershed %s.' % huc4)
      
      # Error handling code swiped from "A Python Primer for ArcGIS"
      tb = sys.exc_info()[2]
      tbinfo = traceback.format_tb(tb)[0]
      pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
      msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

      arcpy.AddWarning(msgs)
      arcpy.AddWarning(pymsg)
      arcpy.AddMessage(arcpy.GetMessages(1)) 






