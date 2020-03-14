#/bin/csh

set PKG_ROOT=`pwd`
python update-meta.py bump-revision
cd pfSense-pkg-FauxAPI
make clean && make package
if ($? == 0) then
  cd work/pkg
  set PKG_NAME=`ls -b *.txz`
  mv $PKG_NAME "${PKG_ROOT}/packages/${PKG_NAME}"
  cd ${PKG_ROOT}/packages
  echo $PKG_NAME > LATEST
  shasum -a 256 $PKG_NAME >> SHA256SUMS
  shasum -a 256 -c SHA256SUMS
endif
cd $PKG_ROOT
