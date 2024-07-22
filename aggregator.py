
#questo modulo dovrà prendere analitiche relative alle visite a vari siti e renderle fruibili al modulo principale
#per ora fornisce staticamente dei dati relativi ad un unico sito di test
try:
    from faker import Faker
except:
    import pip
    pip.main(['install', 'faker'])
    from faker import Faker
try:
    import numpy as np
except:
    import pip
    pip.main(['install', 'numpy'])
    import numpy as np
try:
    import pandas as pd
except:
    import pip
    pip.main(['install', 'pandas'])
    import pandas as pd
try:
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import make_pipeline
except:
    import pip
    pip.main(['install', 'scikit-learn'])
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import make_pipeline


import random

from os import listdir
from os.path import isfile, join
import os

def getFiles():
    return [f for f in listdir('./analytics') if isfile(join('./analytics', f))]


def genera_nome_cognome():
    fake = Faker('it_IT')  # Imposta il generatore per l'Italia
    nome = fake.first_name()
    cognome = fake.last_name()
    return nome, cognome

def getPages():
    pages = []
    for a in getFiles():
        pages.append(a[:-4])
    return pages

def getKindOfUsers(page):
    return ['base']
    
def getInstructions(page, user):
    #url,action,x,y,element,time,session_id
    df = pd.read_csv('./analytics/'+page+'.csv')

    '''ind = random.randrange(0, df.shape[0]-1)
    random_user = df[df['session_id'] == df.at[ind,'session_id']]
    instructions = []
    last_click = 0
    to_visit = True

    for index, row in random_user.iterrows():
        if to_visit:
            instructions.append(['visit', row['url']])
            to_visit = False
        if row['action'] == 'click':
            diff = int(row['time']) - last_click
            last_click = int(row['time'])
            instructions.append(['wait', diff, diff])
            instructions.append(['click', row['element'], 'path'])
    last_time = random_user.loc[random_user.index[-1], 'time']
    instructions.append(['wait', last_time-last_click, last_time-last_click])
            
    return instructions'''

    instructions = []

    #divido i log per sessioni, poi di una sessione random prendo l'url della prima entry in ordine temporale (l'url da cui è entrato l'utente)
    sessions = []
    for s in df.groupby('session_id'):
        s[1].sort_values('time', inplace=True)
        sessions.append(s[1])
    last_url = random.choice(sessions).iloc[0]['url']
    instructions.append(['visit', last_url])

    clicks = df.loc[df['action'] == 'click']

    #calcolo il numero di click da fare creando un modello statistico in base al numero di click di ogni sessione
    num_clicks = []
    for clicks_in_sess in clicks.groupby('session_id'):
        num_clicks.append(len(clicks_in_sess[1].index))
    num_clicks.sort()
    X = np.array([x/len(num_clicks) for x in range(len(num_clicks))]).reshape(-1, 1)
    y = np.array(num_clicks)

    degree = 2
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())

    model.fit(X, y)
    clicks_to_do = int(model.predict(np.array([[random.random()]]))[0])

    for i in range(clicks_to_do):
        #prendo gli eventi dei click fatti al precedente url
        from_last_url = clicks.loc[clicks['url'] == last_url]
        if from_last_url.empty:
            break
        #calcolo quanto tempo è passato tra i click prima e quelli appena selezionati
        #ottengo anche la lista di 
        waiting_times = []
        next_moves = []
        for index, row in from_last_url.iterrows():
            sess = row['session_id']
            time = row['time']
            clicks_in_sess = clicks.loc[clicks['session_id'] == sess]
            prev_clicks = clicks_in_sess.loc[clicks_in_sess['time'] < time]
            if prev_clicks.empty:
                waiting_times.append(time)
            else:
                waiting_times.append(time - prev_clicks.iloc[-1]['time'])
            
            #colleziono tutte le possibilità di click e dove mi portano
            sessions = df.loc[df['session_id'] == sess]
            next_urls = sessions.loc[sessions['time'] > time]
            next_url = None if next_urls.empty else next_urls.sort_values('time').iloc[0]['url']
            next_moves.append({'url':next_url, 'element':row['element']})

        waiting_times.sort()

        num_dati = len(waiting_times)

        if num_dati > 3:
            #alleno un algoritmo di regressione per capire la distribuzione statistica dei tempi relativi ai click
            X = np.array([x/num_dati for x in range(num_dati)]).reshape(-1, 1)
            y = np.array(waiting_times)

            degree = 2
            model = make_pipeline(PolynomialFeatures(degree), LinearRegression())

            model.fit(X, y)

            #aggiungo un'istruzione per aspettare con una lambda che usa la distribuzione trovata e un click
            instructions.append(['wait', lambda x : max(20, model.predict(np.array([[x]]))[0] ) ])
        else:
            instructions.append(['wait', min(waiting_times), max(waiting_times)])

        if len(next_moves)>0:
            next_move = random.choice(next_moves)
            instructions.append(['click', next_move['element'], 'path'])
            last_url = next_move['url']
    
    return instructions
        




