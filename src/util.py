# -*- coding: utf-8 -*-

from math import sqrt

def dist(col1, col2):
    return sqrt(sum([(col1[i]-col2[i])**2 for i in range(3)]))

def sort_dictionnary(dic):
    return {e:dic[e] for e in sorted(dic)}
    
def give_bottom_left_corner(points):
    """"
    Give the bottom left point of the rectangle containing the given points.
    It could be one of the given points.
    """
    bottom_left_corner = list(points[0])
    for point in points:
        if point[0]<bottom_left_corner[0]:      # update the min x
            bottom_left_corner[0] = point[0]
        if point[1]<bottom_left_corner[1]:      # update the min y
            bottom_left_corner[1] = point[1]
    return tuple(bottom_left_corner)


def give_top_right_corner(points):
    """"
    Give the top right point of the rectangle containing the given points.
    It could be one of the given points.
    """
    top_right_corner = list(points[0])
    for point in points:
        if point[0]>top_right_corner[0]:        # update the max x
            top_right_corner[0] = point[0]
        if point[1]>top_right_corner[1]:        # update the max y
            top_right_corner[1] = point[1]
    return tuple(top_right_corner)

def is_inside(rectangle, button):  
    """
    Return true if the button is inside the rectangle.
    rectangle and button are both lists of 2 elements containing bottom left point and top right point
    """    
    if button[0][0] > rectangle[0][0] and button[0][1] > rectangle[0][1] and button[1][0] < rectangle[1][0] and button[1][1] < rectangle[1][1]:
        return True
    else:
        return False
    
def bb_intersection_over_minimum(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    left = max(boxA.left, boxB.left)
    top = max(boxA.top, boxB.top)
    right = min(boxA.right, boxB.right)
    bottom = min(boxA.bottom, boxB.bottom)

    # compute the area of intersection rectangle
    interArea = max(0, right - left + 1) * max(0, bottom - top + 1)

    # compute the area of both bounding boxes
    boxAArea = (boxA.right - boxA.left + 1) * (boxA.bottom - boxA.top + 1)
    boxBArea = (boxB.right - boxB.left + 1) * (boxB.bottom - boxB.top + 1)

    # compute the intersection over minimum by taking the intersection
    # area and dividing it by the minimum of the two bounding box areas
    iom = interArea / float(min(boxAArea, boxBArea))

    return iom
