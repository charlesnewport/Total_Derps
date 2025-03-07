from utils import *

import pygame
import math

class Manager:

	def __init__(self, name):

		self.name = name

		self.x_1 = None
		self.y_1 = None

		self.x_2 = None
		self.y_2 = None

		self.left_was_pressed = False
		self.right_was_pressed = False

	def left_click(self, units, keys, mouse_buttons, mouse_pos):

		###LEFT CLICK

		#On Click
		if mouse_buttons[0]:

			#Update mouse locations
			if self.left_was_pressed:
				self.x_2, self.y_2 = mouse_pos
			else:
				self.x_1, self.y_1 = mouse_pos

		#No Click
		else:

			# On Release
			if self.left_was_pressed:

				#Highlight and Units in rectangle
				for unit in units:

					if unit_in_rectangle(unit, self.x_1, self.y_1, self.x_2, self.y_2):

						unit.highlight = True

					elif point_in_unit(self.x_1, self.y_1, unit):

						if keys[pygame.K_LCTRL]:

							unit.highlight = not unit.highlight

						else:

							unit.highlight = True

					else:

						if not keys[pygame.K_LCTRL]:

							unit.highlight = False

				#Clear previous points
				self.x_1 = None
				self.y_1 = None

				self.x_2 = None
				self.y_2 = None

	def assign_positions(self, units):

		total_highlighted = count_highlighted(units)

		if total_highlighted == 0:

			return

		line_length = distance(self.x_1, self.y_1, self.x_2, self.y_2)
		line_angle = math.atan2(self.y_2 - self.y_1, self.x_2 - self.x_1)

		if total_highlighted == 1:

			for unit in units:

				if unit.highlight:

					unit.set_target((self.x_1, self.y_1), line_angle - math.pi/2)

					return

		line_start_x = self.x_1
		line_start_y = self.y_1

		#min line_length here
		line_length = max(line_length, (total_highlighted * units[0].unit_width) + ((total_highlighted - 1) * units[0].unit_height/4))

		if self.x_1 == self.x_2 and self.y_1 == self.y_2:

			line_start_x, line_start_y = polar(self.x_1, self.y_1, line_length/2, line_angle - math.pi)


		increment = line_length / (total_highlighted - 1)

		points = []

		for i in range(total_highlighted):

			points.append(polar(line_start_x, line_start_y, i * increment, line_angle))

		point_index = 0

		for unit in units:

			if unit.highlight:

				unit.set_target(points[point_index], line_angle - math.pi/2)
				point_index += 1

	def right_click(self, units, keys, mouse_buttons, mouse_pos):

		#RIGHT CLICK

		#On Click
		if mouse_buttons[2]:

			#Update mouse locations
			if self.right_was_pressed:
				self.x_2, self.y_2 = mouse_pos
			else:
				self.x_1, self.y_1 = mouse_pos

		#No Click
		else:

			#On release
			if self.right_was_pressed:

				self.assign_positions(units)

				#Clear previous points
				self.x_1 = None
				self.y_1 = None

				self.x_2 = None
				self.y_2 = None

	def keyboard_events(self, units, keys):

		if keys[pygame.K_SPACE]:

			for unit in units:

				unit.draw_final_location = True

		else:

			for unit in units:

				unit.draw_final_location = False

	def update(self, units, keys, mouse_buttons, mouse_pos):

		self.left_click(units, keys, mouse_buttons, mouse_pos)
		self.right_click(units, keys, mouse_buttons, mouse_pos)

		#Update Click Booleans
		self.left_was_pressed = mouse_buttons[0]			
		self.right_was_pressed = mouse_buttons[2]

		self.keyboard_events(units, keys)

	def draw(self, screen, units):

		# pygame.draw.circle(screen, (255, 0, 0), (self.x_1, self.y_1), 10, 1)

		if self.left_was_pressed:

			print(self.x_1, self.y_1, self.x_2, self.y_2)

			if self.x_1 != None and self.x_2 != None and self.y_1 != None and self.y_2 != None:

				x_1, x_2 = sorted([self.x_1, self.x_2])
				y_1, y_2 = sorted([self.y_1, self.y_2])

				# pygame.draw.line(screen, (255, 0, 0), (self.x_1, self.y_1), (self.x_2, self.y_2), 1)
				pygame.draw.rect(screen, (0, 255, 0), (x_1, y_1, x_2 - x_1, y_2 - y_1), 1)

		if self.right_was_pressed:

			# print(self.x_1, self.y_1, self.x_2, self.y_2)

			if self.x_1 != None and self.x_2 != None and self.y_1 != None and self.y_2 != None:

				total_highlighted = count_highlighted(units)

				if total_highlighted == 0:

					return

				line_length = distance(self.x_1, self.y_1, self.x_2, self.y_2)
				line_angle = math.atan2(self.y_2 - self.y_1, self.x_2 - self.x_1)

				line_length = max(line_length, (total_highlighted * units[0].unit_width) + ((total_highlighted - 1) * units[0].unit_height/4))
				# line_length = max(line_length, (total_highlighted * units[0].unit_width) + ((total_highlighted - 1) * units[0].unit_width/4))

				line_start_x = self.x_1
				line_start_y = self.y_1

				if total_highlighted == 1:

					polygon_points = get_hypothetical_polygon(line_start_x, line_start_y, units[0].unit_height, units[0].unit_width, units[0].unit_radius, line_angle)

					pygame.draw.polygon(screen, (255, 255, 0), polygon_points, 1)

					return

				if self.x_1 == self.x_2 and self.y_1 == self.y_2:

					line_start_x, line_start_y = polar(self.x_1, self.y_1, line_length/2, line_angle - math.pi)

				increment = line_length / (total_highlighted - 1)

				points = []

				for i in range(total_highlighted):

					points.append(polar(line_start_x, line_start_y, i * increment, line_angle))

				for p in points:

					polygon_points = get_hypothetical_polygon(p[0], p[1], units[0].unit_height, units[0].unit_width, units[0].unit_radius, line_angle)

					pygame.draw.polygon(screen, (255, 255, 0), polygon_points, 1)


