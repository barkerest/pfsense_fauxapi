#/bin/csh

set PKG_ROOT=`pwd`
cd pfSense-pkg-FauxAPI
make clean && make package
if ($? == 0) then
  cd work/pkg
  set PKG_NAME=`ls -b *.txz`
  mv $PKG_NAME "${PKG_ROOT}/packages/${PKG_NAME}"
  echo $PKG_NAME > "${PKG_ROOT}/packages/LATEST"
endif
cd $PKG_ROOT
