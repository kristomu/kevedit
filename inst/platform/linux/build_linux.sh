#!/bin/sh
# KevEdit linux AppImage build script
# Run in kevedit/build_appimage container
set -e -x

SOURCE="$1"
KEVEDIT_VERSION="$2"
if [ -z "$SOURCE" ] || [ -z "$KEVEDIT_VERSION" ]; then
    echo "USAGE: build_linux.sh <source.zip> <AppImage version>"
    exit 1
fi
export KEVEDIT_VERSION

rm -rf /work/appdir
mkdir -p /work/appdir/KevEdit.AppDir

rm -rf /work/kevedit
mkdir /work/kevedit
cd /work/kevedit

unzip /vendor/$SOURCE

./bootstrap.sh
./configure --prefix=/work/appdir/KevEdit.AppDir/usr CFLAGS='-O3'
make
make install

cp -a /platform/linux/kevedit.desktop /work/appdir/KevEdit.AppDir/
cp -a /work/kevedit/inst/icon512.png /work/appdir/KevEdit.AppDir/kevedit.png
cp /vendor/AppRun-${KEVEDIT_VERSION}-x86_64 /work/appdir/KevEdit.AppDir/AppRun

mkdir -p /work/appdir/KevEdit.AppDir/usr/lib
cp -a /usr/local/lib/libSDL2*.so* /work/appdir/KevEdit.AppDir/usr/lib/
