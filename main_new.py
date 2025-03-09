from army_manager import Manager
from unit_new import Unit

import pygame
import json

import platform

pygame.init()

width = 720
height = 720

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

unit_info = json.load(open("Data/nations.json"))

unit_width = 31
unit_height = 21
unit_buffer = unit_height / 2

total_player_units = 1
total_width = (total_player_units * unit_width) + ((total_player_units - 1) * unit_buffer)
player_increment = total_width / total_player_units

player_units = [Unit(unit_info["England"]["Dismounted English Knights"], width/2 - total_width/2 + unit_width/2 + (player_increment * i), 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)]

total_enemy_units = 1
total_width = (total_enemy_units * unit_width) + ((total_enemy_units - 1) * unit_buffer)
enemy_increment = total_width / total_enemy_units

enemy_units = [Unit(unit_info["France"]["Armoured Sergeants"], width/2 - total_width/2 + unit_width/2 + (enemy_increment * i), width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_enemy_units)]

manager = Manager("Player")

#FONT
font_size = 30
font = pygame.font.SysFont("dejavuserif", font_size)

while True:

	screen.fill((83, 161, 14))

	#hello world
	#test branch

	#Player units
	for i in range(len(player_units)-1, -1, -1):

		if player_units[i].unit_size <= 0:

			del(player_units[i])
			continue

		#Update Units
		player_units[i].update(enemy_units)

		#Display Units
		player_units[i].draw(screen)

	#Enemy units
	for i in range(len(enemy_units)-1, -1, -1):

		if enemy_units[i].unit_size <= 0:

			del(enemy_units[i])
			continue

		#Update Units
		enemy_units[i].update(player_units)

		#Display Units
		enemy_units[i].draw(screen)

	#Pygame Events
	keys = pygame.key.get_pressed()
	mouse_buttons = pygame.mouse.get_pressed()
	mouse_pos = pygame.mouse.get_pos()

	#Update Manager
	if platform.system() == "Linux":

		mouse_buttons = [keys[pygame.K_LEFT], False, keys[pygame.K_RIGHT]]

	manager.update(player_units, keys, mouse_buttons, mouse_pos)

	#Display Manager
	manager.draw(screen, player_units)

	a = sum([p.unit_size for p in player_units])
	d = sum([p.unit_size for p in enemy_units])

	text = font.render(str(a) + " - " + str(d), False, (0, 0, 255) if d > a else (255, 0, 0))
	text_width = text.get_width()
	text_height = text.get_height()

	screen.blit(text, (0, 0))

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
