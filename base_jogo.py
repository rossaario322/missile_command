import pygame 
from pygame.locals import * # O primeiro importa o pygame, o segundo as dependencias, e o terceiro a função de sair do jogo
from sys import exit
from random import randint

pygame.init() # Dependencia obrigatoria

largura = 820
altura = 480


tela = pygame.display.set_mode((largura, altura)) # Tamanho da tela

clock = pygame.time.Clock() # Confirgurando os fps

class Casa(pygame.sprite.Sprite): # Criando uma classe para a casa, que é um sprite, que é um objeto que pode ser desenhado na tela
    def __init__(self, posicao, imagem):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        self.sprites.append(pygame.image.load('img/cidade.png'))
        self.sprites.append(pygame.image.load('img/cidade_quebrada.png'))
        self.image = self.sprites[0]
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = posicao
        self.viva = True

    def destruir(self): # Quando a casa é destruida, ela muda a imagem para a quebrada e muda o estado para falsa
        self.image = self.sprites[1]
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.viva = False


posicoes_fixas = [
    (100, 370),
    (190, 370),
    (280, 370),
    (500, 370),
    (590, 370),
    (680, 370)
]

todas_as_casas = pygame.sprite.Group() # Criando um grupo de sprites


for pos in posicoes_fixas: #Roda todas as casas e cria uma nova casa em cada posição, adicionando ao grupo de sprites
    nova_casa = Casa(pos, "img/cidade.png")
    todas_as_casas.add(nova_casa)



while True:  # O loop que deixa o jogo rodando para sempre
    tela.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == QUIT: # Se clicar em sair você sai
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONUP: # Quando clica em uma casa, ela é destruida
            if event.button == 1:
                for Casa in todas_as_casas:
                    if Casa.rect.collidepoint(event.pos):  # Capta onde você clicou e verifica se é uma casa, se é, ela é destruida atualizando para a imagem quebrada
                        Casa.destruir()
                        print("Casa destruida")
                        
                
    todas_as_casas.draw(tela) # Desenhando a casa na tela

    chao = pygame.draw.rect(tela, (179, 128, 0), (-40, 400, 860, 300)) # Está desenhando o chão retangulo (rect) laranja, com o primeiro parametro que é a tela, o segundo é a cor, e o terceiro é a posição

    pygame.draw.rect(tela, (179, 128, 0), (-10, 365, 50, 50)) # Blocos dos lados 
    pygame.draw.rect(tela, (179, 128, 0), (780, 365, 50, 50))  # Blocos dos lados 

    torre_do_meio1 = pygame.draw.rect(tela, (179, 128, 0), (350, 390, 100, 20)) 
    torre_do_meio2 = pygame.draw.rect(tela, (179, 128, 0), (365, 380, 70, 20)) 
    torre_do_meio3 = pygame.draw.rect(tela, (179, 128, 0), (380, 370, 40, 20)) 



   
    
    pygame.display.update() # Usado para atualizar novas coisas
    clock.tick(20) # Quantidade de FPS
