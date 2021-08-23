#!/usr/bin/python
# coding=utf-8
import sys
import pylightxl as xl
import requests

file_path = 'G:\\pep.xlsx'


def input_from_file():
    f = open("input.txt", "r")
    file_input = f.read().decode('utf-8')
    input_unicode = u'' + file_input
    split_names(input_unicode)


def split_names(names):
    result = False
    names = names.split(' ')
    last_index = len(names) - 1
    if last_index > 0:
        if last_index >= 0:
            result = name_in_pep(' '.join(names[:last_index]), names[last_index])
        else:
            result = name_in_pep(' '.join(names[:last_index]), "")
    return result


def name_in_pep(firstname, lastname):
    found_match = False
    download_file("https://www.finanstilsynet.dk/-/media/Tal-og-fakta/PEP/PEP_listen-xlsx.xlsx")
    # readxl loader hele databasen ind
    db = xl.readxl(fn=file_path)
    worksheet = db.ws(ws=u"Nuv\xe6rende PEP'ere")
    # Alle rækker tages med fra navnekolonnerne. Vi starter lige inden kolonne-overskrifterne. Der kommer tomme felter med, men de kan ikke påvirke noget på den måde jeg tjekker
    firstnames = worksheet.col(col=3)[3:]
    lastnames = worksheet.col(col=2)[3:]

    ''' Da finanstilsynet har lavet listen så er mit umiddelbare instinkt at stole på at titlecase benyttes konsekvent, og vi skal jo svare tilbage hurtigt - så jeg ville kun sikre inputtet bliver lavet til titlecase, ikke fra excel dokumentet.
        Det giver dog bedre mening at overveje om en liste på langt under 10.000 ikke er værd at konvertere til samme case, også selvom vi prøver ikke at gøre unødvendigt tidstagende arbejde. Juridisk er det nok bedst at intet kan smutte igennem, 
        og jeg ved ikke hvilke krav låne-selskabet eller finanstilsynet laver i fremtiden. Om forkert case kunne snige sig ind. 
        Andre optimeringer der kan nævnes er at man kun '''
    names = zip(firstnames, lastnames)
    for item in names:
        correct_list_item = item[0] or item[1]
        if u'' + item[0] == firstname.title() and correct_list_item and u'' + item[1] == lastname.title():
            found_match = True
            break
    name_filled_out = firstname or lastname

    return name_filled_out and found_match


def download_file(url):
    '''Hurtig metode til at downloade filer'''
    chunk_size = 4096
    filename = file_path
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "Connection": "keep-alive",
    }
    session = requests.Session()
    '''Vi kan tilføje cookies, eller informationer, som skal bruges for at få filen. 
    Det hjælper, hvis man skal have lavet et valg på siden i fremtiden for at downloade'''
    # cookie = requests.cookies.create_cookie('COOKIE_NAME', 'COOKIE_VALUE')
    # s.cookies.set_cookie(cookie)
    with session.get(url, stream=True, headers=headers) as r:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)


if __name__ == '__main__':
    '''Her under main funktionen er mine generelle forklaringer af hvordan jeg tænkte over opgaven.
    Jeg har lavet nogle antagelser. Blandt andet at vi kan give navnene her i terminalen. 
    Inputtet kommer nok fra et andet program over netværket, hvor låne-firmaet har sendt det. 
    Opgaven er egentlig løst af funktionen name_in_pep, som returnerer boolsk værdi. Byggede så omkring at vi henter den allernyeste PEP-liste og tænkte det var bedre at vi giver et brugervenligt svar, som udvidelser.
    I selve funktionerne er der flere kommentarer omkring mine relevante antagelser og tanker omkring problemerne'''
    if len(sys.argv) > 1:
        parameter = u'' + sys.argv[1].decode('utf-8')
        print "{0}".format(split_names(parameter))

    '''Jeg understøtter ét navn fordi der er visse folk med kun et, eller kun fornavne, der kan flytte til landet. Jeg har i min løsning valgt at håndtere alle navne efter første som påkrævede. 
    Man kunne overveje en system hvor man tæller navne og hvor ens efternavn + 2 ens navne ekstra får systemet til at slå ud som mere brugbart. Jeg går ud fra at scammers ikke altid benytter alle en persons navne. 
    Hvis det her ikke er ment til scammers, så går jeg ud fra at der er styr på at det er præcist de rigtige fornavne og efternavn'''

    '''Optimeringer:
    -Man bør flytte ud fra programmet at listen opdateres, at den zippes og case ændres. Den nyeste liste kunne være blevet hentet af et andet script dagligt, zippet og fået ændret case. Så ville vi her bare pege på den lille resulterende fil. Det kører hurtigst.
    -Nu fik jeg brugt python til løsningen, hvor strings bliver behandlet så forskelligt at jeg skulle lave konverteringer mellem unicode og utf-8, og fra peplisten var kun for-/efternavnet med æøå eller andre tegn udenfor det engelske alfabet i unicode, der var i unicode. 
        Man kunne enten have undgået de konverteringers tidsforbrug ved at lave alt input med samme encoding i den dagligt bearbejdede liste, eller ved at importere på en måde, hvor alt havde samme encoding.

    Forbedringer:
    -Når man downloader filen kunne vi bruge selenium til at automatisere at vi trykker på dropdowns tager valg for at en fil bliver served til os, hvis det bliver nødvendigt i fremtiden.
    -Man kan eventuelt lave et mere brugervenligt output, der sendes videre til at blive skrevet på UI. Jeg gik udfra at vi ville have et simpelt resultat.
     Ellers ville jeg gøre ca. sådan her:
        def check_name(firstname, lastname):
            if (name_in_pep(firstname, lastname)):
                print "{0} {1} er i PEPlisten".format(firstname, lastname)
            else:
                print "{0} {1} er IKKE i PEPlisten".format(firstname, lastname)
                
    -Hvis et input skal modtages fra en banks formular, så kan der være forskellige specielle chars, der giver problemer. Der skal man lige lave et lag der sørger for at encode og decode korrekt.
    -At modtage input er den her kode heller ikke sat op til, så vidt jeg forstod var det ikke et krav. Det kunne tilføjes ved at man sætter parametre på programmet eller mere pasende laver man netværksfunktionalitet, hvor andre programmer kan sende input.
    -Man kan vælge at gå op i mellemrum og fjerne dem fra input, hvis det ikke er klaret af lån-hjemmesidens tjek, så test 5 ville returnere True.
    '''

    # Kommenter denne del ud, hvis man ikke vil se tests, men bare have resultatet fra den parameter man gav
    print "Test1 {0}".format(split_names(u"Morten Bæk") is True)
    print "Test2 {0}".format(split_names(u'Morten B\xe6k') is True)
    print "Test3 {0}".format(split_names(u"Morten") is False)
    print "Test4 {0}".format(split_names("Mette Frederiksen") is True)
    print "Test5 {0}".format(split_names("   Mette    Frederiksen ") is False)
    print "Test6 {0}".format(split_names(u"Flemming Mogensen") is False)
    print "Test7 {0}".format(split_names(u"Flamingo Mogensen") is False)
    print "Test8 {0}".format(split_names("") is False)
    print "Test9 {0}".format(split_names("         ") is False)
    print "Test10 {0}".format(split_names(" jens") is False)
    print "Test11 {0}".format(split_names(" jens     ") is False)
    print "Test12 {0}".format(split_names("/(% /(%") is False)

    '''Output ser sådan her ud med Parameteren "Morten Bæk":
        True
        Test1 True
        Test2 True
        Test3 True
        Test4 True
        Test5 True
        Test6 True
        Test7 True
        Test8 True
        Test9 True
        Test10 True
        Test11 True
        Test12 True'''
