import pygame 
from pygame.locals import * # O primeiro importa o pygame, o segundo as dependencias, e o terceiro a função de sair do jogo
from sys import exit
from random import randint

pygame.init() # Dependencia obrigatoria

largura = 640
altura = 480
x = 0
y = 0

tela = pygame.display.set_mode((largura, altura)) # Tamanho da tela

clock = pygame.time.Clock() # Confirgurando os fps


while True:  # O loop que deixa o jogo rodando para sempre
    tela.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == QUIT: # Se clicar em sair você sai
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONUP: # Quando clica na tela, o y volta um pouco pra cima
            if event.button == 1:
                y = y + 20

        
    chao = pygame.draw.rect(tela, (179, 128, 0), (0, 400, 800, 300)) # Está desenhando o chão retangulo (rect) laranja, com o primeiro parametro que é a tela, o segundo é a cor, e o terceiro é a posição

    pygame.draw.rect(tela, (179, 128, 0), (-10, 365, 50, 50)) # Blocos dos lados 
    pygame.draw.rect(tela, (179, 128, 0), (600, 365, 50, 50))  # Blocos dos lados 

    torre_do_meio1 = pygame.draw.rect(tela, (179, 128, 0), (263, 390, 100, 20)) 
    torre_do_meio2 = pygame.draw.rect(tela, (179, 128, 0), (278, 380, 70, 20)) 
    torre_do_meio3 = pygame.draw.rect(tela, (179, 128, 0), (293, 370, 40, 20)) 
    
    
    pygame.display.update() # Usado para atualizar novas coisas
    clock.tick(20) # Quantidade de FPS
