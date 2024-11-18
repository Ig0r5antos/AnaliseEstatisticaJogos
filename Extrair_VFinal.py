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
#options.add_argument("--headless")  # Executa sem interface gráfica
options.add_argument("--disable-gpu")  # Recomendado para compatibilidade no modo headless
options.add_argument("--disable-webgl") # Desativar WebGL
options.add_argument("--log-level=3") # Suprimir logs de erro no console
options.add_argument("--disable-software-rasterizer") # Desativar fallback automático para WebGL
options.add_argument("--disable-notifications")  # Desabilita notificações push
options.add_argument("--window-size=1920,1080")  # Define um tamanho de janela, útil para headless
options.add_argument("--no-sandbox")  # Necessário em alguns sistemas Linux
options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória compartilhada em containers
driver = webdriver.Chrome(service=service, options=options)

'''
ligas =["https://www.flashscore.com.br/futebol/brasil/brasileirao-betano/resultados/",
        "https://www.flashscore.com.br/futebol/brasil/brasileirao-betano-2023/resultados/",
        "https://www.flashscore.com.br/futebol/espanha/laliga/resultados/",
        "https://www.flashscore.com.br/futebol/espanha/laliga-2023-2024/resultados/",
        "https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles/resultados/",
        "https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles-2023-2024/resultados/",
        "https://www.flashscore.com.br/futebol/brasil/serie-b/resultados/",
        "https://www.flashscore.com.br/futebol/brasil/serie-b-2023/resultados/",
        "https://www.flashscore.com.br/futebol/portugal/liga-portugal/resultados/",
        "https://www.flashscore.com.br/futebol/portugal/liga-portugal-2023-2024/resultados/"]
'''

ligas = ["https://www.flashscore.com.br/futebol/brasil/brasileirao-betano/resultados/",
        "https://www.flashscore.com.br/futebol/brasil/brasileirao-betano-2023/resultados/",
        "https://www.flashscore.com.br/futebol/espanha/laliga/resultados/",
        "https://www.flashscore.com.br/futebol/espanha/laliga-2023-2024/resultados/",
        "https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles/resultados/",
        "https://www.flashscore.com.br/futebol/inglaterra/campeonato-ingles-2023-2024/resultados/"]

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
            

    #nome_liga = liga.split('/resultados/')[0].split('/')[1]
    while True: #Localiza e clica em todos os botões de Mostrar Mais da página
        try:
            mostrar_mais = driver.find_element(By.CSS_SELECTOR, 'a.event__more--static')
            driver.execute_script("arguments[0].click();", mostrar_mais)
            time.sleep(3)
        except: 
            break
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'live-table')))
    tabela_de_jogos = driver.find_element(By.ID, 'live-table')
    links_jogos = tabela_de_jogos.find_elements(By.CLASS_NAME, 'eventRowLink')
    for link in links_jogos:
        hrefs.append(link.get_attribute('href'))

cod_jogo = list(map(lambda x: x.split('/jogo/')[1].split('/')[0], hrefs))
print(f'{len(cod_jogo)} Jogos Coletados')
#random.shuffle(cod_jogo)
#codJogo = pd.DataFrame({"Game":cod_jogo})
#codJogo.to_csv('Jogos.csv', index=False)

base_atual = pd.read_csv('./Base.csv')

jogos_analisados = list(base_atual['Id_Jogo'])
set_principal = set(jogos_analisados)

if len(cod_jogo) <= len(jogos_analisados):
    print('Não há jogos novos para analisar')
else:
    cod_jogo = [item for item in cod_jogo if item not in set_principal]
    print(f'{len(cod_jogo)} Jogos Novos')
    
    paises, ligas, data,cod_partida,time1, codigo1, time2, codigo2, gols1, gols2, posse1, posse2  = [],[],[],[],[],[],[],[],[],[],[],[]
    fin1, fin2, chute1, chute2, exp1, exp2, canto1, canto2, faltas1, faltas2 = [],[],[],[],[],[],[],[],[],[]

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
                gols1.append('N/A')
                gols2.append('N/A')
                posse1.append('N/A')
                posse2.append('N/A')
                fin1.append('N/A')
                fin2.append('N/A')
                chute1.append('N/A')
                chute2.append('N/A')
                exp1.append('N/A')
                exp2.append('N/A')
                canto1.append('N/A')
                canto2.append('N/A')
                faltas1.append('N/A')
                faltas2.append('N/A')
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

                #Coleta de Gols
                gols_casa = detail.find_element(By.XPATH,'./div[4]/div[3]/div[1]/div[1]/span[1]').text
                gols1.append(gols_casa)
                #gols_1_tempo_casa = 
                gols_visitante = detail.find_element(By.XPATH,'./div[4]/div[3]/div/div[1]/span[3]').text
                gols2.append(gols_visitante)
                #gols_1_tempo_visitante =

                #Coleta de Estatísticas
                section = driver.find_element(By.CLASS_NAME, 'section') #Quadro geral de stats
                first_stat = section.find_element(By.XPATH, './div[1]/div[1]/div[2]').text
                if first_stat == "Gols Esperados (xG)":
                
                    #Posse de Bola
                    validador = section.find_element(By.XPATH,'./div[2]/div[1]/div[2]').text
                    if validador == "Posse de Bola":
                        #Posse_Casa
                        stat = section.find_element(By.XPATH, './div[2]/div[1]/div[1]').text
                        posse1.append(stat)

                        #Posse_Visitante
                        stat = section.find_element(By.XPATH, './div[2]/div[1]/div[3]').text
                        posse2.append(stat)
                    else:
                        print('Informação em local diferente')
                        posse1.append('N/A')
                        posse2.append('N/A')



                    #Finalização
                    validador = section.find_element(By.XPATH, './div[3]/div[1]/div[2]').text
                    if validador == "Tentativas de Gol":
                        #Finalização_Casa
                        stat = section.find_element(By.XPATH, './div[3]/div[1]/div[1]').text
                        fin1.append(stat)

                        #Finalização_Fora
                        stat = section.find_element(By.XPATH, './div[3]/div[1]/div[3]').text
                        fin2.append(stat)
                    else:
                        print('Informação em local diferente')
                        fin1.append('N/A')
                        fin2.append('N/A')
                    
                    #Chutes_Ao_Gol
                    validador = section.find_element(By.XPATH, './div[4]/div[1]/div[2]').text
                    if validador == "Chutes no Gol":
                        #Chutes_Ao_Gol_Casa
                        stat = section.find_element(By.XPATH, './div[4]/div[1]/div[1]').text
                        chute1.append(stat)

                        #Chutes_Ao_Gol_Visitante
                        stat = section.find_element(By.XPATH, './div[4]/div[1]/div[3]').text
                        chute2.append(stat)
                    else:
                        print('Informação em local diferente')
                        chute1.append('N/A')
                        chute2.append('N/A')
                    
                    #Exp_Gols
                    validador = section.find_element(By.XPATH, './div[1]/div[1]/div[2]').text
                    if validador == "Gols Esperados (xG)":
                        #Exp_Gols_Casa
                        stat = section.find_element(By.XPATH, './div[1]/div[1]/div[1]').text
                        exp1.append(stat)

                        #Exp_Gols_Visitante
                        stat = section.find_element(By.XPATH, './div[1]/div[1]/div[3]').text
                        exp2.append(stat)
                    else:
                        print('Informação em local diferente')
                        exp1.append('N/A')
                        exp2.append('N/A')
                    
                    #Cantos
                    validador = section.find_element(By.XPATH, './div[8]/div[1]/div[2]').text
                    if validador == "Escanteios":
                        #Cantos_Casa
                        stat = section.find_element(By.XPATH, './div[8]/div[1]/div[1]').text
                        canto1.append(stat)
                        
                        #Cantos_Visitante
                        stat = section.find_element(By.XPATH, './div[8]/div[1]/div[3]').text
                        canto2.append(stat)
                    else:
                        validador = section.find_element(By.XPATH,'./div[7]/div[1]/div[2]' ).text
                        if validador == "Escanteios":
                            #Cantos_Casa
                            stat = section.find_element(By.XPATH, './div[7]/div[1]/div[1]').text
                            canto1.append(stat)

                            #Cantos_Visitante
                            stat = section.find_element(By.XPATH, './div[7]/div[1]/div[3]').text
                            canto2.append(stat)
                        else:
                            validador = section.find_element(By.XPATH, './div[6]/div[1]/div[2]').text
                            if validador == "Escanteios":
                                #Cantos_Casa
                                stat = section.find_element(By.XPATH, './div[6]/div[1]/div[1]').text
                                canto1.append(stat)

                                #Cantos_Visitante
                                stat = section.find_element(By.XPATH, './div[6]/div[1]/div[3]').text
                                canto2.append(stat)
                            else:
                                print('Informação em local diferente')
                                canto1.append('N/A')
                                canto2.append('N/A')
                    
                    #Faltas
                    validador = section.find_element(By.XPATH, './div[12]/div[1]/div[2]').text
                    if validador == "Faltas":
                        #Faltas_Casa
                        stat = section.find_element(By.XPATH, './div[12]/div[1]/div[1]').text
                        faltas1.append(stat)

                        #Faltas_Fora
                        stat = section.find_element(By.XPATH, './div[12]/div[1]/div[3]').text
                        faltas2.append(stat)
                    else:
                        validador = section.find_element(By.XPATH, './div[11]/div[1]/div[2]').text
                        if validador == "Faltas":
                            #Faltas_Casa
                            stat = section.find_element(By.XPATH, './div[11]/div[1]/div[1]').text
                            faltas1.append(stat)

                            #Faltas_Visitante
                            stat = section.find_element(By.XPATH, './div[11]/div[1]/div[3]').text
                            faltas2.append(stat)
                        else:
                            validador = section.find_element(By.XPATH, './div[9]/div[1]/div[2]').text
                            if validador == "Faltas":
                                #Faltas_Casa
                                stat = section.find_element(By.XPATH, './div[9]/div[1]/div[1]').text
                                faltas1.append(stat)

                                #Faltas_Visitante
                                stat = section.find_element(By.XPATH, './div[9]/div[1]/div[3]').text
                                faltas2.append(stat)
                            else:
                                validador = section.find_element(By.XPATH, './div[10]/div[1]/div[2]').text
                                if validador == "Faltas":
                                    #Faltas_Casa
                                    stat = section.find_element(By.XPATH, './div[10]/div[1]/div[1]').text
                                    faltas1.append(stat)

                                    #Faltas_Visitantes
                                    stat = section.find_element(By.XPATH, './div[10]/div[1]/div[3]').text
                                    faltas2.append(stat)
                                else:
                                    print('Informação em local diferente')
                                    faltas1.append('N/A')
                                    faltas2.append('N/A')

                elif first_stat == "Posse de Bola":
                    #Posse_de_Bola
                    validador = section.find_element(By.XPATH, './div[1]/div[1]/div[2]').text
                    if validador == "Posse de Bola":
                        #Posse_de_Bola_Casa
                        stat = section.find_element(By.XPATH, './div[1]/div[1]/div[1]').text
                        posse1.append(stat)

                        #Posse_de_Bola_Visitante
                        stat = section.find_element(By.XPATH, './div[1]/div[1]/div[3]').text
                        posse2.append(stat)
                    else:
                        print('Informação em local diferente')
                        posse1.append('N/A')
                        posse2.append('N/A')

                    #Finalização
                    validador = section.find_element(By.XPATH, './div[2]/div[1]/div[2]').text
                    if validador == "Tentativas de Gol":
                        #Finalização_Casa
                        stat = section.find_element(By.XPATH, './div[2]/div[1]/div[1]').text
                        fin1.append(stat)

                        #Finalização_Fora
                        stat = section.find_element(By.XPATH, './div[2]/div[1]/div[3]').text
                        fin2.append(stat)
                    else:
                        print('Informação em local diferente')
                        fin1.append('N/A')
                        fin2.append('N/A')
                    
                    #Chutes_Ao_Gol
                    validador = section.find_element(By.XPATH, './div[3]/div[1]/div[2]').text
                    if validador == "Chutes no Gol":
                        #Chutes_Ao_Gol_Casa
                        stat = section.find_element(By.XPATH, './div[3]/div[1]/div[1]').text
                        chute1.append(stat)

                        #Chutes_Ao_Gol_Visitante
                        stat = section.find_element(By.XPATH, './div[3]/div[1]/div[3]').text
                        chute2.append(stat)
                    else:
                        print('Informação em local diferente')
                        chute1.append('N/A')
                        chute2.append('N/A')
                    
                    #Exp_Gols(Casos onde não temos esta informação disponível)
                    exp1.append('N/A')
                    exp2.append('N/A')
                    
                    #Cantos
                    validador = section.find_element(By.XPATH, './div[7]/div[1]/div[2]').text
                    if validador == "Escanteios":
                        #Cantos_Casa
                        stat = section.find_element(By.XPATH, './div[7]/div[1]/div[1]').text
                        canto1.append(stat)
                        
                        #Cantos_Visitante
                        stat = section.find_element(By.XPATH, './div[7]/div[1]/div[3]').text
                        canto2.append(stat)
                    else:
                        validador = section.find_element(By.XPATH, './div[6]/div[1]/div[2]').text
                        if validador == "Escanteios":
                            #Cantos_Casa
                            stat = section.find_element(By.XPATH, './div[6]/div[1]/div[1]').text
                            canto1.append(stat)

                            #Cantos_Visitante
                            stat = section.find_element(By.XPATH, './div[6]/div[1]/div[3]').text
                            canto2.append(stat)
                        else:
                            print('Informação em local diferente')
                            canto1.append('N/A')
                            canto2.append('N/A')
                    
                    #Faltas
                    validador = section.find_element(By.XPATH, './div[11]/div[1]/div[2]').text
                    if validador == "Faltas":
                        #Faltas_Casa
                        stat = section.find_element(By.XPATH, './div[11]/div[1]/div[1]').text
                        faltas1.append(stat)

                        #Faltas_Fora
                        stat = section.find_element(By.XPATH, './div[11]/div[1]/div[3]').text
                        faltas2.append(stat)
                    else:
                        validador = section.find_element(By.XPATH, './div[10]/div[1]/div[2]').text
                        if validador == "Faltas":
                            #Faltas_Casa
                            stat = section.find_element(By.XPATH, './div[10]/div[1]/div[1]').text
                            faltas1.append(stat)

                            #Faltas_Visitante
                            stat = section.find_element(By.XPATH, './div[10]/div[1]/div[3]').text
                            faltas2.append(stat)
                        else:
                            print('Informação em local diferente')
                            faltas1.append('N/A')
                            faltas2.append('N/A')
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
        "Id_Visitante":codigo2,
        "Gols_Casa":gols1,
        "Gols_Visitante":gols2,
        "Posse_Casa":posse1,
        "Posse_Visitante":posse2,
        "Finalizacoes_Casa":fin1,
        "Finalizacoes_Visitante":fin2,
        "Chutes_Casa":chute1,
        "Chutes_Visitante":chute2,
        "ExpGols_Casa":exp1,
        "ExpGols_Visitante":exp2,
        "Cantos_Casa":canto1,
        "Cantos_Visitante":canto2,
        "Faltas_Casa":faltas1,
        "Faltas_Visitantes":faltas2})

    base_completa = pd.concat([base_atual, base], ignore_index=True)
    base_completa = base_completa.drop_duplicates(subset='Id_Jogo', keep='last')

    base_completa.to_csv('Base.csv',index=False)