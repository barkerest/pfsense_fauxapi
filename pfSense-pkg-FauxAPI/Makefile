# $FreeBSD$

PORTNAME=		pfSense-pkg-FauxAPI
PORTVERSION=	1.3.f38
PORTREVISION=	2
CATEGORIES=		sysutils
MASTER_SITES=	# empty
DISTFILES=		# empty
EXTRACT_ONLY=	# empty

MAINTAINER=	beau@barkerest.com
COMMENT=	pfSense package FauxAPI

LICENSE=	APACHE20

NO_BUILD=	yes
NO_MTREE=	yes

SUB_FILES=	pkg-install pkg-deinstall
SUB_LIST=	PORTNAME=${PORTNAME}

do-extract:
	${MKDIR} ${WRKSRC}

do-install:
	${MKDIR} ${STAGEDIR}/etc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/fauxapi/credentials.sample.ini ${STAGEDIR}/etc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/fauxapi/pfsense_function_calls.sample.txt ${STAGEDIR}/etc/fauxapi

	${MKDIR} ${STAGEDIR}/etc/inc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/inc/fauxapi/fauxapi.inc ${STAGEDIR}/etc/inc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/inc/fauxapi/fauxapi_actions.inc ${STAGEDIR}/etc/inc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/inc/fauxapi/fauxapi_auth.inc ${STAGEDIR}/etc/inc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/inc/fauxapi/fauxapi_logger.inc ${STAGEDIR}/etc/inc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/inc/fauxapi/fauxapi_pfsense_interface.inc ${STAGEDIR}/etc/inc/fauxapi
	${INSTALL_DATA} ${FILESDIR}/etc/inc/fauxapi/fauxapi_utils.inc ${STAGEDIR}/etc/inc/fauxapi

	${MKDIR} ${STAGEDIR}/etc/inc/priv
	${INSTALL_DATA} ${FILESDIR}/etc/inc/priv/fauxapi.priv.inc ${STAGEDIR}/etc/inc/priv

	${MKDIR} ${STAGEDIR}/usr/local/pkg
	${INSTALL_DATA} -m 0644 ${FILESDIR}/usr/local/pkg/fauxapi.xml ${STAGEDIR}/usr/local/pkg

	${MKDIR} ${STAGEDIR}/usr/local/share/pfSense-pkg-FauxAPI
	${INSTALL_DATA} ${FILESDIR}/usr/local/share/pfSense-pkg-FauxAPI/info.xml ${STAGEDIR}/usr/local/share/pfSense-pkg-FauxAPI

	${MKDIR} ${STAGEDIR}/usr/local/www/fauxapi/admin
	${INSTALL_DATA} ${FILESDIR}/usr/local/www/fauxapi/admin/about.php ${STAGEDIR}/usr/local/www/fauxapi/admin
	${INSTALL_DATA} ${FILESDIR}/usr/local/www/fauxapi/admin/credentials.php ${STAGEDIR}/usr/local/www/fauxapi/admin
	${INSTALL_DATA} ${FILESDIR}/usr/local/www/fauxapi/admin/logs.php ${STAGEDIR}/usr/local/www/fauxapi/admin

	${MKDIR} ${STAGEDIR}/usr/local/www/fauxapi/v1
	${INSTALL_DATA} ${FILESDIR}/usr/local/www/fauxapi/v1/index.php ${STAGEDIR}/usr/local/www/fauxapi/v1

	@${REINPLACE_CMD} -i '' -e "s|%%PKGVERSION%%|${PKGVERSION}|" ${STAGEDIR}/usr/local/pkg/fauxapi.xml
	@${REINPLACE_CMD} -i '' -e "s|%%PKGVERSION%%|${PKGVERSION}|" ${STAGEDIR}/usr/local/share/pfSense-pkg-FauxAPI/info.xml
	@${REINPLACE_CMD} -i '' -e "s|%%PKGVERSION%%|${PKGVERSION}|" ${STAGEDIR}/etc/inc/fauxapi/fauxapi_actions.inc

.include <bsd.port.mk>
