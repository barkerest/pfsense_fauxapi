#/bin/sh

set PKG_ROOT=`pwd`
cd pfSense-pkg-FauxAPI
make clean && make package && mv work/pkg/pfSense-pkg-FauxAPI*.txz "${PKG_ROOT}/packages"
cd $PKG_ROOT
