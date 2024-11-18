import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import unicodedata
import random
import time

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


ligas = ["https://www.flashscore.com.br/futebol/brasil/brasileirao-betano/calendario/",
        "https://www.flashscore.com.br/futebol/espanha/laliga/calendario/",
        "https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles/calendario/"]

hrefs = []
nome_ligas = []

#Localizando os Jogos
max_tentativas = 5

for liga in ligas:
    elemento_encontrado = False
    tentativa = 0
    while tentativa <= max_tentativas: #Verifica se a página foi carregada corretamente, caso contrário tenta novamente
        try:
            driver.get(liga)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'header__logo')))
            elemento_encontrado = True
            tentativa=0
            break
        except WebDriverException as e:
            print(f"Erro ao carregar a página: {e}. Tentando novamente...")
            tentativa += 1
            time.sleep(2)
        

    if not elemento_encontrado:
        print('Falha ao carregar após 5 tentativas')
        continue
    else:
        print('Página carregada com sucesso!')
            
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'live-table')))
    tabela_de_jogos = driver.find_element(By.ID, 'live-table')
    links_jogos = tabela_de_jogos.find_elements(By.CLASS_NAME, 'eventRowLink')
    for i, link in enumerate(links_jogos):
        if i <= 10:
            hrefs.append(link.get_attribute('href'))
        else:
            break


cod_jogo = list(map(lambda x: x.split('/jogo/')[1].split('/')[0], hrefs))
print(f'{len(cod_jogo)} Jogos Coletados')
#random.shuffle(cod_jogo)
#codJogo = pd.DataFrame({"Game":cod_jogo})
#codJogo.to_csv('Jogos.csv', index=False)

    
paises, ligas, data,cod_partida,time1, codigo1, time2, codigo2  = [],[],[],[],[],[],[],[]

print("Inciando coleta de dados dos jogos!")

##Coletando info dos jogos
for i, cod in enumerate(tqdm(cod_jogo)):
    if i<=len(cod_jogo):    
        tentativa = 0
        while tentativa < max_tentativas:
            try:
                url_jogo = f"https://www.flashscore.com.br/jogo/{cod}/#/resumo-de-jogo/estatisticas-de-jogo/0"
                driver.get(url_jogo)
                time.sleep(2)
                #Coleta_Liga
                detail = driver.find_element(By.ID, 'detail')
                tentativa = 0
                break
            except Exception as e:
                tentativa += 1
                print(type(e))
                print(f'Jogo {cod} não carregou, tentando novamente...')
                time.sleep(3)

        if tentativa == max_tentativas:
            print(f'Jogo {cod} falhou após {max_tentativas} tentativas.')
            print('Nenhuma informação disponível')
            paises.append('N/A')
            ligas.append('N/A')
            data.append('N/A')
            cod_partida.append(cod)
            time1.append('N/A')
            codigo1.append('N/A')
            time2.append('N/A')
            codigo2.append('N/A')
            continue
        try:
            try:
                info_liga = detail.find_element(By.XPATH, './div[3]/div[1]/span[3]').text
                pais = info_liga.split(":")[0]
                liga = info_liga.split("-")[0].split(":")[1].strip()
                paises.append(remover_acentos(pais))
                ligas.append(remover_acentos(liga))
            except:
                paises.append('N/A')
                ligas.append('N/A')
            
            #Coleta de Data
            data_jogo = detail.find_element(By.XPATH,'./div[4]/div[1]').text.split(" ")[0].replace('.','/')
            data.append(data_jogo)

            #Coleta_Codigo
            cod_partida.append(cod)

            #Coleta de Informações dos Times do Confronto
            time_casa = detail.find_element(By.XPATH,'./div[4]/div[2]/div[3]/div[2]').text
            time1.append(remover_acentos(time_casa))
            cod_casa = detail.find_element(By.XPATH,'./div[4]/div[2]/div[3]/div[2]/a').get_attribute('href').rstrip("/").split("/")[-1]
            codigo1.append(cod_casa)
            time_visitante = detail.find_element(By.XPATH,'./div[4]/div[4]/div[3]/div[1]').text
            time_visitante = remover_acentos(time_visitante)
            time2.append(time_visitante)
            cod_visitante = detail.find_element(By.XPATH,'./div[4]/div[4]/div[3]/div[1]/a').get_attribute('href').rstrip("/").split("/")[-1]
            codigo2.append(cod_visitante)
      
        except Exception as e:
            print(f'Erro ao capturar dados: {e}')
            print(cod)
    else:
        break


base = pd.DataFrame(
    {"Pais":paises,
    "Liga":ligas,
    "Data":data,
    "Id_Jogo":cod_partida,
    "Time_Casa":time1,
    "Id_Casa":codigo1,
    "Time_Visitante":time2,
    "Id_Visitante":codigo2,})

#base_completa = pd.concat([base_atual, base], ignore_index=True)
#base_completa = base_completa.drop_duplicates(subset='Id_Jogo', keep='last')

base.to_csv('Base.csv',index=False)