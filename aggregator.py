
#questo modulo dovrà prendere analitiche relative alle visite a vari siti e renderle fruibili al modulo principale
#per ora fornisce staticamente dei dati relativi ad un unico sito di test

import pathlib
curr_path = pathlib.Path(__file__).parent.resolve().__str__().replace('\\','/')

def getPages():
    return [curr_path+"/prova.html"]

def getKindOfUsers(page):
    if page == curr_path+"/prova.html":
        return ['skillato', 'base']
    
def getInstructions(page, user):
    if page == curr_path+"/prova.html":
        if user == 'skillato':
            return [['type', 'id', 'id', 'http://preview.redd.it/feel-old-yet-i-recreated-the-task-failed-successfully-in-v0-ymrimansgbf91.jpg?width=640&format=pjpg&auto=webp&s=dc94f365a5c7db3011220156c9f3f0bb12b8cfbe'], 
                    ['wait', 0, 1500],
                    ['click', 'button', 'tag']]
        if user == 'base':
            return [['type', 'id', 'id', 'http://preview.redd.it/feel-old-yet-i-recreated-the-task-failed-successfully-in-v0-ymrimansgbf91.jpg?width=640&format=pjpg&auto=webp&s=dc94f365a5c7db3011220156c9f3f0bb12b8cfbe'], 
                    ['wait', 1000, 5000],
                    ['click', 'button', 'tag']]