import pygame, sys
import json
from pygame.locals import *

# Global variables
controls = {"down":pygame.K_DOWN, "right":pygame.K_RIGHT, "up":pygame.K_UP, "left":pygame.K_LEFT}

class EventListener():
              listeners = []

              def __init__(self):
                            EventListener.listeners.append(self)

              @staticmethod
              def listen_all(event):
                            try:
                                          for listener in EventListener.listeners:
                                                        listener.on_event(event)
                            except Exception as e:
                                          print ("Error in EventListener Class :\n!!! %s !!!")%e

class Layer():
              """This class is supposed to display a layer and allow scrolling"""
              def __init__(self, screen, img_filename, scrolling_speed = (1,1), top_priority=False, scale=1):
                            self.scrolling_speed = scrolling_speed # the speed of scrolling in pixels/frame
                            self.screen = screen # the screen
                            self.top_priority = top_priority #it will be displayed in foreground if True
                            self.scale = scale # ratio

                            self.img = pygame.image.load(img_filename).convert_alpha()

                            self.virtual_width = (screen.get_width()/self.img.get_width()+1)*self.img.get_width()
                            self.virtual_height = (screen.get_height()/self.img.get_height()+1)*self.img.get_height()
                            self.width = screen.get_width() + self.virtual_width
                            self.height = screen.get_height() + self.virtual_height
                            self.panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

                            #construction of a big panel in order to make scrolling possible and infinite
                            for i in range(0, self.panel.get_width(), self.img.get_width()):
                                          for j in range(0, self.panel.get_height(), self.img.get_height()):
                                                        pygame.Surface.blit(self.panel, self.img, (i, j))

              def set_scale(self, scale):
                            self.scale = scale
                            new_img_width = (int)(self.img.get_width()*scale)
                            new_img_height = (int)(self.img.get_height()*scale)
                            self.scaled_img = pygame.transform.scale(self.img, (new_img_width, new_img_height))                   
                            
                            self.virtual_width = (screen.get_width()/self.scaled_img.get_width()+1)*self.scaled_img.get_width()
                            self.virtual_height = (screen.get_height()/self.scaled_img.get_height()+1)*self.scaled_img.get_height()
                            self.width = screen.get_width() + self.virtual_width
                            self.height = screen.get_height() + self.virtual_height
                            self.panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

                            #construction of a big panel in order to make scrolling possible and infinite
                            for i in range(0, self.panel.get_width(), self.scaled_img.get_width()):
                                          for j in range(0, self.panel.get_height(), self.scaled_img.get_height()):
                                                        pygame.Surface.blit(self.panel, self.scaled_img, (i, j))
              
              #displaying the right part
              def display(self, coordinates):
                            x = (int)(coordinates[0]*self.scrolling_speed[0]*self.scale)
                            y = (int)(coordinates[1]*self.scrolling_speed[1]*self.scale)
                            w = self.virtual_width
                            h  = self.virtual_height
                            dispx = x - w*(x/w) 
                            dispy = y - h*(y/h)
                            display_rect = pygame.Rect(dispx, dispy, self.screen.get_width(), self.screen.get_height())
                            display = self.panel.subsurface(display_rect)

                            pygame.Surface.blit(screen, display, (0, 0))   
                            

class Stage():
              def __init__(self, screen, stage_filename, camera=None, scale=1):
                            self.screen = screen
                            self.scale = scale

                            self.layers = []
                            self.entities = []
                            self.tiles = []
                            self.characters = []
                            self.main_character = None

                            #parsing the stage file and building the stage
                            try:
                                          stage_file = open(stage_filename)
                                          json_stage = json.loads(stage_file.read())

                                          self.size = json_stage['size']
                                          for layer in json_stage['layers']:
                                                        layer_img_filename = layer['filename']
                                                        if (layer['priority'] > 0):
                                                                      top_priority = True
                                                        else:
                                                                      top_priority = False
                                                        self.layers.append(Layer(self.screen, layer_img_filename, layer['speed'], top_priority, scale))

                                          tiles_list = []
                                          tile_img_filename = json_stage['tiles']['filename']
                                          tile_rect_list = json_stage['tiles']['rect_list']
                                          for tile in json_stage['tiles']['tiles']:
                                                        if (tile['ghostmode'] > 0):
                                                                      tile_ghostmode = True
                                                        else:
                                                                      tile_ghostmode = False
                                                        
                                                        tile_priority = tile['priority']
                                                        tile_rect_id = tile['rect_id']
                                                        tile_position = tile['position']
                                                        tiles_list.append(Tile(self, tile_img_filename, tile_rect_list, tile_rect_id, position=tile_position, ghostmode=tile_ghostmode, priority=tile_priority, scale=scale))
                                                        
                                          self.tiles += tiles_list
                                          self.entities += tiles_list
                                                        
                            except IOError as e:
                                          print ("cannot open file \n!!! %s !!!")%e
                            #except Exception as e:
                            #             print ("Exception :\n!!! %s !!!")%e
                            finally :
                                          stage_file.close()
                            
                            if (camera == None):
                                          self.camera = [self.size[0]/2, self.size[1]/2]
                            else:
                                self.camera = camera

              def add_layers(self, layers):
                            self.layers+=layers

              def add_tiles(self, tiles):
                            self.tiles += tiles
                            self.entities += tiles

              def add_characters(self, characters):
                            self.characters += characters
                            self.entities += characters
                            
              def remove_tile(self, tile):
                            try:
                                          self.tiles.remove(tile)
                                          self.entities.remove(tile)
                            except ValueError as e:
                                          print ("Cannot remove : his tile is not in this stage :\n!!! %s !!!")%e

              def remove_character(self, character):
                            try:
                                          self.characteres.remove(characters)
                                          self.entities.remove(characters)
                                          if character == self.main_character:
                                                        self.main_character = None
                            except ValueError as e:
                                          print ("Cannot remove : this character is not in this stage :\n!!! %s !!!")%e

              def set_main_character(self, character):
                            try:
                                          index = self.characters.index(character)
                                          self.main_character = self.characters[index]
                            except ValueError as e:
                                          print ("This character is not in this stage :\n!!! %s !!!")%e

              def set_scale(self, scale):
                            self.scale = scale
                            for layer in self.layers:
                                          layer.set_scale(scale)

                            for entity in self.entities:
                                          entity.set_scale(scale)
                            
                            
              #position of the camera
              def set_camera(self, position):
                            xmin = (int)((self.screen.get_width()/2)/self.scale)
                            xmax = self.size[0] - (int)((self.screen.get_width()/2)/self.scale)
                            ymin = (int)((self.screen.get_height()/2)/self.scale)
                            ymax = self.size[1] - (int)((self.screen.get_height()/2)/self.scale)

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
                                          if entity == self.main_character:
                                                        self.set_camera(entity.position)
                                                        #print [entity.speed, entity.accel]
                                                        
                                          entity.update()



class Entity(pygame.sprite.Sprite):
              def __init__(self, stage, img_filename, rect_list, hitbox=None, ghostmode=False, start_position=[0,0], priority=0, scale=1):
                            self.stage = stage
                            self.image = pygame.image.load(img_filename).convert_alpha()
                            self.rect_list = rect_list
                            self.hitbox = hitbox
                            self.ghostmode = ghostmode
                            self.position = start_position
                            self.priority = priority
                            self.scale = 1

              def set_scale(self, scale):
                            raise NotImplementedError
              
              def display(self):
                            raise NotImplementedError

              def set_position(self, position):
                            self.position = position
                            
              def set_hitbox(self, hitbox):
                            self.hitbox = hitbox
                            
              def delete(self):
                            self.stage.remove(self)


class Tile(Entity):
              def __init__(self, stage, img_filename, rect_list, rect_id, hitbox=None, ghostmode=False, position=[0, 0], priority=0, scale=1):
                            Entity.__init__(self, stage, img_filename, rect_list, hitbox, ghostmode, position, scale)
                            self.displayed_surf = self.image.subsurface(self.rect_list[rect_id])

                            new_width = self.displayed_surf.get_width()*self.scale
                            new_height = self.displayed_surf.get_height()*self.scale
                            self.scaled_displayed_surf = pygame.transform.scale(self.displayed_surf, (new_width, new_height))

              def set_displayed_surf(self, rect_id):
                            self.displayed_surf = self.image.subsurface(self.rect_list[rect_id])

              def set_scale(self, scale):
                            self.scale = scale

              def display(self):
                            try:
                                          #definition of the limits in which the entity can be displayed
                                          new_width = (int)(self.displayed_surf.get_width()*self.scale)
                                          new_height = (int)(self.displayed_surf.get_height()*self.scale)
                                          self.scaled_displayed_surf = pygame.transform.scale(self.displayed_surf, (new_width, new_height))
                                          
                                          xmin = (int)(self.stage.camera[0]*self.scale) - self.stage.screen.get_width()/2 - self.scaled_displayed_surf.get_width()/2
                                          xmax = (int)(self.stage.camera[0]*self.scale) + self.stage.screen.get_width()/2 + self.scaled_displayed_surf.get_width()/2
                                          ymin = (int)(self.stage.camera[1]*self.scale) - self.stage.screen.get_height()/2 - self.scaled_displayed_surf.get_height()/2
                                          ymax = (int)(self.stage.camera[1]*self.scale) + self.stage.screen.get_height()/2 + self.scaled_displayed_surf.get_height()/2
                                          if ((int)(self.position[0]*self.scale) > xmin and (int)(self.position[0]*self.scale) < xmax and
                                              (int)(self.position[1]*self.scale) > ymin and (int)(self.position[1]*self.scale) < ymax):
                                                        x = (int)(self.position[0]*self.scale) - (int)(self.stage.camera[0]*self.scale) + self.stage.screen.get_width()/2 - self.scaled_displayed_surf.get_width()/2
                                                        y = (int)(self.position[1]*self.scale) - (int)(self.stage.camera[1]*self.scale) + self.stage.screen.get_height()/2 - self.scaled_displayed_surf.get_height()/2

                                                        pygame.Surface.blit(self.stage.screen, self.scaled_displayed_surf, (x,y))
                            except Exception as e:
                                          print ("Cannot blit displayed_surf :\n!!! %s !!!")%e

              
                            
              def update(self):
                            self.display()
              

		
class Character(Entity, EventListener):
              def __init__(self, stage, img_filename, rect_list, hitbox=None, ghostmode=False, start_position=[0,0], priority=0):
                            EventListener.__init__(self)
                            Entity.__init__(self, stage, img_filename, rect_list, hitbox, ghostmode, start_position)
                            self.brut_accel = [0,0]
                            self.speed = [0,0]
                            self.accel = [0,0]
                            self.position = start_position

                            ## TODO : make a way to enter them
                            self.cx = 1
                            self.thrust = 40
                            self.weight = 20

                            self.displayed_surf = self.image.subsurface(self.rect_list[0])

              def on_event(self, event):
                            if event.type == pygame.KEYDOWN:
                                          if event.key == controls['down']:
                                                        self.brut_accel[1] += self.thrust
                                          if event.key == controls['up']:
                                                        self.brut_accel[1] -= self.thrust
                                          if event.key == controls['right']:
                                                        self.brut_accel[0] += self.thrust
                                          if event.key == controls['left']:
                                                        self.brut_accel[0] -= self.thrust
                            if event.type == pygame.KEYUP:
                                          if event.key == controls['down']:
                                                        self.brut_accel[1] -= self.thrust
                                          if event.key == controls['up']:
                                                        self.brut_accel[1] += self.thrust
                                          if event.key == controls['right']:
                                                        self.brut_accel[0] -= self.thrust
                                          if event.key == controls['left']:
                                                        self.brut_accel[0] += self.thrust

              def set_scale(self, scale):
                            self.scale = scale

              def display(self):
                            try:
                                          #definition of the limits in which the entity can be displayed
                                          new_width = (int)(self.displayed_surf.get_width()*self.scale)
                                          new_height = (int)(self.displayed_surf.get_height()*self.scale)
                                          self.scaled_displayed_surf = pygame.transform.scale(self.displayed_surf, (new_width, new_height))
                                          
                                          xmin = (int)(self.stage.camera[0]*self.scale) - self.stage.screen.get_width()/2 - self.scaled_displayed_surf.get_width()/2
                                          xmax = (int)(self.stage.camera[0]*self.scale) + self.stage.screen.get_width()/2 + self.scaled_displayed_surf.get_width()/2
                                          ymin = (int)(self.stage.camera[1]*self.scale) - self.stage.screen.get_height()/2 - self.scaled_displayed_surf.get_height()/2
                                          ymax = (int)(self.stage.camera[1]*self.scale) + self.stage.screen.get_height()/2 + self.scaled_displayed_surf.get_height()/2
                                          if ((int)(self.position[0]*self.scale) > xmin and (int)(self.position[0]*self.scale) < xmax and
                                              (int)(self.position[1]*self.scale) > ymin and (int)(self.position[1]*self.scale) < ymax):
                                                        x = (int)(self.position[0]*self.scale) - (int)(self.stage.camera[0]*self.scale) + self.stage.screen.get_width()/2 - self.scaled_displayed_surf.get_width()/2
                                                        y = (int)(self.position[1]*self.scale) - (int)(self.stage.camera[1]*self.scale) + self.stage.screen.get_height()/2 - self.scaled_displayed_surf.get_height()/2

                                                        pygame.Surface.blit(self.stage.screen, self.scaled_displayed_surf, (x,y))

                            except Exception as e:
                                          print ("Cannot blit displayed_surf :\n!!! %s !!!")%e
              
              def move(self):
                            self.accel[0] = (self.brut_accel[0] - self.speed[0]*self.cx)/(float)(self.weight)
                            self.accel[1] = (self.brut_accel[1] - self.speed[1]*self.cx)/(float)(self.weight)
                            self.speed[0] += self.accel[0]
                            self.speed[1] += self.accel[1]
                            self.position[0] += (int)(self.speed[0])
                            self.position[1] += (int)(self.speed[1])

              def update(self):
                            self.move()
                            self.display()

pygame.init()

screen = pygame.display.set_mode((960, 600), pygame.DOUBLEBUF, 32)
clock = pygame.time.Clock()

carte = Stage(screen, "stage.txt")
perso = Character(carte, "tile.png", [(0,0,100,100),(100,0,100,100),(200,0,100,100),(300,0,100,100)])
carte.add_characters([perso])
carte.set_main_character(perso)
x=0
y=0
scale = 1

while(True):
              time_passed = clock.tick(50)

              for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                          pygame.quit()
                                          sys.exit()

                            if event.type == pygame.KEYDOWN:
                                          if event.key == pygame.K_a:
                                                        print("a push")
                                                        scale -= 0.02
                                                        carte.set_scale(scale)
                            EventListener.listen_all(event)
                            
              carte.update()
              pygame.display.flip()

