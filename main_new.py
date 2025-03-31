from utils import distance, point_in_unit, polar, draw_info_card
from unit_new import Unit, Missile_Unit
from army_manager import Manager

import platform
import random
import pygame
import json
import math

def calc_strength(army):

	total = 0

	for unit in army:

		total += unit.get_strength()

	return total

pygame.init()

width = 720
height = 720

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

unit_info = json.load(open("Data/nations.json"))

unit_width = 31
unit_height = 21
unit_buffer = unit_height / 2

total_player_units = 10
total_width = (total_player_units * unit_width) + ((total_player_units - 1) * unit_buffer)
player_increment = total_width / total_player_units

player_units = [Unit(unit_info["England"]["Dismounted English Knights"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)]
# player_units = [Missile_Unit(unit_info["England"]["Yeoman Archers"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)]
player_units.extend([Missile_Unit(unit_info["England"]["Yeoman Archers"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)])
# player_units.extend([Unit(unit_info["England"]["Peasants"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)])
player_units.extend([Unit(unit_info["England"]["Hobilars"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(5)])

total_enemy_units = 10
total_width = (total_enemy_units * unit_width) + ((total_enemy_units - 1) * unit_buffer)
enemy_increment = total_width / total_enemy_units

# enemy_units = [Unit(unit_info["France"]["Dismounted Feudal Knights"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]
# enemy_units = [Missile_Unit(unit_info["France"]["Crossbowmen"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]
# enemy_units = [Missile_Unit(unit_info["France"]["Crossbowmen"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]
# enemy_units.extend([Unit(unit_info["France"]["Peasants"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4 - 3 * unit_height * 2, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)])
enemy_units = [Unit(unit_info["France"]["Peasants"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4 - 3 * unit_height * 2, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]
# enemy_units.extend([Unit(unit_info["France"]["Peasants"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/8 - 3 * unit_height * 2, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)])

manager = Manager("Player")

missiles = []

#Temp
temp_enemy_targets = [unit for unit in player_units if unit.unit_type == "archer"]

#Find the closest unit to this
for unit in enemy_units:

	if unit.enemy_target != None:

		continue

	min_angle = float("inf")
	min_target = None

	for target in temp_enemy_targets:

		# a = math.atan2(target.y - unit.y, target.x - unit.x)
		a = math.atan2(unit.y - target.y, unit.x - target.x)
		a %= math.pi * 2

		if a + math.pi < min_angle:

			min_angle = a
			min_target = target

	unit.set_enemy(min_target, False)

	temp_enemy_targets.remove(min_target)

# for index, e in enumerate(enemy_units):

# 	e.set_enemy(player_units[random.randint(0, len(player_units)-1)], False)

def set_basic_formation(army, top=False):

	#determine max possible width of the army
	max_width = int(width / (army[0].unit_width + unit_buffer))

	#calculate total infantry
	total_infantry = sum([1 for unit in army if unit.unit_type != "cavalry" and unit.unit_type != "archer" and unit.unit_type != "crossbow"])

	center_x = width / 2
	temp_y = 5 * width / 6 if not top else width / 6

	total_infantry_width = (total_infantry * army[0].unit_width) + ((total_infantry - 1) * unit_buffer)

	infantry_count = 0

	for unit in army:

		if unit.unit_type != "cavalry" and unit.unit_type != "archer" and unit.unit_type != "crossbow":

			temp_unit_x = center_x - (total_infantry_width / 2) + (infantry_count * (unit_width + unit_buffer)) + army[0].unit_width/2
			infantry_count += 1

			unit.x = temp_unit_x

			unit.y = temp_y

	total_missile = sum([1 for unit in army if unit.unit_type == "archer" or unit.unit_type == "crossbow"])

	total_missile_width = (total_missile * army[0].unit_width) + ((total_missile - 1) * unit_buffer)

	missile_count = 0

	for unit in army:

		if unit.unit_type == "archer" or unit.unit_type == "crossbow":

			temp_unit_x = center_x - total_missile_width / 2 + (missile_count * (army[0].unit_width + unit_buffer)) + army[0].unit_width/2
			missile_count += 1

			unit.x = temp_unit_x

			unit.y = temp_y - unit.unit_height - unit_buffer if not top else temp_y + unit.unit_height + unit_buffer

	total_cavalry = sum([1 for unit in army if unit.unit_type == "cavalry"])

	#find half of the cavalry
	half_cavalry = math.floor(total_cavalry / 2)

	#LHS
	lhs_width = (half_cavalry * army[0].unit_width) + ((half_cavalry - 1) * unit_buffer)

	lhs_end = int(center_x - max(total_infantry_width, total_missile_width) / 2)

	lhs_center_x = lhs_end / 2

	lhs_cavalry_counter = 0

	for unit in army:

		if lhs_cavalry_counter == half_cavalry:

			break

		if unit.unit_type == "cavalry":

			temp_x = lhs_center_x - lhs_width / 2 + (lhs_cavalry_counter * (army[0].unit_width + unit_buffer)) + army[0].unit_width/2

			unit.x = temp_x
			unit.y = int(temp_y + army[0].unit_height / 2) if not top else int(temp_y - army[0].unit_height / 2)

			lhs_cavalry_counter += 1

	#RHS
	rhs_width = ((total_cavalry - half_cavalry) * army[0].unit_width) + (((total_cavalry - half_cavalry) - 1) * unit_buffer)
	rhs_end = int(center_x + max(total_infantry_width, total_missile_width) / 2)

	rhs_center_x = int((width + rhs_end) / 2)

	print(rhs_end)

	rhs_cavalry_counter = 0
	rhs_buffer_counter = 0

	for unit in army:

		if unit.unit_type == "cavalry":

			if rhs_buffer_counter < half_cavalry:
				rhs_buffer_counter += 1
				continue

			temp_x = rhs_center_x - rhs_width / 2 + (rhs_cavalry_counter * (army[0].unit_width + unit_buffer)) + army[0].unit_width/2
			unit.x = temp_x
			# unit.y = int(temp_y + army[0].unit_height / 2)
			unit.y = int(temp_y + army[0].unit_height / 2) if not top else int(temp_y - army[0].unit_height / 2)

			rhs_cavalry_counter += 1

set_basic_formation(player_units)
set_basic_formation(enemy_units, True)
#FONT
font_size = 15
font = pygame.font.SysFont("Minecraft", font_size)

units_killed = []

pause = True
first_pause = True

while True:

	screen.fill((83, 161, 14))

	#Updates

	if first_pause:

		for unit in player_units:

			if unit.targets != []:

				unit.x, unit.y = unit.targets[0]
				unit.heaing = unit.target_headings[0]

				unit.reset_target()

	if not pause:

		#Player units
		for i in range(len(player_units)-1, -1, -1):

			if player_units[i].unit_size <= 0:

				units_killed.append(player_units[i].unit_id)
				del(player_units[i])
				continue

			if player_units[i].enemy_target != None and player_units[i].enemy_target.unit_id in units_killed:

				player_units[i].reset_enemy()

			#Update Units
			player_units[i].update(enemy_units)

			if player_units[i].unit_class == "Missile":

				missiles.extend(player_units[i].missiles)
				player_units[i].missiles = []

		#Enemy units
		for i in range(len(enemy_units)-1, -1, -1):

			if enemy_units[i].unit_size <= 0:

				units_killed.append(enemy_units[i].unit_id)
				del(enemy_units[i])
				continue

			if enemy_units[i].enemy_target != None and enemy_units[i].enemy_target.unit_id in units_killed:

				enemy_units[i].reset_enemy()

			#Update Units
			enemy_units[i].update(player_units)

			if enemy_units[i].unit_class == "Missile":

				missiles.extend(enemy_units[i].missiles)
				enemy_units[i].missiles = []

		#Missile
		for i in range(len(missiles)-1, -1, -1):

			missiles[i].update()

			#has landed
			if distance(missiles[i].x, missiles[i].y, missiles[i].t_x, missiles[i].t_y) <= 10:

				for unit in enemy_units + player_units:

					if point_in_unit(missiles[i].t_x, missiles[i].t_y, unit):

						#resolve arrow collision
						a = missiles[i].missile_attack_skill
						d = unit.defence_skill + unit.armour + unit.shield

						if missiles[i].is_armour_piercing:

							d -= unit.armour/2

						p_hit = 0

						if a < d:

							p_hit = (a + 1) / (2 * d)

						else:

							p_hit = ((2 * a) - d + 1) / (2 * a)

						# print(a, d, p_hit)

						outcome = random.random() <= p_hit

						if outcome:

							if unit.unit_size > 0:

								unit.hitpoints_array[0] -= 1

								if unit.hitpoints_array[0] <= 0:

									del(unit.hitpoints_array[0])
									unit.unit_size -= 1

				del(missiles[i])

				continue

	#Pygame Events
	keys = pygame.key.get_pressed()
	mouse_buttons = pygame.mouse.get_pressed()
	mouse_pos = pygame.mouse.get_pos()

	#Update Manager

	if platform.system() == "Linux":

		mouse_buttons = [keys[pygame.K_LEFT], False, keys[pygame.K_RIGHT]]

	manager.update(player_units, enemy_units, keys, mouse_buttons, mouse_pos)

	#Display
	for unit in enemy_units + player_units:

		unit.draw(screen)

	for missile in missiles:

		missile.draw(screen)

	# #Display Units
	# player_units[i].draw(screen)
	# #Display Units
	# enemy_units[i].draw(screen)
	# missiles[i].draw(screen)
	#Display Manager
	manager.draw(screen, player_units)

	#temp
	x, y = pygame.mouse.get_pos()

	for unit in player_units + enemy_units:

		if point_in_unit(x, y, unit):

			x, y = polar(unit.x, unit.y, unit.unit_radius, -math.pi/2)

			draw_info_card(screen, font, x, y, unit.get_information())
			break

	#Temp Debug Info
	a = sum([p.unit_size for p in player_units])
	d = sum([p.unit_size for p in enemy_units])

	text = font.render(str(a) + " - " + str(d), False, (0, 0, 255) if d > a else (255, 0, 0))
	text_width = text.get_width()
	text_height = text.get_height()

	screen.blit(text, (0, 0))

	player_strength = calc_strength(player_units)
	enemy_strength = calc_strength(enemy_units)

	rect_width = 100
	rect_height = 25

	pygame.draw.rect(screen, (0, 0, 255), (width/2 - rect_width/2, 0, rect_width, rect_height))
	pygame.draw.rect(screen, (255, 0, 0), (width/2 - rect_width/2, 0, int(rect_width * player_strength / (player_strength + enemy_strength)), rect_height))

	#Events
	for event in pygame.event.get():

		if event.type == pygame.QUIT:

			pygame.quit()
			exit()

		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_ESCAPE:

				pygame.quit()
				exit()

			if event.key == pygame.K_a:

				for unit in player_units:

					if unit.highlight and unit.unit_class == "Missile":

						unit.fire_at_will = not unit.fire_at_will

			if event.key == pygame.K_r:

				for unit in player_units:

					if unit.highlight:

						unit.is_running = not unit.is_running

			if event.key == pygame.K_p:

				pause = not pause
				first_pause = False

	pygame.display.update()
	clock.tick(60)
