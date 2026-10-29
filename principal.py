import pygame 
from pygame.locals import * # O primeiro importa o pygame, o segundo as dependencias, e o terceiro a função de sair do jogo
from sys import exit
from random import randint

pygame.init() # Dependencia obrigatoria

largura = 640
altura = 480
x = 0
y = 0
y_disparo = randint(30, 440) # Posição do disparo no eixo y
x_disparo = randint(50, 600) # Posição do disparo no eixo x

fonte = pygame.font.SysFont("arial", 40, True, True) # Fonte do texto (arial, tamanho 40, negrito, italico)
vida = 3 # Total de vida

tela = pygame.display.set_mode((largura, altura)) # Tamanho da tela

clock = pygame.time.Clock() # Confirgurando os fps

while True:  # O loop que deixa o jogo rodando para sempre
    tela.fill((0,0,0))
    mensagem = f"Vida: {vida}"
    texto_formatado = fonte.render(mensagem, True, (255, 0 , 0))
    for event in pygame.event.get():
        if event.type == QUIT: # Se clicar em sair você sai
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONUP: # Quando clica na tela, o y volta um pouco pra cima
            if event.button == 1:
                y = y + 20

        
    chao = pygame.draw.rect(tela, (179, 128, 0), (0, 400, 800, 300)) # Está desenhando o chão retangulo (rect) laranja, com o primeiro parametro que é a tela, o segundo é a cor, e o terceiro é a posição

    pygame.draw.rect(tela, (179, 128, 0), (0, 380, 50, 50)) # Blocos dos lados 
    pygame.draw.rect(tela, (179, 128, 0), (590, 380, 50, 50))  

    casa = pygame.draw.rect(tela, (0, 255, 0), (300, 380, 20, 20)) # A casa
    
    disparo1 = pygame.draw.rect(tela, (255, 0, 0), (x_disparo - 60, y, 2, 20))  # Os dois tiros 
    disparo2 = pygame.draw.rect(tela, (255, 0, 0), (x_disparo, y + 25, 2, 20))




    y += 3.5  # Faz o disparo do ceu começar a cair
    if y >= 359: # Quando encosta no chao, ele volta para cima
        y = 0

    if disparo1.colliderect(chao) or disparo2.colliderect(chao): # Se o disparo encostar na casa, ele printa "Colidiu"
        x_disparo = randint(50, 600)
        y_disparo = randint(30, 440)
        vida -= 1
        print("Colidiu")
    if vida == -1:
        pygame.quit()
        exit()

    tela.blit(texto_formatado, (450, 40))

    pygame.display.update() # Usado para atualizar novas coisas
    clock.tick(20) # Quantidade de FPS
