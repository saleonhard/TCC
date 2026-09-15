# Importações de bibliotecas necessárias
import tweepy  # Para interagir com a API do Twitter
import time  # Para pausas e controle de tempo
from keys import *  # Importa chaves de API (arquivo local)
from oauth2client.service_account import ServiceAccountCredentials  # Autenticação Google
import json  # Manipulação de JSON (não utilizado diretamente aqui)
import gspread as gp  # Para trabalhar com Google Sheets
import re  # Expressões regulares para processamento de texto
from dateutil import tz  # Conversão de fuso horário
from datetime import datetime, timedelta  # Manipulação de datas

# Configuração da autenticação com Google Sheets usando credenciais de serviço
sa = gp.service_account(filename='credenciais.json')

# Abertura da planilha do Google Sheets chamada "Twitter"
sh = sa.open("Twitter")

# Configuração da autenticação da API do Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)  # Cria objeto da API

# Acesso às abas específicas da planilha
wks = sh.worksheet("Tweets")  # Aba para armazenar os tweets
wks2 = sh.worksheet("Configs")  # Aba para configurações e controle

# Loop principal de busca contínua
while True:
    busca_palavras = "urna eletronica OR urna OR #urna OR #urnaeletronica"  # Termos de busca
    print("🔍 Pesquisando tweets...")
    ultimo_tweet = int(wks2.acell('B2').value)  # Obtém último ID de tweet processado
    
    # Busca tweets usando a API do Twitter
    dados = tweepy.Cursor(api.search_tweets,
                          q=busca_palavras,
                          since_id=ultimo_tweet,
                          tweet_mode="extended",
                          lang='pt').items(1)  # Limita a 1 tweet por vez
    
    wks2 = sh.worksheet("Configs")  # Recarrega a aba de configurações
    linha = int(wks2.acell('A2').value)  # Obtém próxima linha a ser preenchida

    # Processa cada tweet encontrado (em ordem reversa para manter cronologia)
    for tweet in reversed(list(dados)):
        if tweet.id != ultimo_tweet:  # Verifica se é um novo tweet
            
            print("✍️ Preenchendo planilha...")
            
            # Preenchimento dos dados básicos do tweet
            wks.update_cell(linha, 1, str(tweet.id))  # ID do tweet
            txt = str(tweet.full_text)
            url = re.findall('https?:\/\/\S*', txt)  # Extrai URLs do texto
            
            # Separa texto e URL (se existir)
            if len(url) != 0:
                wks.update_cell(linha, 2, txt.replace(url[0], ''))  # Texto sem URL
                wks.update_cell(linha, 3, url[0])  # URL isolada
            else:
                wks.update_cell(linha, 2, txt)  # Texto completo se não houver URL
            
            # Conversão do fuso horário da data de criação (UTC para BRT)
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('America/Sao_Paulo')
            dt_string = str(tweet.created_at)
            new_dt = dt_string[:19]  # Formata para 'YYYY-MM-DD HH:MM:SS'
            utc = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S')
            utc = utc.replace(tzinfo=from_zone)
            brt = utc.astimezone(to_zone)
            
            # Continuação do preenchimento dos metadados do tweet
            wks.update_cell(linha, 4, str(brt)[:19])  # Data ajustada
            wks.update_cell(linha, 5, str(tweet.in_reply_to_status_id))  # Resposta a outro tweet
            wks.update_cell(linha, 6, str(tweet.in_reply_to_user_id))  # Resposta a usuário
            wks.update_cell(linha, 7, str(tweet.retweet_count))  # Número de retweets
            wks.update_cell(linha, 8, str(tweet.favorite_count))  # Número de likes
            time.sleep(8)  # Pausa para evitar limite de requisições

            # Dados do usuário que postou o tweet
            wks.update_cell(linha, 9, str(tweet.user.id))  # ID do usuário
            wks.update_cell(linha, 10, str(tweet.user.name))  # Nome completo
            wks.update_cell(linha, 11, str(tweet.user.screen_name))  # @username
            wks.update_cell(linha, 12, str(tweet.user.location))  # Localização do perfil
            time.sleep(8)

            # Mais informações do usuário
            wks.update_cell(linha, 13, str(tweet.user.followers_count))  # Seguidores
            
            # Conversão da data de criação do perfil para BRT
            dt_string = str(tweet.user.created_at)
            new_dt = dt_string[:19]
            utc = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S')
            utc = utc.replace(tzinfo=from_zone)
            brt = utc.astimezone(to_zone)
            
            wks.update_cell(linha, 14, str(brt)[:19])  # Data de criação do perfil
            wks.update_cell(linha, 15, str(tweet.user.verified))  # Verificação
            
            # Informações geográficas (geralmente vazias)
            data = datetime.now()  # Data atual para registro
            # Conversão da data/hora atual para BRT
            dt_string = str(data)
            new_dt = dt_string[:19]
            utc = datetime.strptime(new_dt, '%Y-%m-%d %H:%M:%S')
            utc = utc.replace(tzinfo=from_zone)
            brt = utc.astimezone(to_zone)
            
            # Preenche campos restantes
            wks.update_cell(linha, 16, str(tweet.geo))  # Geotag
            wks.update_cell(linha, 17, str(tweet.coordinates))  # Coordenadas
            wks.update_cell(linha, 18, str(tweet.place))  # Local associado
            wks.update_cell(linha, 19, str(tweet.lang))  # Idioma detectado
            wks.update_cell(linha, 20, str(brt)[:19])  # Data/hora de registro
            time.sleep(5)

            linha += 1  # Incrementa linha para próximo tweet
            wks2.update_cell(2, 1, linha)  # Atualiza próxima linha na planilha
            wks2.update_cell(2, 2, str(tweet.id))  # Atualiza último ID processado
    else:
        print("Nenhum novo tweet encontrado 😪")  # Mensagem se não houver novos tweets

    print("💤Tirando um cochilo💤")
    time.sleep(10)  # Intervalo entre verificações