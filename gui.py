import pygame
import sys
import numpy as np
import threading
from time import time
from io import BytesIO, StringIO
from capclient import CapClient
from touchclient import TouchClient
from PIL import Image

class Main():
    def __init__(self):
        assert len(sys.argv) == 4
        self.rotation = 0  # or 90 for landscape
        self.winrotation = self.rotation
        p_size = list(map(int, sys.argv[1].split("x")))
        p_orig = list(map(int, sys.argv[2].split("x")))

        self.size = p_size[0], p_size[1]
        self.orig = p_orig[0], p_orig[1]
        # My Add
        if self.winrotation in [90, 270]:
            self.size = p_size[1], p_size[0]
            self.orig = p_orig[1], p_orig[0]

        self.path = sys.argv[3]
        
        self.cap = CapClient(self)
        self.cap.start()
        self.touch = TouchClient(self)
        self.touch.start()
        
        self.mouse_down = False
        self.mouse_pos = (0, 0)

        self.scale = self.orig[0] / float(self.size[0])
        self.ratio = self.orig[1] / float(self.orig[0])
        print('Scale, ratio:', self.scale, self.ratio)

        self.sizep = self.size[0], int(self.orig[1] / self.scale)
        self.sizel = int(self.orig[1] / self.scale), self.size[0]
        print('Raw image size l/p:', self.sizel, self.sizep)

        #self.rotation = 0 # Mii: 0, 90, 270 == NG 
        self.calc_scale()
        self.state_str = '-Start-'

        pygame.init()
        pygame.font.init()
        # pygame.key.set_repeat(delay, interval)
        pygame.key.set_repeat(30, 30)

        self.screen = pygame.display.set_mode(self.size)

    def calc_scale(self):
        self.landscape = self.rotation in [90, 270]
        if self.winrotation in [90, 270]:
            self.landscape = self.rotation in [0, 180]
        max_w = self.size[0]
        if self.landscape: # == 270 or self.landscape == 90:
            x = 0
            w = max_w
            h = w / self.ratio
            y = (self.size[1] - h) / 2
        else: # self.landscape == 180 or self.landscape == 0:
            y = 0
            h = self.size[1]
            w = h / self.ratio
            x = (self.size[0] - w) / 2

        self.proj = list(map(int, [x, y, w, h]))
        print('Projection:', self.proj)
        self.frame_update = True
        
    def blit_center(self, dst, src, rect):
        x = rect[0] - int((src.get_width() / 2) - (rect[2] / 2))
        y = rect[1] - int((src.get_height() / 2) - (rect[3] / 2))
        dst.blit(src, (x, y))
        
    def exit(self):
        self.running = False
        self.cap.write(["end"])
        self.touch.write(["end"])

    def save_image(self, img, fn):
        img.save(fn,"PNG")

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit()

            if hasattr(event, "pos"):
                ix, iy = event.pos
                fx = min(max(0, (ix - self.proj[0]) / float(self.proj[2])), 1)
                fy = min(max(0, (iy - self.proj[1]) / float(self.proj[3])), 1)
                if self.rotation == 0:
                    x = fx
                    y = fy
                if self.rotation == 90:
                    x = 1.0 - fy
                    y = fx
                if self.rotation == 180:
                    x = 1.0 - fx
                    y = 1.0 - fy
                if self.rotation == 270:
                    x = fy
                    y = 1.0 - fx

                pygame.display.set_caption(str(x) + self.state_str + str(y))

            if hasattr(event, "button"):
                if event.button is not 1:
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.touch.write(["down", x, y, 0])
                    self.mouse_down = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.touch.write(["up", 0])
                    self.mouse_down = False

            if event.type == pygame.MOUSEMOTION:
                if self.mouse_down:
                    self.touch.write(["move", x, y, 0])
                    self.mouse_pos = (x, y)

            if event.type == pygame.KEYUP:
                if (event.key not in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]):
                    self.touch.write(["up", 0])
                    self.mouse_down = False
                elif (event.key == pygame.K_RCTRL):
                    self.state_str = '=Auto='
                elif (event.key == pygame.K_SPACE):
                    self.state_str = '=Stop='
                else:
                    pass


    def run(self):
        self.running = True
        self.screen_update = True
        self.frame_update = False
        self.frame_cache = pygame.Surface(self.size)
        last_frame = None

        while self.running:
            self.events()

            msgs = self.cap.read()
            msgl = len(msgs)
            if msgl:
                msg = msgs[msgl - 1]
                cmd = msg[0]
                if cmd == "data":
                    last_frame = pygame.image.load(BytesIO(msg[1]))
                    self.frame_update = True
                    
            if self.frame_update:
                self.frame_update = False
                if last_frame is not None:
                    if self.landscape:
                        a = last_frame.subsurface(pygame.Rect((0,0), self.sizel))
                    else:
                        a = last_frame.subsurface(pygame.Rect((0,0), self.sizep))
                    aw, ah = a.get_size()
                    if aw != self.proj[2] or ah != self.proj[3]:
                        self.frame_cache = pygame.transform.smoothscale(a, (self.proj[2], self.proj[3]))
                    else:
                        self.frame_cache = a.copy()
                self.screen_update = True
                        
            if self.screen_update:
                self.screen.fill((0, 0, 0))
                self.screen_update = False
                self.screen.blit(self.frame_cache, (self.proj[0], self.proj[1]))
                pygame.display.update()
                        

             
a = Main()
a.run()
