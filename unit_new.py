from utils import *

import numpy as np
import pygame
import random
import math
import cv2

class Unit:

	def __init__(self, unit_class, x, y, unit_width, unit_height, colour):

		#UNIT INFO
		##TYPE
		self.unit_class = unit_class["unit_class"]

		##SIZE
		self.unit_size = unit_class["unit_size"]

		###UNUSED
		self.morale = unit_class["unit_morale"]
		self.discipline = unit_class["unit_discipline"]

		###MELEE
		self.melee_attack_skill = unit_class["melee_weapon"]["attack_skill"]
		self.melee_armour_piercing = unit_class["melee_weapon"]["armour_piercing"]
		self.charge_bonus = unit_class["melee_weapon"]["charge_bonus"]

		self.melee_cooldown_time = 4 * 60 #FPS
		self.melee_cooldown_time_counter = 0

		###DEFENCE
		self.defence_skill = unit_class["defence"]["defence_skill"]
		self.armour = unit_class["defence"]["armour"]
		self.shield = unit_class["defence"]["shield"]
		self.hitpoints = unit_class["defence"]["hitpoints"]

		self.hitpoints_array = [self.hitpoints for _ in range(self.unit_size)]

		#MOVEMENT / POSITION
		##SPEEDS
		self.walking_speed = 0.5
		self.running_speed = 1

		##SPEED BOOLEAN
		self.is_running = False

		##POSITION
		self.x = x
		self.y = y

		##HEADING
		self.heading = -math.pi/2

		#DISPLAY
		##DISPLAY SIZE
		self.unit_width = unit_width
		self.unit_height = unit_height

		##ICON INFORMATION
		self.colour = colour
		self.image = colour_unit(cv2.imread("Images/" + unit_class["unit_image"] + ".png"), self.colour)

		##INTERACTION
		self.highlight = False
		self.draw_final_location = False
		self.unit_radius = math.sqrt((self.unit_width ** 2) + (self.unit_height ** 2)) / 2

		#STATE MANAGEMENT
		##CURRENT STATE
		self.STATE = 0

		##STATE 1 - MOVEMENT VARIABLES
		self.target = None
		self.target_heading = None

		self.target_min_distance = self.walking_speed

		##STATE 2 - Seeking

		##STATE 3 - Attacking
		self.enemy_target = None

	def movement(self):

		#If it has arrived
		if distance(self.target[0], self.target[1], self.x, self.y) < self.target_min_distance:

			#Clear target
			self.x, self.y = self.target
			self.target = None
			self.heading = self.target_heading

			#Set STATE to idle
			self.STATE = 0

			return

		angle_to_target = math.atan2(self.target[1] - self.y, self.target[0] - self.x)

		#set heading = angle_to_target
		self.heading = angle_to_target

		x_speed, y_speed = polar(0, 0, self.running_speed if self.is_running else self.walking_speed, angle_to_target)

		self.x += x_speed
		self.y += y_speed

	def set_target(self, target, target_heading):

		#Set Target
		self.target = target
		self.target_heading = target_heading

		#Set STATE = 1 (Movement)
		self.STATE = 1

	def reset_target(self):

		#Reset Target, Target Heading
		self.target = None
		self.target_heading = None

		#TEMPORARY
		#Set STATE = 0 (Idle)
		self.STATE = 0

	def get_defenders(self):

		return min(self.unit_size, 10)

	def melee_attack(self, enemy_unit):

		a = self.melee_attack_skill
		#apply directionality here (attacking from rear removes shield points)
		d = enemy_unit.defence_skill + enemy_unit.armour + enemy_unit.shield

		#Amour piercing removes half of the defending units armour
		if self.melee_armour_piercing:

			d -= enemy_unit.armour / 2

		#get total defender
		total_defenders = enemy_unit.get_defenders()

		total_attackers = min(self.unit_size, 10)

		# attackers_per_defender = total_attackers / total_defenders
		#how to evenly split these?

		#resolve conflict here
		p_hit = 0
		if a < d:

			p_hit = (a + 1) / (2 * d)

		else:

			p_hit = ((2 * a) - d + 1) / (2 * a)

		total_wins = sum([1 for i in range(total_defenders) if random.random() <= p_hit])

		enemy_unit.resolve_skirmish(total_wins)

		self.melee_cooldown_time_counter = 0

	def check_collisions(self, opposition_units):

		#Using enemy_target as an array of units that are currently being targeted vs
		#Using enemy_target as a unit that the enemy should move towards.

		enemies_collided_with = [opposition_unit for opposition_unit in opposition_units if check_units_collision(self, opposition_unit)]

		if len(enemies_collided_with) == 0:

			return

		self.reset_target()

		if not self.can_attack():

			return

		self.melee_attack(enemies_collided_with[0])

	def resolve_skirmish(self, total_wins):

		for i in range(len(self.hitpoints_array)-1, len(self.hitpoints_array) - total_wins - 1, -1):

			self.hitpoints_array[i] -= 1

			if self.hitpoints_array[i] == 0:

				del(self.hitpoints_array[i])
				self.unit_size -= 1

	def can_attack(self):

		return self.melee_cooldown_time_counter >= self.melee_cooldown_time

	def update(self, opposition_units):

		self.melee_cooldown_time_counter += 1

		self.check_collisions(opposition_units)

		#STATE SPECIFIC LOGIC

		#IDLE
		if self.STATE == 0:

			return

		#MOVING
		elif self.STATE == 1:

			self.movement()

		#SEEKING
		elif self.STATE == 2:

			pass

		#ATTACKING
		elif self.STATE == 3:

			pass

	def get_points(self):

		combs = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5),  (0.5, -0.5)]

		angles = []

		for x, y in combs:

			angles.append(math.atan2(self.unit_height * y, self.unit_width * x))

		return [polar(self.x, self.y, self.unit_radius, theta + self.heading + math.pi/2) for theta in angles]

	def get_lines(self):

		lines = []

		points = self.get_points()

		for i in range(1, len(points)):

			lines.append([points[i], points[i-1]])

		lines.append((points[0], points[-1]))

		return lines

	def draw_movement_lines(self, screen):

		if self.target != None:

			pygame.draw.line(screen, (255, 255, 0), (self.x, self.y), self.target, 3)

	def draw_movement_end(self, screen):

		polygon = get_hypothetical_polygon(self.target[0], self.target[1], self.unit_height, self.unit_width, self.unit_radius, self.target_heading - math.pi/2)

		pygame.draw.polygon(screen, (255, 255, 0), polygon, 1)

	def highlight_unit(self, screen):

		pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y),  self.unit_radius, 1)

	def draw(self, screen):

		if self.highlight:

			self.highlight_unit(screen)

			self.draw_movement_lines(screen)

		if self.draw_final_location and self.target != None:

			self.draw_movement_end(screen)

		#Rotate unit Image by unit Heading
		temp_image = pygame.transform.rotate(self.image, math.degrees(-self.heading + math.pi))

		#Calculate the Width and Height of the image to offset around the Center (x, y)
		w = temp_image.get_width()
		h = temp_image.get_height()

		#Draw image
		screen.blit(temp_image, (self.x - w / 2, self.y - h / 2))

class Archer(Unit):

	def __init__(self, x, y, unit_width, unit_height, unit_class):

		#SETUP PARENT
		super().__init__(x, y, unit_width, unit_height, unit_class)

		#RANGED STATS
		self.ranged_attack_skill = unit_class["ranged_weapon"]["attack_skill"]
		self.ranged_attack_range = unit_class["ranged_weapon"]["range"]
		self.ranged_armour_piercing = unit_class["ranged_weapon"]["armour_piercing"]
		self.ranged_ammunition = unit_class["ranged_weapon"]["ammunition"]

		#SPECIFIC BEHAVIOUS
		self.fire_at_will = False
		self.skirmish_mode = False
		#These will not include artillery

	def update(self):

		if self.STATE == 0:

			pass

		elif self.STATE == 1:

			pass

		elif self.STATE == 2:

			pass