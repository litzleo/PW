
#questo modulo dovrà prendere analitiche relative alle visite a vari siti e renderle fruibili al modulo principale
#per ora fornisce staticamente dei dati relativi ad un unico sito di test
try:
    from faker import Faker
except:
    import pip
    pip.main(['install', 'faker'])
    from faker import Faker
try:
    import pandas as pd
except:
    import pip
    pip.main(['install', 'pandas'])
    import pandas as pd

import random

from os import listdir
from os.path import isfile, join
import os

def getFiles():
    os.chdir('C:/Users/Utente14/Desktop')
    return [f for f in listdir('./analitics') if isfile(join('./analitics', f))]


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
    os.chdir('C:/Users/Utente14/Desktop')
    df = pd.read_csv('./analitics/'+page+'.csv')

    ind = random.randrange(0, df.shape[0]-1)
    random_user = df[df["session_id"] == df.at[ind,"session_id"]]
    instructions = []
    last_click = 0
    to_visit = True

    for row in random_user.itertuples():
        if to_visit:
            instructions.append(['visit', row[1]])
            to_visit = False
        if row[2] == "click":
            diff = int(row[6]) - last_click
            last_click = int(row[6])
            instructions.append(['wait', diff, diff])
            instructions.append(['click', row[5], 'path'])
            
    return instructions
