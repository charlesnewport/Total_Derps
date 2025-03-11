from utils import distance, point_in_unit, polar, draw_info_card
from unit_new import Unit, Missile_Unit
from army_manager import Manager

import platform
import random
import pygame
import json
import math

pygame.init()

width = 720
height = 720

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

unit_info = json.load(open("Data/nations.json"))

unit_width = 31
unit_height = 21
unit_buffer = unit_height / 2

total_player_units = 5
total_width = (total_player_units * unit_width) + ((total_player_units - 1) * unit_buffer)
player_increment = total_width / total_player_units

player_units = [Unit(unit_info["England"]["Dismounted English Knights"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)]
# player_units = [Missile_Unit(unit_info["England"]["Yeoman Archers"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)]
player_units.extend([Missile_Unit(unit_info["England"]["Yeoman Archers"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)])
# player_units.extend([Missile_Unit(unit_info["England"]["Archer Militia"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)])

total_enemy_units = 5
total_width = (total_enemy_units * unit_width) + ((total_enemy_units - 1) * unit_buffer)
enemy_increment = total_width / total_enemy_units

enemy_units = [Unit(unit_info["France"]["Dismounted Feudal Knights"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]
# enemy_units = [Missile_Unit(unit_info["France"]["Crossbowmen"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]
# enemy_units = [Unit(unit_info["France"]["Peasants"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]

manager = Manager("Player")

missiles = []

#Temp
for index, e in enumerate(enemy_units):

	e.set_enemy(player_units[index], False)

#FONT
font_size = 15
font = pygame.font.SysFont("Minecraft", font_size)

units_killed = []

while True:

	screen.fill((83, 161, 14))

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

		#Display Units
		player_units[i].draw(screen)

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

		#Display Units
		enemy_units[i].draw(screen)

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

		missiles[i].draw(screen)

	#Pygame Events
	keys = pygame.key.get_pressed()
	mouse_buttons = pygame.mouse.get_pressed()
	mouse_pos = pygame.mouse.get_pos()

	#Update Manager

	if platform.system() == "Linux":

		mouse_buttons = [keys[pygame.K_LEFT], False, keys[pygame.K_RIGHT]]

	manager.update(player_units, enemy_units, keys, mouse_buttons, mouse_pos)

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

	#Events
	for event in pygame.event.get():

		if event.type == pygame.QUIT:

			pygame.quit()
			exit()

		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_ESCAPE:

				pygame.quit()
				exit()

	pygame.display.update()
	clock.tick(60)
