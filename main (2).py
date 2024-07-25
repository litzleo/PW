try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.ie.service import Service as IEService
    from selenium.webdriver.safari.service import Service as SafariService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager, IEDriverManager
except:
    import pip
    pip.main(['install', 'selenium', 'webdriver-manager'])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.ie.service import Service as IEService
    from selenium.webdriver.safari.service import Service as SafariService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager, IEDriverManager
   
try:
    from faker import Faker
except:
    import pip
    pip.main(['install', 'faker'])
    from faker import Faker

import time
import threading
import aggregator
import random
random.seed()

# funzione che visita la pagina selezionata, viene utilizzata da vari thread per poter visitare la stessa pagina più volte contemporaneamente
def visitPage(instructions, browser):

    fake = Faker('it_IT')

    def getFilter(f):
        if f == 'id':
            return By.ID
        if f == 'tag':
            return By.TAG_NAME
        if f == 'path':
            return By.XPATH
        if f == 'name':
            return By.NAME

    def getElement(i):
        return driver.find_element(by=getFilter(i[2]), value=i[1])

    # Inizializzazione del driver in base al browser selezionato
    driver = None
    if browser == 'Chrome':
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser == 'Firefox':
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    elif browser == 'Edge':
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    elif browser == 'IE':
        driver = webdriver.Ie(service=IEService(IEDriverManager().install()))
    else:
        print("Browser non supportato")
        return

    driver.implicitly_wait(5)

    # ciclo che esegue le varie istruzioni necessarie a navigare la pagina
    for i in instructions:
        if i[0] == 'type':
            el = getElement(i)
            el.send_keys(i[3])

        if i[0] == 'click':
            el = getElement(i)
            el.click()
            if el.tag_name == 'input' and el.get_attribute('type') == 'text' and el.get_attribute('name') in ['name', 'Name', 'nome', 'Nome']:
                el.send_keys(fake.name())

        if i[0] == 'wait':
            waitTime = 0
            if len(i) == 3:
                waitTime = int(i[1] + random.random()*(i[2] - i[1]))
            else:
                waitTime = i[1](random.random())
            time.sleep(waitTime/1000)

        if i[0] == 'visit':
            driver.get(i[1])

    driver.quit()

def isValidPage(pageId, limit):
    try:
        id = int(pageId)
        return id > 0 and id <= limit
    except:
        return False
    
def isValidUserQuantityList(comm, u):
    s = ''
    if comm == '':
        return False
    users = list(u)
    for i in range(len(users)):
        users[i] = users[i].lower()

    state = 'user'
    num = False
    user = ''
    quantity = 0
    for c in comm.lower():
        ascii = ord(c)
        if state == 'user':
            if ascii >= ord('a') and ascii <= ord('z'):
                user += c
            elif c == ':':
                if user not in users:
                    return False
                users.remove(user)
                s += user + ':'
                user = ''
                state = 'quantity'
                num = False
            elif c == ' ':
                pass
            else:
                return False
        elif state == 'quantity':
            if ascii >= ord('0') and ascii <= ord('9'):
                quantity *= 10
                quantity += int(ascii)
                s += c
                num = True
            elif c == ' ':
                if num:
                    state = 'user'
                    s += ' '
            elif c != '\0':
                return False
    return s

def beginBrowsing(comm, page, browser):
    quantities = comm.split()

    # vengono generati dei thread ognuno dei quali imita il comportamento di un utente
    for q in quantities:
        userType, amount = q.split(':')
        for i in range(int(amount)):
            time.sleep(0.1)
            x = threading.Thread(target=visitPage, args=(aggregator.getInstructions(page, userType), browser))
            x.start()

# Si richiede all'utente di selezionare una pagina tra quelle disponibili

pages = aggregator.getPages()


if __name__ == "__main__":

    error_message = ' (input invalido, riprova)'

    print('Siti disponibili:')
    for ind in range(len(pages)):
        print(str(ind + 1) + ' - ' + pages[ind])

    mx = '\nScegli un sito (specificandone solo il numero)'
    pageInd = 0
    firstLoop = True
    while(not isValidPage(pageInd, len(pages))):
        pageInd = input(mx + ': ')
        if firstLoop:
            mx += error_message
        firstLoop = False

    page = pages[int(pageInd) - 1]

    # Permette di scegliere quante istanze di ogni tipo di utente virtuale processare

    users = aggregator.getKindOfUsers(page)

    print("\nTipi di utenti: ")

    for u in users:
        print(' - ' + u)

    comm = ''
    mx = '\nSeleziona tipi e quantità (usa il formato "tipoutente:quantità tipoutente:quantità")'
    firstLoop = True
    invalidInput = True
    while(invalidInput):
        comm = input(mx + ': ')
        comm = isValidUserQuantityList(comm.rstrip(), users)
        if(comm != False):
            invalidInput = False
        if firstLoop:
            mx += error_message
        firstLoop = False

    # Permette di scegliere il browser

    browsers = ["Chrome", "Firefox", "Edge", "IE"]

    print("\nSeleziona un Browser: ")

    for ind in range(len(browsers)):
        print(str(ind + 1) + ' - ' + browsers[ind])

    mx = '\nScegli un browser (specificandone solo il numero)'
    browserInd = 0
    firstLoop = True
    while(not isValidPage(browserInd, len(browsers))):
        browserInd = input(mx + ': ')
        if firstLoop:
            mx += error_message
        firstLoop = False

    browser = browsers[int(browserInd) - 1]

    beginBrowsing(comm, page, browser)