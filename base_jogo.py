
import pygame # Pygame, atalhos do pygame, função de sair, math (raiz quadrada), e requests (para pegar a API do clima)
from pygame.locals import * 
from sys import exit
import math
import requests
import random
import json

pygame.init() # Dependencia obrigatoria

# ==================== VARIÁVEIS ====================

largura = 820 # Define variaveis que são usadas depois
altura = 480
municao = 10
hora_sem_municao = 0 # Variavel que guarda quando não tem munição
fonte = pygame.font.SysFont("arial", 24, True) # Fonte pra escrever (arial, tamanho 24, negrito)
estado = "menu" # Define o estado do jogo, que começa no menu

tela = pygame.display.set_mode((largura, altura)) # Tamanho da tela
clock = pygame.time.Clock() # Confirgurando os fps

# ==================== CLASSES ====================

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

        self.quadros_explosao = [] # Salva as imagens da explosão em uma lista, para depois fazer a animação
        for num in range(1, 7):
            self.quadros_explosao.append(pygame.image.load(f"img/cidade_exp{num}.png"))
        self.explodindo = False
        self.index = 0
        self.counter = 0

    def destruir(self):
        if self.viva:               
            self.viva = False
            self.explodindo = True
            self.index = 0
            self.counter = 0

    def update(self): # Para a ficar trocando a imagem da casa para a de cidade quebrada, e para a animação da explosão
        if self.explodindo:
            self.counter += 1
            if self.counter >= 5:                  
                self.counter = 0
                base = self.rect.midbottom          
                self.image = self.quadros_explosao[self.index]
                self.rect = self.image.get_rect()
                self.rect.midbottom = base          
                self.index += 1
                if self.index >= len(self.quadros_explosao):
                    self.explodindo = False         

class Explosao(pygame.sprite.Sprite): # Classe feita para realizar a explosão no jogo
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
		velocidade_explosao = 4
		self.counter += 1

		if self.counter >= velocidade_explosao and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]
		
		if self.index >= len(self.images) - 1 and self.counter >= velocidade_explosao: # Animacao terminou: remove a explosao
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

class Botao(): # Classe feita para criar os botoes do menu
    def __init__(self,x,y,imagem):
        self.image = imagem
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
    def desenho(self): # Desenha o botão na tela
        tela.blit(self.image, (self.rect.x, self.rect.y))

    def clicado(self, pos): # Verifica se o botão foi clicado
        return self.rect.collidepoint(pos)

class Missil(pygame.sprite.Sprite): #transformando o missil em sprite
    def __init__(self, origemX, origemY, destino, velocidade):
        super().__init__() #garante que a classe mãe seja "vista"
        
        self.image = pygame.Surface((10, 10))
        self.image.fill("red")
        self.rect = self.image.get_rect()
        
        self.origemX = origemX
        self.origemY = origemY
        self.spawnX = origemX   # guarda de onde ele saiu, pro rastro
        self.spawnY = origemY
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

class Boss(pygame.sprite.Sprite): # Base dos dois bosses
    def __init__(self, x, y, cor):
        super().__init__()
        self.image = pygame.Surface((60, 30)) # Retângulo provisório, depois troca por sprite
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.vida = 3
        self.invencivel_ate = 0 # Até que momento ele não toma dano

    def levar_dano(self):
        agora = pygame.time.get_ticks()
        if agora < self.invencivel_ate: # Ainda invencível: ignora
            return
        self.vida -= 1
        self.invencivel_ate = agora + 1000 # 1 segundo sem tomar dano
        if self.vida <= 0:
            self.kill()

    def atirar(self): # Por padrão, boss não atira
        return False





botao_jogar = Botao(300, 100, pygame.image.load("img/botao_jogar.png")) # Botão de start
botao_lederbord = Botao(260, 200, pygame.image.load("img/botao_leaderboard.png")) # Botão de leaderboard
botao_sair = Botao(300, 300, pygame.image.load("img/botao_sair.png")) # Botão de sair

img_nuvem = pygame.image.load("img/nuvem.png").convert_alpha() # As imagens da nuvem e das estrelas do mapa
img_estrela = pygame.image.load("img/estrela.png").convert_alpha()
img_estrela_pequena = pygame.image.load("img/estrela_pequena.png").convert_alpha()




estrelas_grandes = [(150, 60), (480, 40), (620, 150)] # Posições das estrelas grandes e pequenas, para desenhar no mapa
estrelas_pequenas = [(60, 120), (260, 30), (330, 140), (420, 90), (560, 200), (760, 60), (210, 210)]
# ==================== ELEMENTOS DO MAPA ====================
def chao():
    pygame.draw.rect(tela, (179, 128, 0), (-40, 400, 860, 300)) # Está desenhando o chão retangulo (rect) laranja, com o primeiro parametro que é a tela, o segundo é a cor, e o terceiro é a posição
    pygame.draw.rect(tela, (179, 128, 0), (-10, 365, 50, 50)) # Blocos dos lados 
    pygame.draw.rect(tela, (179, 128, 0), (780, 365, 50, 50))  # Blocos dos lados 
    torre_do_meio1 = pygame.draw.rect(tela, (179, 128, 0), (350, 390, 100, 20)) # Os 3 para a torre do meio
    torre_do_meio2 = pygame.draw.rect(tela, (179, 128, 0), (365, 380, 70, 20)) 
    torre_do_meio3 = pygame.draw.rect(tela, (179, 128, 0), (380, 370, 40, 20)) 


def buscar_clima(): # Consulta a API do clima e devolve se é dia e a temperatura de Curitiba
    url = "https://api.open-meteo.com/v1/forecast?latitude=-25.43&longitude=-49.27&current=temperature_2m,is_day"
    try: # Aqui uma tentativa de pegar os dados da API, caso não consiga, cai no except e devolve dia e sem temperatura
        resposta = requests.get(url, timeout=3)
        dados = resposta.json()
        dia = dados["current"]["is_day"]
        temperatura = dados["current"]["temperature_2m"]
        return dia, temperatura
    except requests.exceptions.RequestException: # Sem internet ou API fora do ar: usa dia e sem temperatura
        return 1, None

def desenhar_ceu(): # Desenha o fundo de dia (sol) ou de noite (lua)
    if dia == 1:
        tela.fill((90, 160, 230))                                # Céu azul
        pygame.draw.circle(tela, (255, 220, 60), (700, 80), 35)  # Sol
        tela.blit(img_nuvem, (80, 90)) 
        tela.blit(img_nuvem, (330, 40))#Nuvens
        
    else:
        tela.fill((0, 0, 0))                                     # Céu preto
        pygame.draw.circle(tela, (220, 220, 220), (700, 80), 30) # Lua

        for pos in estrelas_grandes: # Estrelas 
            tela.blit(img_estrela, pos)

        for pos in estrelas_pequenas: # Estrelas pequenas
            tela.blit(img_estrela_pequena, pos)

def carregar_ranking(): # Lê o ranking salvo no arquivo
    try:
        arquivo = open("ranking.json", "r")
        ranking = json.load(arquivo)
        arquivo.close()
        return ranking
    except FileNotFoundError: # Se o arquivo ainda não existe, começa com a lista vazia
        return []

def pegar_pontos(jogador): # Diz pro sort que é pra comparar pelos pontos
    return jogador["pontos"]

def salvar_pontuacao(nome, pontos): # Coloca a pontuação nova no ranking e salva no arquivo
    ranking = carregar_ranking()
    ranking.append({"nome": nome, "pontos": pontos})
    ranking.sort(key=pegar_pontos, reverse=True) # Do maior pro menor

    while len(ranking) > 10: # Deixa só os 10 melhores
        ranking.pop()        # Tira o último da lista

    arquivo = open("ranking.json", "w")
    json.dump(ranking, arquivo)
    arquivo.close()
    return ranking



dia, temperatura = buscar_clima() # Chama a API uma vez só, quando o jogo abre
# ==================== POSIÇÕES E O RANKING ====================

posicoes_fixas = [ # A posição das casas
    (100, 370),
    (190, 370),
    (280, 370),
    (500, 370),
    (590, 370),
    (680, 370)
]

ranking = carregar_ranking()

# ==================== GRUPOS DE SPRITES ====================
grupo_casas = pygame.sprite.Group() # Grupo das casas 
grupo_explosoes = pygame.sprite.Group() # Grupo das explosões
grupo_projeteis = pygame.sprite.Group() # Grupos dos projeteis
grupo_misseis = pygame.sprite.Group()
# ==================== LOOP PRINCIPAL ====================


for pos in posicoes_fixas: # Roda todas as casas e cria uma nova casa em cada posição, adicionando ao grupo de sprites
    nova_casa = Casa(pos, "img/cidade.png")
    grupo_casas.add(nova_casa)


ondaAtual = 1
misseisRestantes = 5
misseisVelocidade = 2
SpawnTime = 1000
ultimoSpawn = pygame.time.get_ticks()
esperandoProximaOnda = False
tempoEspera = 0



while True:  # O loop que deixa o jogo rodando para sempre
    tela.fill((0,0,0)) # Tela preta
    for event in pygame.event.get():
        if event.type == QUIT: # Se clicar em sair você sai
            pygame.quit()
            exit()

        if estado == "menu": # No menu, o clique só serve pro botão
            if event.type == MOUSEBUTTONUP and event.button == 1:
                if botao_jogar.clicado(event.pos): # Se clicar no botão de jogar, muda o estado para jogando
                    estado = "jogando"
                if botao_lederbord.clicado(event.pos): # Se clicar no botão de leaderboard, muda o estado para leaderboard
                    estado = "leaderboard"
                if botao_sair.clicado(event.pos): # Se clicar no botão de sair, sai do jogo
                    pygame.quit()
                    exit()

        elif estado == "jogando": # Jogando, o clique atira
            if event.type == MOUSEBUTTONUP and event.button == 1:
                

                if municao > 0: # Cada tiro gasta 1 de munição
                    grupo_projeteis.add(Projetil(event.pos))
                    municao -= 1
                    if municao == 0: # Quando a última bala é gasta, anota a hora. É aqui que o cronômetro começa.
                        hora_sem_municao = pygame.time.get_ticks()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                estado = "pausado"
        elif estado == "leaderboard":          # aqui
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                estado = "menu"
        elif estado == "pausado":
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                estado = "jogando"


    if estado == "menu": # Se está no menu, desenha os botoes na tela
        desenhar_ceu() # Puxa a função que desenha o céu de dia ou de noite
        botao_jogar.desenho()
        botao_lederbord.desenho()
        botao_sair.desenho()
        

    elif estado == "jogando": # Todo o resto do código é o que acontece quando está jogando
        
        desenhar_ceu() # Puxa a função que desenha o céu de dia ou de noite
        chao() # Puxa a função que faz o ambiente do mapa
        grupo_explosoes.update() # Atualiza as duas classes
        grupo_projeteis.update()
        grupo_casas.update()
        grupo_misseis.update()

        for missil in grupo_misseis:
            pygame.draw.line(tela, "white", (missil.spawnX, missil.spawnY), missil.rect.center, 2)



         # Desenha tudo na tela
        grupo_casas.draw(tela)
        grupo_projeteis.draw(tela)
        grupo_misseis.draw(tela)
        grupo_explosoes.draw(tela)

        for p in grupo_projeteis: # Transforma o tiro em explosão, apagando o disparo e posicionando a explosão
            if p.chegou:
                grupo_explosoes.add(Explosao(p.destino[0], p.destino[1]))
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

        textoOndaAtual = fonte.render(f"Onda Atual: {ondaAtual}", True, (255, 255, 255))
        tela.blit(textoOndaAtual, (20,50)) #posiciona o texto no canto superior esquerdo (x = 10, y = 10)
            
        if esperandoProximaOnda:
                avisoEntreOndas = fonte.render(f"Onda {ondaAtual} concluída! Prepare-se!", True, (255, 255, 0))
                avisoEntreOndasRect = avisoEntreOndas.get_rect(center = (largura // 2, altura //2 )) #// significa dividir por 1 valor inteiro, para não ter serrilhado nos pixels
                tela.blit(avisoEntreOndas, avisoEntreOndasRect)
            
        tempoAtual = pygame.time.get_ticks() #variavel que salva o tempo atual
        if misseisRestantes > 0:
            if tempoAtual - ultimoSpawn >= SpawnTime: # verifica se ja passou o tempo entre misseis
                    
                    origemX = random.randint(0, largura)
                    destino = random.choice(posicoes_fixas) 
                    
                    novoMissil = Missil(origemX, 0, destino, misseisVelocidade)
                    grupo_misseis.add(novoMissil)
                    
                    misseisRestantes -= 1
                    ultimoSpawn = tempoAtual
            
        elif len(grupo_misseis) == 0  and misseisRestantes == 0 and not esperandoProximaOnda:
                
                esperandoProximaOnda = True
                tempoEspera = tempoAtual
            
        elif esperandoProximaOnda and (tempoAtual -  tempoEspera) >= 3000:
                
                ondaAtual += 1 #soma o numero da wave
                misseisRestantes = 5 + ondaAtual #aumenta em 1 o numero de inimigos a cada wave
                
                misseisVelocidade = 2 + (ondaAtual * 0.2) #aumenta a velocidade dos misseis a cada onda
                
                SpawnTime = max(500, 1500 - (ondaAtual * 50)) #diminui o tempo entre o nascimento de um missil e outro
                
                esperandoProximaOnda = False



        texto = fonte.render(str(municao), True, (0, 0, 0)) # Desenham o numero de munição embaixo da torre
        texto_rect = texto.get_rect(center=(400, 425))
        tela.blit(texto, texto_rect)

        if municao == 0: # Se a munição for zero, deixa na tela "OUT" ate a munição voltar a ser 10
            aviso = fonte.render("OUT", True, (255, 0, 0))
            aviso_rect = aviso.get_rect(center=(400, 450))
            tela.blit(aviso, aviso_rect)

        if temperatura is not None:
            clima = fonte.render(f"Curitiba: {temperatura}°C", True, (255, 255, 255))
            tela.blit(clima, (20, 20))


    elif estado == "leaderboard": # Se o estado for leaderboard, desenha o ranking na tela
        desenhar_ceu()
        titulo = fonte.render("LEADERBOARD", True, (255, 0, 0))
        tela.blit(titulo, titulo.get_rect(center=(410, 80)))

        y = 150
        posicao = 1
        for jogador in ranking:   # cada jogador é um dicionário, ex.: {"nome": "Victor", "pontos": 1200}
            linha = fonte.render(f"{posicao}. {jogador['nome']}   {jogador['pontos']}", True, (255, 255, 255))
            tela.blit(linha, linha.get_rect(center=(410, y)))
            y += 40
            posicao += 1

        dica = fonte.render("ESC para voltar", True, (150, 150, 150))
        tela.blit(dica, dica.get_rect(center=(410, 420)))

    elif estado == "pausado": # Se o jogo estiver pausado, desenha o texto de pausa e fica em uma tela que so é possivel sair apertando ESC
        desenhar_ceu()
        pausa_texto = fonte.render("PAUSADO", True, (255, 255, 0))
        tela.blit(pausa_texto, pausa_texto.get_rect(center=(410, 240)))
        dica = fonte.render("ESC para voltar", True, (150, 150, 150))
        tela.blit(dica, dica.get_rect(center=(410, 280)))
        
    pygame.display.update() # Usado para atualizar novas coisas
    clock.tick(40) # Quantidade de FPS
