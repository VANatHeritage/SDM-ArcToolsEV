# ExtractSeaOcean.py
# Version:  Python 2.7.5
# Creation Date: ???
# Last Edit: ???
# Creator:  KirstenHazler
#
# Summary: Extracts Sea/Ocean Polygons from the list of watershed codes input by user. These are polygons that extend inland and should be classified as something other than Sea/Ocean.

# Syntax:
# ----------------------------------------------------------------------------------------
# Import required modules
import arcpy
from arcpy.sa import *
from arcpy.da import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system funtionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
from datetime import datetime # for time-stamping


nhdWorkspace = arcpy.GetParameterAsText(0) # Workspace containing subfolder with NHD polygons
inHUC = arcpy.GetParameterAsText(1)        #List of the 4-digit HUCs used for extracting the affected watersheds
spatRef = arcpy.GetParameterAsText(2)       #Raster (nhd_Hydro) to use as the reference coordinate system for the projection
outGDB = arcpy.GetParameterAsText(3)       #Output workspace to store the new SeaOcean polygons for review

inHUCList = inHUC.split(";")       # Convert the input semicolon separated string to a list
outCS = arcpy.Describe(spatRef).spatialReference

arcpy.env.workspace = nhdWorkspace # Set current workspace
arcpy.env.overwriteOutput = True

#Set up some variables to use later
sdmNorth = nhdWorkspace + os.sep + 'SDM_north'
sdmSouth = nhdWorkspace + os.sep + 'SDM_south'
sdmVA =  nhdWorkspace + os.sep + 'Virginia' 
subdirsList = [sdmNorth, sdmSouth, sdmVA]
field = 'FType'         #Field 
seaOcean = 'SeaOcean'


arcpy.AddMessage('All GDBs: ')

for dir in subdirsList:
   try:
      arcpy.env.workspace = dir                    #Set the current workspace to the subdirectory so ListWorkspaces will work
      gdbs = arcpy.ListWorkspaces('*', 'FileGDB')  #Get the list of GDBs within each subdirectory
      for gdb in gdbs:        
         huc4 = os.path.basename(gdb)[4:8]          #Extract the 4 digit HUC from each GDB, for comparing with the input list
         nhdArea = gdb + os.sep + 'Hydrography' + os.sep + 'NHDArea'   #NHD Area feature class for the current HUC
         arcpy.AddMessage(gdb)
         arcpy.AddMessage(huc4)
         
         for code in inHUCList:                     #Iterate through the input HUC numbers to make comparisons to the GDB codes
            if code == huc4:                        #Compare input huc codes with the codes in the directory, and if it's a match, continue with the extraction and projection         
               arcpy.AddMessage('Working on watershed %s...' % huc4)
               outPolys = outGDB + os.sep + 'SeaOcean' + huc4
               arcpy.Select_analysis(nhdArea, outPolys + '_gcs', 'FType = 445')     #Select the SeaOcean features and output with unique name --> 445 is the Long code for SeaOean
               arcpy.Project_management(outPolys + '_gcs', outPolys, outCS)         #Project the new polys to the input spatial reference, overwrite old file
               arcpy.AddField_management(outPolys, "ysnSea", "Short")               #Add binary field
               arcpy.Delete_management(outPolys + '_gcs')                           #Delete pre-projected file
      
      #arcpy.env.workspace = nhdWorkspace    #Reset the current workspace
   except:
      arcpy.AddWarning('Failed to process watershed %s.') # % huc4)
      
      # Error handling code swiped from "A Python Primer for ArcGIS"
      tb = sys.exc_info()[2]
      tbinfo = traceback.format_tb(tb)[0]
      pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n " + str(sys.exc_info()[1])
      msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

      arcpy.AddWarning(msgs)
      arcpy.AddWarning(pymsg)
      arcpy.AddMessage(arcpy.GetMessages(1)) 
   
   
   
   # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "SeaOcean0314"








