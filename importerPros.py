#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ABOUT THIS SCRIPT:

Importation des données pour remplir l'annuaire des pros

Le fichier d'annuaire vide doit être ouvert
La police Font Awesome doit être installée (Préférences > Polices > Chemins additionnels > Ajouter... le répertoire de la police).

############################

LICENSE:

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

Author: Christian Bonnin

please report bugs to: appli@lestuck.eu
"""
from __future__ import division
import sys

__version__=1.1


try:
    # Please do not use 'from scribus import *' . If you must use a 'from import',
    # Do so _after_ the 'import scribus' and only import the names you need, such
    # as commonly used constants.
    import scribus
except ImportError,err:
    print "This Python script is written for the Scribus scripting interface."
    #print "It can only be run from within Scribus."
    #sys.exit(1)

#########################
# YOUR IMPORTS GO HERE  #
#########################
import csv
import os
import datetime
import re
import time
import locale

#PREFIX="*"
QRCODE="/qrcode.png"
LOGO="/logo.png"
SMALL_LOGO="/petitLogo.png"
SOCIETE= "/export_societe.csv"
CATEGORIE= "/categorie.csv"
filParam="/parametres.csv"
ENCODING= "utf8"  #encodage du fichier provenant de Odoo
DESC_MAX_LEN=80
NB_TXT=8
SCRIBUS_BUG=True
polygone=[] #Filtrage des pros par polygone géographique
codesPostaux=[] #Filtrage des pros par une liste de codes postaux
bSaufCodes=False
bLivret=False
locale.setlocale(locale.LC_TIME, "fr_FR")

def toUnicode(str):
	return unicode(str.replace('"','\\"').replace("\t",""), ENCODING)

def checkValue(c, m, y, k):
    """returns true if the cmyk values are between 0 and 255"""
    MINVAL=0
    MAXVAL=255
    valueOk=True
    for val in c, m, y, k:
        if val >=MINVAL and val <=255:
            pass
        else:
            valueOk=False
        
    return valueOk
"""get colors and other parameters from csv file and return a list with color name and cmyk 255 values""" 
def getColorsFromCsv(filename, idxPro):
    csvreader=csv.reader(file(filename))
    csvcolors=[]
    for row in csvreader:
        if len(row)>1 and idxPro==1:
          name=row[0].strip()
          if len(row)>4 and name[0:7]=='couleur': 
            c=int(row[1] )* 2.55
            c=int(c)
            m=int(row[2] )* 2.55
            m=int(m)
            y=int(row[3] )* 2.55
            y=int(y)
            k=int(row[4] )* 2.55
            k=int(k)        
            if checkValue(c, m, y, k) ==False:
                scribus.messageBox("importerPros", "At least one CMYK value in your csv file is not correct \n(must be between 0 and 100)\nAborting script - nothing imported.",  icon=scribus.ICON_WARNING)
                sys.exit()

            color=(name, c, m, y, k)
            csvcolors.append(color)
          elif name[0:3]=='txt':
            if scribus.objectExists(name):
                scribus.setText(row[1].replace("\\n","\n"), name)
                nbContent=scribus.getTextLength(name)
                scribus.selectText(0, nbContent, name)
                scribus.setStyle("style"+name[3:], name)
            else:
                scribus.messageBox("Objet non trouvé","Aucun objet correspondant au paramètre %s n'a été trouvé dans le document vierge"%name)

        readGlobalParameter(row)

    return csvcolors
""" Lecture des paramètres généraux (hors couleurs et zones de texte) """
def readGlobalParameter(row):
    global polygone, codesPostaux, bSaufCodes, bLivret, NB_TXT
    if len(row)>0:
        # log(str(len(row))+ " parametres : "+str(row)+"\n")
        if row[0]=="filtreGeo":
            if len(row)>1 and '.' in row[1]: #Coordonnées géographiques : latitude, longitude
                for iCoor in range(1,len(row), 2):
                    polygone.append((float(row[iCoor].strip()), float(row[iCoor+1].strip())))
            elif len(row)>1: # Codes postaux
                if row[1].strip()=="sauf":
                    codesPostaux=map(str.strip, row[2:])
                    bSaufCodes=True
                else:
                    codesPostaux=map(str.strip, row[1:])
        elif row[0]=="livret" and (len(row)<=1 or row[1]):
            bLivret=True

def getColorDict():
    """get the colors that already exist from the opened Document and return a dictionary"""
    colornames = scribus.getColorNames()
    scribus.progressTotal(len(colornames))
    colordict={}
    for name in colornames:
        colordict[name]=None

    return colordict #we can ask this dict if the color already exists
        
def importParametres(filename, idxPro):
    """check if colors exists and import"""
    log("importParametres: "+filename+"\n")
    colordict=getColorDict()
    colorlist=getColorsFromCsv(filename, idxPro)
    if idxPro==1:
      for color in colorlist:
        name=color[0]
        c=color[1]
        m=color[2]
        y=color[3]
        k=color[4]
        #while colordict.has_key(name): name = PREFIX+name# check if color already exists - then add PREFIX to name
        scribus.defineColor(name, c, m, y, k)

    return len(colorlist)

"""importation de toutes les données à insérer comme texte ou comme images ou comme couleurs dans le document .sla de Scribus"""
def importData(filename, idxPro):
    (nbLogo, nbImg, nbChange, nbPro, nbCol, nbCat) =(0,0,0,0,0,0)

    global filParam
    strDir = os.path.dirname(filename)
    if os.path.isfile(filParam):
            nbCol=importParametres(filParam, idxPro)

    if idxPro==1: 
        if os.path.isfile(strDir+LOGO) and scribus.objectExists("imgLogo"): #Logo de la première page lorsque le document est entièrement plié en huit
            scribus.loadImage(strDir+LOGO, "imgLogo")
            nbLogo+=1

        if os.path.isfile(strDir+LOGO) and scribus.objectExists("imgSmallLogo"): #Petit logo de la dernière page lorsque le document est entièrement plié en huit
            scribus.loadImage(strDir+SMALL_LOGO, "imgSmallLogo")
            nbLogo+=1

        if os.path.isfile(strDir+QRCODE) and scribus.objectExists("imgQrcode"): #QR code de la dernière page
            scribus.loadImage(strDir+QRCODE, "imgQrcode")
            nbImg=1

        for img in range(1,5):
            if os.path.isfile(strDir+("/image%d.png"%img)): #images facultatives
                scribus.loadImage(strDir+("/image%d.png"%img), "img%d"%img)
                nbImg+=1
                
            
    datJ=datetime.date.today() # Date de l'importation comme date de l'annuaire
    scribus.setText(datJ.strftime("%B %Y"), "txtDate")
    scribus.setStyle("styleDate","txtDate")
    if os.path.isfile(filename):  #Sociétés de l'annuaire et les noms des catégories
        (nbChange, nbPro, nbCat)=importSocietes(filename, strDir+CATEGORIE, idxPro)

    return (nbLogo, nbImg, nbCol, nbChange, nbPro, nbCat)
# Ouverture et lecture des fichiers de données et des catégories 
def readSocietes(filename, fileCat, mapCat, arrLines, mapCol):
    bHeader=True
    nbCat=0
    with open(fileCat,'rb') as fCsv:#Lecture du fichier CSV des catégories
        reader=csv.reader(fCsv)
        for line in reader:
            if bHeader:
                bHeader=False
            elif len(line)>0:
                # mapCat[int(line[1])]=line[0]
                nbCat+=1
    
    bHeader=True
    iLig=0
    with open(filename,'rb') as fCsv:#Lecture du fichier CSV des pros
        reader=csv.reader(fCsv)
        for line in reader:
            iLig+=1
            if bHeader:
                bHeader=False
                iCol=0
                for colName in line:#table de correspondance des colonnes du fichier des pros
                    if "name" == colName.lower(): mapCol["nom"]=iCol
                    elif "street" == colName.lower(): mapCol["adr"]=iCol
                    elif "zip" in colName.lower(): mapCol["post"]=iCol
                    elif "city" in colName.lower(): mapCol["ville"]=iCol
                    elif "email" in colName.lower(): mapCol["mail"]=iCol
                    elif "phone_pro" in colName.lower(): mapCol["tel"]=iCol
                    elif "industry_id/name" == colName.lower(): mapCol["cat"]=iCol
                    elif "detailed_activity" in colName.lower(): mapCol["desc"]=iCol
                    elif "currency_exchange" in colName.lower(): mapCol["chg"]=iCol
                    elif "latitude" in colName.lower(): mapCol["lat"]=iCol
                    elif "longitude" in colName.lower(): mapCol["lng"]=iCol
                    iCol+=1

            elif len(line)>0 and estSelectionnee(line, mapCol, iLig):
                arrLines.append(line)
                try: 
                    strCat=line[mapCol["cat"]]
                    # i=int(strCat)
                    # if not i in mapCat:     
                    #     scribus.messageBox("Erreur","le domaine de la ligne %d n'est pas dans la liste des catégories (%s)"%(iLig, line))
                        
                except:
                    log(("domaine incorrect ligne %d : %s\n")%(iLig, line)) 
                    scribus.messageBox( "Erreur","le domaine de la ligne %d est incorrect (%s):\n%s" %(iLig, strCat, line))
                    sys.exit()

    arrLines.sort(key=lambda line: (line[mapCol["cat"]], line[mapCol["nom"]])) #classement par nom de categorie puis nom
    return nbCat
#Vrai si le lieu est à l'intérieur du polygone ou dans la liste des codes postaux
def estSelectionnee(line, mapCol, iLig):
    return (not polygone and not codesPostaux) \
            or (polygone and inside_polygon(line[mapCol["lat"]].strip(), line[mapCol["lng"]].strip(), polygone, iLig) ) \
            or (codesPostaux and ((not bSaufCodes and line[mapCol["post"]].strip() in codesPostaux) or (bSaufCodes and not line[mapCol["post"]].strip() in codesPostaux)))

"""
Return True if a coordinate (x, y) is inside a polygon defined by a list of verticies [(x1, y1), (x2, x2), ... , (xN, yN)].  
Reference: http://www.ariel.com.au/a/python-point-int-poly.html
"""
def inside_polygon(x, y, points, iLig):
    if not x or not y:
        print "Mauvaises coordonnées à la ligne %d"%iLig
        return True

    x,y = float (x), float (y)
    n = len(points)
    inside = False
    p1x, p1y = points[0]
    for i in range(1, n + 1):
        p2x, p2y = points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# Ouverture et lecture des fichiers de données et des catégories puis importation dans Scribus
def importSocietes(filename, fileCat, iPro):
    arrLines=[]#liste de lignes du fichier csv, chaque ligne est une liste de champs 
    mapCol={}#table de correspondance entre les champs à importer et les numéros de colonne du fichier csv
    mapCat={}#table de correspondance entre numéro de catégorie et nom de catégorie
    nbCat=readSocietes(filename, fileCat, mapCat, arrLines, mapCol)
    (nbChg, nbPro)=(0,0)
    numPro=1
    while scribus.getTextLength("txtPros%d" % numPro)>0 and numPro<=NB_TXT:
        numPro+=1
    if iPro==1 and scribus.objectExists("txtBureauxChange"):
        scribus.deleteText("txtBureauxChange")

    scribus.progressTotal(len(arrLines))
    strPro="txtPros%d"%numPro
    scribus.statusMessage("Remplissage du cadre de texte %s..."%strPro)
    bFirstPro=True
    strCat="#"
    for record in arrLines:#Pour chaque pro
        # log("nbPro=%d\n"%nbPro)
        if strCat != record[mapCol["cat"]]:#nouvelle categorie
            strCat=record[mapCol["cat"]]
            bNewCat=True
        else:
            bNewCat=False

        nbPro+=1
        if nbPro<iPro:#déjà importé à l'exécution précédente
            continue
        try:
          scribus.progressSet(nbPro)
          if record[mapCol["chg"]]=="True" and scribus.objectExists("txtBureauxChange"):
            try:
                nbCarBureau=scribus.getTextLength("txtBureauxChange")
                appendText(u"● "+toUnicode(record[mapCol["nom"]])+"\n","styleChangeTitre","txtBureauxChange")
                appendText(toUnicode(record[mapCol["adr"]].replace("\\n"," - "))+"\n","styleChangeAdresse","txtBureauxChange")
                appendText(record[mapCol["post"]]+" "+toUnicode(record[mapCol["ville"]].upper()+"\n"),"styleChangeAdresse","txtBureauxChange")
                nbChg+=1
            except Exception as ex:
                scribus.messageBox( "Erreur","Une erreur est survenue sur ce bureau de change: \n%s\n\n%s" %(record, str(ex)))
                sys.exit()
          else :
            nbCarBureau=0

          nbCar=scribus.getTextLength(strPro)
          if bNewCat or bFirstPro:    
            if bFirstPro and not bNewCat:
                appendText(toUnicode(strCat+" (suite)")+"\n","styleProCatSuite",strPro)
            else:
                appendText(toUnicode(strCat)+"\n","styleProCat",strPro)

          bFirstPro=False
          appendText(u"● "+toUnicode(record[mapCol["nom"]])+"\n","styleProTitre",strPro)
          if record[mapCol["chg"]]=="True" :
            appendText(u"\n","styleProBureau",strPro) #icone du bureau de change en police FontAwesome
         
          appendText(processDesc(toUnicode(record[mapCol["desc"]]))+"\n","styleProDesc",strPro)
          if bLivret:
              strAdr=toUnicode(record[mapCol["adr"]].replace("\\n"," - "))+" - " + toUnicode(record[mapCol["post"]])+" "
              strAdr+=processDesc(toUnicode(record[mapCol["ville"]].upper()))
              if record[mapCol["tel"]].strip():
                  strAdr+=" ("+toUnicode(record[mapCol["tel"]].strip().replace(" ","\xC2\xA0"))+")\n" #numéro de téléphone insécable
              else:
                  strAdr+="\n"

              appendText(strAdr, "styleProAdresse", strPro)
          else:
            appendText(toUnicode(record[mapCol["adr"]].replace("\\n"," - "))+"\n","styleProAdresse",strPro)
            appendText(toUnicode(record[mapCol["post"]])+" "+processDesc(toUnicode(record[mapCol["ville"]]).upper())+"\n","styleProAdresse",strPro)
            if record[mapCol["tel"]].strip(): 
                appendText(processTelephone(record[mapCol["tel"]])+"\n","styleProAdresse",strPro)


          if scribus.textOverflows(strPro, nolinks=1): #effacement du paragraphe de pro tronqué et du bureau de change en double
            scribus.selectText(nbCar, scribus.getTextLength(strPro)-nbCar, strPro)
            scribus.deleteText(strPro)
            if nbCarBureau:
                scribus.selectText(nbCarBureau, scribus.getTextLength("txtBureauxChange")-nbCarBureau, "txtBureauxChange")
                scribus.deleteText("txtBureauxChange")

            #log("Cadre rempli : le cadre de texte %s est plein à la ligne %d\n" % (strPro, nbPro))
            break
        except Exception as exc:
                scribus.messageBox( "Erreur","Une erreur est survenue sur ce professionnel: \n%s\n\n%s" %(record, str(exc)))
                sys.exit()
    
        
    return (nbChg, nbPro, nbCat)
#traitement du champ description (et ville)
def processDesc(strDesc):
    strRet=strDesc.replace('&#39;',"'").replace('&rsquo;',"'").replace('&nbsp;',' ').replace('&laquo;','"').replace('&raquo;','"').replace('&quot;','"').replace('&amp;',u'&').replace('&sup2;',u'²')
    strRet=strRet.replace('&eacute;',u"é").replace('&egrave;',u'è').replace('&ecirc;',u'ê').replace('&euml;',u'ë').replace('&agrave;',u'à').replace('&acirc;',u'â').replace('&icirc;',u'î').replace('&iuml;',u'ï').replace('&ocirc;',u'ô').replace('&ucirc;',u'û').replace('&ugrave;',u'ù').replace('&uuml;',u'ü').replace('&ccedil;',u'ç')
    strRet=strRet.replace('&Eacute;',u"É").replace('&Egrave;',u'È').replace('&Ecirc;',u'Ê').replace('&Euml;',u'Ë').replace('&Agrave;',u'À').replace('&Acirc;',u'Â').replace('&Icirc;',u'Î').replace('&Iuml;',u'Ï').replace('&Ocirc;',u'Ô').replace('&Ucirc;',u'Û').replace('&Ugrave;',u'Ù').replace('&Uuml;',u'Ü').replace('&Ccedil;',u'Ç')
    strRet=re.sub(r'^\\n','',strRet) #Suppression d'un éventuel retour chariot initial
    strRet=re.sub(r'[.!;\\].*','',strRet) #tronqué avant le premier point ou retour chariot
    if len(strRet)>DESC_MAX_LEN: #si encore trop long, la fin est remplacé par des points de suspension après la fin du mot
        strRet=strRet[0:DESC_MAX_LEN] + re.sub(r'[ .,!;].*','...', strRet[DESC_MAX_LEN:])

    return strRet

#Traitement du numéro de téléphone
def processTelephone(strTel):
    strTel=strTel.replace("+33(0)","0")
    if len(strTel)==10 and not " " in strTel:
        strTel=strTel[0:2]+" "+strTel[2:4]+" "+strTel[4:6]+" "+strTel[6:8]+" "+strTel[8:]

    return strTel

#Ajout d'une chaîne de caractères à la fin d'un cadre de texte dans Scribus
def appendText(strTxt, strStyle, strName):
    #log(strName+"<- "+strTxt) 
    scribus.setStyle(strStyle, strName)
    scribus.insertText(strTxt, -1, strName)

#Ecriture d'information de debug dans un fichier temporaire
def log(strLog):
    with open("/tmp/scribusLog.txt", "a") as dbg: dbg.write(strLog) 

def main(argv):
    """Main method"""
    global filParam
    if not scribus.haveDoc(): #do we have a doc?
        scribus.messageBox("importerPros", "Le fichier d'annuaire vierge doit être ouvert pour importer les données")
        sys.exit()
    else:
        filename=scribus.fileDialog("Fichier de données à importer",  "Données (*.csv)", "", False) # Images (*.png *.xpm *.jpg)
        if not filename : sys.exit()
        filParam=scribus.fileDialog("Fichier de paramètres à utiliser",  "Données (*.csv)", filParam, False) 
        if not filParam : sys.exit()
        else:
            try:
                strNum=scribus.getText("txtNumPro") #récupération du dernier numéro de professionnel qui a été écrit dans une zone invisible
                if scribus.messageBox("Importation des données", 
                            "Importation du fichier de données : %s \net des fichiers suivants issus du même répertoire : \n.%s, \n.%s, \n.%s, \n.%s, \n.%s\nNuméro du professionnel à partir duquel le prochain cadre de texte vide sera rempli : %s" % (filename, QRCODE, LOGO, SMALL_LOGO, CATEGORIE, filParam, strNum), scribus.ICON_INFORMATION,scribus.BUTTON_CANCEL, scribus.BUTTON_OK)==scribus.BUTTON_CANCEL:
                    sys.exit()
                else:
                  nbPro=1
                  iExec=0
                  while iExec < NB_TXT:
                    idxPro=nbPro #int(strNum)
                    (nbLogo, nbImg, nbCol, nbChange, nbPro, nbCat)=importData(filename, idxPro)
                    scribus.docChanged(True)
                    #scribus.setText( str(nbPro), "txtNumPro")
                    #scribus.setStyle("styleProTitre", "txtNumPro")
                    if SCRIBUS_BUG and iExec<NB_TXT-1 and scribus.messageBox("importerPros", "%d logos importés \n%d images importées \n%d couleurs importées \n%d bureaux de change \n%d professionnels \n%d catégories\n\nContinuer ?" % (nbLogo, nbImg, nbCol, nbChange, nbPro, nbCat), scribus.ICON_INFORMATION,scribus.BUTTON_CANCEL, scribus.BUTTON_OK)==scribus.BUTTON_CANCEL:
                        sys.exit()
                    else:
                        iExec+=1
            except Exception as ex:
                scribus.messageBox("importerPros", "Erreur : "+str(ex), icon=scribus.ICON_WARNING)
                sys.exit()
            


def main_wrapper(argv):
    """The main_wrapper() function disables redrawing, sets a sensible generic
    status bar message, and optionally sets up the progress bar. It then runs
    the main() function. Once everything finishes it cleans up after the main()
    function, making sure everything is sane before the script terminates."""
    try:
        #scribus.statusMessage("Running script...")
        scribus.progressReset()
        main(argv)
    finally:
        # Exit neatly even if the script terminated with an exception,
        # so we leave the progress bar and status bar blank and make sure
        # drawing is enabled.
        if scribus.haveDoc() > 0:
            scribus.setRedraw(True)
        scribus.statusMessage("")
        scribus.progressReset()

# This code detects if the script is being run as a script, or imported as a module.
# It only runs main() if being run as a script. This permits you to import your script
# and control it manually for debugging.
if __name__ == '__main__':
    main_wrapper(sys.argv)
