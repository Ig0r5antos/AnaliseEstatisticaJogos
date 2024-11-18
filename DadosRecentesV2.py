import pandas as pd
from datetime import datetime


def calcular_medias(df, coluna_time,coluna_gols,coluna_fin,coluna_chute, coluna_gols_sofridos, coluna_cantos, coluna_cantos_adv):
    medias_por_time = {}
    
    for time in df[coluna_time].unique():
        # Filtra os jogos do time específico
        ultimos_jogos = bd_historico[bd_historico[coluna_time] == time]
        ultimo_jogo = ultimos_jogos['Data'].max()
        
        # Calcula as médias e armazena em um dicionário
        medias_por_time[time] = {
            'ultima_partida' : ultimo_jogo,
            'media_gols': ultimos_jogos[coluna_gols].mean(),
            'media_gols_sofridos': ultimos_jogos[coluna_gols_sofridos].mean(),
            'media_finalizacoes' : ultimos_jogos[coluna_fin].mean(),
            'media_chutes' : ultimos_jogos[coluna_chute].mean(),
            'media_cantos': ultimos_jogos[coluna_cantos].mean(),
            'media_cantos_adv': ultimos_jogos[coluna_cantos_adv].mean()
        }
    
    return medias_por_time

def adicionar_medias(df,coluna_time,dicionario_medias):
    df['ultimo_jogo'] = df[coluna_time].map(lambda x: dicionario_medias[x]['ultima_partida'] if x in dicionario_medias else None)
    df['media_gols'] = df[coluna_time].map(lambda x: dicionario_medias[x]['media_gols'] if x in dicionario_medias else None)
    df['media_gols_sofridos'] = df[coluna_time].map(lambda x: dicionario_medias[x]['media_gols_sofridos'] if x in dicionario_medias else None)
    df['media_finalizações'] = df[coluna_time].map(lambda x: dicionario_medias[x]['media_finalizacoes'] if x in dicionario_medias else None)
    df['media_chutes'] = df[coluna_time].map(lambda x: dicionario_medias[x]['media_finalizacoes'] if x in dicionario_medias else None)
    df['media_cantos'] = df[coluna_time].map(lambda x: dicionario_medias[x]['media_cantos'] if x in dicionario_medias else None)
    df['media_cantos_adv'] = df[coluna_time].map(lambda x: dicionario_medias[x]['media_cantos_adv'] if x in dicionario_medias else None)

#Importando o histórico
bd_historico = pd.read_csv("./Base.csv")
#print(bd_historico.columns)
#Transformando as datas de objeto para data
bd_historico['Data'] = bd_historico['Data'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))

#Ordenando por ordem decrescente
bd_historico.sort_values('Data',ascending=False,inplace=True)

#equipes_casa = bd_historico.groupby('Time_Casa')[['Gols_Casa','Finalizacoes_Casa','Chutes_Casa','Gols_Visitante','Cantos_Casa', 'Cantos_Visitante']].mean()
#print(equipes_casa)
equipes_casa = bd_historico.groupby('Time_Casa').agg(
    {
        'Data':'max', #Ultima partida
        'Gols_Casa':'mean', #Media de Gols
        'Finalizacoes_Casa':'mean', #Media de Finalizaçoes
        'Chutes_Casa':'mean', #Media de Chutes
        'Gols_Visitante':'mean', #Gols Sofridos
        'Cantos_Casa':'mean', #Escanteios Casa
        'Cantos_Visitante':'mean' #Escanteios Sofridos
    })

    
equipes_visitante = bd_historico.groupby('Time_Visitante').agg(
    {
        'Data':'max', #Ultima partida
        'Gols_Visitante':'mean', #Media de Gols
        'Finalizacoes_Visitante':'mean', #Media de Finalizaçoes
        'Chutes_Visitante':'mean', #Media de Chutes
        'Gols_Casa':'mean', #Gols Sofridos
        'Cantos_Visitante':'mean', #Escanteios Visitante
        'Cantos_Casa':'mean' #Escanteios Sofridos
    })

print(equipes_casa)


"""
#Criando a lista de times (Mandante e Visitante)
equipes_casa = bd_historico[['Id_Casa','Time_Casa','Liga']]
equipes_casa = equipes_casa.drop_duplicates(subset='Id_Casa')

equipes_visitante = bd_historico[['Id_Visitante','Time_Visitante','Liga']]
equipes_visitante = equipes_casa.drop_duplicates(subset='Id_Casa')

#print(equipes_casa)
#print(equipes_visitante)

ligas = list(bd_historico['Liga'].unique())

media_casa = calcular_medias(bd_historico, 'Time_Casa', 'Gols_Casa','Finalizacoes_Casa','Chutes_Casa','Gols_Visitante','Cantos_Casa', 'Cantos_Visitante')
media_visitante = calcular_medias(bd_historico, 'Time_Visitante', 'Gols_Visitante','Finalizacoes_Casa','Chutes_Casa', 'Gols_Casa', 'Cantos_Visitante', 'Cantos_Casa')

adicionar_medias(equipes_casa,'Time_Casa',media_casa)
adicionar_medias(equipes_visitante,'Time_Casa',media_visitante)

equipes_casa.to_excel("./Bases/Casa.xlsx", index=False)
equipes_visitante.to_excel("./Bases/Visitantes.xlsx", index=False)"""



