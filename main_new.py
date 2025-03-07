from army_manager import Manager
from unit_new import Unit

import pygame
import json

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
increment = total_width / total_player_units

player_units = [Unit(unit_info["England"]["Armoured Swordsmen"], width/2 - total_width/2 + unit_width/2 + increment * i, 3*width/4, unit_width, unit_height, [255, 0, 0]) for i in range(total_player_units)]
enemy_units = [Unit(unit_info["France"]["Armoured Sergeants"], width/2 - total_width/2 + unit_width/2 + increment * i, width/4, unit_width, unit_height, [0, 0, 255]) for i in range(total_player_units)]

manager = Manager("Player")

while True:

	screen.fill((83, 161, 14))

	#Player units
	for unit in player_units:

		#Update Units
		unit.update()

		#Display Units
		
		unit.draw(screen)

	#Enemy units
	for unit in enemy_units:

		#Update Units
		unit.update()

		#Display Units
		unit.draw(screen)

	#Pygame Events
	keys = pygame.key.get_pressed()
	mouse_buttons = pygame.mouse.get_pressed()
	mouse_pos = pygame.mouse.get_pos()

	#Update Manager
	manager.update(player_units, keys, mouse_buttons, mouse_pos)

	#Display Manager
	manager.draw(screen, player_units)

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
