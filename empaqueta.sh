#!/bin/sh

svn ci -m "packaging"
svn export . tmp
cd tmp
makeinstaller
mv *.package ../bin/setup.bin
echo "moved to bin/setup.bin"
cd ..
rm -rf tmp
echo ":-)"
