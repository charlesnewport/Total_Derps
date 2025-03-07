import numpy as np
import pygame
import cv2

def colour_unit(unit_icon, unit_colour):

	rows, cols, _ = unit_icon.shape

	image_1d = unit_icon.reshape(rows * cols, 3)

	image_1d = np.where(image_1d == np.array([0, 0, 0]), np.array(unit_colour[::-1]), image_1d)

	return image_1d.reshape(rows, cols, 3).astype(np.uint8)

image = colour_unit(cv2.imread("Images/bills.png"), [0, 255, 0])

cv2.imshow("test", image)
cv2.waitKey(0)
# exit()
# screen = pygame.display.set_mode((width, width))

# while True:

# 	screen.fill((255, 255, 255))

# 	for event in pygame.event.get():

# 		if event.type == pygame.QUIT:

# 			pygame.quit()
# 			exit()

# 	pygame.display.update()


# A = 22
# D = 22

# ph = (2 * A - D + 1)/(2 * A)
# print(ph)
# ph = (A+1)/(2*D)
# print(ph)
# spans = ["1","The Byzantine Empire","2","Denmark","3","Egypt","4","England","5","France","6","The Holy Roman Empire","7","Hungary","8","Milan","9","Moors","10","Poland","11","Portugal","12","Russia","13","Scotland","14","Sicily","15","Spain","16","The Turks","17","Venice","18","The original Unit Planner","19","Abbreviations","20","External links","The Byzantine Empire","Denmark","Egypt","England","France","The Holy Roman Empire","Hungary","Milan","Moors","Poland","Portugal","Russia","Scotland","Sicily","Spain","The Turks","Venice","The original Unit Planner","Abbreviations","External links"]


# print(nations)

# import pygame

# width = 400

# screen = pygame.display.set_mode((width, width))

# s_x, s_y = 0, width / 2
# e_x, e_y = width, width / 2

# m_x = (s_x + e_x) / 2
# m_y = (s_y + e_y) / 2

# def lerp(a, b, t):

# 	return (1 - t) + t * b

# min_size = 1
# max_size = 10

# x_value = 0
# inc = 0.01
