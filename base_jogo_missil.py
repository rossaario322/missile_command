
import pygame # Pygame, atalhos do pygame, função de sair e math (raiz quadrada)
from pygame.locals import * 
from sys import exit
import math
import random


pygame.init() # Dependencia obrigatoria

largura = 820 # Define variaveis que são usadas depois
altura = 480
municao = 10


tela = pygame.display.set_mode((largura, altura)) # Tamanho da tela

clock = pygame.time.Clock() # Confirgurando os fps

class Casa(pygame.sprite.Sprite): # Criando uma classe para a casa, que é um sprite, que é um objeto que pode ser desenhado na tela
    def __init__(self, posicao, imagem): #
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        self.sprites.append(pygame.image.load('img/cidade.png')) # Essa e a de baixo são as duas fotos da cidade
        self.sprites.append(pygame.image.load('img/cidade_quebrada.png'))
        self.image = self.sprites[0] # Começa com ela viva
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = posicao # Serve para posicionar os sprites pegando-os pela esquerda superior e coloca-los na variavel "posicao"
        self.viva = True # Define a caracteristica "True" para um sprite com a casa viva

    def destruir(self): # Quando a casa é destruida, ela muda a imagem para a quebrada e muda o estado para falsa
        self.image = self.sprites[1] # Troca para o sprite da casa destruida
        self.image = pygame.transform.scale(self.image, (30, 30)) # Define o tamanho igual
        self.viva = False # Define a caracteristica "False" para um sprite com a casa destruida

class Explosion(pygame.sprite.Sprite): # Classe feita para realizar a explosão no jogo
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6): # Faz um loop para pegar todas as imagens da explosão e coloca-las na mesma escala
			img = pygame.image.load(f"img/exp{num}.png")
			img = pygame.transform.scale(img, (100, 100))
			self.images.append(img)
		self.index = 0 # Número do quadro atual da animação (começa no primeiro)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y] # Coloca o centro da explosão na variavel x e y
		self.counter = 0
		self.raio = 40 

	def update(self): # Uma função criada para trocar entre os 5 sprites da explosao"
		explosion_speed = 4
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]
		
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed: # Animacao terminou: remove a explosao
			self.kill()

	def atinge(self, x, y): # Uma função feita para se ter a colisão da explosão
		dx = self.rect.centerx - x
		dy = self.rect.centery - y
		distancia = math.sqrt(dx**2 + dy**2)
		return distancia <= self.raio

class Projetil(pygame.sprite.Sprite): # Tiro que sai do canhão e avisa quando chega no destino
    def __init__(self, destino): # Roda quando atira, recebe o ponto do clique 
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (4, 4), 4) # aparencia: bola branca com fundo transparente

        
        self.x = 400 # Posicao atual (comeca no topo da torre do meio onde estará o canhão)
        self.y = 370
        self.destino = destino
        self.velocidade = 8
        self.chegou = False

        self.rect = self.image.get_rect()
        self.rect.center = [self.x, self.y]

        
        dx = destino[0] - self.x # Quanto falta andar na horizontal
        dy = destino[1] - self.y # Quanto falta andar na vertical
        distancia = math.sqrt(dx**2 + dy**2) # Quanto falta andar em linha reta 
        if distancia == 0: # Se clicou em cima do canhão, a distância é 0 e não dá pra dividir: já marca como chegou
            self.chegou = True # Afirma que já chegou
            self.vx = 0 # Não anda mais 
            self.vy = 0
        else:
            self.vx = dx / distancia * self.velocidade
            self.vy = dy / distancia * self.velocidade

    def update(self): # Função feita para o jogo ficar atualizando e movendo o projetil ate o local desejado 

        self.x += self.vx # Anda um passo
        self.y += self.vy
        self.rect.center = [self.x, self.y]

        
        dx = self.destino[0] - self.x # Quanto falta ate o destino
        dy = self.destino[1] - self.y
        falta = math.sqrt(dx**2 + dy**2)
        if falta <= self.velocidade:
            self.chegou = True

class Missil(pygame.sprite.Sprite): #transformando o missil em sprite
    def __init__(self, origemX, origemY, destino, velocidade):
        super().__init__() #garante que a classe mãe seja "vista"
        
        self.image = pygame.Surface((10, 10))
        self.image.fill("red")
        self.rect = self.image.get_rect()
        
        self.origemX = origemX
        self.origemY = origemY
        self.destinoX = destino[0]
        self.destinoY = destino[1]
        self.velocidade = velocidade
        
        self.rect.center = (self.origemX, self.origemY)
        
    def update(self): # Função feita para o jogo ficar atualizando e movendo o projetil ate o local desejado 
        dx = self.destinoX - self.origemX
        dy = self.destinoY - self.origemY
        
        distancia = math.hypot(dx,dy)
    
        if distancia > 0:
            if distancia <= self.velocidade:
                self.origemX = self.destinoX
                self.origemY = self.destinoY
                self.kill() 
            else:
                direcaoX = dx/distancia
                direcaoY = dy/distancia    
                self.origemX += direcaoX*self.velocidade
                self.origemY += direcaoY*self.velocidade
            
        self.rect.center = (int(self.origemX), int(self.origemY))

def chao():
    pygame.draw.rect(tela, (179, 128, 0), (-40, 400, 860, 300)) # Está desenhando o chão retangulo (rect) laranja, com o primeiro parametro que é a tela, o segundo é a cor, e o terceiro é a posição
    pygame.draw.rect(tela, (179, 128, 0), (-10, 365, 50, 50)) # Blocos dos lados 
    pygame.draw.rect(tela, (179, 128, 0), (780, 365, 50, 50))  # Blocos dos lados 
    torre_do_meio1 = pygame.draw.rect(tela, (179, 128, 0), (350, 390, 100, 20)) # Os 3 para a torre do meio
    torre_do_meio2 = pygame.draw.rect(tela, (179, 128, 0), (365, 380, 70, 20)) 
    torre_do_meio3 = pygame.draw.rect(tela, (179, 128, 0), (380, 370, 40, 20)) 

posicoes_fixas = [ # A posição das casas
    (100, 370),
    (190, 370),
    (280, 370),
    (500, 370),
    (590, 370),
    (680, 370)
]

grupo_casas = pygame.sprite.Group() # Grupo das casas 
grupo_explosoes = pygame.sprite.Group() # Grupo das explosões
grupo_projeteis = pygame.sprite.Group() # Grupos dos projeteis
grupo_misseis = pygame.sprite.Group() #grupo dos misseis 

fonte = pygame.font.SysFont("arial", 24, True) # Fonte pra escrever (arial, tamanho 24, negrito)
hora_sem_municao = 0 # Variavel que guarda quando não tem munição



for pos in posicoes_fixas: #Roda todas as casas e cria uma nova casa em cada posição, adicionando ao grupo de sprites
    nova_casa = Casa(pos, "img/cidade.png")
    grupo_casas.add(nova_casa)

grupo_misseis.add(Missil(random.randint(0,820), 0, (random.choice(posicoes_fixas)), 3)) #testando a geração e colisão dos misseis
grupo_misseis.add(Missil(random.randint(0,820), 0, (random.choice(posicoes_fixas)), 3))

while True:  # O loop que deixa o jogo rodando para sempre
    tela.fill((0,0,0)) # Tela preta
    for event in pygame.event.get():
        if event.type == QUIT: # Se clicar em sair você sai
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONUP: 
            if event.button == 1:
                for casa in grupo_casas:
                    if casa.rect.collidepoint(event.pos):  # Capta onde você clicou e verifica se é uma casa, se é, ela é destruida atualizando para a imagem quebrada
                        casa.destruir()
                        print("Casa destruida")
                if municao > 0: # Cada tiro gasta 1 de munição
                    grupo_projeteis.add(Projetil(event.pos))
                    municao -= 1
                    if municao == 0: # Quando a última bala é gasta, anota a hora. É aqui que o cronômetro começa.
                        hora_sem_municao = pygame.time.get_ticks()
                
     

    chao() # Puxa a função que faz o ambiente do mapa
    grupo_explosoes.update() # Atualiza as duas classes
    grupo_projeteis.update()
    grupo_misseis.update()


    for p in grupo_projeteis: # Transforma o tiro em explosão, apagando o disparo e posicionando a explosão
        if p.chegou:
            grupo_explosoes.add(Explosion(p.destino[0], p.destino[1]))
            p.kill()

    for explosao in grupo_explosoes:
        for missil in grupo_misseis:
            if explosao.atinge(missil.rect.centerx, missil.rect.centery):
                missil.kill()
    
    colisoes = pygame.sprite.groupcollide(grupo_misseis, grupo_casas, True, False)
    for missil_atingiu, casas_atingidas in colisoes.items():
        for casa in casas_atingidas:
            if casa.viva: 
                casa.destruir()

    if municao == 0 and pygame.time.get_ticks() - hora_sem_municao >= 3000: # Aqui ele pega o tempo que tem de jogo, e diminui pelo tempo que tinha de jogo e que foi marcado, fazendo verificar se ja passaram 3000 milisengundos para voltar a munição
        municao = 10


    texto = fonte.render(str(municao), True, (0, 0, 0)) # Desenham o numero de munição embaixo da torre
    texto_rect = texto.get_rect(center=(400, 425))
    tela.blit(texto, texto_rect)
    
    chao() 
    grupo_casas.draw(tela)
    grupo_misseis.draw(tela) # Desenha os mísseis caindo
    grupo_projeteis.draw(tela)
    grupo_explosoes.draw(tela)

    if municao == 0: # Se a munição for zero, deixa na tela "OUT" ate a munição voltar a ser 10
        aviso = fonte.render("OUT", True, (255, 0, 0))
        aviso_rect = aviso.get_rect(center=(400, 450))
        tela.blit(aviso, aviso_rect)


   
    
    pygame.display.update() # Usado para atualizar novas coisas
    clock.tick(40) # Quantidade de FPS
