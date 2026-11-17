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
fonte = pygame.font.Font("fonts/PressStart2P.ttf", 16) # Fonte pixelada (Press Start 2P), tamanho 16
fonte_pequena = pygame.font.Font("fonts/PressStart2P.ttf", 8) # Mesma fonte, menor, pra textos de apoio
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
        self.rect = self.image.get_rect()
        self.rect.midbottom = posicao # Posiciona pelo meio da base, pra cidade ficar em pé no chão
        self.viva = True # Define a caracteristica "True" para um sprite com a casa viva

        self.quadros_explosao = [] # Salva as imagens da explosão em uma lista, para depois fazer a animação
        for num in range(1, 7):
            self.quadros_explosao.append(pygame.image.load(f"img/cidade_exp{num}.png"))
        self.explodindo = False
        self.index = 0
        self.counter = 0

    def destruir(self):# Momento que ela quebra, muda a imagem da casa para a de cidade quebrada e inicia a animação da explosão
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

class Botao(): # Botão do menu, com imagem normal e imagem com o mouse em cima
    def __init__(self, x, y, imagem, imagem_hover):
        self.imagem = imagem # Guarda a imagem do botão normal
        self.imagem_hover = imagem_hover # Guarda a imagem do botão com o mouse em cima
        self.rect = self.imagem.get_rect()
        self.rect.topleft = (x, y)

    def desenho(self): # Se o mouse está em cima, desenha a versão hover
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            tela.blit(self.imagem_hover, self.rect)
        else:
            tela.blit(self.imagem, self.rect)

    def clicado(self, pos): # Recebe a posição do clique
        return self.rect.collidepoint(pos) # Recebe se o clique foi dentro do botão, devolvendo True ou False

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

class Boss(pygame.sprite.Sprite): # Base dos bosses: cai em direção a uma casa
    def __init__(self, imagem, velocidade): # Cria a classe Boss, que é um sprite, recebe a imagem e a velocidade
        super().__init__() #  Garante que a classe mãe seja "vista"
        self.image = imagem
        self.rect = self.image.get_rect()
        self.vida = 3
        self.invencivel_ate = 0
        self.velocidade = velocidade
        self.reposicionar() # Já nasce lá em cima mirando uma casa

    def reposicionar(self): # Vai pra um ponto aleatório no alto e mira uma casa
        self.x = random.randint(50, largura - 50)
        self.y = random.randint(20, 120)
        destino = random.choice(posicoes_fixas)
        dx = destino[0] - self.x
        dy = destino[1] - self.y
        distancia = math.sqrt(dx**2 + dy**2)
        self.vx = dx / distancia * self.velocidade
        self.vy = dy / distancia * self.velocidade
        self.rect.center = (self.x, self.y)

    def update(self): # Anda um passo em direção à casa
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def levar_dano(self): # Se o boss for atingido, perde 1 de vida e fica invencível por 1 segundo
        agora = pygame.time.get_ticks()
        if agora < self.invencivel_ate:
            return
        self.vida -= 1
        self.invencivel_ate = agora + 1000
        if self.vida <= 0:
            self.kill()

    def atirar(self):
        return False

class Boss1(Boss):
    def __init__(self):
        super().__init__(img_boss1, 1) # Chama a classe mãe, passando a imagem e a velocidade (vira filho da classe Boss)

    def levar_dano(self):
        vida_antes = self.vida
        super().levar_dano()
        if self.vida < vida_antes and self.vida > 0: # Tomou dano e continua vivo
            self.reposicionar() # Teleporta pra cima e mira outra casa

class Boss2(Boss):
    def __init__(self):
        super().__init__(img_boss2, 0) # Chama a classe mãe, passando a imagem e a velocidade (vira outro filho da classe Boss)
        self.rect.center = (100, 100)
        self.direcao = 3
        self.ultimo_tiro = pygame.time.get_ticks()

    def update(self): # Anda de um lado pro outro
        self.rect.x += self.direcao
        if self.rect.left <= 0 or self.rect.right >= largura:
            self.direcao *= -1 # Bateu na borda: inverte

    def atirar(self): # A cada 2 segundos, avisa que quer atirar
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_tiro >= 2000:
            self.ultimo_tiro = agora
            return True
        return False

botao_jogar = Botao(290, 150, pygame.image.load("img/botao_jogar.png"), pygame.image.load("img/botao_jogar_hover.png")) # Os botões do menu, com a posição e as imagens
botao_lederbord = Botao(290, 220, pygame.image.load("img/botao_leaderboard.png"), pygame.image.load("img/botao_leaderboard_hover.png"))
botao_sair = Botao(290, 290, pygame.image.load("img/botao_sair.png"), pygame.image.load("img/botao_sair_hover.png"))

img_nuvem = pygame.image.load("img/nuvem.png").convert_alpha() # As imagens da nuvem e das estrelas do mapa
img_estrela = pygame.image.load("img/estrela.png").convert_alpha()
img_estrela_pequena = pygame.image.load("img/estrela_pequena.png").convert_alpha()
img_boss1 = pygame.image.load("img/boss1.png").convert_alpha()
img_boss2 = pygame.image.load("img/boss2.png").convert_alpha()
img_titulo = pygame.image.load("img/titulo.png").convert_alpha()
img_sol = pygame.image.load("img/sol.png").convert_alpha()
img_lua = pygame.image.load("img/lua.png").convert_alpha()
img_municao = pygame.image.load("img/municao.png").convert_alpha()

estrelas_grandes = [(150, 60), (480, 40), (620, 150)] # Posições das estrelas grandes e pequenas, e das montanhas para desenhar no mapa
estrelas_pequenas = [(60, 120), (260, 30), (330, 140), (420, 90), (560, 200), (760, 60), (210, 210)]
montanhas = [(0, 480), (0, 300), (80, 250), (160, 310), (250, 230), (340, 300), (420, 260), (500, 320), (590, 240), (680, 300), (760, 250), (820, 290), (820, 480)]
# ==================== ELEMENTOS DO MAPA ====================

def chao(): # Desenha o chão, a torre do meio e os blocos dos lados, com cores diferentes de dia e de noite
    if dia == 1:
        cor, cor_topo = (214, 168, 96), (236, 200, 132)
    else:
        cor, cor_topo = (120, 90, 60), (150, 115, 80)

    pygame.draw.rect(tela, cor, (-40, 400, 860, 300))       # chão
    pygame.draw.rect(tela, cor_topo, (-40, 400, 860, 6))    # faixa clara
    pygame.draw.rect(tela, cor, (-10, 365, 50, 50))         # blocos dos lados
    pygame.draw.rect(tela, cor, (780, 365, 50, 50))
    pygame.draw.rect(tela, cor, (350, 390, 100, 20))        # torre do meio
    pygame.draw.rect(tela, cor, (365, 380, 70, 20))
    pygame.draw.rect(tela, cor, (380, 370, 40, 20))

def desenhar_municao(): # Desenha os mísseis em pirâmide embaixo da torre
    posicoes = []
    for linha in range(4):                      # Linha 0 = base (4 mísseis) ... linha 3 = topo (1)
        quantidade = 4 - linha
        largura_linha = quantidade * 11 - 5
        inicio_x = 400 - largura_linha // 2     # Centraliza a linha embaixo da torre
        y = 440 - linha * 16                    # Cada linha 16 pixels acima da outra
        for i in range(quantidade):
            posicoes.append((inicio_x + i * 11, y))

    for i in range(municao):                    # Desenha um míssil pra cada bala
        tela.blit(img_municao, posicoes[i])

def buscar_clima(): # Consulta a API do clima: devolve se é dia, a temperatura, se está chovendo e se conseguiu conectar
    url = "https://api.open-meteo.com/v1/forecast?latitude=-25.43&longitude=-49.27&current=temperature_2m,is_day,rain"
    try: # Tenta pegar os dados reais da API
        resposta = requests.get(url, timeout=3)
        dados = resposta.json()
        dia = dados["current"]["is_day"]
        temperatura = dados["current"]["temperature_2m"]
        chovendo = dados["current"]["rain"] > 0 # Rain é a chuva em milímetros; maior que 0 = está chovendo
        return dia, temperatura, chovendo, True # True = dados reais da API
    except (requests.exceptions.RequestException, KeyError, ValueError): # Sem internet ou resposta estranha da API: modo simulado, de dia, com calor e chuva
        return 1, 30.0, True, False              # False = dados simulados

def calcular_fator_clima(temperatura): # Quanto mais quente, mais rápidos os mísseis
    if temperatura is None: # Sem temperatura: velocidade normal
        return 1.0
    if temperatura >= 28:
        return 1.3  # Muito quente: 30% mais rápido
    if temperatura >= 22:
        return 1.15 # Quente: 15% mais rápido
    if temperatura <= 12:
        return 0.8  # Frio: 20% mais lento
    return 1.0      # Ameno: normal

def criar_chuva(): # Cria as gotas em posições aleatórias
    gotas = []
    for i in range(120):
        gotas.append([random.randint(0, largura), random.randint(0, 400)]) # Cada gota é [x, y]
    return gotas

def desenhar_chuva(): # Move e desenha as gotas (só se estiver chovendo)
    if not chovendo:
        return
    for gota in gotas:
        gota[0] -= 2 # Vai um pouco pra esquerda (chuva inclinada)
        gota[1] += 9 # Cai
        if gota[1] > 400: # Chegou no chão: volta pro topo num lugar aleatório
            gota[0] = random.randint(0, largura + 100)
            gota[1] = random.randint(-40, 0)
        pygame.draw.line(tela, (170, 200, 255), (gota[0], gota[1]), (gota[0] + 2, gota[1] - 8), 1)

def desenhar_ceu(): # Desenha o fundo de dia (sol) ou de noite (lua)
    if dia == 1:
        cores = [(40, 90, 190), (55, 115, 210), (75, 140, 225), (100, 165, 235), (130, 190, 240)] # Céu de dia, mais claro perto do chão
    else:
        cores = [(5, 5, 20), (10, 10, 35), (20, 15, 50), (30, 20, 65), (45, 30, 80)] # Céu de noite, azul escuro pra roxo

    altura_faixa = 400 // len(cores)
    for i in range(len(cores)): # Desenha cada faixa, uma embaixo da outra
        pygame.draw.rect(tela, cores[i], (0, i * altura_faixa, largura, altura_faixa))

    if dia == 1:
        pygame.draw.polygon(tela, (40, 80, 140), montanhas)      # Montanhas azuladas
        tela.blit(img_sol, img_sol.get_rect(center=(700, 80)))   # Sol
        tela.blit(img_nuvem, (80, 90))                           # Nuvens
        tela.blit(img_nuvem, (330, 40))

    else:
        pygame.draw.polygon(tela, (15, 10, 30), montanhas)       # Montanhas escuras
        tela.blit(img_lua, img_lua.get_rect(center=(700, 80)))   # Lua

        tempo = pygame.time.get_ticks()
        for i, pos in enumerate(estrelas_grandes): # i é o número da estrela (0, 1, 2...)
            if (tempo // 300 + i) % 4 != 0:        # some 1 a cada 4 "batidas"
                tela.blit(img_estrela, pos)

        for i, pos in enumerate(estrelas_pequenas):
            if (tempo // 450 + i) % 3 != 0:
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

def resetarJogo(): # Volta tudo pro começo, pra começar uma partida nova
    # Definido a alteração dessas variáveis globais
    global municao, hora_sem_municao
    global ondaAtual, misseisRestantes, misseisVelocidade, SpawnTime
    global ultimoSpawn, esperandoProximaOnda, tempoEspera
    global pontos, gameOver, digitarNome, nomeJogador

    # Controle de Waves
    municao = 10
    hora_sem_municao = 0
    ondaAtual = 1
    misseisRestantes = 5
    misseisVelocidade = 2 * fator_clima   # A velocidade dos mísseis é multiplicada pelo fator do clima, que depende da temperatura
    SpawnTime = 1000
    ultimoSpawn = pygame.time.get_ticks()
    esperandoProximaOnda = False
    tempoEspera = 0

    # Reseta pontuação e as telas de fim de jogo
    pontos = 0
    gameOver = False
    digitarNome = False
    nomeJogador = ""

    # Esvazia todos os grupos de sprites da partida anterior
    grupo_casas.empty()
    grupo_misseis.empty()
    grupo_projeteis.empty()
    grupo_explosoes.empty()
    grupo_boss.empty()

    # Reconstrói as casas
    for pos in posicoes_fixas:
        nova_casa = Casa(pos, "img/cidade.png")
        grupo_casas.add(nova_casa)

dia, temperatura, chovendo, online = buscar_clima() # Chama a API uma vez só, quando o jogo abre
fator_clima = calcular_fator_clima(temperatura) # Multiplicador da velocidade dos mísseis
gotas = criar_chuva()
# ==================== POSIÇÕES E O RANKING ====================

posicoes_fixas = [
    (115, 400),
    (205, 400),
    (295, 400),
    (515, 400),
    (605, 400),
    (695, 400)
]

ranking = carregar_ranking()

# ==================== GRUPOS DE SPRITES ====================
grupo_casas = pygame.sprite.Group() # Grupo das casas
grupo_explosoes = pygame.sprite.Group() # Grupo das explosões
grupo_projeteis = pygame.sprite.Group() # Grupos dos projeteis
grupo_misseis = pygame.sprite.Group()
grupo_boss = pygame.sprite.Group()

# ==================== VARIÁVEIS DA PARTIDA ====================
# As variáveis das ondas, dos pontos e do game over são criadas aqui pelo resetarJogo()
resetarJogo()

botaoAvancar = pygame.Rect(largura // 2 - 90, altura // 2 + 50, 180, 50) # Botão "Avançar" da tela de game over

# ==================== LOOP PRINCIPAL ====================

while True:  # O loop que deixa o jogo rodando para sempre
    tela.fill((0,0,0)) # Tela preta
    for event in pygame.event.get():
        if event.type == QUIT: # Se clicar em sair você sai
            pygame.quit()
            exit()

        if estado == "menu": # No menu, o clique só serve pro botão
            if event.type == MOUSEBUTTONUP and event.button == 1:
                if botao_jogar.clicado(event.pos): # Se clicar no botão de jogar, começa uma partida nova
                    resetarJogo()
                    estado = "jogando"
                if botao_lederbord.clicado(event.pos): # Se clicar no botão de leaderboard, muda o estado para leaderboard
                    estado = "leaderboard"
                if botao_sair.clicado(event.pos): # Se clicar no botão de sair, sai do jogo
                    pygame.quit()
                    exit()

        elif estado == "jogando":
            if gameOver: # Tela de game over: o clique só serve pro botão Avançar
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    if botaoAvancar.collidepoint(event.pos):
                        gameOver = False
                        digitarNome = True

            elif digitarNome: # Tela de digitar o nome: o teclado escreve o nome
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        nomeJogador = nomeJogador[:-1] # Apaga a última letra
                    elif event.key == K_RETURN:
                        if nomeJogador.strip() != "": # Tira os espaços e confere se o nome não está vazio
                            ranking = salvar_pontuacao(nomeJogador.strip(), pontos) # Salva e já devolve o ranking atualizado
                            digitarNome = False
                            estado = "leaderboard"
                    elif event.unicode.isprintable() and len(nomeJogador) < 10: # Só letras, números e símbolos visíveis, até 10 caracteres
                        nomeJogador += event.unicode # unicode é a letra da tecla apertada; += junta no final do nome

            else: # Jogando normal: o clique atira e o ESC pausa
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    if municao > 0: # Cada tiro gasta 1 de munição
                        grupo_projeteis.add(Projetil(event.pos))
                        municao -= 1
                        if municao == 0: # Quando a última bala é gasta, anota a hora. É aqui que o cronômetro começa.
                            hora_sem_municao = pygame.time.get_ticks()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    estado = "pausado"

        elif estado == "leaderboard":
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                estado = "menu"
        elif estado == "pausado":
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                estado = "jogando"


    if estado == "menu": # Se está no menu, desenha os botoes na tela
        desenhar_ceu() # Puxa a função que desenha o céu de dia ou de noite
        desenhar_chuva()
        tela.blit(img_titulo, img_titulo.get_rect(center=(410, 60)))
        botao_jogar.desenho()
        botao_lederbord.desenho()
        botao_sair.desenho()


    elif estado == "jogando": # Todo o resto do código é o que acontece quando está jogando

        desenhar_ceu() # Puxa a função que desenha o céu de dia ou de noite
        chao() # Puxa a função que faz o ambiente do mapa
        grupo_casas.update() # As casas animam sempre, pra explosão da última cidade aparecer mesmo no game over
        grupo_explosoes.update()

        if not gameOver and not digitarNome: # Só mexe nas coisas enquanto a partida está rolando
            grupo_projeteis.update()
            grupo_misseis.update()
            grupo_boss.update()

            for boss in grupo_boss: # Boss que quer atirar solta um míssil
                if boss.atirar():
                    grupo_misseis.add(Missil(boss.rect.centerx, boss.rect.bottom, random.choice(posicoes_fixas), misseisVelocidade))

            for explosao in grupo_explosoes: # Explosão acertando o boss
                for boss in grupo_boss:
                    if explosao.atinge(boss.rect.centerx, boss.rect.centery):
                        boss.levar_dano()
                        if not boss.alive(): # alive() é False quando o boss acabou de morrer (saiu do grupo)
                            pontos += 200 # Boss derrotado vale 200 pontos

            colisoes_boss = pygame.sprite.groupcollide(grupo_boss, grupo_casas, True, False) # Testa todos os bosses contra todas as casas; o boss que encostar some (True), a casa continua (False)
            for boss, casas_atingidas in colisoes_boss.items():
                for casa in casas_atingidas:
                    casa.destruir()

            for p in grupo_projeteis: # Transforma o tiro em explosão, apagando o disparo e posicionando a explosão
                if p.chegou:
                    grupo_explosoes.add(Explosao(p.destino[0], p.destino[1]))
                    p.kill()

            for explosao in grupo_explosoes: # A morte dos misseis quando a explosão atinge o centro do missil, usando a função atinge da classe Explosao
                for missil in grupo_misseis:
                    if explosao.atinge(missil.rect.centerx, missil.rect.centery):
                        missil.kill()
                        pontos += 25 # Soma 25 pontos por missil destruido

            colisoes = pygame.sprite.groupcollide(grupo_misseis, grupo_casas, True, False) # Testa todos os misseis contra todas as casas; o missil que encostar some (True), a casa continua (False)
            for missil_atingiu, casas_atingidas in colisoes.items():
                for casa in casas_atingidas:
                    if casa.viva:
                        casa.destruir()

            casasVivas = 0 # Conta quantas casas ainda estão vivas
            for casa in grupo_casas:
                if casa.viva:
                    casasVivas += 1
            if casasVivas == 0: # Todas as cidades destruídas: fim de jogo
                gameOver = True

            if municao == 0 and pygame.time.get_ticks() - hora_sem_municao >= 3000: # Confere a cada foto se ja passaram 3 segundos desde que a munição acabou
                municao = 10

            tempoAtual = pygame.time.get_ticks() #variavel que salva o tempo atual
            if misseisRestantes > 0:
                if tempoAtual - ultimoSpawn >= SpawnTime: # verifica se ja passou o tempo entre misseis
                    origemX = random.randint(0, largura)
                    destino = random.choice(posicoes_fixas)
                    novoMissil = Missil(origemX, 0, destino, misseisVelocidade)
                    grupo_misseis.add(novoMissil)
                    misseisRestantes -= 1
                    ultimoSpawn = tempoAtual

            elif len(grupo_misseis) == 0 and len(grupo_boss) == 0 and misseisRestantes == 0 and not esperandoProximaOnda:
                pontos += casasVivas * 100 # Bônus: 100 pontos por cidade que sobreviveu à onda
                esperandoProximaOnda = True
                tempoEspera = tempoAtual

            elif esperandoProximaOnda and (tempoAtual -  tempoEspera) >= 3000:
                ondaAtual += 1 #soma o numero da wave
                if ondaAtual % 3 == 0: # Onda 3, 6, 9...
                    if (ondaAtual // 3) % 2 == 1:
                        grupo_boss.add(Boss1()) # Ondas 3, 9, 15...
                    else:
                        grupo_boss.add(Boss2()) # Ondas 6, 12, 18...

                misseisRestantes = 5 + ondaAtual #aumenta em 1 o numero de inimigos a cada wave
                misseisVelocidade = (2 + (ondaAtual * 0.2)) * fator_clima  #aumenta a velocidade dos misseis a cada onda (A velocidade dos misseis é multiplicada pelo fator do clima, que depende da temperatura)
                SpawnTime = max(500, 1500 - (ondaAtual * 50)) #diminui o tempo entre o nascimento de um missil e outro
                esperandoProximaOnda = False

        # ---------- DESENHO DA PARTIDA (aparece até atrás do game over) ----------
        for missil in grupo_misseis: # O rastro dos misseis
            pygame.draw.line(tela, "white", (missil.spawnX, missil.spawnY), missil.rect.center, 2)

        grupo_casas.draw(tela)  # Desenha tudo na tela
        grupo_projeteis.draw(tela)
        grupo_misseis.draw(tela)
        grupo_boss.draw(tela)
        grupo_explosoes.draw(tela)
        desenhar_chuva()
        desenhar_municao()

        if municao == 0: # Se a munição for zero, deixa na tela "OUT" ate a munição voltar a ser 10
            aviso = fonte.render("OUT", False, (255, 0, 0))
            tela.blit(aviso, aviso.get_rect(center=(400, 425)))

        if online: # Dados reais da API
            clima = fonte.render(f"Curitiba: {temperatura}°C", False, (255, 255, 255))
        else:      # Sem internet: deixa claro que é simulado
            clima = fonte.render(f"Simulado: {temperatura}°C", False, (255, 200, 120))
        tela.blit(clima, (20, 20))

        textoOndaAtual = fonte.render(f"Onda Atual: {ondaAtual}", False, (255, 255, 255))
        tela.blit(textoOndaAtual, (20, 50)) # Embaixo da temperatura

        if fator_clima > 1: # Mostra o efeito do clima na dificuldade
            efeito = fonte_pequena.render(f"Calor: misseis +{round((fator_clima - 1) * 100)}%", False, (255, 140, 60))
            tela.blit(efeito, (20, 80))
        elif fator_clima < 1:
            efeito = fonte_pequena.render(f"Frio: misseis -{round((1 - fator_clima) * 100)}%", False, (120, 200, 255))
            tela.blit(efeito, (20, 80))

        texto_pontos = fonte.render(f"Pontos: {pontos}", False, (255, 255, 255))
        tela.blit(texto_pontos, texto_pontos.get_rect(topright=(largura - 20, 20))) # Alinhado pela direita, não sai da tela quando o número cresce

        if esperandoProximaOnda and not gameOver:
            avisoEntreOndas = fonte.render(f"Onda {ondaAtual} concluída! Prepare-se!", False, (255, 255, 0))
            tela.blit(avisoEntreOndas, avisoEntreOndas.get_rect(center=(largura // 2, altura // 2)))

        # ==================== TELA GAME OVER COM BOTAO AVANÇAR ====================
        if gameOver:
            telaGameOver = pygame.Surface((largura, altura)) #cria a surface do game over (no caso do mesmo tamanho da tela do jogo)
            telaGameOver.set_alpha(170) #Definição do nivel de transparencia
            telaGameOver.fill((0,0,0)) # Pinta a superficie (nesse caso, de preto)
            tela.blit(telaGameOver, (0, 0)) # Coloca a superficie em cima da tela do jogo, partindo da cordenada (0,0)

            textoGameOver = fonte.render("GAME OVER", False, (255, 60, 60))
            tela.blit(textoGameOver, textoGameOver.get_rect(center=(largura // 2, altura // 2 - 70)))

            textoFinal = fonte.render(f"Pontos: {pontos}   Onda: {ondaAtual}", False, (255, 220, 60)) # Resumo da partida
            tela.blit(textoFinal, textoFinal.get_rect(center=(largura // 2, altura // 2 - 30)))

            corBorda = (255, 220, 40) if botaoAvancar.collidepoint(pygame.mouse.get_pos()) else (0, 220, 255) # Borda amarela com o mouse em cima
            pygame.draw.rect(tela, (8, 8, 28), botaoAvancar)
            pygame.draw.rect(tela, corBorda, botaoAvancar, 3)
            textoBotaoAvancar = fonte.render("AVANÇAR", False, (255, 220, 60))
            tela.blit(textoBotaoAvancar, textoBotaoAvancar.get_rect(center=botaoAvancar.center))

        # ==================== TELA PARA DIGITAR O NOME ====================
        if digitarNome:
            tela.fill((0, 0, 0)) #tela preta limpa

            textoNome = fonte.render("Digite seu nome:", False, (255, 255, 255))
            tela.blit(textoNome, textoNome.get_rect(center=(largura // 2, (altura // 2) - 60)))

            caixaNome = pygame.Rect(largura // 2 - 150, altura // 2 - 20, 300, 50)
            pygame.draw.rect(tela, (8, 8, 28), caixaNome)
            pygame.draw.rect(tela, (0, 220, 255), caixaNome, 2)

            cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else "" # a cada 500 ms alterna entre caracter _ e uma string vazia
            textoNomeRender = fonte.render(nomeJogador + cursor, False, (255, 255, 0)) # junção do cursor + caractere digitado pelo usuario
            tela.blit(textoNomeRender, textoNomeRender.get_rect(center=caixaNome.center))

            textoEnter = fonte.render("ENTER para confirmar", False, (150, 150, 150)) # para confirmar o nome
            tela.blit(textoEnter, textoEnter.get_rect(center=(largura // 2, altura // 2 + 60)))

    elif estado == "leaderboard": # Se o estado for leaderboard, desenha o ranking na tela
        desenhar_ceu()
        titulo = fonte.render("LEADERBOARD", False, (255, 0, 0))
        tela.blit(titulo, titulo.get_rect(center=(410, 80)))

        y = 130
        posicao = 1
        for jogador in ranking:   # cada jogador é um dicionário, ex.: {"nome": "Victor", "pontos": 1200}
            linha = fonte.render(f"{posicao}. {jogador['nome']}   {jogador['pontos']}", False, (255, 255, 255))
            tela.blit(linha, linha.get_rect(center=(410, y)))
            y += 28
            posicao += 1

        dica = fonte.render("ESC para voltar", False, (150, 150, 150))
        tela.blit(dica, dica.get_rect(center=(410, 440)))

    elif estado == "pausado": # Se o jogo estiver pausado, desenha o texto de pausa e fica em uma tela que so é possivel sair apertando ESC
        desenhar_ceu()
        pausa_texto = fonte.render("PAUSADO", False, (255, 255, 0))
        tela.blit(pausa_texto, pausa_texto.get_rect(center=(410, 240)))
        dica = fonte.render("ESC para voltar", False, (150, 150, 150))
        tela.blit(dica, dica.get_rect(center=(410, 280)))

    pygame.display.update() # Usado para atualizar novas coisas
    clock.tick(60) # Quantidade de FPS