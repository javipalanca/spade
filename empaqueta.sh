#!/bin/sh

svn export . tmp
cd tmp
rm usr/share/spade/jabberd/*.exe -f
rm usr/share/spade/jabberd/libs/*.dll -f
touch usr/share/spade/jabberd/spool/.spool
makeinstaller
mv *.package ../setup.bin
cd ..
rm -rf tmp
echo ":-)"
