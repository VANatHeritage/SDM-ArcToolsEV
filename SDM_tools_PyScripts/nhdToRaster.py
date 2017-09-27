# ----------------------------------------------------------------------------------------
# nhdToRaster.py
# Version:  Python 2.7.5
# Creation Date: 2015-07-22
# Last Edit: 2016-08-17
# Creator:  Kirsten R. Hazler/Roy Gilb
#
# Summary:
# For a set of National Hydrography Dataset geodatabases, converts NHDArea, NHDWaterbody, and NHDFlowline features to rasters based on a table of FCodes.  Creates final output rasters classified as follows:
# 1 = streams (inland linear features)
# 2 = inland lakes and rivers (inland polygon features)
# 3 = estuary
# 4 = sea/ocean
#
# Usage Notes:
# A set of 46 geodatabases needed for an SDM project required about 7 hours to run.
#
# Syntax:
# nhdToRaster(inGDB, inFCodes,fldMarine,fldEstuary,fldInland,inSnap,outGDB,scratchGDB)
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
inFCodes = arcpy.GetParameterAsText(1) # Input table containing FCodes to include in rasterization process
   # Default:  tb_nhdFCodes
fldMarine = arcpy.GetParameterAsText(2) # Binary field; marine indicator
   # Default:  sdmMarine
fldEstuary = arcpy.GetParameterAsText(3) # Binary field; estuary indicator
   # Default:  sdmEstuary
fldInland = arcpy.GetParameterAsText(4) # Binary field; inland indicator
   # Default:  sdmInland
inSnap = arcpy.GetParameterAsText(5) # Raster to set cell size and alignment
   # Default: nlcd_2011_lc_sdm
outGDB = arcpy.GetParameterAsText(6) # Geodatabase to hold final products
scratchGDB = arcpy.GetParameterAsText(7) # Geodatabase to hold intermediate products

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

# Define function to create selection expressions based on a selection field
def PopFCodeList(SelFld):
   code_list = list() #Create empty list
   where_clause = '"%s" = 1' %(SelFld) #Selection expression
   with arcpy.da.SearchCursor(inFCodes, 'FCode', where_clause) as FCodes:  
      for code in FCodes:
         code_list.append(code[0])
   code_list = str(code_list).replace('[', '(').replace(']',')')
   where_clause = '"FCode" in %s' % code_list
   return where_clause

# Define function to create subsets, add burn field, and dissolve features (to flatten overlaps)
def Subset(inFeats, inFld, outName, outVal):
   outName = scratchGDB + os.sep + outName + huc4
   tmpName = outName + '_tmp'
   where_clause = PopFCodeList(inFld)
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
      nhdArea = gdb + os.sep + 'Hydrography' + os.sep + 'NHDArea'
      nhdFline = gdb + os.sep + 'Hydrography' + os.sep + 'NHDFlowline'
      
      arcpy.AddMessage('Working on watershed %s...' % huc4)
      
      # Merge the Area and Waterbody feature classes
      arcpy.AddMessage('Merging Area and Waterbody polygon features...')
      mergePFC = scratchGDB + os.sep + 'nhdMergedPolys' + huc4
      fldMap = "FCode \"FCode\" true true false 4 Long 0 0 ,First,#,%s,FCode,-1,-1,%s,FCode,-1,-1" %(nhdArea, nhdWB)
      arcpy.Merge_management ([nhdWB, nhdArea], mergePFC, fldMap)
      
      #Projection operations --------------------------------------------------------------------------------------
      ###Note: Replaced the Project function with the Copy Features function because (a) Projection does not allow writing to  "in_memory" and (b) Projection fails for NHD lines altogether, if writing to a geodatabase.  Copied features end up in the correct coordinate system b/c we set the output coordinate system environment at the top of the script.
      
      # Project polygons to match the snap raster's coordinate system
      arcpy.AddMessage('Projecting polygon features...')
      prjPFC = scratchGDB + os.sep + 'prjPFC' + huc4
      arcpy.CopyFeatures_management (mergePFC, prjPFC)
      
      # Project lines to match the snap raster's coordinate system
      arcpy.AddMessage('Projecting line features...')
      prjFline = scratchGDB + os.sep + 'prjFline' + huc4
      arcpy.CopyFeatures_management (nhdFline, prjFline) 
      
      #Subset and erase operations ----------------------------------------------------------------------------------------     
      # Create subsets of MARINE features based on FCodes, and add a 'Burn' field  
      arcpy.AddMessage('Subsetting marine polygons...')
      MarinePolys = Subset(prjPFC, fldMarine, 'MarinePolys', 4)
      
      # Create subsets of ESTUARY features based on FCodes, and add a 'Burn' field  
      arcpy.AddMessage('Subsetting estuary polygons...')
      EstuaryPolys = Subset(prjPFC, fldEstuary, 'EstuaryPolys', 3)
              
      # Create subsets of INLAND polygon features based on FCodes, and add a 'Burn' field  
      arcpy.AddMessage('Subsetting inland rivers and lakes...')
      InlandPolys = Subset(prjPFC, fldInland, 'InlandPolys', 2)

      #Create subset of line features based on FCodes, and add a 'Burn' field
      arcpy.AddMessage('Subsetting streams and flowpaths...')
      LineFeats = Subset(prjFline, fldInland, 'LineFeats', 1)
          
      # Remove line features that occur within polygons
      arcpy.AddMessage('Extracting streams...')
      Streams_rtn1 = scratchGDB + os.sep + 'Streams_rtn1' + huc4
      arcpy.Erase_analysis(LineFeats, MarinePolys, Streams_rtn1)
      Streams_rtn2 = scratchGDB + os.sep + 'Streams_rtn2' + huc4
      arcpy.Erase_analysis(Streams_rtn1, EstuaryPolys, Streams_rtn2)
      burnStreams = scratchGDB + os.sep + 'burnStreams' + huc4
      arcpy.Erase_analysis(Streams_rtn2, InlandPolys, burnStreams)
              
      # Create subset of line features that are within the inland features polygons 
      arcpy.AddMessage('Extracting non-stream flowpaths...')
      arcpy.MakeFeatureLayer_management (LineFeats, 'lyrFline')
      arcpy.SelectLayerByLocation_management ('lyrFline', 'WITHIN', InlandPolys)
      arcpy.FeatureClassToFeatureClass_conversion ('lyrFline', scratchGDB, 'burnFlowPaths' + huc4)
      burnFlowPaths = scratchGDB + os.sep + 'burnFlowPaths' + huc4
      arcpy.AddField_management (burnFlowPaths, 'Burn', 'SHORT')
      arcpy.CalculateField_management (burnFlowPaths, 'Burn', 2, 'PYTHON')

      
      #Rasterize operations --------------------------------------------------------------------------------------- 
      raster_list = list() # list of rasters to combine
      
      # Rasterize the marine polygon features
      arcpy.AddMessage('Rasterizing marine polygons...')
      rd_Marine = scratchGDB + os.sep + 'rdMarine' + huc4
      try:
         arcpy.PolygonToRaster_conversion (MarinePolys, 'Burn', rd_Marine, "MAXIMUM_COMBINED_AREA", 'None', inSnap)
         raster_list.append(rd_Marine)
      except:
         arcpy.AddMessage('There are no marine polygons to rasterize')
              
      # Rasterize the estuary polygon features
      arcpy.AddMessage('Rasterizing estuary polygons...')
      rd_Estuary = scratchGDB + os.sep + 'rdEstuary' + huc4
      try:
         arcpy.PolygonToRaster_conversion (EstuaryPolys, 'Burn', rd_Estuary, "MAXIMUM_COMBINED_AREA", 'None', inSnap)
         raster_list.append(rd_Estuary)
      except:
         arcpy.AddMessage('There are no estuary polygons to rasterize')

      #Rasterize the streams
      arcpy.AddMessage('Rasterizing streams...')
      rd_Streams = scratchGDB + os.sep + 'rdStreams' + huc4
      try:
         arcpy.PolylineToRaster_conversion(burnStreams, 'Burn', rd_Streams, "MAXIMUM_COMBINED_LENGTH", 'None', inSnap)
         raster_list.append(rd_Streams)
      except:
         arcpy.AddMessage('There are no streams to rasterize')
      
      #Rasterize the non-stream flowpaths
      arcpy.AddMessage('Rasterizing non-stream flowpaths...')
      rd_FlowPaths = scratchGDB + os.sep + 'rdFlowPaths' + huc4
      try:
         arcpy.PolylineToRaster_conversion(burnFlowPaths, 'Burn', rd_FlowPaths, "MAXIMUM_COMBINED_LENGTH", 'None', inSnap)
         raster_list.append(rd_FlowPaths)
      except:
         arcpy.AddMessage('There are no flowpaths to rasterize')
      
      # Rasterize the lakes and rivers
      arcpy.AddMessage('Rasterizing lake and river polygons...')
      rd_LakesRivers = scratchGDB + os.sep + 'rdInlandPolys' + huc4
      try:
         arcpy.PolygonToRaster_conversion (InlandPolys, 'Burn', rd_LakesRivers, "MAXIMUM_COMBINED_AREA", 'None', inSnap)
         raster_list.append(rd_LakesRivers)
      except:
         arcpy.AddMessage('There are no lakes or rivers to rasterize')
 
      # Combine rasters to create final hydro raster
      arcpy.AddMessage('Creating final classified hydro raster...')
      tmpFinal = CellStatistics (raster_list, 'MAXIMUM', 'DATA')
      rd_Hydro = outGDB + os.sep + 'rdAllHydro' + huc4
      tmpFinal.save(rd_Hydro)

      #Final arcpy messages
      arcpy.AddMessage('Completed watershed %s.' %huc4)
      arcpy.AddMessage('The output hydro raster is %s.' %rd_Hydro)
      
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













