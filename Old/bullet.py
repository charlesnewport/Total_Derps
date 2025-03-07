import pygame
import random
import math

def polar(x, y, r, theta):

	return (r * math.cos(theta)) + x, (r * math.sin(theta)) + y

def lerp(a, b, t):

	return (1 - t) + t * b

def quad_lerp(total_frames, total_distance, distance_traveled):

	a = -(4 * total_frames)/(total_distance ** 2)

	b = -(total_distance * a)

	return (a * (distance_traveled ** 2)) + (b * distance_traveled)

class Bullet:

	def __init__(self, x, y, angle, max_range, colour):

		self.x = x
		self.y = y

		self.x_dif = math.cos(angle)
		self.y_dif = math.sin(angle)

		self.colour = colour

		mag = math.sqrt((self.x_dif ** 2) + (self.y_dif ** 2))

		self.angle = angle

		self.speed = 4

		self.x_dif *= self.speed / mag
		self.y_dif *= self.speed / mag

		self.start_x = x
		self.start_y = y
		self.max_dist = random.randint(int(max_range * 0.75), max_range)

		self.end_x, self.end_y = polar(self.start_x, self.start_y, self.max_dist, self.angle)

		self.m_x, self.m_y = polar(self.start_x, self.start_y, self.max_dist / 2, self.angle)

		self.total_frames = 7

		self.images = [pygame.image.load(f"Images/arrow_sprite{index+1}.png") for index in range(self.total_frames)]
		self.w = self.images[0].get_width()
		self.h = self.images[0].get_height()



	def finished(self):

		return math.sqrt((self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2) >= self.max_dist

	def update(self):

		self.x += self.x_dif
		self.y += self.y_dif

	def draw(self, screen):

		distance_from_start = math.sqrt((self.start_x - self.x)**2 + (self.start_y - self.y)**2)
		distance_to_centre = math.sqrt((self.x - self.m_x)**2 + (self.y - self.m_y)**2)

		index = int(quad_lerp(self.total_frames * 4, self.max_dist, distance_from_start) / 4) 

		current_image = pygame.transform.rotate(self.images[index - 1], -math.degrees(self.angle) - 90)

		screen.blit(current_image, (int(self.x - self.w/2), int(self.y - self.h/2)))

		# pygame.draw.circle(screen, (255, 255, 0), (int(self.end_x), int(self.end_y)), 10, 1)

		# pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 1, 1)