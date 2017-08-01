# ----------------------------------------------------------------------------------------
# nhdToDistanceRasters.py
# Version:  Python 2.7.8
# Creation Date: 2017-03-29
# Last Edit: 2017-04-03
# Creator: Roy Gilb
#
# Summary: For a directory containing sets of National Hydrography Dataset geodatabases, merges all NHDArea and NHDWaterbody features into a large regional feature class, 
#          projects the resulting NHD polygons to Albers, subsets the projected polygons into 3 classes (stream/river, lake/pond <= 1 ha, and lake/pond > 1 ha), 
#          rasterizes the subset polygons to source rasters, and then calculates the euclidean distance for each of the three source rasters. The output rasters should be 
#          clipped to the SDM Study Region.
#   
#
## Note: Some lines of codetaken and edited from nhdToRaster.py script.
# ----------------------------------------------------------------------------------------

# Import required modules
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system funtionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
from datetime import datetime # for time-stamping

# Script arguments to be input by user
inNHD = arcpy.GetParameterAsText(0) # Input set of NHD geodatabases to process -> H:\DataDownloads\NHD_Extracted\SDM
inSnap = arcpy.GetParameterAsText(1) #Input snap raster (use an SDM env varaiable) ex: AnnMnTemp.tif
outGDB = arcpy.GetParameterAsText(2) # Geodatabase to hold final products
scratchGDB = arcpy.GetParameterAsText(3) # Geodatabase to hold intermediate products

# Additional script parameters and environment settings
arcpy.env.overwriteOutput = True # Set overwrite option so that existing data may be overwritten
arcpy.env.snapRaster = inSnap # Make sure outputs align with snap raster
arcpy.env.extent = 'MAXOF' # Make sure outputs are not truncated
outCS = arcpy.Describe(inSnap).SpatialReference
arcpy.env.outputCoordinateSystem = outCS
if not scratchGDB:
   scratchGDB = "in_memory"
   
# Validate that snap raster has NAD83 datum
if outCS.GCS.Name != 'GCS_North_American_1983':
   arcpy.AddWarning('NHD data use the NAD83 datum, but your snap raster has a different datum.')
   arcpy.AddWarning('Proceeding, but the resulting raster may be suspect.')

   
#Create where clause variables for the 3 nhd selections
wcRiver = 'FCode = 46000  Or FCode = 46003 Or FCode = 46006 Or FCode = 46007'  #Where_clause to select river features

#Where_clause to select pond/resevoir polys <= 1 ha
wcPond = "(FCode = 43617 Or FCode = 43614 Or FCode = 43615 Or FCode = 43613 Or FCode = 43621 Or FCode = 43600 Or FCode = 43618 Or FCode = 43619 Or FCode = 43601 Or " + \
         "FCode = 39000 Or FCode = 39001 Or FCode = 39006 Or FCode = 39005 Or FCode = 39004 Or FCode = 39009 Or FCode = 39011 Or FCode = 39010 Or FCode = 39012)" + \
         " And (Area_ha <= 1)"
#Where_clause to select pond/resevoir polys > 1 ha
wcLake = "(FCode = 43617 Or FCode = 43614 Or FCode = 43615 Or FCode = 43613 Or FCode = 43621 Or FCode = 43600 Or FCode = 43618 Or FCode = 43619 Or FCode = 43601 Or " + \
         "FCode = 39000 Or FCode = 39001 Or FCode = 39006 Or FCode = 39005 Or FCode = 39004 Or FCode = 39009 Or FCode = 39011 Or FCode = 39010 Or FCode = 39012)" + \
         " And (Area_ha > 1)"

         
walk = arcpy.da.Walk(inNHD, datatype="FeatureClass", type="Polygon")# datatype="FeatureClass", type="Polygon") #Change to feature dataset ?
         
for root, dirs, files in walk:
   for gdb in dirs:
      try:
         bn = os.path.basename(gdb)
         if bn.startswith('NHDH'):        #Control statement to only use GDBs in the loop, the feature dataset paths are then set up manually below
            #Set up some variables
            huc4 = os.path.basename(gdb)[4:8]
            nhdWB = root + os.sep + gdb + os.sep + 'Hydrography' + os.sep + 'NHDWaterbody'       
            nhdArea = root + os.sep + gdb + os.sep + 'Hydrography' + os.sep + 'NHDArea'
            #arcpy.AddMessage('This is the root folder: ' + root)
            #arcpy.AddMessage('This is the gdb: ' + gdb)
            #arcpy.AddMessage('This is the whole WB path: ' + root + os.sep + gdb + os.sep + 'Hydrography' + os.sep + 'NHDWaterbody' )
            #arcpy.AddMessage('This is the whole Area path: ' + root + os.sep + gdb + os.sep + 'Hydrography' + os.sep + 'NHDArea' )
            
            arcpy.AddMessage('Working on watershed %s...' % huc4)
            
            #Merge the Area and Waterbody feature classes
            arcpy.AddMessage('Merging Area and Waterbody polygon features...')
            mergePFC = scratchGDB + os.sep + 'nhdMergedPolys' + huc4
            arcpy.Merge_management ([nhdWB, nhdArea], mergePFC)
            
         else:
            continue
         
      except:
         arcpy.AddWarning('Failed to process watershed %s.' % huc4)
         
         #Error handling code swiped from "A Python Primer for ArcGIS"
         tb = sys.exc_info()[2]
         tbinfo = traceback.format_tb(tb)[0]
         pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
         msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

         arcpy.AddWarning(msgs)
         arcpy.AddWarning(pymsg)
         arcpy.AddMessage(arcpy.GetMessages(1)) 
         
         
#Merge all of the nhd polygon classes created above into one big feature class, and then continue with the projection, subsetting, rasterization, and euclidean distance steps

arcpy.AddMessage('Merging Region-wide NHD polygon feature class...')
arcpy.env.workspace = scratchGDB
fcList = arcpy.ListFeatureClasses("nhdMergedPolys*")
nhdRegionMerge = scratchGDB + os.sep + "nhdRegionMerge"
arcpy.Merge_management (fcList, nhdRegionMerge)

# Project polygons to match the snap raster's coordinate system
arcpy.AddMessage('Projecting polygon features...')
prjPFC = scratchGDB + os.sep + 'prjPFC'
arcpy.CopyFeatures_management (nhdRegionMerge, prjPFC)
      
#Add and calculate Area_ha field
arcpy.AddMessage('Calculating area...')
arcpy.AddField_management (prjPFC, 'Area_ha', 'DOUBLE')
arcpy.CalculateField_management (prjPFC, 'Area_ha', "!shape.area@hectares!","PYTHON_9.3")
     
#Make selections and export to 3 different feature classes - add to scratch gdb and merge them all together at the end
arcpy.AddMessage('Subsetting NHD features...')
outStreamRiver = scratchGDB + os.sep + "riverSubset"
outPond = scratchGDB + os.sep + "pondSubset"
outLake = scratchGDB + os.sep + "lakeSubset"
arcpy.arcpy.Select_analysis (prjPFC, outStreamRiver, wcRiver)
arcpy.arcpy.Select_analysis (prjPFC, outPond, wcPond)
arcpy.arcpy.Select_analysis (prjPFC, outLake, wcLake)

#Create source rasters for stream/river, pond, and lake polys
arcpy.AddMessage('Creating source rasters...')
rivRast = scratchGDB + os.sep + "rivRast"
pondRast = scratchGDB + os.sep + "pondRast"
lakeRast = scratchGDB + os.sep + "lakeRast"
arcpy.PolygonToRaster_conversion(outStreamRiver, "FCode", rivRast, "", "", inSnap)
arcpy.PolygonToRaster_conversion(outStreamRiver, "FCode", pondRast, "", "", inSnap)
arcpy.PolygonToRaster_conversion(outStreamRiver, "FCode", lakeRast, "", "", inSnap)

#Run euclidean distance for the 3 merged source rasters - in SDM east extent    ----MOVE THIS OUTSIDE OF LOOP ONCE WORKING
arcpy.AddMessage('Calculating distance to source rasters...')
distStream = outGDB + os.sep + "distRiver"
distPond = outGDB + os.sep + "distPond"
distLake = outGDB + os.sep + "distLake"
arcpy.gp.EucDistance_sa(outStreamRiver, distStream, "", inSnap, "")
arcpy.gp.EucDistance_sa(outPond, distPond, "", inSnap, "")
arcpy.gp.EucDistance_sa(outLake, distLake, "", inSnap, "")
   
      
#Delete scratch vars?



