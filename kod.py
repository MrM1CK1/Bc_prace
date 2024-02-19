##comparison of Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##


import os
from pprint import pprint
import earthpy.spatial as es
import geopandas as gpd
import numpy as np
import pandas as pa
import tifffile as tf
from fiona.crs import from_epsg
from rasterio.mask import mask
from scipy import ndimage
from shapely.geometry import box

import calc_kod
import sys
#print('The import was successful!')


### postup pro výpocet LST
# 1. BT - potřebná data: Kelvin consrant 1, Kelvin constant 2, Radiance add Band, Radiance Multi Band, pásmo L1_B10
#       - uroven zpracovani L1 !!!!
#       - pásmo: B10
# 
# 2. NDVI - potrebna data: B4, B5     
#       - úroveň zpracování L2
# 
# 3. VegC - potrebná data: ndvi
#       -úroven zpracovani: L2

# 5. LSE - Surface Emissivity
#       - úroven zpracování: L2
#       - potrebná data: B4, NDVI, VegC
#
# 6. LST - potrebna data: LSE, BT, B10_L1
#        - úroven zpracovani: L1/L2
#


SCRIPT_DIR = os.path.dirname((os.path.abspath(__file__)))   #Directory of the script
IN_FOLDER = (os.path.join(SCRIPT_DIR, r'input'))            #Input folder in the same directory
OUT_FOLDER = (os.path.join(SCRIPT_DIR, r'output'))          #Output folder in the same directory
CLIPPED = (os.path.join(SCRIPT_DIR, r'output'))             #Clipped folder in the output folder

SQUARE = box(17.0846,49.5122,18.5743,49.9015) #Coordinates of the area of interest
EPSG_CODE = 32633       #EPSG code of the area of interest
L8_dict = {}
L9_dict = {}
L8_metadata = {}
landsate_date = []


landsat_tif = calc_kod.find_path(IN_FOLDER, ".TIF")   ###L1 i L2
# 'input/LC08_L1TP_190025_20220627_20220706_02_T1/LC08_L1TP_190025_20220627_20220706_02_T1_SAA.TIF'


#Finding the Landsat images (Landsat Level 1)
for landsat_path in landsat_tif:
    
    landsat_name = os.path.basename(landsat_path) #'LC08_L1TP_190025_20220627_20220706_02_T1_SAA.TIF'
    if 'L1TP' in landsat_name:
        date = landsat_name.split('_')[3] #20220627
        if date not in landsate_date:
            landsate_date.append(date)

        if date in L8_dict:
            L8_dict[date].append(landsat_path)
        else:
            L8_dict[date] = [landsat_path]      

#for landsat_path in landsat_tif: #'input/LC08_L1TP_190025_20220627_20220706_02_T1/LC08_L1TP_190025_20220627_20220706_02_T1_B6.TIF'
for landsat_path in landsat_tif:
    
    #'/home/tereza/Documents/GitHub/repos/Bachelor_Thesis/output\\LC08_L1TP_190025_20220627_20220706_02_T1_B5_Clipped.TIF'
    if 'B1.TIF' in landsat_path:
        txt_path = landsat_path.replace('B1.TIF', 'MTL.txt')
        
        metadata_file = open(txt_path, 'r')
        for line in metadata_file:
            if '=' in line:
                key, value = line.strip().split(' = ')
                L8_metadata[key] = value                                 
        metadata_file.close()
        #{'CLOUD_COVER': '5.20',
            #'CLOUD_COVER_LAND': '5.20'...}
        break
    
# Clipping the images
#for path in landsat_path:
list_of_paths_clipped = []
for landsat_path in landsat_tif:
    image_name = os.path.basename(landsat_path).replace('.TIF', '')   
    if 'B' in image_name.split('_')[-1]: ## vyfiltruje pouze pásma s DATY (Bx)
        out_path = os.path.join(CLIPPED, image_name + '_Clipped.TIF') #output/LC08_L1TP_190025_20220627_20220706_02_T1_B9_Clipped.TIF
        calc_kod.Raster_clip(landsat_path, out_path, SQUARE)
        list_of_paths_clipped.append(out_path) # pripojit oklipovane paths do seznamu
        #['output/LC08_L2SP_190025_20220627_20220706_02_T1_ST_B10_Clipped.TIF',
        #'/output/LC08_L2SP_190025_20220627_20220706_02_T1_SR_B1_Clipped.TIF']

for date in landsate_date:
    for path in list_of_paths_clipped:
        if date in path:
            if 'SR_B1' in path:
                b1_l2 = path
                
            elif 'SR_B2' in path:
                b2_l2 = path
                reflectance_MULT_B2 = float((L8_metadata['REFLECTANCE_MULT_BAND_2']))
                reflectance_ADD_B2 = float((L8_metadata['REFLECTANCE_ADD_BAND_2']))
                
            elif 'SR_B3' in path:
                b3_l2 = path
                
            elif 'SR_B4' in path:
                b4_l2 = path
                reflectance_MULT_B4 = float((L8_metadata['REFLECTANCE_MULT_BAND_4']))
                reflectance_ADD_B4 = float((L8_metadata['REFLECTANCE_ADD_BAND_4']))
                
            elif 'SR_B5' in path:
                b5_l2 = path
                reflectance_MULT_B5 = float((L8_metadata['REFLECTANCE_MULT_BAND_5']))
                reflectance_ADD_B5 = float((L8_metadata['REFLECTANCE_ADD_BAND_5']))
                
            elif 'SR_B6' in path:
                b6_l2  = path
                reflectance_MULT_B6 = float((L8_metadata['REFLECTANCE_MULT_BAND_6']))
                reflectance_ADD_B6 = float((L8_metadata['REFLECTANCE_ADD_BAND_6']))
                
            elif 'SR_B7' in path:
                b7_l2  = path
                reflectance_MULT_B7 = float((L8_metadata['REFLECTANCE_MULT_BAND_7']))
                reflectance_ADD_B7 = float((L8_metadata['REFLECTANCE_ADD_BAND_7']))
                
            elif 'ST_B10' in path:
                b10_l2  = path
                radiance_MULT_B10 = float((L8_metadata['RADIANCE_MULT_BAND_10']))
                radiance_ADD_B10 = float((L8_metadata['RADIANCE_ADD_BAND_10']))

                K1_CONSTANT_BAND_10 = float((L8_metadata['K1_CONSTANT_BAND_10']))
                K2_CONSTANT_BAND_10 = float((L8_metadata['K2_CONSTANT_BAND_10']))
                
            elif 'L1TP' and 'B10' in path:
                b10_l1  = path
                radiance_MULT_B10_l1 = float((L8_metadata['RADIANCE_MULT_BAND_10']))
                radiance_ADD_B10_l1 = float((L8_metadata['RADIANCE_ADD_BAND_10']))
                K1_CONSTANT_BAND_10_L1 = float((L8_metadata['K1_CONSTANT_BAND_10']))
                K2_CONSTANT_BAND_10_L1 = float((L8_metadata['K2_CONSTANT_BAND_10']))
    
    ndvi_TIF = calc_kod.NDVI(b4_l2, b5_l2, OUT_FOLDER, 'NDVI_' + date)   
    VegC = calc_kod.VC(ndvi_TIF, OUT_FOLDER, 'VC_' + date)

    TOA_radiance_B10_L1 = calc_kod.TOA_Radiance(b10_l1, radiance_ADD_B10_l1, radiance_MULT_B10_l1, OUT_FOLDER, 'TOA_Radiance_B10_' + date)
    BrighTemp = calc_kod.Brightness_Temperature(radiance_ADD_B10_l1,radiance_MULT_B10_l1, b10_l1, OUT_FOLDER, 'BrightTemp_' + date)

    Emmisivity = calc_kod.LSE(b4_l2, ndvi_TIF, VegC, OUT_FOLDER, 'Emiss_' + date)
    LSTemperature = calc_kod.LST(Emmisivity, BrighTemp, b10_l1, OUT_FOLDER, 'LST_' + date)

    TOA_refle_b2 = calc_kod.TOA_Reflectance(b2_l2, reflectance_ADD_B2, reflectance_MULT_B2, OUT_FOLDER, 'TOARef_b2_' + date)
    TOA_refle_b4 = calc_kod.TOA_Reflectance(b4_l2, reflectance_ADD_B4, reflectance_MULT_B4, OUT_FOLDER, 'TOARef_b4_' + date)
    TOA_refle_b5 = calc_kod.TOA_Reflectance(b5_l2, reflectance_ADD_B5, reflectance_MULT_B5, OUT_FOLDER, 'TOARef_b5_' + date)
    TOA_refle_b6 = calc_kod.TOA_Reflectance(b6_l2, reflectance_ADD_B6, reflectance_MULT_B6, OUT_FOLDER, 'TOARef_b6_' + date)
    TOA_refle_b7 = calc_kod.TOA_Reflectance(b7_l2, reflectance_ADD_B7, reflectance_MULT_B7, OUT_FOLDER, 'TOARef_b7_' + date)
    Albedo_liang = calc_kod.Albedo_liang(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b6, TOA_refle_b7, OUT_FOLDER, 'Albedo_Liang_' + date)
    Albedo_Tasumi = calc_kod.Albedo_Tasumi(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b7, OUT_FOLDER, 'Albedo_Tasumi_' + date)


    #Rn = calc_kod.Rn(Emmisivity, LSTemperature, Albedo_liang, Rsin_value, OUT_FOLDER, 'Rn_' + date)
    #GroundHeatFlux = calc_kod.GHFlux_1(Rn, ndvi_TIF, OUT_FOLDER, 'GHF_' + date)
    GroundHeatFlux_2 = calc_kod.GHFlux_2(Albedo_liang,LSTemperature, ndvi_TIF,TOA_radiance_B10_L1, OUT_FOLDER, 'GHF_2_' + date)
    #Gr = calc_kod.Gr(Rn, OUT_FOLDER, 'G_' + date)

pprint('All done and in order')
