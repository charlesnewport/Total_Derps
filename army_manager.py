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

	def assign_positions(self, units, keys):

		total_highlighted = count_highlighted(units)

		if total_highlighted == 0:

			return

		line_length = distance(self.x_1, self.y_1, self.x_2, self.y_2)
		line_angle = math.atan2(self.y_2 - self.y_1, self.x_2 - self.x_1)

		if total_highlighted == 1:

			for unit in units:

				if unit.highlight:

					unit.set_target((self.x_1, self.y_1), line_angle - math.pi/2, append=keys[pygame.K_LSHIFT])

					return

		line_start_x = self.x_1
		line_start_y = self.y_1

		#min line_length here
		unit_buffer = units[0].unit_height / 4
		min_line_length = (total_highlighted * units[0].unit_width) + ((total_highlighted - 1) * unit_buffer)

		line_length = max(line_length, min_line_length)

		if self.x_1 == self.x_2 and self.y_1 == self.y_2:

			line_start_x, line_start_y = polar(self.x_1, self.y_1, line_length/2, line_angle - math.pi)

		increment = line_length / total_highlighted

		points = []

		for i in range(total_highlighted):

			points.append(polar(line_start_x, line_start_y, i * increment, line_angle))

		point_index = 0

		for unit in units:

			if unit.highlight:

				unit.set_target(points[point_index], line_angle - math.pi/2, append=keys[pygame.K_LSHIFT])
				point_index += 1

	def right_click(self, units, enemy_units, keys, mouse_buttons, mouse_pos):

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

				#Check if unit was attacked
				attack_created = False

				#temp ideas
				for enemy_unit in enemy_units:

					if point_in_unit(mouse_pos[0], mouse_pos[1], enemy_unit):

						for unit in units:

							if unit.highlight:

								unit.set_enemy(enemy_unit, append=keys[pygame.K_LSHIFT])

								attack_created = True

				if attack_created:

					#Clear previous points
					self.x_1 = None
					self.y_1 = None

					self.x_2 = None
					self.y_2 = None

					return

				#Else move unit(s)
				self.assign_positions(units, keys)

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

		#Select infantry
		if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and keys[pygame.K_i]:

			for unit in units:
				
				unit.highlight = not (unit.unit_class == "Missile" or unit.unit_type.lower() == "cavalry")

		#Select missiles
		if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and keys[pygame.K_m]:

			for unit in units:
				
				unit.highlight = unit.unit_class == "Missile"

		if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and keys[pygame.K_a]:

			for unit in units:
				
				unit.highlight = True

		if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and keys[pygame.K_c]:

			for unit in units:
				
				unit.highlight = unit.unit_type == "cavalry"


		# if keys[pygame.K_a]:

		# 	for unit in units:

		# 		if unit.highlight and unit.unit_class == "Missile":

		# 			unit.fire_at_will = not unit.fire_at_will

		if keys[pygame.K_BACKSPACE]:

			for unit in units:

				if unit.highlight:

					unit.cancel_orders()


	def update(self, units, enemy_units, keys, mouse_buttons, mouse_pos):

		self.left_click(units, keys, mouse_buttons, mouse_pos)
		self.right_click(units, enemy_units, keys, mouse_buttons, mouse_pos)

		#Update Click Booleans
		self.left_was_pressed = mouse_buttons[0]			
		self.right_was_pressed = mouse_buttons[2]

		self.keyboard_events(units, keys)

	def draw(self, screen, units):

		# pygame.draw.circle(screen, (255, 0, 0), (self.x_1, self.y_1), 10, 1)

		if self.left_was_pressed:

			if self.x_1 != None and self.x_2 != None and self.y_1 != None and self.y_2 != None:

				x_1, x_2 = sorted([self.x_1, self.x_2])
				y_1, y_2 = sorted([self.y_1, self.y_2])

				pygame.draw.rect(screen, (0, 255, 0), (x_1, y_1, x_2 - x_1, y_2 - y_1), 1)

		if self.right_was_pressed:

			if self.x_1 != None and self.x_2 != None and self.y_1 != None and self.y_2 != None:

				total_highlighted = count_highlighted(units)

				if total_highlighted == 0:

					return

				line_length = distance(self.x_1, self.y_1, self.x_2, self.y_2)
				line_angle = math.atan2(self.y_2 - self.y_1, self.x_2 - self.x_1)

				# line_length = max(line_length, (total_highlighted * units[0].unit_width) + ((total_highlighted - 1) * units[0].unit_height/4))

				unit_buffer = units[0].unit_height / 4
				min_line_length = (total_highlighted * units[0].unit_width) + ((total_highlighted - 1) * unit_buffer)

				line_length = max(line_length, min_line_length)

				line_start_x = self.x_1
				line_start_y = self.y_1

				if total_highlighted == 1:

					polygon_points = get_hypothetical_polygon(line_start_x, line_start_y, units[0].unit_height, units[0].unit_width, units[0].unit_radius, line_angle)

					pygame.draw.polygon(screen, (255, 255, 0), polygon_points, 1)

					return

				if self.x_1 == self.x_2 and self.y_1 == self.y_2:

					line_start_x, line_start_y = polar(self.x_1, self.y_1, line_length/2, line_angle - math.pi)

				# increment = line_length / (total_highlighted - 1)
				increment = line_length / total_highlighted

				points = []

				for i in range(total_highlighted):

					points.append(polar(line_start_x, line_start_y, i * increment, line_angle))

				for p in points:

					polygon_points = get_hypothetical_polygon(p[0], p[1], units[0].unit_height, units[0].unit_width, units[0].unit_radius, line_angle)

					pygame.draw.polygon(screen, (255, 255, 0), polygon_points, 1)
