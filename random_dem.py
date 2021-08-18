#!/usr/bin/env python3
import os
from osgeo import gdal
from osgeo import osr
import numpy
import numpy as np
from scipy import signal

# config
GDAL_DATA_TYPE = gdal.GDT_Float32 
GEOTIFF_DRIVER_NAME = r'GTiff'
NO_DATA = 15
# Spherical mercator
SPATIAL_REFERENCE_SYSTEM_WKID = 4326
def create_raster(output_path,
                  columns,
                  rows,
                  nband = 1,
                  gdal_data_type = GDAL_DATA_TYPE,
                  driver = GEOTIFF_DRIVER_NAME):
    ''' returns gdal data source raster object

    '''
    # create driver
    driver = gdal.GetDriverByName(driver)

    output_raster = driver.Create(output_path,
                                  int(columns),
                                  int(rows),
                                  nband,
                                  eType = gdal_data_type)    
    return output_raster

def numpy_array_to_raster(output_path,
                          numpy_array,
                          upper_left_tuple,
                          cell_resolution,
                          nband = 1,
                          no_data = NO_DATA,
                          gdal_data_type = GDAL_DATA_TYPE,
                          spatial_reference_system_wkid = SPATIAL_REFERENCE_SYSTEM_WKID,
                          driver = GEOTIFF_DRIVER_NAME):
    ''' returns a gdal raster data source

    keyword arguments:

    output_path -- full path to the raster to be written to disk
    numpy_array -- numpy array containing data to write to raster
    upper_left_tuple -- the upper left point of the numpy array (should be a tuple structured as (x, y))
    cell_resolution -- the cell resolution of the output raster
    nband -- the band to write to in the output raster
    no_data -- value in numpy array that should be treated as no data
    gdal_data_type -- gdal data type of raster (see gdal documentation for list of values)
    spatial_reference_system_wkid -- well known id (wkid) of the spatial reference of the data
    driver -- string value of the gdal driver to use

    '''

    #print 'UL: (%s, %s)' % (upper_left_tuple[0],
    #                        upper_left_tuple[1])

    rows, columns = numpy_array.shape
    print ('ROWS: %s\n COLUMNS: %s\n' % (rows,columns))

    # create output raster
    output_raster = create_raster(output_path,
                                  int(columns),
                                  int(rows),
                                  nband,
                                  gdal_data_type) 

    geotransform = (upper_left_tuple[0],
                    cell_resolution,
                    upper_left_tuple[1] + cell_resolution,
                    -1 *(cell_resolution),
                    0,
                    0)

    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromEPSG(spatial_reference_system_wkid)
    output_raster.SetProjection(spatial_reference.ExportToWkt())
    output_raster.SetGeoTransform(geotransform)
    output_band = output_raster.GetRasterBand(1)
    output_band.SetNoDataValue(no_data)
    output_band.WriteArray(numpy_array)          
    output_band.FlushCache()
    output_band.ComputeStatistics(False)

    if os.path.exists(output_path) == False:
        raise Exception('Failed to create raster: %s' % output_path)

    return  output_raster

def create_dem():
    nx = 3600
    ny = 3600
    dem1 = np.random.rand(nx,ny)
    rows, columns = dem1.shape
    print ('ROWS: %s\n COLUMNS: %s\n' % (rows,columns))
    sizex = 300
    sizey = 100
    x, y = np.mgrid[-sizex:sizex+1, -sizey:sizey+1]
    g = np.exp(-0.333*(x**2/float(sizex)+y**2/float(sizey)))
    rows, columns = g.shape
    print ('ROWS: %s\n COLUMNS: %s\n' % (rows,columns))
    filter = g/g.sum()
    demSmooth = signal.convolve(dem1,filter,mode='valid')
    rows, columns = demSmooth.shape
    print ('ROWS: %s\n COLUMNS: %s\n' % (rows,columns))
    # rescale so it lies between 0 and 1
    #demSmooth = (demSmooth - demSmooth.min())/(demSmooth.max() - demSmooth.min())
    numpy_array_to_raster('dem.tif',demSmooth,(1,1), 50)

create_dem()
