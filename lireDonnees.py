#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importerPros as pro
import sys
import os
import csv

filename=sys.argv[1]
strDir = os.path.dirname(filename)
if not strDir:
    strDir='.'

csvreader=csv.reader(file(strDir+pro.PARAMETRES))
for row in csvreader:
    """
    if row[0]=="filtreGeo":
        if len(row)>1 and '.' in row[1]:
            for iCoor in range(1,len(row), 2):
                pro.polygone.append((float(row[iCoor].strip()), float(row[iCoor+1].strip())))
        elif len(row)>1:
            pro.codesPostaux=map(str.strip, row[1:])
    """
    pro.readGlobalParameter(row)
    if row[0]=="txtBandeau":
            print row[1]
arrLines=[]#liste de lignes du fichier csv, chaque ligne est une liste de champs 
mapCol={}#table de correspondance entre les champs à importer et les numéros de colonne du fichier csv
mapCat={}#table de correspondance entre numéro de catégorie et nom de catégorie
if pro.polygone:
    print "polygone :", pro.polygone
elif pro.codesPostaux:
    if pro.bSaufCodes:
        print "Sauf codes postaux :", pro.codesPostaux
    else:
        print "codes postaux :", pro.codesPostaux

nbCat=pro.readSocietes(filename, strDir+pro.CATEGORIE, mapCat, arrLines, mapCol)
for record in arrLines: print  record[mapCol["post"]]

print "%d catégories, %d professionnels" % (nbCat, len(arrLines))
