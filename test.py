import pygame
import math

import random

total = 20

ticks = 10

# random_array = [random.random() for i in range(10)]
# random_array = [i/sum(random_array) for i in random_array]

# arrows_to_fire = [int(i * total) for i in random_array]

# arrows_to_fire = [i for i in arrows_to_fire if i != 0]

# arrows_to_fire[-1] -= (sum(arrows_to_fire) - total)

# if arrows_to_fire[-1] <= 0:

# 	del(arrows_to_fire[-1])

# print(arrows_to_fire, sum(arrows_to_fire))

import numpy as np

def gaussian(x, mu, sig):
	return (1.0 / (np.sqrt(2.0 * np.pi) * sig) * np.exp(-np.power((x - mu) / sig, 2.0) / 2))

x = np.linspace(-3, 3, ticks)
y = [gaussian(i, 0, 1) for i in x]

# normalise the y
y = [i / sum(y) for i in y]

arrows_to_fire = [int(i * total) for i in y]
arrows_to_fire = [i for i in arrows_to_fire if i != 0]

print(arrows_to_fire)
print(sum(arrows_to_fire))

exit()

width = 800

screen = pygame.display.set_mode((width, width))

while True:

	screen.fill((0, 0, 0))

	for event in pygame.event.get():

		if event.type == pygame.QUIT:

			pygame.quit()
			exit()

		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_ESCAPE:

				pygame.quit()
				exit()

	pygame.display.update()