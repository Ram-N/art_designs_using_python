
from datetime import datetime
import math
from math import pi, sin, cos, sqrt

from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, Ellipse, Polygon, Wedge
import matplotlib.pyplot as plt

import numpy as np


def hex_corner(center, size, i, flat=True):
    '''Return the ith vertex of a regular hex with center of size i and flat/pointy orientation'''

    if flat:
        angle_rad = PI / 180 * (60*i)
    else:
        angle_rad = PI / 180 * (60*i-30)
        
    return Point(center.x + size * cos(angle_rad),
                 center.y + size * sin(angle_rad))

  


class Point():
    def __init__(self, x, y):
        '''Defines x and y coordinates'''
        self.x = x
        self.y = y
        
    def __str__(self):
        return "Point(%s,%s)"%(self.x,self.y)

class Hex():
    """Represents one Hexagon. Typically on a hexagonal grid
    
    The hexagon can be flat topped (flat = True) or pointy-topped (flat=False)
    Each Hexagon has:
    a center (x,y)
    size (of its edge)
    flat = True (or False if Pointy-topped)
    verts = xy of its 6 vertices
    h = height of the hexaxon from top to bottom
    w = width = distance between 2 adjacent centers to the right/left of each other
    
    """
    def __init__(self, x, y, size=1, flat=True, h=None, w=None, cube=None):
        '''Define properties of one single Hexagon'''
        self.x = x
        self.y = y
        self.center= Point(x, y)
        
        self.size = size
        self.flat = flat
        self.verts = None
        
        if self.flat:
            self.h = sqrt(3) * size
            self.w = 2 * size
        else:
            self.w = sqrt(3) * size
            self.h = 2 * size
            
        self.cube = cube # cube coords of this particular hex

    def __str__(self):
        desc = 'Flat' if self.flat else 'Pointy'
        return f" {desc}-Hex @ {(self.x,self.y)} size {self.size}"
    
        
    def get_verts(self):
        ''' Calculate all 6 verticles of the hex'''
        verts = []
        for v in range(6):
            verts.append(hex_corner(self.center, self.size, v, self.flat))
            
        self.verts = verts
        return self.verts

    def render_border(self, ax=None, **kwargs):
        """ Draws all 6 borders of a given Hexagon. fc will color the face."""
                
        if ax is None:
            ax = plt.gca()
            
        rot_radians = pi/6 if self.flat else 0
        polygon = mpatches.RegularPolygon((self.x, self.y), 
                                         numVertices=6, radius=self.size,   
                                         orientation=rot_radians,
                                          **kwargs)
        ax.add_patch(polygon)
        return ax,

    def render(self, ax=None, **kwargs):
        """ Draws the edges of a given Hexagon. fc will color the face."""
                
        if ax is None:
            ax = plt.gca()
            
        if self.verts:
            vs = self.verts
        else:
            vs = self.get_verts()
                    

        rot_radians = pi/6 if self.flat else 0
        polygon = mpatches.RegularPolygon((self.x, self.y), 
                                         numVertices=6, radius=self.size,   
                                         orientation=rot_radians,
                                          **kwargs)
        ax.add_patch(polygon)
                    
        if 0: #planning to use this if optionally only specified edges are to be drawn...
            x_arr = [v.x for v in vs] + [vs[0].x]
            y_arr = [v.y for v in vs] + [vs[0].y]
            edge = Line2D([x_arr],[y_arr], **kwargs)
            ax.add_line(edge)

        return ax,

    
    def v_connect(self, v_pairs, ax=None, **kwargs):
        """ Draws edges from specific vertices to specified vertices..."""
                
        if ax is None:
            ax = plt.gca()
            
        
        if self.verts is None:
            self.verts = self.get_verts()

        #for each vp in v_pairs, connect vi to vj by drawing a Line2D
        for i, j in v_pairs:
            #print(i, j)
            #plot this line for this hexagon
            x_arr = [self.verts[i].x, self.verts[j].x]
            y_arr = [self.verts[i].y, self.verts[j].y]            
            edge = Line2D([x_arr],[y_arr], **kwargs)
            ax.add_line(edge)
        return ax,

    
    def render_spokes(self, vlist, ax=None, **kwargs):
        """ Draws spokes from center to specific vertices"""
                
        if ax is None:
            ax = plt.gca()
            
        if self.verts is None:
            self.verts = self.get_verts()

        #for each vp in v_pairs, connect vi to vj by drawing a Line2D
        for v in vlist:
            x_arr = [self.verts[v].x, self.x]
            y_arr = [self.verts[v].y, self.y]            
            edge = Line2D([x_arr],[y_arr], **kwargs)
            ax.add_line(edge)
        return ax,

    def render_regular_polygon_from_center(self, polygon_sides, polygon_size=None, angle_radians=None, ax=None, **kwargs):
        """ Draws a regular polygon that shares its center with hexagon

            Useful for drawing polygon _within_ the existing hexagonal space. For example, smaller hexagons inside the main grid.
        
            Parameters: 

                polygon_sides = number of sides in the regular polygon

                polygon_size = Size of the polygon's side to be drawn. (defaults to hexagon's size)
                angle_radians = will rotate the regular polygon by radians angle
                fc:  will color the face

        """
                
        if ax is None:
            ax = plt.gca()

        if polygon_size is None:
            polygon_size = self.size

        if angle_radians is None:
            angle_radians = 0
            if polygon_sides == 6 and self.flat:            
                angle_radians = pi/6 
                
        polygon = mpatches.RegularPolygon((self.x, self.y), 
                                         numVertices=polygon_sides, 
                                         radius=polygon_size,   
                                         orientation=angle_radians,
                                          **kwargs)
        ax.add_patch(polygon)
        return ax,

    
    def render_polygon(self, pt_list, include_center, ax=None, **kwargs):
        """ Draw a Polygon to connect specific vertices and optionally center
        
        
        Parameters:
        
        include_center: Boolean
            Indicates whether the Center of the hexagon should to a vertex of the Polygon being rendered
        
        """
                
        if ax is None:
            ax = plt.gca()
            
        if self.verts is None:
            self.verts = self.get_verts()

        #Make a polygon of all the pts in pt_list
        xy_arr = []        
        if include_center:
            xy_arr.append([self.x, self.y])            
        
        for v in pt_list:
            if v in range(6):
                xy_arr.append([self.verts[v].x, self.verts[v].y])            
            
        polygon = Polygon(xy_arr,
                          closed=True,
                          **kwargs)            
        ax.add_patch(polygon)

        return ax,




    
class HexGrid():

    """Represents the a hexagonal grid as painted on the screen.
    The hex grid can be flat topped (flat = True) or pointy-topped (flat=False)
    
    It has a list of hexs in hlist
    And there is a rectangle (a bounding box) for the grid, since it has to be rendered in the xy plane
    
    """
    def __init__(self, num_rows, num_cols, size=1, flat=True, rect_h=None, rect_w=None):
        
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.size = size
        self.flat = flat
        self.hlist = []
        self.centers = []
        
        if flat:
            hexh = sqrt(3) * size
            hexw = 2 * size
            xdist = 3/2*hexw
            ydist = hexh/2
        else:
            hexw = sqrt(3) * size
            hexh = 2 * size
            ydist = 3/4*hexh
            xdist = hexw
        
        for row in range(num_rows):
            if flat:
                xoffset = (3/4*hexw if row%2 else 0) - ((num_cols+1)*size)
                yoffset = -1 * hexh * (num_rows // 4)
            else:
                xoffset = (0 if row%2 else hexw/2 ) - (num_cols//2 * hexw)       
                yoffset = -1 * (hexh * (num_rows // 2)) + (size*(num_rows//2-1))

            for col in range(num_cols):        
                c = Point(xoffset + col*xdist, ydist*row + yoffset)
                hx = Hex(c.x, c.y, size, flat=flat) #instantiate Hex based on center and size
                hx.get_verts()
                self.hlist.append(hx) 
                self.centers.append(c)
                
                
    def __str__(self):
        desc = 'Flat' if self.flat else 'Pointy'
        str1 = f" HexGrid: {len(self.centers)} {desc}-hexagons {self.num_rows} by {self.num_cols} of size {self.size}\n"
        return str1
    
    
    def render_grid(self, **kwargs):
        
        for h in self.hlist:
            h.render(**kwargs)
            
        plt.axis('on');    
        ax.axis('scaled')

        
    def render_grid_vconnect(self, v_pairs=None, **kwargs):
        """ For entire HexGrid connect vert to vert without necessarily going through the center"""
        
        if v_pairs is not None:
            for h in self.hlist:
                h.v_connect(v_pairs, **kwargs)
                            
        plt.axis('on');    
        ax.axis('scaled')

        
    def render_grid_spokes(self, c_to_vlist=None, **kwargs):
        """ For entire HexGrid connect center to specified vertices"""
        if c_to_vlist is not None:
            for h in self.hlist:
                h.render_spokes(c_to_vlist, **kwargs)
            
        plt.axis('on');    
        ax.axis('scaled')

    def render_grid_polygons(self, pt_list=None, **kwargs):
        """ For entire HexGrid connect center to vlist"""
        
        # connect from hex center to each of the specified vertices
        if pt_list is not None:
            for h in self.hlist:
                h.render_polygon(pt_list, **kwargs)
            
        
        
    def render_grid_vertices(self, **kwargs):
        for h in self.hlist:
            for v in h.verts[:3]:
                plt.scatter(v.x, v.y, **kwargs)

                plt.scatter(h.x, h.y, **kwargs)

        #plt.axis('scaled')
        plt.axis('on');    
        ax.axis('scaled')


PI = math.pi

