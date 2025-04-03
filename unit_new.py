from missile import Missile
from utils import *

import numpy as np
import pygame
import random
import math
import uuid
import cv2

class Unit:

	def __init__(self, unit_class, x, y, unit_width, unit_height, colour):

		#UNIT INFO
		##TYPE
		self.unit_class = unit_class["unit_class"]
		self.unit_type = unit_class["unit_type"]
		self.unit_name = unit_class["unit_name"]

		##SIZE
		self.unit_size = unit_class["unit_size"]

		###UNUSED
		self.morale = unit_class["unit_morale"]
		self.discipline = unit_class["unit_discipline"]

		###MELEE
		self.melee_attack_skill = unit_class["melee_weapon"]["attack_skill"]
		self.melee_armour_piercing = unit_class["melee_weapon"]["armour_piercing"]

		self.melee_cooldown_time = 4 * 60 #FPS
		self.melee_cooldown_time_counter = random.randint(0, self.melee_cooldown_time)

		####Charge Bonus
		self.charge_bonus = unit_class["melee_weapon"]["charge_bonus"]

		self.charge_bonus_total_time = 30 * 60
		self.charge_bonus_timer = 0

		self.was_colliding = False

		###DEFENCE
		self.defence_skill = unit_class["defence"]["defence_skill"]
		self.armour = unit_class["defence"]["armour"]
		self.shield = unit_class["defence"]["shield"]
		self.hitpoints = unit_class["defence"]["hitpoints"]

		self.hitpoints_array = [self.hitpoints for _ in range(self.unit_size)]

		#MOVEMENT / POSITION
		##SPEEDS
		self.walking_speed = 0.25
		self.running_speed = 0.5

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

		#UNIT BEHAVIOURS
		self.guard_mode = False

		#STATE MANAGEMENT
		##CURRENT STATE
		self.STATE = 0

		##STATE 1 - MOVEMENT VARIABLES
		self.targets = []
		self.target_headings = []

		self.target_min_distance = self.walking_speed

		##STATE 2 - Seeking

		##STATE 3 - Attacking
		self.enemy_target = None

		#ID
		self.unit_id = str(uuid.uuid4())

	def get_strength(self):

		return self.unit_size * (self.melee_attack_skill + self.charge_bonus + self.defence_skill + self.shield + self.armour) + sum(self.hitpoints_array)

	def __equal__(self, test):

		return self.id == test.id

	def get_information(self):

		return [
			self.unit_name,
			"Unit class: " + self.unit_class,
			"Troops: " + str(self.unit_size),
			"Has Charge Bonus: " + str(self.has_charge_bonus())
		]

	def cancel_orders(self):

		self.reset_enemy()
		self.reset_target()

	def idle(self, enemy_units):

		if len(self.targets) == 0:

			if self.enemy_target != None:

				self.STATE = 2

		else:

			self.STATE = 1

	def movement(self):

		#If it has arrived
		if distance(self.targets[0][0], self.targets[0][1], self.x, self.y) < self.target_min_distance:

			#Clear target
			self.x, self.y = self.targets[0]
			self.heading = self.target_headings[0]

			del(self.targets[0])
			del(self.target_headings[0])

			#Set STATE to idle
			self.STATE = 0

			return

		self.move_to_target(self.targets[0][0], self.targets[0][1])

	def seeking(self):

		e_x = self.enemy_target.x
		e_y = self.enemy_target.y

		self.move_to_target(e_x, e_y)

	def move_to_target(self, t_x, t_y):

		angle_to_target = math.atan2(t_y - self.y, t_x - self.x)

		self.heading = angle_to_target

		x_speed, y_speed = polar(0, 0, self.running_speed if self.is_running else self.walking_speed, angle_to_target)

		self.x += x_speed
		self.y += y_speed

	def set_target(self, target, target_heading, append=False):

		if not append:

			#Set Target
			self.targets = [target]
			self.target_headings = [target_heading]

		else:

			self.targets.append(target)
			self.target_headings.append(target_heading)

		#Reset Enemy Unit
		self.reset_enemy()
		#Set STATE = 1 (Movement)

		self.STATE = 1

	def reset_target(self):

		#Reset Target, Target Heading
		self.targets = []
		self.target_headings = []

		#TEMPORARY
		#Set STATE = 0 (Idle)
		self.STATE = 0

	def get_defenders(self):

		return min(self.unit_size, 10)

	def has_charge_bonus(self):

		return self.is_running and self.was_colliding and self.charge_bonus_timer <= self.charge_bonus_total_time

	def melee_attack(self, enemy_unit):

		a = self.melee_attack_skill

		#apply charge bonus
		if self.has_charge_bonus():

			a += self.charge_bonus

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

			#reset bonus timer
			self.was_colliding = False
			self.charge_bonus_timer = 0

			return

		self.was_colliding = True

		#reset any movement targets
		self.reset_enemy()
		self.reset_target()

		if not self.can_melee_attack():

			return

		self.melee_attack(enemies_collided_with[0])

	def resolve_skirmish(self, total_wins):

		for i in range(len(self.hitpoints_array)-1, len(self.hitpoints_array) - total_wins - 1, -1):

			self.hitpoints_array[i] -= 1

			if self.hitpoints_array[i] == 0:

				del(self.hitpoints_array[i])
				self.unit_size -= 1

	def can_melee_attack(self):

		return self.melee_cooldown_time_counter >= self.melee_cooldown_time

	def attack(self):

		pass

	def update_alarms(self):

		self.melee_cooldown_time_counter += 1

		if self.was_colliding:

			self.charge_bonus_timer += 1

	def update(self, opposition_units):

		self.update_alarms()

		#attacks automatically conducted based on collisions
		self.check_collisions(opposition_units)

		#STATE SPECIFIC LOGIC

		#IDLE
		if self.STATE == 0:

			self.idle(opposition_units)

		#MOVING
		elif self.STATE == 1:

			self.movement()

		#SEEKING
		elif self.STATE == 2:

			self.seeking()

		#ATTACKING
		elif self.STATE == 3:

			self.attack()

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

	def set_enemy(self, enemy_unit, append = False):

		self.enemy_target = enemy_unit

		#clears any movement targets
		if not append:

			self.reset_target()

			self.STATE = 2

	def append_enemy(self, enemy_unit):

		self.enemy_target = enemy_unit

	def reset_enemy(self):

		self.enemy_target = None
		self.STATE = 0

	def draw_movement_lines(self, screen):

		#if has enemy target
		#if has movement targets

		movement_lines_array = [(self.x, self.y)]

		if len(self.targets) != 0:

			movement_lines_array.extend(self.targets)

		movement_lines_len = len(movement_lines_array)

		if movement_lines_len == 2:

			l_1, l_2 = movement_lines_array

			pygame.draw.line(screen, (255, 255, 0), l_1, l_2, 3)

		elif movement_lines_len > 2:

			pygame.draw.lines(screen, (255, 255, 0), False, movement_lines_array, 3)

		if self.enemy_target != None:

			movement_lines_array.append((self.enemy_target.x, self.enemy_target.y))

			pygame.draw.line(screen, (255, 0, 0), movement_lines_array[-2], movement_lines_array[-1], 3)

	def draw_movement_end(self, screen):

		if self.enemy_target != None:

			final_target_x = self.enemy_target.x
			final_target_y = self.enemy_target.y

			final_heading = math.atan2(self.enemy_target.y - (self.y if len(self.targets) == 0 else self.targets[-1][1]), self.enemy_target.x - (self.x if len(self.targets) == 0 else self.targets[-1][0]))

		else:

			final_target_x = self.targets[-1][0]
			final_target_y = self.targets[-1][1]

			final_heading = self.target_headings[-1]

		polygon = get_hypothetical_polygon(final_target_x, final_target_y, self.unit_height, self.unit_width, self.unit_radius, final_heading - math.pi/2)

		pygame.draw.polygon(screen, (255, 255, 0), polygon, 1)

	def highlight_unit(self, screen):

		pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y),  self.unit_radius, 1)

	def draw(self, screen):

		if self.highlight:

			self.highlight_unit(screen)

			self.draw_movement_lines(screen)

		if self.draw_final_location and (self.targets != [] or self.enemy_target != None):

			self.draw_movement_end(screen)

		if self.enemy_target != None:
			
			pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (self.enemy_target.x, self.enemy_target.y))

		#Rotate unit Image by unit Heading
		temp_image = pygame.transform.rotate(self.image, math.degrees(-self.heading + math.pi))

		#Calculate the Width and Height of the image to offset around the Center (x, y)
		w = temp_image.get_width()
		h = temp_image.get_height()

		#Draw image
		screen.blit(temp_image, (self.x - w / 2, self.y - h / 2))

class Missile_Unit(Unit):

	def __init__(self, unit_class, x, y, unit_width, unit_height, unit_colour):

		#SETUP PARENT
		super().__init__(unit_class, x, y, unit_width, unit_height, unit_colour)

		#RANGED STATS
		self.ranged_attack_skill = unit_class["ranged_weapon"]["attack_skill"]
		self.ranged_attack_range = unit_class["ranged_weapon"]["range"] * (self.unit_width / 16)
		self.ranged_armour_piercing = unit_class["ranged_weapon"]["armour_piercing"]
		self.ranged_ammunition = unit_class["ranged_weapon"]["ammunition"]
		self.rate_of_fire = unit_class["ranged_weapon"]["rate_of_fire"] #RPM

		#RANGED COOLDOWN
		self.ranged_cooldown_time = 5 * 60 #FPS
		# self.ranged_cooldown_time = 60 * 60 / self.rate_of_fire
		self.ranged_cooldown_time_counter = self.ranged_cooldown_time#random.randint(0, self.ranged_cooldown_time)

		#SPECIFIC BEHAVIOUS
		self.fire_at_will = True
		self.skirmish_mode = False #This will not include artillery

		#PROJECTILES CREATED
		self.missiles = []

	def get_strength(self):

		if self.ranged_ammunition > 0:

			#could add rate of fire

			return self.unit_size * (self.ranged_attack_skill + self.defence_skill + self.shield + self.armour) + sum(self.hitpoints_array)

		return self.unit_size * (self.melee_attack_skill + self.charge_bonus + self.defence_skill + self.shield + self.armour) + sum(self.hitpoints_array)

	def get_information(self):

		return [
			self.unit_name,
			"Unit class: " + self.unit_class,
			"Troops: " + str(self.unit_size),
			"Ammunition: " + str(int(self.ranged_ammunition))
		]

	def seeking(self):

		e_x = self.enemy_target.x
		e_y = self.enemy_target.y

		self.move_to_target(e_x, e_y)

		if self.enemy_in_range():

			self.STATE = 3

	def can_missile_attack(self):

		return self.ranged_cooldown_time_counter >= self.ranged_cooldown_time and self.ranged_ammunition > 0

	def update_alarms(self):

		self.melee_cooldown_time_counter += 1

	#Overrides Idle from Parent
	def idle(self, enemy_units):

		if len(self.targets) == 0:

			if self.enemy_target != None:

				self.STATE = 2

		else:

			self.STATE = 1

		if not self.fire_at_will:

			return

		min_dist = float("inf")
		min_unit = None

		for unit in enemy_units:

			d = distance(self.x, self.y, unit.x, unit.y)

			#would need to account for triangle height
			if d < self.ranged_attack_range:

				if d < min_dist:

					min_dist = d
					min_unit = unit

		if min_unit != None:

			self.set_enemy(min_unit, False)

	def enemy_in_range(self):

		return distance(self.x, self.y, self.enemy_target.x, self.enemy_target.y) <= self.ranged_attack_range

	#Overriden from the parent "Unit" class
	def attack(self):

		#only update the counter if all missiles are expended
		#UPDATE could only update if not moving

		if len(self.missiles) == 0:
			self.ranged_cooldown_time_counter += 1

		#check enemy in range
		if not self.enemy_in_range():

			#Guard mode
			if self.guard_mode:

				self.cancel_orders()

			#No Guard mode - Seek enemy
			else:

				self.STATE = 2

		if not self.can_missile_attack():

			return

		#find the center of the front of the unit
		self.missiles = []

		for _ in range(self.unit_size):

			c_x, c_y = polar(self.x, self.y, self.unit_height / 2, self.heading)

			s_x, s_y = polar(c_x, c_y, self.unit_width / 2, self.heading - math.pi/2)
			e_x, e_y = polar(c_x, c_y, self.unit_width / 2, self.heading - math.pi/2 + math.pi)

			angle = math.atan2(e_y - s_y, e_x - s_x)

			r = random.randint(0, self.unit_width)

			p_x, p_y = polar(s_x, s_y, r, angle)

			self.missiles.append(Missile(p_x, p_y, self.enemy_target.x, self.enemy_target.y, self.ranged_attack_skill, self.ranged_attack_range, self.ranged_armour_piercing))

		self.ranged_cooldown_time_counter = 0
		self.ranged_ammunition -= 1

		#if right click, calculate position in range of target to aim from
		#when at position, begin firing

		#accuracy based on distance to target
		#future update will take into account any units in the way.
		#i.e. if firing from behind a friendly unit the accuracy will be lower as the arrows have to go over that unit.
		#arrows are an independent unit that inherits the missile classes' missile damager and armour piercing stats which
		#should allow it to damaged any unit it may hit (friend/foe)

		#TODO
		#If enemy_unit != None
		#Target enemy_unit x
		#Add arrows to main_new x
		#Add melee cooldown time x
		#Reset to idle on going out of range
		#is guardmode disabled, chase down.

	def draw_range_indicator(self, screen):

		self.shooting_angle = math.radians(45)

		#test firing radius/range
		points = self.get_points()

		#left handside
		l_x, l_y = points[2]

		#right handside
		r_x, r_y = points[3]

		#middle of front line
		mid_x = (l_x + r_x) / 2
		mid_y = (l_y + r_y) / 2

		#Find the origin of the curve

		##Triangle top corner angle
		theta_2 = math.pi - (self.shooting_angle / 2) - (math.pi / 2)

		##Height of the triangle
		h = (self.unit_width / 2) * math.tan(theta_2)

		o_x, o_y = polar(mid_x, mid_y, h, self.heading + math.pi)

		##Angle dif from corner point
		a = (math.pi / 2) - theta_2

		##Draw straight bounds
		a_l_x, a_l_y = polar(l_x, l_y, self.ranged_attack_range, self.heading - a)
		pygame.draw.line(screen, (255, 255, 0), (a_l_x, a_l_y), (l_x, l_y), 2)

		a_r_x, a_r_y = polar(r_x, r_y, self.ranged_attack_range, self.heading + a)
		pygame.draw.line(screen, (255, 255, 0), (a_r_x, a_r_y), (r_x, r_y), 2)

		#Draw Arc

		##Hypotenuse of triangle
		b = math.sqrt((self.unit_width/2)**2 + (h)**2)

		##Find Arc points
		total_increments = 10

		increment_angle = self.shooting_angle / total_increments

		lines = []

		for i in range(total_increments + 1):

			lines.append(polar(o_x, o_y, self.ranged_attack_range + b, self.heading - a + (i * increment_angle)))

		#Draw Arc
		pygame.draw.lines(screen, (255, 255, 0), False, lines, 2)

	#Overridden from parent class
	def draw(self, screen):

		if self.highlight:

			self.highlight_unit(screen)

			self.draw_movement_lines(screen)

			self.draw_range_indicator(screen)

		if self.draw_final_location and (self.targets != [] or self.enemy_target != None):

			self.draw_movement_end(screen)

		#Rotate unit Image by unit Heading
		temp_image = pygame.transform.rotate(self.image, math.degrees(-self.heading + math.pi))

		#Calculate the Width and Height of the image to offset around the Center (x, y)
		w = temp_image.get_width()
		h = temp_image.get_height()

		#Draw image
		screen.blit(temp_image, (self.x - w / 2, self.y - h / 2))

		#TEMP
		if self.fire_at_will:

			lines = self.get_lines()

			for l_1, l_2 in lines:

				pygame.draw.line(screen, (0, 255, 0), l_1, l_2, 2)