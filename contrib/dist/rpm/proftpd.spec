# $Id: proftpd.spec,v 1.81 2011-11-11 18:18:34 castaglia Exp $

# Module List:
#
# Dynamic modules with no/minimal additional build or runtime dependencies, always built
#   mod_auth_pam
#   mod_ban
#   mod_ctrls_admin
#   mod_exec
#   mod_facl
#   mod_ifsession
#   mod_load
#   mod_quotatab
#   mod_quotatab_file
#   mod_quotatab_radius
#   mod_quotatab_sql
#   mod_radius
#   mod_ratio
#   mod_readme
#   mod_rewrite
#   mod_shaper
#   mod_site_misc
#   mod_sql
#   mod_sql_passwd
#
# Dynamic modules with additional build or runtime dependencies, not built by default
#
#   mod_ldap (needs openldap [--with ldap])
#   mod_quotatab_ldap (needs openldap [--with ldap])
#   mod_sftp (needs openssl [--with ssl])
#   mod_sftp_pam (needs openssl [--with ssl])
#   mod_sftp_sql (needs openssl [--with ssl])
#   mod_sql_mysql (needs mysql client libraries [--with mysql])
#   mod_sql_postgres (needs postgresql client libraries [--with postgresql])
#   mod_tls (needs openssl [--with ssl])
#   mod_tls_shmcache (needs openssl [--with ssl])
#   mod_wrap (needs tcp_wrappers [--with wrap])
#   mod_wrap2 (needs tcp_wrappers [--with wrap])
#   mod_wrap2_file (needs tcp_wrappers [--with wrap])
#   mod_wrap2_sql (needs tcp_wrappers [--with wrap])
#
# Note: ALL optional features can be enabled using --with everything
# RHEL5 and clones don't have suitably recent versions of pcre/libmemcached
# so use --with rhel5 to inhibit those features when using --with everything

%global proftpd_version           1.3.5

# When doing a stable or maint release, this line is to be commented out.
# When doing an RC, define it to be e.g. 'rc2'.
#
# NOTE: rpmbuild is really bloody stupid, and CANNOT handle a leading '#'
# character followed by a '%' character.  
%global release_cand_version      rc1

%global usecvsversion             0%{?_with_cvs:1}
%global proftpd_cvs_version_main  1.3.5rc1
%global proftpd_cvs_version_date  20110525

# Handle optional functionality
#
# --with everything (for all optional functionality)
# --with rhel5 inhibits features not available on RHEL5 and clones
# --with rhel6 inhibits features not available on RHEL6 and clones
%if 0%{?_with_everything:1}
%global _with_ldap 1
%if 0%{!?_with_rhel5:1} && 0%{!?_with_rhel6:1}
%global _with_memcache 1
%endif
%global _with_mysql 1
%if 0%{!?_with_rhel5:1}
%global _with_pcre 1
%endif
%global _with_postgresql 1
%global _with_ssl 1
%global _with_wrap 1
%endif
#
# --with ldap (for mod_ldap, mod_quotatab_ldap)
%if 0%{?_with_ldap:1}
BuildRequires: openldap-devel
%endif
#
# --with memcache (for mod_memcache, mod_tls_memcache)
%if 0%{?_with_memcache:1}
BuildRequires: libmemcached-devel >= 0.41
%endif
#
# --with mysql (for mod_sql_mysql)
%if 0%{?_with_mysql:1}
BuildRequires: mysql-devel
%endif
#
# --with pcre (to use pcre rather than glibc regex engine)
%if 0%{?_with_pcre:1}
BuildRequires: pcre-devel >= 7.0
%endif
#
# --with postgresql (for mod_sql_postgres)
%if 0%{?_with_postgresql:1}
BuildRequires: postgresql-devel
%endif
#
# --with ssl (for mod_sftp, mod_sftp_pam, mod_sftp_sql, mod_sql_passwd, mod_tls, mod_tls_shmcache)
%if 0%{?_with_ssl:1}
BuildRequires: openssl-devel
%endif
#
# --with wrap (for mod_wrap, mod_wrap2, mod_wrap2_file, mod_wrap2_sql)
%if 0%{?_with_wrap:1}
# This header file might be in package tcp_wrappers or tcp_wrappers-devel
BuildRequires: /usr/include/tcpd.h
%endif

# Assume init is systemd if /run/lock exists, else SysV
%global use_systemd %([ -d /run/lock ] && echo 1 || echo 0)

# rundir is /run/proftpd under systemd, else %%{_localstatedir}/run/proftpd
%if %{use_systemd}
%global rundir /run/proftpd
%else
%global rundir %{_localstatedir}/run/proftpd
%endif

Summary:                ProFTPD - Professional FTP Server
Name:                   proftpd
License:                GPLv2+
Group:                  System Environment/Daemons
Packager:               The ProFTPD Project <core@proftpd.org>
Vendor:                 The ProFTPD Project
URL:                    http://www.proftpd.org/
%if %{usecvsversion}
Version:                %{proftpd_cvs_version_main}
Release:                0.1.cvs%{proftpd_cvs_version_date}%{?dist}
Source0:                ftp://ftp.proftpd.org/devel/source/proftpd-cvs-%{proftpd_cvs_version_date}.tar.gz
%else
Version:                %{proftpd_version}
Release:                %{?release_cand_version:0.}1%{?release_cand_version:.%{release_cand_version}}%{?dist}
Source0:                ftp://ftp.proftpd.org/distrib/source/proftpd-%{version}%{?release_cand_version}.tar.bz2
%endif
BuildRoot:              %{_tmppath}/%{name}-%{version}-root
Requires:               pam >= 0.99, /sbin/chkconfig
Requires(preun):        coreutils, findutils
%if %{use_systemd}
BuildRequires:          systemd-units
Requires:               systemd-units
Requires(post):         systemd-units
Requires(preun):        systemd-units
Requires(postun):       systemd-units
%else
Requires(post):         /sbin/chkconfig
Requires(preun):        /sbin/service, /sbin/chkconfig
Requires(postun):       /sbin/service
%endif
BuildRequires:          pkgconfig, pam-devel, ncurses-devel, zlib-devel
BuildRequires:          libacl-devel, libcap-devel
Provides:               ftpserver
Obsoletes:              proftpd-core < %{version}-%{release}, proftpd-standalone < %{version}-%{release}, proftpd-inetd < %{version}-%{release}
Provides:               proftpd-core = %{version}-%{release}, proftpd-standalone = %{version}-%{release}, proftpd-inetd = %{version}-%{release}

%description
ProFTPD is an enhanced FTP server with a focus toward simplicity, security,
and ease of configuration.  It features a very Apache-like configuration
syntax, and a highly customizable server infrastructure, including support for
multiple 'virtual' FTP servers, anonymous FTP, and permission-based directory
visibility.

This package defaults to the standalone behavior of ProFTPD, but all the
needed scripts to have it run by xinetd instead are included.

Modules requiring additional dependencies such as mod_sql_mysql, mod_ldap,
etc. are in separate sub-packages so as not to inconvenience users that
do not need that functionality.

%if 0%{?_with_ldap:1}
%package ldap
Summary:        ProFTPD - Modules relying on LDAP
Group:          System Environment/Daemons
Requires:       proftpd = %{version}-%{release}

%description ldap 
This optional package contains the modules using LDAP.
%endif

%if 0%{?_with_mysql:1}
%package mysql
Summary:        ProFTPD - Modules relying on MySQL
Group:          System Environment/Daemons
Requires:       proftpd = %{version}-%{release}

%description mysql
This optional package contains the modules using MySQL.
%endif

%if 0%{?_with_postgresql:1}
%package postgresql
Summary:        ProFTPD - Modules relying on PostgreSQL
Group:          System Environment/Daemons
Requires:       proftpd = %{version}-%{release}

%description postgresql
This optional package contains the modules using PostgreSQL.
%endif

%if 0%{?_with_wrap:1}
%package wrap
Summary:        ProFTPD - Modules relying on TCP Wrappers
Group:          System Environment/Daemons
Requires:       proftpd = %{version}-%{release}

%description wrap
This optional package contains the modules using tcpwrappers/libwrap.
%endif

%package devel
Summary:        ProFTPD - Tools and header files for developers
Group:          Development/Libraries
Requires:       proftpd = %{version}-%{release}
# devel package requires the same devel packages as were build-required
# for the main package
Requires:       libacl-devel
Requires:       libcap-devel
Requires:       pkgconfig
Requires:       pam-devel
Requires:       ncurses-devel
Requires:       zlib-devel
%{?_with_ldap:Requires:       openldap-devel}
%{?_with_memcache:Requires:   libmemcached-devel >= 0.41}
%{?_with_mysql:Requires:      mysql-devel}
%{?_with_pcre:Requires:       pcre-devel >= 7.0}
%{?_with_postgresql:Requires: postgresql-devel}
%{?_with_ssl:Requires:        openssl-devel}
%{?_with_wrap:Requires:       /usr/include/tcpd.h}

%description devel
This package is required to develop additional modules for ProFTPD.

%package utils
Summary:        ProFTPD - Additional utilities
Group:          System Environment/Daemons
Requires:       proftpd = %{version}-%{release}

%description utils
This package contains additional utilities for monitoring and configuring the
ProFTPD server:

* ftpasswd: generate passwd(5) files for use with AuthUserFile
* ftpcount: show the current number of connections per server/virtualhost
* ftpmail: monitor transfer log and send email when files uploaded
* ftpquota: manipulate quota tables
* ftptop: show the current status of FTP sessions
* ftpwho: show the current process information for each FTP session

%prep
%if %{usecvsversion}
%setup -q -n %{name}-%{proftpd_cvs_version_main}
%else
%setup -q -n %{name}-%{version}%{?release_cand_version}
%endif

# Avoid documentation name conflicts
mv contrib/README contrib/README.contrib

# Prefer documentation to be UTF-8 encoded
iconv -f iso-8859-1 -t utf-8 < ChangeLog > ChangeLog.utf-8
mv ChangeLog ChangeLog.iso-8859-1
mv ChangeLog.utf-8 ChangeLog

# Default PAM configuration file uses password-auth common config;
# revert to system-auth if password-auth is not available
if [ ! -f /etc/pam.d/password-auth ]; then
    sed -i -e s/password-auth/system-auth/ contrib/dist/rpm/proftpd.pam
fi

# Compile the module list (note: mod_ifsession is always included - last)
STANDARD_MODULE_LIST="  mod_auth_pam            \
                        mod_ban                 \
                        mod_ctrls_admin         \
                        mod_exec                \
                        mod_facl                \
                        mod_load                \
                        mod_quotatab            \
                        mod_quotatab_file       \
                        mod_quotatab_radius     \
                        mod_quotatab_sql        \
                        mod_radius              \
                        mod_ratio               \
                        mod_readme              \
                        mod_rewrite             \
                        mod_shaper              \
                        mod_site_misc           \
                        mod_sql                 "

OPTIONAL_MODULE_LIST="                          \
%{?_with_ldap:          mod_ldap}               \
%{?_with_ldap:          mod_quotatab_ldap}      \
%{?_with_ssl:           mod_sftp}               \
%{?_with_ssl:           mod_sftp_pam}           \
%{?_with_ssl:           mod_sftp_sql}           \
%{?_with_mysql:         mod_sql_mysql}          \
%{?_with_ssl:           mod_sql_passwd}         \
%{?_with_postgresql:    mod_sql_postgres}       \
%{?_with_ssl:           mod_tls}                \
%{?_with_ssl:           mod_tls_shmcache}       \
%{?_with_ssl:%{?_with_memcache:mod_tls_memcache}} \
%{?_with_wrap:          mod_wrap}               \
%{?_with_wrap:          mod_wrap2}              \
%{?_with_wrap:          mod_wrap2_file}         \
%{?_with_wrap:          mod_wrap2_sql}          "

MODULE_LIST=$(echo ${STANDARD_MODULE_LIST} ${OPTIONAL_MODULE_LIST} mod_ifsession | tr -s '[:space:]' ':' | sed 's/:$//')

%configure \
        --libexecdir=%{_libexecdir}/proftpd \
        --localstatedir=%{rundir} \
        --disable-strip \
        --enable-ctrls \
        --enable-dso \
        --enable-facl \
        --enable-ipv6 \
        --enable-nls \
        %{?_with_memcache:--enable-memcache} \
        %{?_with_pcre:--enable-pcre} \
        %{?_with_ssl:--enable-openssl} \
        --enable-shadow \
        --with-lastlog \
        --with-libraries=%{_libdir}/mysql \
        --with-includes=%{_includedir}/mysql \
        --with-pkgconfig=%{_lib}/pkgconfig \
        --with-shared=${MODULE_LIST}

%build
make

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} rundir=%{rundir} \
     INSTALL_USER=`id -un` INSTALL_GROUP=`id -gn` \
     INSTALL="install -p" \
     install

# Red Hat style distributions use PAM so install a PAM configuration
mkdir -p %{buildroot}/etc/pam.d
install -p -m 644 contrib/dist/rpm/proftpd.pam %{buildroot}/etc/pam.d/proftpd

# Use the basic-pam config as a default
install -m 644 contrib/dist/rpm/basic-pam.conf %{buildroot}/etc/proftpd.conf

%if %{use_systemd}
# Systemd unit file
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 contrib/dist/rpm/proftpd.service \
    %{buildroot}%{_unitdir}/proftpd.service
# Ensure /run/proftpd exists
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
install -p -m 644 contrib/dist/rpm/proftpd-tmpfs.conf \
    %{buildroot}%{_sysconfdir}/tmpfiles.d/proftpd.conf
%else
# SysV initscript
mkdir -p %{buildroot}/etc/rc.d/init.d
install -p -m 755 contrib/dist/rpm/proftpd.init.d \
    %{buildroot}/etc/rc.d/init.d/proftpd
%endif

# xinetd configuration for socket-based activation (not used by default)
mkdir -p %{buildroot}/etc/xinetd.d/
install -p -m 644 contrib/dist/rpm/xinetd %{buildroot}/etc/xinetd.d/proftpd

# Rotate the logs periodically
mkdir -p %{buildroot}/etc/logrotate.d/
install -p -m 644 contrib/dist/rpm/proftpd.logrotate %{buildroot}/etc/logrotate.d/proftpd

# Create anonymous ftp area
mkdir -p %{buildroot}%{_localstatedir}/ftp/pub/

# We do not want this dangling symlink to make it into the RPM
rm -f contrib/README.mod_sql

%post
%if %{use_systemd}
/bin/systemctl daemon-reload &>/dev/null || :
%endif
if [ $1 -eq 1 ]; then
    # Initial installation
%if ! %{use_systemd}
    /sbin/chkconfig --add proftpd || :
%endif
    IFS=":"; cat /etc/passwd | \
    while { read username nu nu gid nu nu nu nu; }; do \
        if [ $gid -lt 500 -a "$username" != "ftp" ]; then
            echo $username >> %{_sysconfdir}/ftpusers
        fi
    done
fi

%preun
if [ $1 -eq 0 ]; then
    # Package removal, not upgrade
%if %{use_systemd}
    /bin/systemctl --no-reload disable proftpd.service &>/dev/null || :
    /bin/systemctl stop proftpd.service &>/dev/null || :
%else
    /sbin/service proftpd stop &>/dev/null || :
    /sbin/chkconfig --del proftpd || :
%endif
    find %{rundir} -depth -mindepth 1 | xargs rm -rf &>/dev/null || :
fi

%postun
%if %{use_systemd}
/bin/systemctl daemon-reload &>/dev/null || :
%endif
if [ $1 -ge 1 ]; then
    # Package upgrade, not uninstall
%if %{use_systemd}
    /bin/systemctl try-restart proftpd.service &>/dev/null || :
%else
    /sbin/service proftpd condrestart &>/dev/null || :
%endif
else
    # Package removal, not upgrade
%if %{use_systemd}
    /bin/systemctl reload xinetd.service &>/dev/null || :
%else
    /sbin/service xinetd reload &>/dev/null || :
%endif
fi

%clean
rm -rf %{buildroot}
rm -rf %{_builddir}/%{name}-%{version}

%files
%defattr(-,root,root)
%{_bindir}/ftpdctl
%{_sbindir}/ftpscrub
%{_sbindir}/ftpshut
%{_sbindir}/in.proftpd
%{_sbindir}/proftpd
%dir %{_libexecdir}/proftpd/
%{_libexecdir}/proftpd/mod_auth_pam.so
%{_libexecdir}/proftpd/mod_ban.so
%{_libexecdir}/proftpd/mod_ctrls_admin.so
%{_libexecdir}/proftpd/mod_exec.so
%{_libexecdir}/proftpd/mod_facl.so
%{_libexecdir}/proftpd/mod_ifsession.so
%{_libexecdir}/proftpd/mod_load.so
%{_libexecdir}/proftpd/mod_quotatab.so
%{_libexecdir}/proftpd/mod_quotatab_file.so
%{_libexecdir}/proftpd/mod_quotatab_radius.so
%{_libexecdir}/proftpd/mod_quotatab_sql.so
%{_libexecdir}/proftpd/mod_radius.so
%{_libexecdir}/proftpd/mod_ratio.so
%{_libexecdir}/proftpd/mod_readme.so
%{_libexecdir}/proftpd/mod_rewrite.so
%{?_with_ssl:%{_libexecdir}/proftpd/mod_sftp.so}
%{?_with_ssl:%{_libexecdir}/proftpd/mod_sftp_pam.so}
%{?_with_ssl:%{_libexecdir}/proftpd/mod_sftp_sql.so}
%{_libexecdir}/proftpd/mod_shaper.so
%{_libexecdir}/proftpd/mod_site_misc.so
%{_libexecdir}/proftpd/mod_sql.so
%{?_with_ssl:%{_libexecdir}/proftpd/mod_sql_passwd.so}
%{?_with_ssl:%{_libexecdir}/proftpd/mod_tls.so}
%{?_with_ssl:%{?_with_memcache:%{_libexecdir}/proftpd/mod_tls_memcache.so}}
%{?_with_ssl:%{_libexecdir}/proftpd/mod_tls_shmcache.so}
%exclude %{_libexecdir}/proftpd/*.a
%exclude %{_libexecdir}/proftpd/*.la
%dir %{rundir}/
%dir %{_localstatedir}/ftp/
%dir %{_localstatedir}/ftp/pub/
%if %{use_systemd}
%{_unitdir}/proftpd.service
%{_sysconfdir}/tmpfiles.d/proftpd.conf
%else
%{_sysconfdir}/rc.d/init.d/proftpd
%endif
%{?_with_ssl:%config(noreplace) %{_sysconfdir}/blacklist.dat}
%{?_with_ssl:%config(noreplace) %{_sysconfdir}/dhparams.pem}
%config(noreplace) %{_sysconfdir}/proftpd.conf
%config(noreplace) %{_sysconfdir}/pam.d/proftpd
%config(noreplace) %{_sysconfdir}/logrotate.d/proftpd
%config(noreplace) %{_sysconfdir}/xinetd.d/proftpd

%doc COPYING CREDITS ChangeLog NEWS README RELEASE_NOTES
%doc README.DSO README.modules README.IPv6 README.PAM
%doc README.capabilities README.classes README.controls README.facl
%doc contrib/README.contrib contrib/README.ratio
%doc doc/* sample-configurations/
%{_mandir}/man5/xferlog.5*
%{_mandir}/man8/ftpdctl.8*
%{_mandir}/man8/ftpscrub.8*
%{_mandir}/man8/ftpshut.8*
%{_mandir}/man8/proftpd.8*

%if 0%{?_with_ldap:1}
%files ldap
%defattr(-,root,root)
%doc README.LDAP contrib/mod_quotatab_ldap.ldif contrib/mod_quotatab_ldap.schema
%{_libexecdir}/proftpd/mod_ldap.so
%{_libexecdir}/proftpd/mod_quotatab_ldap.so
%endif

%if 0%{?_with_mysql:1}
%files mysql
%defattr(-,root,root)
%{_libexecdir}/proftpd/mod_sql_mysql.so
%endif

%if 0%{?_with_postgresql:1}
%files postgresql
%defattr(-,root,root)
%{_libexecdir}/proftpd/mod_sql_postgres.so
%endif

%if 0%{?_with_wrap:1}
%files wrap
%defattr(-,root,root)
%{_libexecdir}/proftpd/mod_wrap.so
%{_libexecdir}/proftpd/mod_wrap2.so
%{_libexecdir}/proftpd/mod_wrap2_file.so
%{_libexecdir}/proftpd/mod_wrap2_sql.so
%endif

%files devel
%defattr(-,root,root)
%{_bindir}/prxs
%{_includedir}/proftpd/
%{_libdir}/pkgconfig/proftpd.pc

%files utils
%defattr(-,root,root)
%doc contrib/xferstats.holger-preiss
%{_bindir}/ftpquota
%{_bindir}/ftpasswd
%{_bindir}/ftpcount
%{_bindir}/ftpmail
%{_bindir}/ftptop
%{_bindir}/ftpwho
%{_mandir}/man1/ftpasswd.1*
%{_mandir}/man1/ftpcount.1*
%{_mandir}/man1/ftpmail.1*
%{_mandir}/man1/ftpquota.1*
%{_mandir}/man1/ftptop.1*
%{_mandir}/man1/ftpwho.1*

%changelog
* Tue Oct  4 2011 Paul Howarth <paul@city-fan.org>
- Upstream RPM package refactored to support Red Hat/Fedora based distributions
  from EL-5 onwards:
  - Fix build failure on CentOS 5 (bug 3640)
  - Build all modules that don't require additional dependencies by default
  - Optionally build other modules (use --with everything for all modules)
  - Use PAM-based configuration by default
  - Add systemd support
  - Merge inetd subpackage back into main package
  - Create new utils subpackage
  - Lots of minor fixes

* Mon Sep 11 2007 Philip Prindeville <philipp_subx@redfish-solutions.com>
- Cleaned up the .spec file to work with more recent releases of RPM.  Moved
  header files into separate component.

* Sun Mar 5 2006 Itamar Reis Peixoto <itamar@ispbrasil.com.br>
- Added "--with mod_quotatab" and "--with mod_quotatab_sql" to enable Quota Support while building the RPM

* Sun Nov  2 2003 John Morrissey <jwm@horde.net>
- This changelog is not frequently updated - please check the CVS revision
  history at http://cvs.proftpd.org/ instead.

* Tue Sep 23 2003 Daniel Roesen <dr@proftpd.org>
- Added "--with ipv6" to enable IPv6 support while building the RPM

* Sun May 25 2003 John Morrissey <jwm@horde.net>
- Permit selection of additional contrib modules when building the RPM
  Submitted by: Ivan F. Martinez <ivanfm@users.sourceforge.net>

* Sat Nov  2 2002 John Morrissey <jwm@horde.net>
- Don't let dangling contrib/README.* symlinks get into the built RPM
- logrotate for xferlog

* Wed Aug 14 2002 John Morrissey <jwm@horde.net>
- Added removal of build leftover directory in %%clean.
  Submitted by: Christian Pelealu <kurisu@mweb.co.id>

* Wed Jul  3 2002 John Morrissey <jwm@horde.net> 1.2.6rc1-1
- 1.2.6rc1 release.

* Sun Jun  9 2002 John Morrissey <jwm@horde.net> 1.2.5-1
- 1.2.5 release.

* Fri May 10 2002 TJ Saunders <tj@castaglia.org>
- Added use of %%defattr to allow build of RPMs by non-root users
  For details see http://bugs.proftpd.org/show_bug.cgi?id=1580

* Mon Mar 05 2001 Daniel Roesen <droesen@entire-systems.com>
- PAM >= 0.72 is now a requirement. Versions before are broken and
  Red Hat provides a PAM update for all RH 6.x releases. See:
  http://www.redhat.com/support/errata/RHSA-2000-120.html
  Thanks to O.Elliyasa <osman@Cable.EU.org> for the suggestion.
  For details see http://bugs.proftpd.org/show_bug.cgi?id=1048
- release: 1.2.1-2

* Wed Mar 01 2001 Daniel Roesen <droesen@entire-systems.com>
- Update to 1.2.1
- release: 1.2.1-1

* Wed Feb 27 2001 Daniel Roesen <droesen@entire-systems.com>
- added "Obsoletes: proftpd-core" to make migration to new RPMs easier.
  Thanks to Sébastien Prud'homme <prudhomme@easy-flying.com> for the hint.
- release: 1.2.0-3

* Wed Feb 26 2001 Daniel Roesen <droesen@entire-systems.com>
- cleaned up .spec formatting (cosmetics)
- fixed CFLAGS (fixes /etc/shadow support)
- included COPYING, CREDITS, ChangeLog and NEWS
- Renamed main package from "proftpd-core" to just "proftpd"
- release: 1.2.0-2

* Wed Feb 14 2001 Daniel Roesen <droesen@entire-systems.com>
- moved Changelog to bottom
- fixed %%pre script /etc/ftpusers generator
- removed /ftp/ftpusers from package management. Deinstalling ProFTPD
  should _not_ result in removal of this file.

* Thu Oct 03 1999 O.Elliyasa <osman@Cable.EU.org>
- Multi package creation.
  Created core, standalone, inetd (&doc) package creations.
  Added startup script for init.d
  Need to make the "standalone & inetd" packages being created as "noarch"
- Added URL.
- Added prefix to make the package relocatable.

* Wed Sep 08 1999 O.Elliyasa <osman@Cable.EU.org>
- Corrected inetd.conf line addition/change logic.

* Sat Jul 24 1999 MacGyver <macgyver@tos.net>
- Initial import of spec.
