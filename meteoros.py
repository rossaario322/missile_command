#teste
import pygame
import random
import math

posicoes_fixas = [ # A posição das casas
    (100, 370),
    (190, 370),
    (280, 370),
    (500, 370),
    (590, 370),
    (680, 370)
]

class Missil:
    def __init__(self, origemX, origemY, destinoX, destinoY):
        self.origemX = origemX
        self.origemY = origemY
        self.destinoX = destinoX
        self.destinoY = destinoY
