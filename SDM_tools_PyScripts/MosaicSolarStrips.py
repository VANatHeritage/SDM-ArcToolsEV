# ----------------------------------------------------------------------------------------
# MosaicSolarStrips.py
# Version:  Python 2.7.5
# Creation Date: 2016-06-15
# Last Edit: 2016-07-12
# Creator:  Roy Gilb/Kirsten Hazler
#
# Summary: 
# Mosaics the SDM Solar Radiation strips into a single raster dataset. Must be run three times, once for equinox, once for summer, and once for winter.  

# Syntax: 
# MosaicSolarStrips (inGDB, inFprints, joinFld, mosaicName, scratchGDB, outGDB, ProcLog)
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
inGDB = arcpy.GetParameterAsText(0) # Input GDBs containing the raster strips to mosaic
inFprints = arcpy.GetParameterAsText(1) # Input footprint polygons
   # example: fc_LatStrips100
joinFld= arcpy.GetParameterAsText(2) # Join field relating raster names to footprints
   # example:  rName_equ
mosaicName = arcpy.GetParameterAsText(3) # Name for output mosaic
scratchGDB = arcpy.GetParameterAsText(4) # Scratch GDB to store the mosaic dataset
outGDB = arcpy.GetParameterAsText(5) # Output GDB to store the final raster dataset
procLog = arcpy.GetParameterAsText(6) #Log to store data on the mosaicking progress

# Open processing log.
Log = open(procLog, 'w+') 
timeStamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
Log.write('Solar radiation mosaic creation started %s.\n' % timeStamp)

# Local variables:
coordSys = arcpy.Describe(inFprints).spatialReference

# Process: Create Mosaic Dataset
# This creates the blank (empty) mosaic dataset
arcpy.AddMessage('Creating empty mosaic dataset...')
md = 'md_' + mosaicName
solarMosaic = arcpy.CreateMosaicDataset_management(scratchGDB, md, coordSys)  

# Loop through the geodatabases and add rasters to the mosaic dataset
for gdb in inGDB.split(';'):
   try:
      # Process: Add Rasters To Mosaic Dataset
      arcpy.AddMessage('Adding rasters from %s to mosaic dataset...' %gdb)
      arcpy.AddRastersToMosaicDataset_management(solarMosaic, "Raster Dataset", gdb, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "", "SUBFOLDERS", "OVERWRITE_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE") 
      Log.write('Successfully added rasters from %s to mosaic dataset. \n' %gdb)
   except:
      arcpy.AddWarning('Failed to add rasters from %s.' %gdb)
      Log.write('Failed to add rasters from %s to mosaic dataset. \n' %gdb)

# Process: Import Mosaic Dataset Geometry
arcpy.AddMessage('Importing footprint geometry...')
arcpy.ImportMosaicDatasetGeometry_management(solarMosaic, "FOOTPRINT", "Name", inFprints, joinFld)

# Process: Calculate Statistics
# This takes a long time and isn't actually necessary unless you want to view the mosaic dataset.
# arcpy.AddMessage('Calculating mosaic statistics...')
# arcpy.CalculateStatistics_management(solarMosaic, "", "", "", "", inFprints)

# Process: Copy final output raster dataset
try:
   arcpy.AddMessage('Exporting final raster dataset.  This may take awhile...')
   rd = outGDB + os.sep + mosaicName
   arcpy.CopyRaster_management(solarMosaic, rd)
except:
   arcpy.AddWarning('Unable to export raster dataset.')
   Log.write('Unable to export to %s' %rd)

# Close processing log.
timeStamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
Log.write('Processing finished %s.\n' % timeStamp)
Log.write('Mosaic dataset stored here: %s.\n' % scratchGDB)
Log.write('Final raster output is %s.\n' % rd )
Log.close()










