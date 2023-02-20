import pygame as pg
from sys import path
from sys import exit
import math
from math import *
import os
import random
import sqlite3

# Make path point to current directory
my_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(my_path)
path.append(my_path)

#Setup
pg.init()
pg.mouse.set_cursor(*pg.cursors.broken_x)
screen = pg.display.set_mode((800,600)) #set your window size, (x,y)
icon = pg.image.load('images/icon.png')
pg.display.set_caption("ReactFast")
pg.display.set_icon(icon)
clock = pg.time.Clock()
conn = sqlite3.connect('score.db')
c = conn.cursor()
try:
	c.execute("CREATE TABLE scores (score)")
	conn.commit()
except:
	print("Table already made | SCORES")

#colors
white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0,0,255)

#variables
myangle = 0
state = 0
make = True

#classes
class GunGameSingleplayer:
    def __init__(self):
        #self.gun_hitbox = pg.Rect(55, 400, 100, 100)
        self.gun_hitbox = pg.Rect(55, 75, 100, 100)
        self.gunman = pg.image.load("images/rifle_person.png")
        self.gun2 = pg.image.load("images/rifle_person.png")
        self.gunman = pg.transform.scale(self.gunman, (100,100))
        self.gun2 = pg.transform.scale(self.gunman, (100,100))
        self.hitbox = pg.Rect(900,400,50,50)
        self.bulletSurface = pg.Rect(55,75,50,20)
        self.bulletImage = pg.image.load('images/bullet.png')
        self.bulletImage = pg.transform.scale(self.bulletImage, (50, 35))
        self.ballImage = pg.image.load('images/target.png')
        self.ballImage = pg.transform.scale(self.ballImage, (50,50))
        self.mouse = False
        self.timer_start = True
        self.timer = 0
        self.timer2_start = False
        self.timer2 = 0
        self.timer3_start = False
        self.timer3 = 0
        self.score = 0
        self.bullets = 5
        self.already_played_reloading = False
        self.draw_bullet = False
        self.bullet = False
        self.already_rotated = False
        self.shoot = True
        self.shoot_time = 0

    def changepos(self):
        self.hitbox[0] = random.randint(200,750)
        self.hitbox[1] = random.randint(305, 500)

    def bulletReset(self):
        self.bullet = False
        self.draw_bullet = False
        self.already_rotated = False
        self.bulletImage = pg.image.load("images/bullet.png")
        self.bulletImage = pg.transform.scale(self.bulletImage, (50, 35))
        self.bulletSurface[0] = 55
        self.bulletSurface[1] = 75

    def update(self):
        global state, make
        if self.timer2_start == True:
            self.timer2 += 1
        l, m, r = pg.mouse.get_pressed()
        if l == 1 and self.shoot == True:
            self.bullet = True
        if self.timer_start == True:
            self.timer += 1
        if self.timer3_start == True:
            self.timer3 += 1
        if self.bullet:
            self.bulletUpdate()
        else:
            self.draw_bullet = False
        if self.timer > 60:
            self.changepos()
            self.timer = 0
            self.bulletReset()
            self.timer_start = False
            self.timer3_start = True
        if self.timer3 > self.shoot_time:
            print(self.shoot_time)
            self.timer3 = 0
            self.bullets -= 1
            self.bulletReset()
            self.timer_start = True
            self.timer3_start = False
            c.execute("SELECT * FROM scores")
            result = c.fetchall()
            if not result:
                c.execute(f"INSERT INTO scores VALUES ({self.score})")
                conn.commit()
            else:
                if self.score > int(result[0][0]):
                    c.execute(f"DELETE FROM scores")
                    conn.commit()
                    c.execute(f"INSERT INTO scores VALUES ({self.score})")
                    conn.commit()
            make = True
            state = 4
        if self.draw_bullet:
            self.bulletDraw()

    def bulletUpdate(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        if not self.already_rotated:
            self.bulletImage = pg.transform.rotate(self.bulletImage, myangle)
            self.already_rotated = True
        rect = self.bulletImage.get_rect(center=self.bulletSurface.center)
        dx = mouse_x - 55
        dy = mouse_y - 75
        angle = math.atan2(dy, dx)
        self.bulletSurface[0] += 50 * math.cos(angle)
        self.bulletSurface[1] += 50 * math.sin(angle)
        self.draw_bullet = True
        if self.hitbox.colliderect(self.bulletSurface) and self.draw_bullet:
            self.hitbox[0] = 900
            self.score += 1
            self.timer = 0
            self.timer3 = 0
            self.bullets -= 1
            self.timer_start = True
            self.timer3_start = False
            bullet_sound = pg.mixer.Sound("sounds/bullet.wav")
            pg.mixer.Sound.play(bullet_sound)
            self.bulletReset()

    def draw(self):
        font = pg.font.Font('fonts/really_free.ttf', 50)
        text = font.render(f'Score: {self.score}', True, black)
        textRect = text.get_rect()
        textRect.center = (90, 250)
        #textRect.center = (90, 575)
        font1 = pg.font.Font('fonts/really_free.ttf', 50)
        text1 = font1.render(f'Bullets: {self.bullets}/5', True, black)
        textRect1 = text1.get_rect()
        textRect1.center = (90, 50)
        #textRect1.center = (90, 375)
        screen.blit(self.ballImage, (self.hitbox[0], self.hitbox[1]))
        screen.blit(text, textRect)
        screen.blit(text1, textRect1)

    def bulletDraw(self):
        screen.blit(self.bulletImage, (self.bulletSurface[0], self.bulletSurface[1]))
    def reload(self):
        if self.already_played_reloading == True:
            pass
        else:
            reloadSound = pg.mixer.Sound("sounds/reload.wav")
            pg.mixer.Sound.play(reloadSound)
            self.timer2_start = True
        if self.timer2 > 40:
            self.bullets = 5
            self.timer2_start = False
            self.timer2 = 0

    def gunUpdate(self):
        global myangle
        mouse_x, mouse_y = pg.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.gun_hitbox[0], mouse_y - self.gun_hitbox[1]
        myangle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.gunman = pg.transform.rotate(self.gun2, int(myangle))
        self.rect = self.gunman.get_rect(center=self.gun_hitbox.center)
        if self.bullets <= 0:
            self.reload()
            self.shoot = False
        else:
            self.shoot = True
    def gunDraw(self):
        screen.blit(self.gunman, (self.gun_hitbox[0],self.gun_hitbox[1]))

p = GunGameSingleplayer()
def game():
    global state, make, p
    if make:
        p = GunGameSingleplayer()
    lines = []
    lines.append(pg.Rect(200, 0, 5, 600))
    lines.append(pg.Rect(0,295,800,5))
    bg = pg.image.load("images/sand.png")
    bg = pg.transform.scale(bg, (800,600))
    #gameloop
    while state == 1:
        # Quit game window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
        # Input
        pg.event.pump()

        #startup
        screen.fill(white)
        screen.blit(bg,(0,0))

        # Update
        p.gunUpdate()
        p.update()
        if p.draw_bullet:
            p.bulletDraw()
        # Events

        # Drawings
        p.gunDraw()
        p.draw()
        #screen.blit(text,textRect)
        for line in lines:
            pg.draw.rect(screen,blue,line)
        pg.display.flip()

        # Clock
        clock.tick(30)
    rectNew = pg.Rect(215, 235, 375, 14)
    rectNew2 = pg.Rect(215, 236, 2, 12)
    rectNew3 = pg.Rect(570, 470, 200, 100)
    font = pg.font.Font('fonts/game_font.ttf', 96)
    text = font.render(f'CONFIG:', True, black)
    textRect = text.get_rect()
    textRect.center = (400, 75)
    font2 = pg.font.Font('fonts/really_free.ttf', 28)
    text2 = font2.render(f'How long you have; to shoot the bot:(in ticks, 30 ticks per second)', True, black)
    textRect2 = text2.get_rect()
    textRect2.center = (400, 220)
    font5 = pg.font.Font('fonts/really_free.ttf', 43)
    text5 = font5.render(f'Start Playing!', True, black)
    textRect5 = text5.get_rect()
    textRect5.center = rectNew3.center
    cursor_text = '40'
    while state == 2:
        # Quit game window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    cursor_text = cursor_text[:-1]
                    print(cursor_text)
                else:
                    cursor_text += event.unicode
                    print(cursor_text)
        # Input
        pg.event.pump()
        mx, my = pg.mouse.get_pos()
        l,m,r = pg.mouse.get_pressed()

        #startup
        screen.fill(white)
        screen.blit(bg,(0,0))
        c.execute("SELECT * FROM scores")
        result = c.fetchall()
        if not result:
            result = [(0,0), (0,0)]
        font3 = pg.font.Font('fonts/really_free.ttf', 48)
        text3 = font3.render(f'Highest Score: {str(result[0][0])}', True, black)
        textRect3 = text3.get_rect()
        textRect3.center = (150, 550)
        font4 = pg.font.Font('fonts/really_free.ttf', 15)
        text4 = font4.render(cursor_text, True, black)

        # Update
        if l == 1 and rectNew3.collidepoint(mx,my):
            p.shoot_time = int(cursor_text)
            print(cursor_text)
            make = False
            state = 1
        # Events

        # Drawings
        screen.blit(text,textRect)
        screen.blit(text2, textRect2)
        screen.blit(text3, textRect3)
        pg.draw.rect(screen, white, rectNew)
        pg.draw.rect(screen, red, rectNew3)
        screen.blit(text5, textRect5)
        screen.blit(text4, rectNew)
        pg.display.flip()

        # Clock
        clock.tick(30)
    bg2 = pg.image.load("images/lost.png")
    while state == 4:
        # Quit game window if the user clicks the X button
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        # Get mouse position and button state
        mx, my = pg.mouse.get_pos()
        l, m, r = pg.mouse.get_pressed()

        # Update the database with the player's score
        c.execute("SELECT * FROM scores")
        result = c.fetchall()
        if not result:
            c.execute(f"INSERT INTO scores VALUES ({p.score})")
            conn.commit()
        elif p.score > int(result[0][0]):
            c.execute(f"DELETE FROM scores")
            conn.commit()
            c.execute(f"INSERT INTO scores VALUES ({p.score})")
            conn.commit()

        # Display the player's score and highest score
        score_text_font = pg.font.Font("fonts/really_free.ttf", 90)
        score_text_text = score_text_font.render(str(p.score), True, black)
        score_text_rect = pg.Rect(410, 234, 50, 50)

        c.execute("SELECT * FROM scores")
        highest_score = c.fetchall()
        highest_score_text_font = pg.font.Font("fonts/really_free.ttf", 90)
        highest_score_text_text = highest_score_text_font.render(str(highest_score[0][0]), True, black)
        highest_score_text_rect = pg.Rect(500, 290, 50, 50)

        # Check if the user clicked the "continue" button
        continue_rect = pg.Rect(400, 400, 400, 200)
        if l == 1 and continue_rect.collidepoint(mx, my):
            state = 0

        # Update the screen
        screen.fill(red)
        screen.blit(bg2, (0, 0))
        screen.blit(score_text_text, score_text_rect)
        screen.blit(highest_score_text_text, highest_score_text_rect)
        pg.display.flip()

        # Cap the frame rate at 60 FPS
        clock.tick(60)


def menu():
    global state
    font = pg.font.Font('fonts/really_free.ttf', 64)
    text = font.render('SINGLEPLAYER', True, black)
    textRect = text.get_rect()
    textRect.center = (400, 300)
    font2 = pg.font.Font('fonts/game_font.ttf', 96)
    text2 = font2.render('ReactFast', True, black)
    textRect2 = text2.get_rect()
    textRect2.center = (400, 190)
    newRect = pg.Rect(200,250,400,100)
    bg = pg.image.load("images/sand.png")
    bg = pg.transform.scale(bg, (800,600))
    help = pg.image.load("images/help.png")
    help = pg.transform.scale(help, (50, 50))
    helpRect = pg.Rect(735,535,50,50)
    while state == 0:
        # Quit game window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
        pg.event.pump()
        mx, my = pg.mouse.get_pos()
        l,m,r = pg.mouse.get_pressed()

        if l == 1 and newRect.collidepoint(mx,my):
            state = 2
        if l == 1 and helpRect.collidepoint(mx, my):
            state = 3

        screen.fill(white)
        screen.blit(bg, (0,0))
        pg.draw.rect(screen, red, newRect)
        screen.blit(text, textRect)
        screen.blit(text2, textRect2)
        screen.blit(help, helpRect)
        pg.display.flip()

        clock.tick(60)

def help():
    global state
    instructions = pg.image.load('images/instructions.png')
    back = pg.image.load('images/back.png')
    back = pg.transform.scale(back, (75,75))
    backRect = pg.Rect(15,23,75,75)

    while state == 3:
        # Quit game window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        pg.event.pump()
        mx, my = pg.mouse.get_pos()
        l,m,r = pg.mouse.get_pressed()

        if l == 1 and backRect.collidepoint(mx,my):
            state = 0

        screen.fill(white)
        screen.blit(instructions, (0,0))
        screen.blit(back, backRect)
        pg.display.flip()

        clock.tick(60)

while True:
    if state == 0:
        menu()
    elif state == 1:
        game()
    elif state == 2:
        game()
    elif state == 3:
        help()
