#!/bin/bash

APPNAME="webapp"
VERSION=$(cat ./version|awk '{print $1}')

echo "======================================================="
echo ""
echo "WebApp build script started"
echo ""
echo "Usage: build.sh - make application archive"
echo "       build.sh install - install application (need root privilege)"
echo ""
echo ""

if [ $1 == "" ]
then
    echo "Current mode is BUILD"
else
    echo "Current mode is INSTALL"
fi

echo "======================================================="
echo ""


echo "Create build directory"
rm -rf build
mkdir -p build
echo "OK"
echo ""

echo "Copy main application file"
mkdir -p build/usr/bin
cp webapp.py build/usr/bin/webapp
chmod +x build/usr/bin/webapp
echo "OK"
echo ""

echo "Build locale files"
mkdir -p build/usr/share
po/autogen.sh
cp -r po/locale build/usr/share
echo "OK"
echo ""

echo "Copy application data files"
cp -r data build/usr/share/webapp
echo "OK"
echo ""

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
echo ""
#=========================================

if [ $1 = "install"  ]
then
    echo $APPNAME-$VERSION "installation"
    if [ $UID != 0  ]
    then
        echo "You must be root"
        echo "Error!!"
        echo ""
    else
        cp -r build/* /
        rm -rf build
        echo "Installation complete"
        echo ""
    fi
else
echo "Make archive distribution"
rm -rf dist
mkdir -p dist
cd build
tar -cf ../dist/$APPNAME-$VERSION.tar.gz usr
echo $APPNAME-$VERSION " build complete!!!"
echo ""
fi
echo "======================================================="