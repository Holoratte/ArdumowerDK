import pygame
from Tkinter import *
file = 'Track 01.mp3'
root = Tk()
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(file)
pygame.mixer.music.play()
root.mainloop()