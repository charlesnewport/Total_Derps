import numpy as np
import pygame
import math
import cv2

def polar(x, y, radius, angle):

	return x + (radius * math.cos(angle)), y + (radius * math.sin(angle))

def colour_unit(unit_icon, unit_colour):

	rows, cols, _ = unit_icon.shape

	image_1d = unit_icon.reshape(rows * cols, 3)

	image_1d = np.where(image_1d == np.array([0, 0, 0]), np.array(unit_colour), image_1d)

	image = image_1d.reshape(rows, cols, 3).astype(np.uint8)

	# return pygame.image.frombuffer(image.flatten(), (cols, rows), "RGB")
	return pygame.transform.flip(pygame.surfarray.make_surface(image).convert_alpha(), False, True)

def distance(x1, y1, x2, y2):

	return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def check_intersection(x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4):

	d = ((y_4-y_3)*(x_2-x_1) - (x_4-x_3)*(y_2-y_1))

	if d == 0:

		return False

	uA = ((x_4-x_3)*(y_1-y_3) - (y_4-y_3)*(x_1-x_3)) / d
	uB = ((x_2-x_1)*(y_1-y_3) - (y_2-y_1)*(x_1-x_3)) / d
	
	return uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1

def intersection_point(x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4):

	#assumes already intersecting

	d = ((y_4-y_3)*(x_2-x_1) - (x_4-x_3)*(y_2-y_1))

	if d == 0:

		return False

	uA = ((x_4-x_3)*(y_1-y_3) - (y_4-y_3)*(x_1-x_3)) / d
	uB = ((x_2-x_1)*(y_1-y_3) - (y_2-y_1)*(x_1-x_3)) / d
	
	iX = x_1 + (uA * (x_2 - x_1))
	iY = y_1 + (uA * (y_2 - y_1))

	return iX, iY

def get_hypothetical_polygon(unit_x, unit_y, unit_height, unit_width, radius, angle):

	combs = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5),  (0.5, -0.5)]

	angles = []

	for x, y in combs:

		angles.append(math.atan2(unit_height * y, unit_width * x))

	return [polar(unit_x, unit_y, radius, theta + angle) for theta in angles]

def count_highlighted(units):

	return sum([1 for unit in units if unit.highlight])

def point_in_unit(m_x, m_y, unit):#(p_x, p_y, polygon_points):

	lines = unit.get_lines()
	points = unit.get_points()

	intersection_count = 0

	intersections = []

	for x, y in points:

		for ((x_1, y_1), (x_2, y_2)) in lines:

			if check_intersection(x_1, y_1, x_2, y_2, m_x, m_y, x, y):

				intersection_count += 1

				intersections.append(intersection_point(x_1, y_1, x_2, y_2, m_x, m_y, x, y))

	intersections = [i for i in intersections if i not in points]

	# return intersection_count == len(lines) * 2
	return len(intersections) == 0

def unit_in_rectangle(unit, x_1, y_1, x_2, y_2):

	x_1, x_2 = sorted([x_1, x_2])
	y_1, y_2 = sorted([y_1, y_2])

	return unit.x <= x_2 and unit.x >= x_1 and unit.y <= y_2 and unit.y >= y_1


	# highlight_points = [(x_1, y_1), (x_2, y_2), (x_1, y_2), (x_2, y_1)]

	# highlight_lines = []

	# for i in range(1, len(highlight_points)):

	# 	highlight_lines.append([highlight_points[i], highlight_points[i-1]])

	# highlight_lines.append((highlight_points[0], highlight_points[-1]))

	# for ((x_1, y_1), (x_2, y_2)) in highlight_lines:

	# 	for ((x_3, y_3), (x_4, y_4)) in unit.get_lines():

	# 		if check_intersection(x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4):

	# 			return True

	# return False


	# #check if any lines collide
