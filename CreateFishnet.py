
# coding: utf-8


from shapely import geometry
import geopandas as gpd
import utm
import numpy as np
import math


def divide_polygons_into_grids(grid_size, shp_file):
    """
    shp_file: the path of a polygon shapefile, crs: {'init': 'epsg:4326'}
    grid_size: 100m, 200m, ...
    """
    # Read shapefile using geopandas
    boundary = gpd.read_file(shp_file)
    [miny, minx, maxy, maxx] = boundary.geometry.bounds.values[0]

    # Transform wgs84 to UTM
    minx, miny, zone_number, zone_letter = utm.from_latlon(minx, miny)
    maxx, maxy, zone_number, zone_letter = utm.from_latlon(maxx, maxy)

    center_p = [(minx+maxx)/2, (miny+maxy)/2]

    dist_x = maxx - minx
    dist_y = maxy - miny
            
    num_x = math.ceil(dist_x / grid_size)
    num_y = math.ceil(dist_y / grid_size)

    grid_minx = center_p[0] - num_x*grid_size/2
    grid_maxx = center_p[0] + num_x*grid_size/2

    grid_miny = center_p[1] - num_y*grid_size/2
    grid_maxy = center_p[1] + num_y*grid_size/2

    grids_xs = np.linspace(start=grid_minx, stop=grid_maxx, num=num_x+1, endpoint=True)
    grids_ys = np.linspace(start=grid_miny, stop=grid_maxy, num=num_y+1, endpoint=True)

    polygons = []
    for i in range(len(grids_xs)-1):
        for j in range(len(grids_ys)-1):
            pointList = [[grids_xs[i], grids_ys[j]], [grids_xs[i+1], grids_ys[j]], 
                         [grids_xs[i+1], grids_ys[j+1]], [grids_xs[i], grids_ys[j+1]]]
            pointList = [utm.to_latlon(p[0], p[1], zone_number, zone_letter) for p in pointList]
        
            polygons.append(geometry.Polygon([[p[1], p[0]] for p in pointList]))
        
    grids_shp = gpd.GeoDataFrame(geometry=polygons, crs={'init': 'epsg:4326'})
    grids_within_bound = gpd.sjoin(grids_shp, south_side, how="inner", op='intersects')
                        
    grids_shp = gpd.GeoDataFrame(geometry=polygons, crs={'init': 'epsg:4326'})
    grids_within_poly = gpd.sjoin(grids_shp, boundary, how="inner", op='intersects')
    return grids_within_poly

