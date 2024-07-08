
#importo un paio di cose da selenium, se non ho installato selenium lo installo
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
except:
    import pip
    pip.main(['install', 'selenium'])
    from selenium import webdriver
    from selenium.webdriver.common.by import By


import time
import threading
import aggregator
import random
random.seed()

#funzione che visita la pagina selezionata, viene utilizzata da vari thread per poter visitare la stessa pagina più volte contemporaneamente
def visitPage(page, instructions):

    def getFilter(f):
        if f == 'id':
            return By.ID
        if f == 'tag':
            return By.TAG_NAME
        
    def getElement(i):
        return driver.find_element(by=getFilter(i[2]), value=i[1])

    driver = webdriver.Chrome()
    driver.get(page)

    #ciclo che esegue le varie istruzioni necessarie a navigare la pagina
    for i in instructions:
        if i[0] == 'type':
            el = getElement(i)
            el.send_keys(i[3])

        if i[0] == 'click':
            el = getElement(i)
            el.click()

        if i[0] == 'wait':
            waitTime = int(i[1] + random.random()*(i[2] - i[1]))
            time.sleep(waitTime/1000)
    driver.quit()


#Si richiede all'utente di selezionare una pagina tra quelle disponibili

pages = aggregator.getPages()

print('Siti disponibili:')
for ind in range(len(pages)):
    print(str(ind+1)+' - '+pages[ind])

pageInd = input('\nScegli un sito: ')
page = pages[int(pageInd)-1]

#Permette di scegliere quante istanze di ogni tipo di utente virtuale processare

users = aggregator.getKindOfUsers(page)

print("\nTipi di utenti: ")

for u in users:
    print(' - '+u)

comm = input('\nSeleziona quantità e tipi: ')

#vengono generati dei thread ognuno dei quali imita il comportamento di un utente

quantities = comm.split()

for q in quantities:
    userType, amount = q.split(':')
    for i in range(int(amount)):
        time.sleep(0.1)
        x = threading.Thread(target=visitPage, args=(page, aggregator.getInstructions(page, userType),))
        x.start()


