#!/bin/bash

cd /Users/criphonetouch/Documents/Christian/stuck/annuairePapier
echo 'Dans la gestion des Membres, '
echo 'Rechercher les Professionnels, Membres, dont le secteur est défini (Favori Annuaire)'
echo 'Téléchargement du fichier res.partner.csv'
echo "Appuyez sur ENTREE pour déplacer le fichier dans le répertoire de génération d'annuaire"
read
set -x #echo on
mv ~/Downloads/res.partner.csv ../annuairePapier/res.partner.csv
set +x
echo
echo 'Lancer Scribus et ouvrir le fichier désiré (livret.sla, A4-150.sla, A4-140.sla)'
echo 'Exécuter le script importerPros.py'
echo 'Exporter vers la destination PDF désirée (livret.pdf, A4eurometropole.pdf, A4horsStrasbourg.pdf'
echo 'Appuyez sur ENTREE pour copier les 3 PDF sur le serveur du site'
read
set -x #echo on
sftp 275444@sftp.sd3.gpaas.net:/lamp0/web/vhosts/www.lestuck.eu/htdocs/wp-content/uploads/2019/06 <<< $'put *.pdf'
set +x
echo 'Appuyez sur ENTREE pour aller dans le répertoire des importations'
read
set -x
cd ../cyclos
set +x
echo 'Appuyez sur ENTREE pour générer les données pour le site, les applications, Cyclos'
read
set -x
./csv2umap.py ../annuairePapier/export_societe_id.csv professionnels_du_stuck.umap 
#adherents.csv
set +x
echo 'Appuyez sur ENTREE pour transférer les données des applications'
read
set -x
sftp 275444@sftp.sd3.gpaas.net:/lamp0/web/vhosts/www.lestuck.eu/htdocs/ <<< $'put professionnels_du_stuck'
set +x
echo 'Mettre les carte à jour sur le site framacarte.org avec le fichier .../stuck/cyclos/professionnels_du_stuck.umap'
