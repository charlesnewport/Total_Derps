from bullet import Bullet

import random
import pygame
import math

'''

STATES

0 - IDLE
1 - MOVING
2 - TARGETING
3 - FIRING

'''

def lerp(a, b, t):

	return (1 - t) * a + t * b

def lerp_colour(colour_1, colour_2, t):

	return [lerp(colour_1[i], colour_2[i], t) for i in range(3)]

def lerp_colours(value, value_total):

	if value > value_total / 2:

		return lerp_colour((255, 255, 0), (0, 255, 0), (value - value_total / 2) / (value_total / 2))

	return lerp_colour((255, 0, 0), (255, 255, 0), value / (value_total / 2))

def polar(x, y, r, theta):

	return (r * math.cos(theta)) + x, (r * math.sin(theta)) + y


'''
Next: Firing Radius/Distance

Radius a circle offset behind the unit.



'''

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

def point_in_shape_new(m_x, m_y, lines, points):#(p_x, p_y, polygon_points):

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


colour_dict = {"red": (255, 0, 0), "blue": (0, 0, 255)}

class Unit:

	def __init__(self, x, y, colour):

		self.x = x
		self.y = y

		self.unit_colour = colour
		self.colour = colour_dict[colour]

		self.angle = 0

		self.unit_width = 30
		self.unit_height = 20

		self.unit_radius = math.sqrt((self.unit_width ** 2) + (self.unit_height ** 2)) / 2

		self.highlight = False

		self.enemy_target = None

		self.movement_target = []
		self.movement_target_heading = []

		self.speed = 0.5
		self.is_running = False

		#temp
		self.bullets = []

		self.firing_order = list(range(0, 10))
		random.shuffle(self.firing_order)

		self.firing_index = 0

		self.is_firing = False

		self.reload_time = 60
		self.reload_timer = 0

		self.firing_cooldown = 5
		self.firing_counter = 0

		self.firing_delay = 0

		self.shooting_angle = math.radians(30)
		self.shooting_range = 300

		self.max_ammo = 20
		self.ammo = 20
		self.health = 100

		self.has_fired = False

		self.test_image = pygame.image.load(f"Images/{self.unit_colour}_spearmen.png")


	def get_bullet(self):

		p_x, p_y = polar(self.x, self.y, self.unit_height/2 + 1, self.angle - math.pi/2)

		p_x_1, p_y_1 = polar(p_x, p_y, self.unit_width/2, self.angle - math.pi/2 - math.pi/2)
		p_x_2, p_y_2 = polar(p_x, p_y, self.unit_width/2, self.angle - math.pi/2 + math.pi/2)

		denominator = len(self.firing_order)

		line_length = math.sqrt((p_x_1 - p_x_2) ** 2 + (p_y_1 - p_y_2) ** 2)

		spacing = line_length / denominator

		r = self.firing_order[self.firing_index]

		line_angle = math.atan2(p_y_2 - p_y_1, p_x_2 - p_x_1)

		b_x, b_y = polar(p_x_1, p_y_1, r * spacing, line_angle)

		return Bullet(b_x, b_y, self.angle - math.pi/2, self.shooting_range, self.colour)


	def get_speed(self):

		return self.speed * 2 if self.is_running else self.speed

	def can_fire(self):

		return self.reload_timer >= self.reload_time and self.ammo > 0

	def fire(self):

		if self.can_fire():

			self.is_firing = True

	def display_info(self, screen):

		min_y = 1000

		for point in self.get_points():

			if point[1] < min_y:

				min_y = point[1]

		buf = self.unit_height / 2

		bar_x = self.x - self.unit_width / 2
		bar_y = min_y - self.unit_height - buf

		pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, self.unit_width, self.unit_height))

		#draw ammo amount
		ammo_x = bar_x + 2
		max_ammo_width = self.unit_width - 4
		ammo_width = max_ammo_width * self.ammo / self.max_ammo

		ammo_y = bar_y + 2
		ammo_height = (self.unit_height - 4) / 2 - 1

		pygame.draw.rect(screen, (80, 202, 220), (ammo_x, ammo_y, ammo_width, ammo_height))

		health_x = bar_x + 2
		max_health_width = self.unit_width - 4
		health_width = max_health_width * self.health / 100

		health_y = bar_y + self.unit_height / 2 + 1
		health_height = (self.unit_height - 4) / 2 - 1

		# pygame.draw.rect(screen, (0, 202, 0), (health_x, health_y, health_width, health_height))
		pygame.draw.rect(screen, lerp_colours(self.health, 100), (health_x, health_y, health_width, health_height))

		pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, self.unit_width, self.unit_height), 1)		

	def update(self, enemies):

		self.has_fired = False

		# for enemy in enemies:

			# if len(enemy.bullets) == 0:

				# continue

			# for i in range(len(enemy.bullets)-1, -1, -1):

			# 	if point_in_shape_new(enemy.bullets[i].x, enemy.bullets[i].y, self.get_lines(), self.get_points()):

			# 		self.health -= 0.5

			# 		del(enemy.bullets[i])

		# for i in range(len(self.bullets)-1, -1, -1):

		# 	self.bullets[i].update()

		# 	if self.bullets[i].finished():

		# 		del(self.bullets[i])


		if self.can_fire() and self.enemy_target != None:

			#distance to center to self.enemy_target
			d2coe = math.sqrt((self.x - self.enemy_target.x) ** 2 + (self.y - self.enemy_target.y) ** 2)

			_, _, lhs, rhs = self.get_points()
			c_x = (lhs[0] + rhs[0]) / 2
			c_y = (lhs[1] + rhs[1]) / 2

			cou2mou = math.sqrt((self.x - c_x) ** 2 + (self.y - c_y) ** 2)

			#find coe to iwe
			i_x, i_y = None, None

			for ((x_1, y_1), (x_2, y_2)) in self.enemy_target.get_lines():

				if check_intersection(x_1, y_1, x_2, y_2, self.enemy_target.x, self.enemy_target.y, self.x, self.y):

					i_x, i_y = intersection_point(x_1, y_1, x_2, y_2, self.enemy_target.x, self.enemy_target.y, self.x, self.y)

			coe2iwe = math.sqrt((i_x - self.enemy_target.x) ** 2 + (i_y - self.enemy_target.y) ** 2)

			final_distance = d2coe - cou2mou - coe2iwe

			if final_distance < self.shooting_range:

				#stop moving and fire

				self.movement_target = []
				self.movement_target_heading = []

				self.fire()

				self.angle = math.atan2(self.y - self.enemy_target.y, self.x - self.enemy_target.x) - math.pi/2

		if self.is_firing and self.firing_delay > 1:

			# p_x, p_y = polar(self.x, self.y, self.unit_height/2 + 1, self.angle - math.pi/2)

			# p_x_1, p_y_1 = polar(p_x, p_y, self.unit_width/2, self.angle - math.pi/2 - math.pi/2)
			# p_x_2, p_y_2 = polar(p_x, p_y, self.unit_width/2, self.angle - math.pi/2 + math.pi/2)

			# denominator = len(self.firing_order)

			# line_length = math.sqrt((p_x_1 - p_x_2) ** 2 + (p_y_1 - p_y_2) ** 2)

			# spacing = line_length / denominator

			# r = self.firing_order[self.firing_index]

			# line_angle = math.atan2(p_y_2 - p_y_1, p_x_2 - p_x_1)

			# b_x, b_y = polar(p_x_1, p_y_1, r * spacing, line_angle)

			# self.bullets.append(Bullet(b_x, b_y, self.angle - math.pi/2, self.shooting_range))
			self.has_fired = True


			self.firing_index += 1
			self.firing_delay = 0
			if self.firing_index == len(self.firing_order):

				self.firing_index = 0
				self.is_firing = False

				self.reload_timer = 0
				self.ammo -= 1

				random.shuffle(self.firing_order)

		else:

			self.firing_delay += 1
			self.reload_timer += 1

		if self.movement_target != []:

			theta = math.atan2(self.movement_target[0][1] - self.y, self.movement_target[0][0] - self.x)

			self.angle = theta + math.pi/2

			mag_x = math.cos(theta)
			mag_y = math.sin(theta)

			mag = math.sqrt(mag_x ** 2 + mag_y ** 2)

			#set mag

			x_dif = mag_x * self.get_speed() / mag
			y_dif = mag_y * self.get_speed() / mag

			self.x += x_dif
			self.y += y_dif

			if math.sqrt((self.movement_target[0][0] - self.x) ** 2 + (self.movement_target[0][1] - self.y) ** 2) < 2:#self.unit_height/2:

				self.x, self.y = self.movement_target[0]

				self.angle = self.movement_target_heading[0]

				del(self.movement_target[0])
				del(self.movement_target_heading[0])

				self.is_running = False

		if len(self.movement_target) > 0:

			return

	def get_points_at_angle(self, pos_x, pos_y, theta):

		combs = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5),  (0.5, -0.5)]

		angles = []

		for x, y in combs:

			angles.append(math.atan2(self.unit_height * y, self.unit_width * x))

		return [polar(pos_x, pos_y, self.unit_radius, angle + theta) for angle in angles]


	def get_points(self):

		combs = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5),  (0.5, -0.5)]

		angles = []

		for x, y in combs:

			angles.append(math.atan2(self.unit_height * y, self.unit_width * x))

		return [polar(self.x, self.y, self.unit_radius, theta + self.angle) for theta in angles]

	def get_lines(self):

		lines = []

		points = self.get_points()

		for i in range(1, len(points)):

			lines.append([points[i], points[i-1]])

		lines.append((points[0], points[-1]))

		return lines

	def in_bounds(self, x_1, y_1, x_2, y_2):

		if x_1 > x_2:

			x_1, x_2 = x_2, x_1

		if y_1 > y_2:

			y_1, y_2 = y_2, y_1

		for p_x, p_y in self.get_points():

			if p_x >= x_1 and p_x <= x_2 and p_y >= y_1 and p_y <= y_2:

				return True

		return False 

	def draw(self, screen, highlight_route, hovered):

		# for bullet in self.bullets:

		# 	bullet.draw(screen)

		if self.highlight:

			pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y), self.unit_radius, 1)


		test_image = pygame.transform.rotate(self.test_image, -math.degrees(self.angle))
		w = test_image.get_width()
		h = test_image.get_height()
		screen.blit(test_image, (int(self.x - w/2), int(self.y - h/2)))

		points = self.get_points()

		#for debug

		# pygame.draw.polygon(screen, self.colour, points)
		pygame.draw.lines(screen, (255, 255, 0), True, points)


		if self.movement_target != [] and self.highlight:

			# pygame.draw.circle(screen, (0, 255, 0), (int(self.movement_target[0]), int(self.movement_target[1])), 10, 1)

			colour = (255, 0, 0) if self.enemy_target != None and len(self.movement_target) == 1 else (0, 255, 0)

			pygame.draw.line(screen, colour, (self.x, self.y), (int(self.movement_target[0][0]), int(self.movement_target[0][1])), 2)

			#arrow
			p_x, p_y = polar(self.movement_target[0][0], self.movement_target[0][1], 20, math.atan2(self.y - self.movement_target[0][1], self.x - self.movement_target[0][0]) - math.radians(30))
			pygame.draw.line(screen, colour, self.movement_target[0], (p_x, p_y), 2)

			p_x, p_y = polar(self.movement_target[0][0], self.movement_target[0][1], 20, math.atan2(self.y - self.movement_target[0][1], self.x - self.movement_target[0][0]) + math.radians(30))
			pygame.draw.line(screen, colour, self.movement_target[0], (p_x, p_y), 2)

			if len(self.movement_target) > 1:

				for i in range(1, len(self.movement_target)):

					colour = (255, 0, 0) if self.enemy_target != None and i == len(self.movement_target) - 1 else (0, 255, 0)

					fp_x, fp_y = (self.enemy_target.x, self.enemy_target.y) if self.enemy_target != None and i == len(self.movement_target) - 1 else self.movement_target[i]

					pygame.draw.line(screen, colour, (int(fp_x), int(fp_y)), (int(self.movement_target[i - 1][0]), int(self.movement_target[i - 1][1])), 2)

					#arrow

					p_x, p_y = polar(fp_x, fp_y, 20, math.atan2(self.movement_target[i - 1][1] - fp_y, self.movement_target[i - 1][0] - fp_x) - math.radians(30))
					pygame.draw.line(screen, colour, (fp_x, fp_y), (p_x, p_y), 2)

					p_x, p_y = polar(fp_x, fp_y, 20, math.atan2(self.movement_target[i - 1][1] - fp_y, self.movement_target[i - 1][0] - fp_x) + math.radians(30))
					pygame.draw.line(screen, colour, (fp_x, fp_y), (p_x, p_y), 2)

		if self.highlight:

			#test firing radius/range

			#left handside
			l_x, l_y = points[2]

			#right handside
			r_x, r_y = points[3]

			mid_x = (l_x + r_x) / 2
			mid_y = (l_y + r_y) / 2

			a = (math.pi - self.shooting_angle) / 2

			h = (self.unit_width / 2) * math.tan(a)

			b = h / math.sin(a)

			h_x, h_y = polar(mid_x, mid_y, h, self.angle + math.pi/2)

			# pygame.draw.line(screen, (255, 255, 255), (mid_x, mid_y), (h_x, h_y), 1)

			p_x_1, p_y_1 = polar(l_x, l_y, self.shooting_range, self.angle - math.pi/2 - self.shooting_angle/2)
			pygame.draw.line(screen, (0, 0, 255), (p_x_1, p_y_1), (l_x, l_y), 1)

			p_x_1, p_y_1 = polar(r_x, r_y, self.shooting_range, self.angle - math.pi/2 + self.shooting_angle/2)
			pygame.draw.line(screen, (0, 0, 255), (p_x_1, p_y_1), (r_x, r_y), 1)

			total_points = 10

			increment = self.shooting_angle / total_points

			points = []

			for i in range(total_points + 1):

				temp_x, temp_y = polar(h_x, h_y, self.shooting_range + b, self.angle - math.pi/2 - self.shooting_angle/2 + increment * i)

				points.append((temp_x, temp_y))

			pygame.draw.lines(screen, (0, 0, 255), False, points)

		if hovered:

			self.display_info(screen)

		if highlight_route:

			for i in range(len(self.movement_target)):

				points = self.get_points_at_angle(self.movement_target[i][0], self.movement_target[i][1], self.movement_target_heading[i])

				pygame.draw.lines(screen, (255, 255, 0), True, points)

				#draw direction lines

				_, _, lhs, rhs = points

				m_x = (lhs[0] + rhs[0]) / 2
				m_y = (lhs[1] + rhs[1]) / 2

				line_angle = math.atan2(m_y - self.movement_target[i][1], m_x - self.movement_target[i][0])
				# line_angle = math.atan2(self.movement_target[i][1] - m_y, self.movement_target[i][0] - m_x)

				lines = [(m_x, m_y)]

				lines.append(polar(m_x, m_y, self.unit_height/2, line_angle + math.pi - math.radians(20)))

				lines.append(polar(m_x, m_y, self.unit_height/2, line_angle + math.pi + math.radians(20)))

				pygame.draw.polygon(screen, (255, 255, 0), lines)

			#test heading line

			'''
			draw a line ahead of the direction the unit is facing
			use this line to random fire bullets (or fire in a random sequence)
			
			'''