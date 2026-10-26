import pygame 
from pygame.locals import * # O primeiro importa o pygame, o segundo as dependencias, e o terceiro a função de sair do jogo
from sys import exit

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
    pygame.draw.rect(tela, (179, 128, 0), (0, 400, 800, 300)) # Está desenhando o chão retangulo (rect) laranja, com o primeiro parametro que é a tela, o segundo é a cor, e o terceiro é a posição
    pygame.draw.rect(tela, (255, 0, 0), (300, y, 2,20))
    pygame.draw.rect(tela, (255, 0, 0), (200, y + 25, 2,20))
    y += 3  # Faz o disparo do ceu começar a cair
    if y >= 400: # Quando encosta no chao, ele volta para cima
        y = 0



    pygame.display.update() # Usado para atualizar novas coisas
    clock.tick(20) # Quantidade de FPS