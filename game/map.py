import pygame, sys
from pygame.locals import *

class Layer():
              """This class is supposed to display a layer and allow scrolling"""
              def __init__(self, screen, img_filename, scrolling_speed = (1,1), top_priority=False):
                            self.scrolling_speed = scrolling_speed
                            self.screen = screen
                            self.top_priority = top_priority

                            img = pygame.image.load(img_filename).convert_alpha()

                            self.virtual_width = (screen.get_width()/img.get_width()+1)*img.get_width()
                            self.virtual_height = (screen.get_height()/img.get_height()+1)*img.get_height()
                            self.width = screen.get_width() + self.virtual_width
                            self.height = screen.get_height() + self.virtual_height
                            self.panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

                            #construction of a big panel in order to make scrolling possibleand infinite
                            for i in range(0, self.panel.get_width(), img.get_width()):
                                          for j in range(0, self.panel.get_height(), img.get_height()):
                                                        pygame.Surface.blit(self.panel, img, (i, j))

              #displaying the right part
              def display(self, coordinates):
                            x = coordinates[0]*self.scrolling_speed[0]
                            y = coordinates[1]*self.scrolling_speed[1]
                            w = self.virtual_width
                            h  = self.virtual_height
                            dispx = x - w*(x/w) 
                            dispy = y - h*(y/h)
                            display_rect = pygame.Rect(dispx, dispy, self.screen.get_width(), self.screen.get_height())
                            display = self.panel.subsurface(display_rect)

                            pygame.Surface.blit(screen, display, (0, 0))   
                            

class Stage():
              def __init__(self, screen, size, camera=None):
                            self.screen = screen
                            self.layers = []
                            self.entities = []
                            self.tiles = []
                            self.size = size
                            if (camera == None):
                                          self.camera = [self.size[0]/2, self.size[1]/2]
                            else:
                                          self.camera = camera

              def add_layers(self, layers):
                            self.layers+=layers

              def add_tiles(self, tiles):
                            self.tiles += tiles
                            self.entities += tiles

              #position of the camera
              def set_camera(self, position):
                            xmin = self.screen.get_width()/2
                            xmax = self.size[0] - self.screen.get_width()/2
                            ymin = self.screen.get_height()/2
                            ymax = self.size[1] - self.screen.get_height()/2

                            #setting x position
                            if (position[0] < xmin):
                                          self.camera[0] = xmin
                            elif (position[0] > xmax ):
                                          self.camera[0] = xmax
                            else:
                                          self.camera[0] = position[0]
                            
                            #setting y position
                            if (position[1] < ymin):
                                          self.camera[1] = ymin
                            elif (position[1] > ymax ):
                                          self.camera[1] = ymax
                            else:
                                          self.camera[1] = position[1]

              def update(self):
                            for layer in self.layers:
                                          layer.display(self.camera)

                            for entity in self.entities:
                                          entity.update()
                                          



class Entity(pygame.sprite.Sprite):
              def __init__(self, stage, img_filename, rect_ids, hitbox=None, ghostmode=False, start_position=[0,0], priority=0):
                            self.stage = stage
                            self.image = pygame.image.load(img_filename).convert_alpha()
                            self.rect_list = rect_list
                            self.displayed_surf = rect_list[0]
                            self.hitbox = hitbox
                            self.ghostmode = ghostmode
                            self.position = start_position
                            self.priority = priority
                            
              def set_displayed_surf(self, rect_id):
                            self.displayed_surf = self.image.subsurface(self.rect_list[rect_id])

              def set_position(self, position):
                            self.position = position
                            
              def set_hitbox(self, hitbox):
                            self.hitbox = hitbox
                            
              def display(self):
                            #definition of the limits in which the entity can be displayed
                            xmin = self.stage.camera[0] - self.stage.screen.get_width()/2 - self.displayed_surf.get_width()/2
                            xmax = self.stage.camera[0] + self.stage.screen.get_width()/2 + self.displayed_surf.get_width()/2
                            ymin = self.stage.camera[1] - self.stage.screen.get_height()/2 - self.displayed_surf.get_height()/2
                            ymax = self.stage.camera[1] + self.stage.screen.get_height()/2 + self.displayed_surf.get_height()/2

                            if (self.position[0] > xmin and self.position[0] < xmax and
                                self.position[1] > ymin and self.position[1] < ymax):
                                          x = self.position[0] - self.stage.camera[0] + self.stage.screen.get_width()/2 - self.displayed_surf.get_width()/2
                                          y = self.position[1] - self.stage.camera[1] + self.stage.screen.get_height()/2 - self.displayed_surf.get_height()/2

                                          pygame.Surface.blit(self.stage.screen, self.displayed_surf, (x,y))


class Tile(Entity):
              def __init__(self, stage, img_filename, rect_list, hitbox=None, ghostmode=False, position=[0, 0], priority=0):
                            Entity.__init__(self, stage, img_filename, rect_list, hitbox, ghostmode, position)

              def update(self):
                            Entity.display(self)
              

		
##class Character(Entity):
##	def __init__(self, screen, image, ghostmode=True, thrust=10, weight=10):
##		Entity.__init__(self, screen, image, ghostmode=ghostmode):
##		self.speed = (0,0)
##		self.accel = (0,0)
##		self.thrust = 10
##


	

pygame.init()

screen = pygame.display.set_mode((640, 400), pygame.DOUBLEBUF, 32)
clock = pygame.time.Clock()


fond  = Layer(screen, "fond.png", (2, 1))
cadre = Layer(screen, "cadre.png", (0, 0))

carte = Stage(screen, (4000,2000))
carte.add_layers([fond])
x=0
y=0

rect_list = [(0,0,100,100),(100,0,100,100),(200,0,100,100),(300,0,100,100)]
tile1 = Tile(carte, "tile.png", rect_list, position=[900,400])
tile1.set_displayed_surf(1)
carte.add_tiles([tile1])


while(True):
              time_passed = clock.tick(50)

              for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                          pygame.quit()
                                          sys.exit()
                            if event.type == pygame.KEYDOWN:
                                          if event.key == pygame.K_DOWN:
                                                        y = y + 10
                                          elif event.key == pygame.K_UP:
                                                        y = y - 10
                                          elif event.key == pygame.K_LEFT:
                                                        x = x - 10
                                          elif event.key == pygame.K_RIGHT:
                                                        x = x + 10
              carte.set_camera([x, y])
              carte.set_camera([x, y])
              carte.update()
              pygame.display.flip()

