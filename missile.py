from utils import lerp, distance, polar

import pygame
import random
import math

class Missile:

	def __init__(self, x, y, t_x, t_y, missile_attack_skill, missile_attack_range, is_armour_piercing):

		self.x = x
		self.y = y

		self.t_x = t_x
		self.t_y = t_y

		self.missile_attack_skill = missile_attack_skill
		self.missile_attack_range = missile_attack_range

		self.is_armour_piercing = is_armour_piercing

		self.speed = 10

		self.distance_to_target = distance(self.x, self.y, self.t_x, self.t_y)

		#Base Variables
		self.base_radius_uncertainty = 31/2 #unit_width/2
		self.min_radius_unceratinty_bonus = 0
		self.max_radius_unceratinty_bonus = 31*2 #arrows could be one full unit's width away

		#Create final radius uncerctainty. Lerp between 0 and max distance.
		# self.radius_uncertainty = self.base_radius_uncertainty + lerp(self.min_radius_unceratinty_bonus, self.max_radius_unceratinty_bonus, self.distance_to_target / self.missile_attack_range)
		self.radius_uncertainty = self.base_radius_uncertainty + lerp(self.min_radius_unceratinty_bonus, self.max_radius_unceratinty_bonus, self.distance_to_target / self.missile_attack_range)

		#Random radius
		self.random_radius = random.uniform(0, self.radius_uncertainty)

		#Rand angle
		self.random_angle = random.uniform(0, 2 * math.pi)

		#Find the random point
		self.t_x, self.t_y = polar(self.t_x, self.t_y, self.random_radius, self.random_angle)

		self.heading = math.atan2(self.t_y - self.y, self.t_x - self.x)

	def update(self):

		x_speed, y_speed = polar(0, 0, self.speed, self.heading)

		self.x += x_speed
		self.y += y_speed

	def draw(self, screen):

		pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 2)

		pygame.draw.circle(screen, (255, 0, 0), (self.t_x, self.t_y), 2)
