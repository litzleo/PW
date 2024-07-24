
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
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import normalize
except:
    import pip
    pip.main(['install', 'scikit-learn'])
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.cluster import KMeans


import random

from os import listdir, chdir
from os.path import isfile, join
separator = '/' if '/' in __file__ else '\\'
path = separator.join(__file__.split(separator)[:-1])
chdir(path)

def getFiles():
    return [f for f in listdir('.'+separator+'analytics') if isfile(join('.'+separator+'analytics', f))]


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

kind_of_users = {}
def getKindOfUsers(page):
    global kind_of_users
    kind_of_users[page] = {}
    analytics = pd.read_csv('./analytics/'+page+'.csv')
    sessions = analytics.groupby('session_id')
    features = {}
    ml_input = []
    min_clicks = None
    max_clicks = None
    min_time = None
    max_time = None
    for sess, events in sessions:
        clicks = events.loc[events['action'] == 'click']
        clicks = clicks.sort_values('time')
        num_clicks = len(clicks.index)
        avg_wait = clicks.iloc[-1]['time'] / len(clicks.index)
        features[str(sess)] = [num_clicks, avg_wait]
        ml_input.append(features[str(sess)])
        if min_clicks == None or num_clicks < min_clicks:
            min_clicks = num_clicks
        if max_clicks == None or num_clicks > max_clicks:
            max_clicks = num_clicks
        if min_time == None or avg_wait < min_time:
            min_time = avg_wait
        if max_time == None or avg_wait > max_time:
            max_time = avg_wait

    def min_max_stand(val, m, M):
        if m==M:
            return 0.5
        return (val-m)/(M-m)
    def standardize(input, max_c, max_w, min_c, min_w):
        output = []
        for i in input:
            output.append([min_max_stand(i[0], min_c, max_c),   min_max_stand(i[1], min_w, max_w)])
        return output
    
    ind = 0
    for data in standardize(ml_input, max_clicks, max_time, min_clicks, min_time):
        ml_input[ind][0] = data[0]
        ml_input[ind][1] = data[1]
        ind += 1

    num_kinds = 3
    labels = ['']
    corners = []
    corners.append([0, 0])
    corners.append([1, 0])
    corners.append([1, 1])
    kinds = set()
    while '' in labels:
        labels = []
        for i in range(num_kinds):
            labels.append('')
        if num_kinds == 1:
            kind_of_users['normale'] = analytics
            return ['normale']
        try:
            kmeans = KMeans(init="k-means++", n_clusters=num_kinds, n_init=4)
            kmeans.fit(np.array(ml_input))
        except ValueError:
            num_kinds -= 1
            continue
        corners_class = []
        for i in range(3):
            corners_class.append(kmeans.predict(np.array([corners[i]]))[0])
        if num_kinds == 3:
            labels[corners_class[0]] = 'esperto'
            labels[corners_class[1]] = 'base'
            labels[corners_class[2]] = 'curioso'
        elif num_kinds == 2:
            def addClasses(c1, c2):
                if c1 == '':
                    return c2
                if c2 == '':
                    return c1
                c = [c1,c2]
                if 'esperto' in c and 'base' in c:
                    return 'frettoloso'
                if 'esperto' in c and 'curioso' in c:
                    return 'comune'
                if 'curioso' in c and 'base' in c:
                    return 'esploratore'
                return ''
            labels[corners_class[0]] = addClasses(labels[corners_class[0]], 'esperto')
            labels[corners_class[1]] = addClasses(labels[corners_class[1]], 'base')
            labels[corners_class[2]] = addClasses(labels[corners_class[2]], 'curioso')
        kinds = set()
        kinds.update(labels)
        num_kinds -= 1

    for sess in features:
        features[sess].append(labels[ kmeans.predict(np.array([features[str(sess)]]))[0] ])

    for ind, row in analytics.iterrows():
        kind = features[str(row['session_id'])][2]
        if kind in kinds:
            if kind not in kind_of_users[page]:
                kind_of_users[page][kind] = pd.DataFrame([row], columns=analytics.columns)
            else:
                kind_of_users[page][kind].loc[len(kind_of_users[page][kind])] = pd.DataFrame([row], columns=analytics.columns).iloc[0]

    return kinds
    
def getInstructions(page, user):

    def regress(values):
        num_values = len(values)
        X = np.array([x/num_values for x in range(num_values)]).reshape(-1, 1)
        y = np.array(values)

        degree = 2
        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())

        model.fit(X, y)
        return lambda v :  model.predict(np.array([[v]]))[0]

    #url,action,x,y,element,time,session_id
    df = kind_of_users[page][user]

    instructions = []

    #divido i log per sessioni, poi di una sessione random prendo l'url della prima entry in ordine temporale (l'url da cui è entrato l'utente)
    sessions = []
    for s in df.groupby('session_id'):
        s[1].sort_values('time', inplace = True)
        sessions.append(s[1])
    last_url = random.choice(sessions).iloc[0]['url']
    instructions.append(['visit', last_url])

    clicks = df.loc[df['action'] == 'click']

    #calcolo il numero di click da fare creando un modello statistico in base al numero di click di ogni sessione
    num_clicks = []
    for clicks_in_sess in clicks.groupby('session_id'):
        num_clicks.append(len(clicks_in_sess[1].index))
    num_clicks.sort()
    
    clicks_to_do = int(regress(num_clicks)(random.random()))

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
            session = df.loc[df['session_id'] == sess]
            next_urls = session.loc[session['time'] > time]
            next_url = None if next_urls.empty else next_urls.sort_values('time').iloc[0]['url']
            next_moves.append({'url':next_url, 'element':row['element']})

        waiting_times.sort()

        if len(waiting_times) > 3:
            #alleno un algoritmo di regressione per capire la distribuzione statistica dei tempi relativi ai click
            waiting_time = regress(waiting_times)
            #aggiungo un'istruzione per aspettare con una lambda che usa la distribuzione trovata e un click
            instructions.append(['wait', lambda x : max(20, waiting_time(x)) ])
        else:
            instructions.append(['wait', min(waiting_times), max(waiting_times)])

        if len(next_moves)>0:
            next_move = random.choice(next_moves)
            instructions.append(['click', next_move['element'], 'path'])
            last_url = next_move['url']

    #calcolo quanto aspettare prima di chiudere la sessione
    waiting_times = []
    for s in sessions:
        exit_time = s.iloc[-1]['time']
        last_click_time = 0
        clicks = s.loc[s['action'] == 'click']
        if not clicks.empty:
            last_click_time = clicks.iloc[-1]['time']
        waiting_times.append(exit_time-last_click_time)

    if len(waiting_times) > 3:
        #alleno un algoritmo di regressione per capire la distribuzione statistica dei tempi relativi ai click
        waiting_time = regress(waiting_times)
        #aggiungo un'istruzione per aspettare con una lambda che usa la distribuzione trovata e un click
        instructions.append(['wait', lambda x : max(20, waiting_time(x)) ])
    else:
        instructions.append(['wait', min(waiting_times), max(waiting_times)])

    return instructions
        




