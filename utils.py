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

def lerp(a, b, t):

	return ((1 - t) * a) + (t * b)

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

def check_units_collision(unit_a, unit_b):

	#NOTE
	#could also be done check checking the units heading and closest point to other unit

	#early exit due to units being too far away from each other.
	if distance(unit_a.x, unit_a.y, unit_b.x, unit_b.y) > unit_a.unit_width/2 + unit_b.unit_width/2:

		return False

	for ((x_1, y_1), (x_2, y_2)) in unit_a.get_lines():

		for ((x_3, y_3), (x_4, y_4)) in unit_b.get_lines():

			if check_intersection(x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4):

				return True

	return False

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

def draw_info_card(screen, font, x, y, information):

	background_colour = (150, 150, 150)
	outline_colour = (0, 0, 0)
	text_colour = (0, 0, 0)

	line_buffer = 5
	width_buffer = 5

	text_to_render = []

	max_width = -float("inf")
	sum_height = 0

	for i in information:

		text = font.render(i, False, text_colour)

		max_width = max(max_width, text.get_width())
		sum_height += text.get_height()

		text_to_render.append(text)

	tl_x = x - max_width / 2 - width_buffer
	tl_y = y - sum_height - ((len(information) + 1) * line_buffer)

	pygame.draw.rect(screen, background_colour, (tl_x, tl_y, max_width + 2 * width_buffer, sum_height + (len(information) + 1) * line_buffer))
	pygame.draw.rect(screen, outline_colour, (tl_x, tl_y, max_width + 2 * width_buffer, sum_height + (len(information) + 1) * line_buffer), 1)

	text_x = tl_x + width_buffer
	text_y = tl_y + line_buffer

	for index, t in enumerate(text_to_render):

		screen.blit(t, (text_x, text_y))

		text_y += t.get_height() + line_buffer

def line_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):

	uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
	uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))

	return (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1)

def get_front_line(x, y, width, height, radius, heading):

	angle_to_tl = math.atan2(height * -0.5, width * -0.5)
	tl_x, tl_y = polar(x, y, radius, angle_to_tl + heading + math.pi/2)

	angle_to_tr = math.atan2(height * -0.5, width * 0.5)
	tr_x, tr_y = polar(x, y, radius, angle_to_tr + heading + math.pi/2)

	return tl_x, tl_y, tr_x, tr_y