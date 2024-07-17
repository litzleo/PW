
#questo modulo dovrà prendere analitiche relative alle visite a vari siti e renderle fruibili al modulo principale
#per ora fornisce staticamente dei dati relativi ad un unico sito di test
try:
    from faker import Faker
except:
    import pip
    pip.main(['install', 'faker'])
    from faker import Faker

def genera_nome_cognome():
    fake = Faker('it_IT')  # Imposta il generatore per l'Italia
    nome = fake.first_name()
    cognome = fake.last_name()
    return nome, cognome

def getPages():
    return ["palestra"]

def getKindOfUsers(page):
    if page == "palestra":
        return ['base', 'curioso','determinato']
    
def getInstructions(page, user):
    if page == "palestra":
        if user == 'base':
            return [ 
                    ['visit', 'https://litzleo.github.io/PW/siti%20di%20test/sito_palestra'], 
                    ['wait', 4000, 7000],
                    ['click', '/html/body/ul/li[3]/a', 'path'],
                    ['wait', 7000, 10000],                    
                    ['click', '/html/body/ul/li[4]/a', 'path'],
                    ['wait', 7000, 10000]                  
                    ]
        

        if user == 'curioso':
            nome, cognome = genera_nome_cognome()
            return [ 
                    ['visit', 'https://litzleo.github.io/PW/siti%20di%20test/sito_palestra'], 
                    ['wait', 4000, 7000],
                    ['click', '/html/body/ul/li[1]/a', 'path'],
                    ['wait', 8000, 10000],                    
                    ['click', '/html/body/ul/li[2]/a', 'path'],
                    ['wait', 7000, 10000],                 
                    ['click', '/html/body/ul/li[3]/a', 'path'],
                    ['wait', 7000, 10000],               
                    ['click', '/html/body/ul/li[4]/a', 'path'],
                    ['wait', 7000, 10000],
                    ['click', '/html/body/ul/li[5]/a', 'path'],
                    ['wait', 7000, 10000],
                    ['type', 'nome', 'name',nome + ' ' + cognome],
                    ['type', 'mail', 'name',nome+cognome+'@gmail.com'],
                    ['type', 'commento', 'name','bel sito'],
                    ['click', '/html/body/form/table/tbody/tr[5]/td[2]/input[5]','path'],
                    ['click', '/html/body/form/table/tbody/tr[6]/td[2]/input[3]','path']
                    ]
        
