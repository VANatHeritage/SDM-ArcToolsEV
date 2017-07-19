# ----------------------------------------------------------------------------------------
# MosaicRasterNHD.py
# Version:  Python 2.7.5
# Creation Date: 2016-06-15
# Last Edit: 2016-07-15
# Creator:  Roy Gilb/Kirsten Hazler
#
# Summary: 
# Mosaics rasters derived from NHD features, in multiple watersheds, into a single raster.  

# Syntax: 
# MosaicRasterNHD (inGDB, inSnap, mosaicName, scratchGDB, outGDB, ProcLog)
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
inSnap = arcpy.GetParameterAsText(1) # Snap raster to set cell size and alignment
mosaicName = arcpy.GetParameterAsText(2) # Name for output mosaic
scratchGDB = arcpy.GetParameterAsText(3) # Scratch GDB to store the mosaic dataset
outGDB = arcpy.GetParameterAsText(4) # Output GDB to store the final raster dataset
procLog = arcpy.GetParameterAsText(5) #Log to store data on the mosaicking progress

# Open processing log.
Log = open(procLog, 'w+') 
timeStamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
Log.write('Hydro mosaic creation started %s.\n' % timeStamp)

# Local variables:
coordSys = arcpy.Describe(inSnap).spatialReference

# Process: Create Mosaic Dataset
# This creates the blank (empty) mosaic dataset
arcpy.AddMessage('Creating empty mosaic dataset...')
md = 'md_' + mosaicName
hydroMosaic = arcpy.CreateMosaicDataset_management(scratchGDB, md, coordSys)  
md = scratchGDB + os.sep + md

# Loop through the geodatabases and add rasters to the mosaic dataset
for gdb in inGDB.split(';'):
   try:
      # Process: Add Rasters To Mosaic Dataset
      arcpy.AddMessage('Adding rasters from %s to mosaic dataset...' %gdb)
      arcpy.AddRastersToMosaicDataset_management(hydroMosaic, "Raster Dataset", gdb, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "", "SUBFOLDERS", "OVERWRITE_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE") 
      Log.write('Successfully added rasters from %s to mosaic dataset. \n' %gdb)
   except:
      arcpy.AddWarning('Failed to add rasters from %s.' %gdb)
      Log.write('Failed to add rasters from %s to mosaic dataset. \n' %gdb)

# Process: Set mosaic properties
arcpy.SetMosaicDatasetProperties_management (md, '', '', '', '', '', '', 'NEAREST', 'NOT_CLIP', 'FOOTPRINTS_DO_NOT_CONTAIN_NODATA', '', '', '', '', '', '', '', '', '', 'MAX') 

# Process: Copy final output raster dataset and build raster attribute table
try:
   arcpy.AddMessage('Exporting final raster dataset.  This may take awhile...')
   rd = outGDB + os.sep + mosaicName
   arcpy.CopyRaster_management(hydroMosaic, rd)
   arcpy.BuildRasterAttributeTable_management (rd, 'OVERWRITE')
except:
   arcpy.AddWarning('Unable to export raster dataset.')
   Log.write('Unable to export to %s' %rd)

# Close processing log.
timeStamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
Log.write('Processing finished %s.\n' % timeStamp)
Log.write('Mosaic dataset stored here: %s.\n' % scratchGDB)
Log.write('Final raster output is %s.\n' % rd )
Log.close()








