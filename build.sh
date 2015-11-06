#!/bin/bash

APPNAME="webapp"
VERSION=$(cat ./version|awk '{print $1}')

echo "======================================================="
echo "Create build directory"
rm -rf build
mkdir -p build
echo "OK"

echo "Copy main application file"
mkdir -p build/usr/bin
cp webapp.py build/usr/bin/webapp
chmod +x build/usr/bin/webapp
echo "OK"

echo "Build locale files"
mkdir -p build/usr/share
po/autogen.sh
cp -r po/locale build/usr/share
echo "OK"

echo "Copy application data files"
cp -r data build/usr/share/webapp
echo "OK"

echo "Copy application shortcuts"
mkdir -p build/etc/xdg/menus/applications-merged/
cp data/webapp.menu build/etc/xdg/menus/applications-merged

mkdir -p build/usr/share/desktop-directories/
cp data/webapp.directory build/usr/share/desktop-directories

mkdir -p build/usr/share/applications
cp data/webapp.desktop build/usr/share/applications

mkdir -p build/usr/share/icons
cp data/wa-logo.png build/usr/share/icons
echo "OK"
#=========================================

if [ $1 = "install"  ]
then
    echo $APPNAME-$VERSION "installation"
    if [ $UID != 0  ]
    then
        echo "You must be root"
        echo "Error!!"
    else
        cp -r build/* /
        rm -rf build
        echo "Installation complete"
    fi
else
echo "Make archive distribution"
rm -rf dist
mkdir -p dist
cd build
tar -cf ../dist/$APPNAME-$VERSION.tar.gz usr
echo $APPNAME-$VERSION " build complete!!!"
fi
echo "======================================================="