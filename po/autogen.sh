#!/bin/bash
#
# Autogenerate .mo files for project
#
# Usage: fill $encondings variable below for nesessary languages and add all needed filenames to be translated in POTFILES.in
#
#
# (C)2015 Kamensky Vladimir (info@mastersoft24.ru, megalion73@inbox.ru)
#

APPNAME=webapp

#list of space separated  languages for translations. 
encodings="ru en_US de"


ABSOLUTE_FILENAME=`readlink -e "$0"`
DIRECTORY=`dirname "$ABSOLUTE_FILENAME"`
_dir=$DIRECTORY
echo $_dir
cd $_dir


xgettext --files-from=POTFILES.in --directory=.. --output=messages.pot

	# change encoding to UTF-8
	cat messages.pot |sed  's/CHARSET/UTF-8/g' > PKGB 
	mv PKGB messages.pot



for loc in $encodings
do

	echo "Generate "$loc.mo
		if [ -a $loc.po ]
		then
			msgmerge --update --no-fuzzy-matching --backup=off $loc.po messages.pot

		else
			msginit --no-translator --locale=$loc --input=messages.pot
		fi

	mkdir -p locale/$loc/LC_MESSAGES
	msgfmt $loc.po -o locale/$loc/LC_MESSAGES/$APPNAME.mo

done


