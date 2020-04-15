#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importerPros as pro
import sys
import os
import csv

if len(sys.argv)<2:
	print "Test d'un fichier de données avec son paramétrage\n"
	print "Utilisation :",sys.argv[0], "<CSV data file> [<CSV parameter file>]\n"
	exit(0)

filename=sys.argv[1]
strDir = os.path.dirname(filename)
if not strDir:
    strDir='.'

paramFile=strDir+pro.filParam
if len(sys.argv)>2:
    paramFile=sys.argv[2]

csvreader=csv.reader(file(paramFile))
for row in csvreader:
    pro.readGlobalParameter(row)
    if len(row)>1 and row[0]=="txtBandeau":
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
for record in arrLines: print  record[mapCol["nom"]]

print "%d catégories, %d professionnels" % (nbCat, len(arrLines))
