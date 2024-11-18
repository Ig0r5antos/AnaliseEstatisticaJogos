import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unicodedata
import re

def remover_acentos(texto):
    # Normaliza o texto para a forma NFKD e remove caracteres não-ASCII (acentos)
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

service = Service()
options = Options()
options.add_argument("--headless")  # Executa sem interface gráfica
options.add_argument("--disable-gpu")  # Recomendado para compatibilidade no modo headless
options.add_argument("--disable-webgl") # Desativar WebGL
options.add_argument("--log-level=3") # Suprimir logs de erro no console
options.add_argument("--disable-software-rasterizer") # Desativar fallback automático para WebGL
options.add_argument("--disable-notifications")  # Desabilita notificações push
options.add_argument("--window-size=1920,1080")  # Define um tamanho de janela, útil para headless
options.add_argument("--no-sandbox")  # Necessário em alguns sistemas Linux
options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória compartilhada em containers
driver = webdriver.Chrome(service=service, options=options)

ligas = ["https://www.flashscore.com.br/futebol/brasil/brasileirao-betano/#/Klz7n21m/table/overall",
        "https://www.flashscore.com.br/futebol/espanha/laliga/#/dINOZk9Q/table/overall",
        "https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles/#/lAkHuyP3/table/overall"]

pos_tabela = {}


for liga in ligas:
    driver.get(liga)
    nome_liga_pai = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, 'container__livetable')))
    nome_liga = nome_liga_pai.find_element(By.XPATH, './div[1]/div[2]/div[1]').text
    nome_liga = remover_acentos(nome_liga)
    pos_tabela[nome_liga] = []
    tabela_pai = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, 'tournament-table-tabs-and-content')))
    tabela_filho = tabela_pai.find_element(By.XPATH, './div[3]')
    tabela = tabela_filho.find_elements(By.CLASS_NAME, 'tableCellParticipant')
    for posicao, linha in enumerate(tabela, start=1):
        nome_time = linha.text
        nome_time = remover_acentos(nome_time)

        pos_tabela[nome_liga].append({'Posição':posicao, "Time":nome_time})

for liga, times in pos_tabela.items():
    
    df = pd.DataFrame(times)
    nome_arquivo = remover_acentos(liga).replace(" ", "_").lower()+".csv"
    df.to_csv(f"./Bases/{nome_arquivo}", index=False, encoding='utf-8')
    print(f'arquivo {nome_arquivo} criado com sucesso!')
        


