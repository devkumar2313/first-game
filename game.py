import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity,Player,Enemy
from scripts.utils import load_image,load_images,Animation
from scripts.tilemap import Tilemap
from scripts.cloud import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
import os
class Adventure:
  def __init__(self):
    pygame.init()
    pygame.display.set_caption("Adventure fuji")
    self.screen = pygame.display.set_mode((640,480))
    self.display = pygame.Surface((320,240),pygame.SRCALPHA)
    self.display_2 = pygame.Surface((320,240))
    
    
#this is for enlargement  
   #  self.display = pygame.Surface((320,240))


#this is for making tree to move   
   #  self.img = pygame.image.load('Surface_data/PNG/Objects_separated/Tree1.png')
   #  self.img.set_colorkey((0,0,0))
   #  self.rect1 = pygame.Rect(100,100,30,40)

    self.pos1 = [170,200]
    self.mov1 = [False,False]
    self.mov2 = [False,False]
    self.clock = pygame.time.Clock()
    self.assets = {
       'grass':load_images('ground_grass'),
       'player':load_image('character/idle/idle1.png'),
       'tree':load_images('tree'),
       'bush':load_images('bush'),
       'background':load_image('background.png'),
       'clouds':load_images('clouds'),
       'player/idle':Animation(load_images('character/idle'),img_dur = 6),
       'player/jump':Animation(load_images('character/jump'),img_dur=7),
       'particle/leaf':Animation(load_images('particle/leaf'),img_dur=20,loop=False),
       'player/wall_slide':Animation(load_images('character/idle'),img_dur=6),
       'particle/particle':Animation(load_images('particle/particle'),img_dur=6,loop=False),
       'enemy/idle':Animation(load_images('enemy/idle'),img_dur = 6),
       'enemy/run':Animation(load_images('enemy/run'),img_dur=4),
       'gun':load_image('gun.png'),
       'projectile':load_image('projectile.png')

    }
    
    self.sfx = {
       'jump':pygame.mixer.Sound('sfx/jump.wav'),
       'dash':pygame.mixer.Sound('sfx/dash.wav'),
       'hit':pygame.mixer.Sound('sfx/hit.wav'),
       'shoot':pygame.mixer.Sound('sfx/shoot.wav'),
       'ambience':pygame.mixer.Sound('sfx/ambience.wav'),
    }
    
    self.sfx['ambience'].set_volume(0.2)
    self.sfx['shoot'].set_volume(0.4)
    self.sfx['hit'].set_volume(0.8)
    self.sfx['dash'].set_volume(0.3)
    self.sfx['jump'].set_volume(0.7)
    
    self.clouds = Clouds(self.assets['clouds'],count=16)
    self.player = Player(self,(50,50),(8,15))

    self.tilemap = Tilemap(self,tile_size=16)
    self.level = 0
    self.load_level(self.level)
    
    self.screenshake = 0
    
    
  def load_level(self,map_id):
     self.tilemap.load('maps/' +str(map_id) + '.json')
   #   self.tilemap.load('map.json')

     self.leaf_spawners = []
     for tree in self.tilemap.extract([('tree',0)],keep=True):
       self.leaf_spawners.append(pygame.Rect(4+tree['pos'][0],4+tree['pos'][1],23,19))

     self.enemies = []
     for spawner in self.tilemap.extract([('spawners',0),('spawners',1)]):
       if spawner['variant'] == 0:
          self.player.pos = spawner['pos']
          self.player.air_time = 0
       else:
          self.enemies.append(Enemy(self,spawner['pos'],(8,15)))

     print(self.leaf_spawners)
     self.projectiles = []
     self.particles = []
     self.sparks = []
    
     self.scroll = [0,0]
     self.dead = 0 
     self.transition = -30
   
    
    
    
  
  def run(self):
     
    pygame.mixer.music.load('music.wav')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    
    self.sfx['ambience'].play(-1)
    while True:
 #this is for enlargement        
         # self.display.fill((14,219,248))
         self.display.fill((0,0,0,0))
         self.display_2.blit(self.assets['background'],(0,0))
         
         self.screenshake = max(0,self.screenshake - 1)
         
         if not len(self.enemies):
            self.transition += 1
            if self.transition > 30:
               self.level = min(self.level + 1,len(os.listdir('maps')) - 1)
               self.load_level(self.level)
         if self.transition < 0:
            self.transition += 1
         
         if self.dead:
            self.dead += 1
            if self.dead >= 10:
               self.transition = min(30,self.transition + 1)
            if self.dead > 40:
               self.load_level(self.level)

         self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0]) /30
         self.scroll[1] += (self.player.rect().centery - self.display.get_width()/2 - self.scroll[1]) /30
         render_scroll = (int(self.scroll[0]),int(self.scroll[1]))
         for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
               pos = (rect.x + random.random() * rect.width,rect.y +random.random() * rect.height)
               self.particles.append(Particle(self,'leaf',pos,velocity=[-0.1,0.3],frame=random.randint(0,20)))
         self.clouds.update()
         self.clouds.render(self.display_2,offset=render_scroll)


         self.tilemap.render(self.display,offset = render_scroll)

         for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap,(0,0))
            enemy.render(self.display,offset=render_scroll)
            if kill:
               self.enemies.remove(enemy)
               
         if not self.dead:
            self.player.update(self.tilemap,(self.mov2[1] - self.mov2[0],0))
            self.player.render(self.display,offset=render_scroll)
         


         # self.player.update(self.tilemap,(self.mov2[1] - self.mov2[0],0))
         # # self.player.render(self.display)
         # self.player.render(self.display,offset = self.scroll)
         # print(self.tilemap.physics_rects_around(self.player.pos))


         self.pos1[1] += (self.mov1[1] - self.mov1[0])*4
         self.pos1[0] += (self.mov2[1] - self.mov2[0])*4

         for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            img = self.assets['projectile']
            self.display.blit(img,(projectile[0][0] - img.get_width() / 2 - render_scroll[0],projectile[0][1] -img.get_height() / 2 - render_scroll[1]))

            if self.tilemap.solid_check(projectile[0]):
               self.projectiles.remove(projectile)
               for i in range(4):
                   self.sparks.append(Spark(projectile[0],random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0) ,2+random.random()))
               
            elif projectile[2] > 360:
               self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50:
               if self.player.rect().collidepoint(projectile[0]):
                  self.projectiles.remove(projectile)
                  self.dead += 1
                  self.sfx['hit'].play()
                  self.screenshake = max(16,self.screenshake)
                  for i in range(30):
                     angle = random.random() * math.pi * 2
                     speed = random.random() * 5
                     self.sparks.append(Spark(self.player.rect().center,angle,2+ random.random()))
                     self.particles.append(Particle(self,'particle',self.player.rect().center,velocity=[math.cos(angle+math.pi) * speed * 0.5,math.sin(angle + math.pi) * speed * 0.5],frame= random.randint(0,7)))
                     
         for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display,offset=render_scroll)
            if kill:
               self.sparks.remove(spark)
               
         display_mask = pygame.mask.from_surface(self.display)
         display_sillhouette = display_mask.to_surface(setcolor=(0,0,0,180),unsetcolor=(0,0,0,0))
         
         for offset in [(-1,0),(1,0),(0,-1),(0,1)]:
            self.display_2.blit(display_sillhouette,offset)
            
         
         for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.display,offset=render_scroll)
            if particle.type == 'leaf':
               particle.pos[0] += math.sin(particle.animation.frame * 0.035)*0.3
            if kill:
               self.particles.remove(particle)
  #this is for making tree to move       
         # self.screen.blit(self.img,self.pos1)
         # img_mask = pygame.Rect(self.pos1[0],self.pos1[1],self.img.get_width(),self.img.get_height())
         # if img_mask.colliderect(self.rect1):
         #    pygame.draw.rect(self.screen,(0,100,243),self.rect1)
         # else:
         #    pygame.draw.rect(self.screen,(0,40,155),self.rect1)
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
              pygame.quit()
              sys.exit()
            if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_UP:
                  # this for infinite jump
                  # self.player.velocity[1] = -3
                  if self.player.jump():
                     self.sfx['jump'].play()
                  
               if event.key == pygame.K_DOWN:
                  self.mov1[1] = True
               if event.key == pygame.K_LEFT:
                  self.mov2[0] = True
               if event.key == pygame.K_RIGHT:
                  self.mov2[1] = True
               if event.key == pygame.K_x:
                  self.player.dash()
            if event.type == pygame.KEYUP:
               if event.key == pygame.K_UP:
                  self.mov1[0] = False
               if event.key == pygame.K_DOWN:
                  self.mov1[1] = False
               if event.key == pygame.K_LEFT:
                  self.mov2[0] = False
               if event.key == pygame.K_RIGHT:
                  self.mov2[1] = False
                  
         if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(transition_surf,(255,255,255),(self.display.get_width() // 2,self.display.get_height() // 2),(30 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255,255,255))
            self.display.blit(transition_surf,(0,0))
            
         self.display_2.blit(self.display,(0,0))
              

#this is for enlargement
         # self.screen.blit(pygame.transform.scale(self.display,self.screen.get_size()),(0,0))
         screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,random.random() * self.screenshake - self.screenshake / 2)
         self.screen.blit(pygame.transform.scale(self.display_2,self.screen.get_size()),screenshake_offset)
         pygame.display.update()
         self.clock.tick(60)


Adventure().run()
