# Missile Command

Recriação do Missile Command (Atari, 1980) em Python com Pygame, feita como projeto final de Raciocínio Algorítmico na PUCPR.

A diferença do original: o jogo usa o clima real de Curitiba. Se for noite, o jogo fica de noite. Se estiver chovendo, chove na tela. E quanto mais quente estiver, mais rápido os mísseis caem.

## Como jogar

### Pelo executável (Windows)

1. Baixe o arquivo `MissileCommand_windows.zip`
2. Extraia o zip
3. Abra a pasta `dist` e dê dois cliques em `MissileCommand.exe`

Não precisa instalar nada.

### Pelo Python

Precisa do Python 3.12.

```
python -m pip install -r requirements.txt
python base_jogo.py
```

### Controles

- **Mouse:** mira
- **Clique esquerdo:** atira
- **ESC:** pausa e volta ao menu
- **Enter:** confirma o nome no ranking

## O que tem no jogo

- 6 cidades para defender. Se todas forem destruídas, é game over
- 10 tiros de munição, com recarga automática depois de 2 segundos
- Ondas que vão ficando mais difíceis, com mais mísseis e mais rápidos
- Dois bosses que aparecem a cada 3 ondas, alternando:
  - **Boss 1:** desce em direção a uma cidade, tem 3 vidas e se teleporta quando é atingido
  - **Boss 2:** anda de um lado para o outro no céu e solta um míssil a cada 2 segundos
- Pontos: 25 por míssil, 200 por boss e 100 por cidade que sobreviver à onda
- Ranking com os 10 melhores, salvo em `ranking.json`
- Sons, explosões animadas e fonte estilo arcade

### Clima

O jogo consulta a API [Open-Meteo](https://open-meteo.com/) quando abre. A API é gratuita e não precisa de chave nem de cadastro.

| Temperatura em Curitiba | Velocidade dos mísseis |
|---|---|
| 28 °C ou mais | +30% |
| 22 °C a 27 °C | +15% |
| 13 °C a 21 °C | normal |
| 12 °C ou menos | -20% |

Sem internet, o jogo entra no modo simulado (dia, 30 °C e chuva) e mostra "Simulado" no canto da tela.

## Arquivos

```
base_jogo.py                  código do jogo
requirements.txt              bibliotecas (pygame e requests)
ranking.json                  ranking salvo
MissileCommand_windows.zip    executável
img/  fonts/  audios/         imagens, fonte e sons
registros_individuais/        registros de cada integrante
```

## Autores

Victor Eduardo Ramos e João Vitor de Deus Viana
Sistemas de Informação, PUCPR, 2026
Professora: Marina de Lara

## Créditos

- Fonte Press Start 2P (SIL Open Font License, ver `fonts/OFL.txt`)
- Dados de clima: Open-Meteo
- Sprites feitos com ajuda de IA e ajustados por nós
