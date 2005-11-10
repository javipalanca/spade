#!/bin/sh

svn export . tmp
cd tmp
rm usr/share/spade/jabberd/*.exe -f
rm usr/share/spade/jabberd/libs/*.dll -f
makeinstaller
mv *.package ../setup.bin
cd ..
rm -rf tmp
echo ":-)"
