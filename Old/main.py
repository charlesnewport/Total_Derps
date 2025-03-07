from bullet import Bullet
from unit import Unit

import random
import pygame
import math

width = 720
# width = 1280
height = 720

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
'''
TODO

Make unit class x
Make unit:
	-clickable x
	-moveable x
Make units:
	-move together x
	-path find to grouped positions x
Add unit statistics
-damage from bullets/cannon/melee 
-attack from bullets/melee
health x 
total soldiers x (could be used as health)
movement speed x
movement radius (only for turn based)
shooting radius x
defence/charge bonus
firing/melee damaged based on unit strength
'''

'''
UPDATES

Attack stats
Upper and Lower bound of kills per volley/tick(melee)

MAJOR
Enemy takes damage
Unit routs when enough damage is done
Fire and Advance
Total Ammunition, melee attack when ammunition complete
Unit health bar (on click)
How to withdraw from attacking (
obably requires having an enemy set and then removing that enemy)
Unit selection bar at bottom of screen
Unit dimensions could change and depth could become an attack/defence multiplier
Unselect enemy when right clicking off of it
ctrl + click to add units to highlighted
right click to attack uses current unit position
arrow "max_dist" should be based on distance to target
lower total number of frames by distance to target, i.e. arch more at distance/(or when behind unit) 
arrow damage could be based on distance + enemy units armour level, shield, and then some randomness. Given value on creation so that it can be refenced when it hits.
-probability of killing unit = ..... 
give unit orders that will be carried out after an attack is complete (enemy dead / routs)
Add has fired to units, then add all arrows to an array within the main file. Hopefully should require less looping (could have a fired by COLOR, INDEX to ensure the arrows don't hit themselves)
-could remove calculation of where to send archer to attack. Instead send it towards enemy (could change each tick) and when in range, fire. When out of range, chase.
-could use a state machine to make the unit update method easier to read.
Behaviours: Skirmish (run away if enemy within x distance), Fire at Will (aim at closest enemy unit if within range), Guard mode(?)


MINOR
Turn while moving rather than just instant turning (turning speed?)
could turn before moving

BUGS
Attacking enemy after moving (shift + attack) not working correctly
Now that enemys can attack, right click to attack no longer works

'''
def check_intersection(x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4):

	d = ((y_4-y_3)*(x_2-x_1) - (x_4-x_3)*(y_2-y_1))

	if d == 0:

		return False

	uA = ((x_4-x_3)*(y_1-y_3) - (y_4-y_3)*(x_1-x_3)) / d
	uB = ((x_2-x_1)*(y_1-y_3) - (y_2-y_1)*(x_1-x_3)) / d

	if uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1:

		iX = x_1 + (uA * (x_2 - x_1))
		iY = y_1 + (uA * (y_2 - y_1))	

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

def point_in_shape():#(p_x, p_y, polygon_points):

	lines = enemy.get_lines()

	points = enemy.get_points()

	m_x, m_y = pygame.mouse.get_pos()

	intersection_count = 0

	for x, y in points:

		for ((x_1, y_1), (x_2, y_2)) in lines:

			if check_intersection(x_1, y_1, x_2, y_2, m_x, m_y, x, y):

				intersection_count += 1

	return intersection_count == len(lines) * 2

def polar(x, y, r, theta):

	return (r * math.cos(theta)) + x, (r * math.sin(theta)) + y

def draw_rect(screen, x, y, angle):

	unit_width = 30
	unit_height = 20

	unit_radius = math.sqrt((unit_width ** 2) + (unit_height ** 2)) / 2

	combs = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5),  (0.5, -0.5)]

	angles = []

	for a_x, a_y in combs:

		angles.append(math.atan2(unit_height * a_y, unit_width * a_x))

	points = [polar(x, y, unit_radius, theta + angle) for theta in angles]

	pygame.draw.lines(screen, (255, 255, 0), True, points)

total_units = 1

units = [Unit(width / 2, 3 * height / 4, "blue") for x in range(total_units)]

unit_width = units[0].unit_width
unit_buffer = units[0].unit_width / 3

total_width = (total_units * unit_width) + ((total_units - 1) * unit_buffer)

increment = unit_width + unit_buffer

start_x = (width / 2) - (total_width / 2) + unit_width/2

for i in range(total_units):

	units[i].x = start_x + (increment * i)

enemy = Unit(width / 2, height / 4, "red")

drag_x_1 = 0
drag_y_1 = 0

drag_x_2 = 0
drag_y_2 = 0

left_mouse_pressed = False
right_mouse_pressed = False

total_units_selected = 0

attack_action = False
attack_target = enemy

bullets = []

while True:

	screen.fill((83, 161, 14))

	pygame.display.set_caption(str(int(clock.get_fps())))

	keys = pygame.key.get_pressed()

	if pygame.mouse.get_pressed()[2]:

		drag_x_2, drag_y_2 = pygame.mouse.get_pos()

		#attack
		if point_in_shape():

			attack_action = True

		else:	

			attack_action = False
			for unit in units:

				if unit.highlight:

					unit.enemy_target = None

			if not right_mouse_pressed:

				drag_x_1, drag_y_1 = drag_x_2, drag_y_2

				right_mouse_pressed = True

			total_units_selected = sum([1 for unit in units if unit.highlight])

			if total_units_selected > 1:

				line_angle = math.atan2(drag_y_2 - drag_y_1, drag_x_2 - drag_x_1)

				#Update here to ensure angle of unit remains if mouse not dragged when right click released
				# if drag_x_1 == drag_x_2 and drag_y_1 == drag_y_2:

				# 	line_angle = player.angle

				line_length = math.sqrt(((drag_y_2 - drag_y_1) ** 2) + ((drag_x_1 - drag_x_2) ** 2))

				# min_sep = 

				separation_length = max(line_length/(total_units_selected - 1), units[0].unit_width + 10)
				separation_length = min(separation_length, units[0].unit_width + 40)

				for i in range(total_units_selected):

					p_x, p_y = polar(drag_x_1, drag_y_1, separation_length * i, line_angle)

					draw_rect(screen, p_x, p_y, line_angle)

					_, _, lhs, rhs = units[0].get_points_at_angle(p_x, p_y, line_angle)

					m_x = (lhs[0] + rhs[0]) / 2
					m_y = (lhs[1] + rhs[1]) / 2

					# line_angle = math.atan2(m_y - self.target[i][1], m_x - self.target[i][0])
					# line_angle = math.atan2(self.target[i][1] - m_y, self.target[i][0] - m_x)

					lines = [(m_x, m_y)]

					lines.append(polar(m_x, m_y, units[0].unit_height/2, line_angle + math.pi/2 - math.radians(20)))

					lines.append(polar(m_x, m_y, units[0].unit_height/2, line_angle + math.pi/2 + math.radians(20)))

					pygame.draw.polygon(screen, (255, 255, 0), lines)

			elif total_units_selected == 1:

				line_angle = math.atan2(drag_y_2 - drag_y_1, drag_x_2 - drag_x_1)

				p_x, p_y = polar(drag_x_1, drag_y_1, 0, line_angle)

				draw_rect(screen, p_x, p_y, line_angle)

	else:

		if attack_action:

			for unit in units:

				if unit.highlight:

					unit.enemy_target = enemy

					pos_x = unit.x
					pos_y = unit.y

					if len(unit.movement_target) > 0 and keys[pygame.K_LSHIFT]:

						pos_x = unit.movement_target[-1][0]
						pos_y = unit.movement_target[-1][1]

					#attack location
					target_angle = math.atan2(pos_y - enemy.y, pos_x - enemy.x)

					target_location = polar(enemy.x, enemy.y, unit.shooting_range, target_angle)

					if math.sqrt((enemy.x - pos_x)** 2 + (enemy.y - pos_y)**2) < math.sqrt((enemy.y - target_location[1])** 2 + (enemy.x - target_location[0])**2):

						target_location = (pos_x, pos_y)

					if keys[pygame.K_LSHIFT]:

						unit.movement_target.append((target_location))
						unit.movement_target_heading.append((target_angle - math.pi/2))

					else:

						unit.movement_target = [target_location]
						unit.movement_target_heading = [target_angle - math.pi/2]

			attack_action = False

		else:

			if right_mouse_pressed:

				points = []

				total_units_selected = sum([1 for unit in units if unit.highlight])

				if total_units_selected > 1:

					line_angle = math.atan2(drag_y_2 - drag_y_1, drag_x_2 - drag_x_1)

					line_length = math.sqrt(((drag_y_2 - drag_y_1) ** 2) + ((drag_x_1 - drag_x_2) ** 2))

					# min_sep = 

					separation_length = max(line_length/(total_units_selected - 1), units[0].unit_width + 10)
					separation_length = min(separation_length, units[0].unit_width + 40)

					for i in range(total_units_selected):

						p_x, p_y = polar(drag_x_1, drag_y_1, separation_length * i, line_angle)

						points.append((p_x, p_y))

				elif total_units_selected == 1:

					line_angle = math.atan2(drag_y_2 - drag_y_1, drag_x_2 - drag_x_1)

					p_x, p_y = polar(drag_x_1, drag_y_1, 0, line_angle)

					points.append((p_x, p_y))

				if total_units_selected > 0:

					selected_units = [unit for unit in units if unit.highlight]

					for index, p in enumerate(points):

						if keys[pygame.K_LSHIFT]:

							selected_units[index].movement_target.append(p)
							selected_units[index].movement_target_heading.append(line_angle)

						else:

							selected_units[index].movement_target = [p]
							selected_units[index].movement_target_heading = [line_angle]

			right_mouse_pressed = False

	if pygame.mouse.get_pressed()[0]:

		drag_x_2, drag_y_2 = pygame.mouse.get_pos()

		if not left_mouse_pressed:

			drag_x_1, drag_y_1 = drag_x_2, drag_y_2

			left_mouse_pressed = True

		if drag_x_2 < drag_x_1:

			draw_x_1, draw_x_2 = drag_x_2, drag_x_1

		else:

			draw_x_1, draw_x_2 = drag_x_1, drag_x_2 

		if drag_y_2 < drag_y_1:

			draw_y_1, draw_y_2 = drag_y_2, drag_y_1

		else:

			draw_y_1, draw_y_2 = drag_y_1, drag_y_2 


		pygame.draw.rect(screen, (0, 255, 0), (draw_x_1, draw_y_1, draw_x_2 - draw_x_1, draw_y_2 - draw_y_1), 1)

	else:

		total_units_selected = 0

		#on release event
		if left_mouse_pressed:

			for unit in units:

				if unit.in_bounds(drag_x_1, drag_y_1, drag_x_2, drag_y_2) or point_in_shape_new(drag_x_1, drag_y_1, unit.get_lines(), unit.get_points()) or point_in_shape_new(drag_x_2, drag_y_2, unit.get_lines(), unit.get_points()):

					unit.highlight = True

					total_units_selected += 1

				else:

					unit.highlight = False

		left_mouse_pressed = False

	x, y = pygame.mouse.get_pos()

	min_d = width
	min_unit = None

	for unit in units:

		d = math.sqrt((enemy.y - unit.y) ** 2 + (enemy.x - unit.x) ** 2)

		if d < min_d:

			min_d = d
			min_unit = unit

	enemy.target_location = []

	#attack location
	target_angle = math.atan2(enemy.y - min_unit.y, enemy.x - min_unit.x)

	target_location = polar(min_unit.x, min_unit.y, unit.shooting_range, target_angle)

	if math.sqrt((min_unit.x - enemy.x)** 2 + (min_unit.y - enemy.y)**2) < math.sqrt((min_unit.y - target_location[1])** 2 + (min_unit.x - target_location[0])**2):

		target_location = (enemy.x, enemy.y)

	enemy.movement_target = [target_location]
	enemy.movement_target_heading = [target_angle - math.pi/2]
	enemy.enemy_target = min_unit

	enemy.update(units)

	if enemy.has_fired:

		bullets.append(enemy.get_bullet())

	for i in range(len(bullets)-1, -1, -1):

		bullets[i].update()
		bullets[i].draw(screen)

		if bullets[i].finished():

			del(bullets[i])
			continue

		for unit in units + [enemy]:

			if bullets[i].colour == unit.colour:

				continue

			if point_in_shape_new(bullets[i].x, bullets[i].y, unit.get_lines(), unit.get_points()):

				unit.health -= 0.5

				unit.health = max(unit.health, 0)

				del(bullets[i])
				break

	for unit in units:

		unit.update([enemy])

		if unit.has_fired:

			bullets.append(unit.get_bullet())

		unit.draw(screen, keys[pygame.K_SPACE], point_in_shape_new(x, y, unit.get_lines(), unit.get_points()) and unit.highlight)

	enemy.draw(screen, keys[pygame.K_SPACE], point_in_shape_new(x, y, enemy.get_lines(), enemy.get_points()))

	if keys[pygame.K_LCTRL] and keys[pygame.K_a]:

		for unit in units:

			unit.highlight = True
 
	if keys[pygame.K_r]:

		for unit in units:

			if unit.highlight:

				unit.is_running = not unit.is_running     

	for event in pygame.event.get():

		if event.type == pygame.QUIT:

			pygame.quit()
			exit()

		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_r:

				for unit in units:

					if unit.highlight:

						unit.is_running = not unit.is_running

	pygame.display.update()
	clock.tick(60)

      