%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           openscap
Version:        1.0.10
Release:        3%{?dist}
Summary:        Set of open source libraries enabling integration of the SCAP line of standards
Group:          System Environment/Libraries
License:        LGPLv2+
URL:            http://www.open-scap.org/
Source0:        http://fedorahosted.org/releases/o/p/openscap/%{name}-%{version}.tar.gz
Patch0:         bz998824-754e5643-Fix-possible-double-free.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  swig libxml2-devel libxslt-devel m4 perl-XML-Parser
BuildRequires:  rpm-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  pcre-devel
BuildRequires:  libacl-devel
BuildRequires:  libselinux-devel libcap-devel
BuildRequires:  libblkid-devel
%if %{?_with_check:1}%{!?_with_check:0}
BuildRequires:  perl-XML-XPath
%endif
Requires(post):   /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Obsoletes:      openscap-perl

%description
OpenSCAP is a set of open source libraries providing an easier path
for integration of the SCAP line of standards. SCAP is a line of standards
managed by NIST with the goal of providing a standard language
for the expression of Computer Network Defense related information.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       libxml2-devel
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        python
Summary:        Python bindings for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
BuildRequires:  python-devel

%description    python
The %{name}-python package contains the bindings so that %{name}
libraries can be used by python.

%package        scanner
Summary:        OpenSCAP Scanner Tool (oscap)
Group:          Applications/System
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libcurl >= 7.12.0
BuildRequires:  libcurl-devel >= 7.12.0

%description    scanner
The %{name}-scanner package contains oscap command-line tool. The oscap
is configuration and vulnerability scanner, capable of performing
compliance checking using SCAP content.

%package        utils
Summary:        OpenSCAP Utilities
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       rpmdevtools rpm-build
Requires:       %{name}-scanner%{?_isa} = %{version}-%{release}
Requires(post):  chkconfig
Requires(preun): chkconfig initscripts

%description    utils
The %{name}-utils package contains command-line tools build on top
of OpenSCAP library. Historically, openscap-utils included oscap
tool which is now separated to %{name}-scanner sub-package.

%package        content
Summary:        SCAP content
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description    content
Example of SCAP content for Red Hat Enterprise Linux. Please note
that this content is for testing purposes only.

%package        extra-probes
Summary:        SCAP probes
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
BuildRequires:  openldap-devel
BuildRequires:  GConf2-devel
#BuildRequires:  opendbx - for sql

%description    extra-probes
The %{name}-extra-probes package contains additional probes that are not
commonly used and require additional dependencies.

%package        engine-sce
Summary:        Script Check Engine plug-in for OpenSCAP
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description    engine-sce
The Script Check Engine is non-standard extension to SCAP protocol. This
engine allows content authors to avoid OVAL language and write their assessment
commands using a scripting language (Bash, Perl, Python, Ruby, ...).

%package        engine-sce-devel
Summary:        Development files for %{name}-engine-sce
Group:          Development/Libraries
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       %{name}-engine-sce%{?_isa} = %{version}-%{release}
Requires:       pkgconfig

%description    engine-sce-devel
The %{name}-engine-sce-devel package contains libraries and header files
for developing applications that use %{name}-engine-sce.

%prep
%setup -q
%patch0 -p1 -b .bz998824

%build
%ifarch sparc64
#sparc64 need big PIE
export CFLAGS="$RPM_OPT_FLAGS -fPIE"
export LDFLAGS="-pie -Wl,-z,relro -Wl,-z,now"
%else
export CFLAGS="$RPM_OPT_FLAGS -fpie"
export LDFLAGS="-pie -Wl,-z,relro -Wl,-z,now"
%endif
%configure --enable-sce

make %{?_smp_mflags}
# Remove shebang from bash-completion script
sed -i '/^#!.*bin/,+1 d' dist/bash_completion.d/oscap

%check
#to run make check use "--with check"
%if %{?_with_check:1}%{!?_with_check:0}
make check
%endif


%install
rm -rf $RPM_BUILD_ROOT

make install INSTALL='install -p' DESTDIR=$RPM_BUILD_ROOT

install -d -m 755 $RPM_BUILD_ROOT%{_initrddir}
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -p -m 755 dist/fedora/oscap-scan.init $RPM_BUILD_ROOT%{_initrddir}/oscap-scan
install -p -m 644 dist/fedora/oscap-scan.sys  $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/oscap-scan

# create symlinks to default content
ln -s  %{_datadir}/openscap/scap-rhel6-oval.xml $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-oval.xml
ln -s  %{_datadir}/openscap/scap-rhel6-xccdf.xml $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-xccdf.xml

# remove content for another OS
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-fedora14-oval.xml
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-fedora14-xccdf.xml

# Remove sectool SCE content which is not distributed along RHEL7
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/sectool-sce/sectool-xccdf.xml
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/sectool-sce/*.sh
rmdir $RPM_BUILD_ROOT/%{_datadir}/openscap/sectool-sce

# bash-completion script
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/bash_completion.d
install -pm 644 dist/bash_completion.d/oscap $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/oscap

find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%post utils
/sbin/chkconfig --add oscap-scan

%preun utils
if [ $1 -eq 0 ]; then
   /sbin/service oscap-scan stop > /dev/null 2>&1
   /sbin/chkconfig --del oscap-scan
fi


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_libdir}/libopenscap.so.*
%{_libexecdir}/openscap/probe_dnscache
%{_libexecdir}/openscap/probe_environmentvariable
%{_libexecdir}/openscap/probe_environmentvariable58
%{_libexecdir}/openscap/probe_family
%{_libexecdir}/openscap/probe_file
%{_libexecdir}/openscap/probe_fileextendedattribute
%{_libexecdir}/openscap/probe_filehash
%{_libexecdir}/openscap/probe_filehash58
%{_libexecdir}/openscap/probe_iflisteners
%{_libexecdir}/openscap/probe_inetlisteningservers
%{_libexecdir}/openscap/probe_interface
%{_libexecdir}/openscap/probe_partition
%{_libexecdir}/openscap/probe_password
%{_libexecdir}/openscap/probe_process
%{_libexecdir}/openscap/probe_process58
%{_libexecdir}/openscap/probe_routingtable
%{_libexecdir}/openscap/probe_rpminfo
%{_libexecdir}/openscap/probe_rpmverify
%{_libexecdir}/openscap/probe_rpmverifyfile
%{_libexecdir}/openscap/probe_rpmverifypackage
%{_libexecdir}/openscap/probe_runlevel
%{_libexecdir}/openscap/probe_selinuxboolean
%{_libexecdir}/openscap/probe_selinuxsecuritycontext
%{_libexecdir}/openscap/probe_shadow
%{_libexecdir}/openscap/probe_sysctl
%{_libexecdir}/openscap/probe_system_info
%{_libexecdir}/openscap/probe_textfilecontent
%{_libexecdir}/openscap/probe_textfilecontent54
%{_libexecdir}/openscap/probe_uname
%{_libexecdir}/openscap/probe_variable
%{_libexecdir}/openscap/probe_xinetd
%{_libexecdir}/openscap/probe_xmlfilecontent
%dir %{_datadir}/openscap
%dir %{_datadir}/openscap/schemas
%dir %{_datadir}/openscap/xsl
%dir %{_datadir}/openscap/cpe
%{_datadir}/openscap/schemas/*
%{_datadir}/openscap/xsl/*
%{_datadir}/openscap/cpe/*

%files python
%defattr(-,root,root,-)
%{python_sitearch}/*

%files devel
%defattr(-,root,root,-)
%doc docs/examples/
%{_libdir}/libopenscap.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/openscap
%exclude %{_includedir}/openscap/sce_engine_api.h

%files engine-sce-devel
%defattr(-,root,root,-)
%{_libdir}/libopenscap_sce.so
%{_includedir}/openscap/sce_engine_api.h

%files scanner
%{_mandir}/man8/oscap.8.gz
%{_bindir}/oscap
%{_sysconfdir}/bash_completion.d

%files utils
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/oscap-scan
%doc docs/oscap-scan.cron
%{_initrddir}/oscap-scan
%{_mandir}/man8/*
%exclude %{_mandir}/man8/oscap.8.gz
%{_bindir}/*
%exclude %{_bindir}/oscap

%files content
%defattr(-,root,root,-)
%{_datadir}/openscap/scap-oval.xml
%{_datadir}/openscap/scap-xccdf.xml
%{_datadir}/openscap/scap-rhel6-oval.xml
%{_datadir}/openscap/scap-rhel6-xccdf.xml

%files extra-probes
%{_libexecdir}/openscap/probe_ldap57
%{_libexecdir}/openscap/probe_gconf

%files engine-sce
%{_libdir}/libopenscap_sce.so.*

%changelog
* Wed Apr 15 2015 Šimon Lukašík <slukasik@redhat.com> - 1.0.10-3
- fixed minor coverity defect

* Mon Feb 16 2015 Šimon Lukašík <slukasik@redhat.com> - 1.0.10-2
- introduce openscap-scanner sub-package: #1115114

* Mon Feb 16 2015 Šimon Lukašík <slukasik@redhat.com> - 1.0.10-1
- upgrade
- This upstream release addresses: #1192428, #1036741, #998824, #1092013

* Wed Mar 26 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.8-1
- upgrade

* Thu Mar 20 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.7-1
- upgrade

* Wed Mar 19 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.6-1
- upgrade

* Fri Mar 14 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.5-1
- upgrade

* Thu Feb 13 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.4-1
- upgrade

* Tue Jan 14 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.3-1
- upgrade
- This upstream release addresses: #1052142

* Fri Jan 10 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.2-1
- upgrade
- This upstream release addresses: #1018291, #1029879, #1026833

* Fri Nov 29 2013 Šimon Lukašík <slukasik@redhat.com> - 1.0.1-3
- disable scap-as-rpm on RHEL5

* Thu Nov 28 2013 Šimon Lukašík <slukasik@redhat.com> - 1.0.1-2
- correct requirements of openscap-utils (remove redundant line)

* Thu Nov 28 2013 Šimon Lukašík <slukasik@redhat.com> - 1.0.1-1
- upgrade

* Tue Nov 26 2013 Šimon Lukašík <slukasik@redhat.com> - 1.0.0-3
- expand LT_CURRENT_MINUS_AGE correctly

* Thu Nov 21 2013 Šimon Lukašík <slukasik@redhat.com> - 1.0.0-2
- dlopen libopenscap_sce.so.{current-age} explicitly
  That allows for SCE to work without openscap-engine-sce-devel

* Tue Nov 19 2013 Šimon Lukašík <slukasik@redhat.com> - 1.0.0-1
- upgrade
- package openscap-engine-sce-devel separately

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-4
- specify dependency between engine and devel sub-package

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-3
- correct openscap-utils dependencies

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-2
- drop openscap-content package from fedora (use scap-security-guide instead)

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-1
- upgrade

* Thu Sep 26 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.12-2
- Start building SQL probes for Fedora

* Wed Sep 11 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.12-1
- upgrade

* Thu Jul 18 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.11-1
- upgrade
  Resolves: rhbz#956763

* Thu Jul 11 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.9-1
- upgrade
  Resolves: rhbz#956763

* Mon Dec 17 2012 Petr Lautrbach <plautrba@redhat.com> 0.9.3-1
- upgrade
  Resolves: rhbz#829349

* Mon Nov 19 2012 Petr Lautrbach <plautrba@redhat.com> 0.9.2-1
- upgrade
  Resolves: rhbz#829349

* Tue Oct 23 2012 Petr Lautrbach <plautrba@redhat.com> 0.9.1-2
- obsolete openscap-perl subpackage
  Resolves: rhbz#829349

* Tue Oct 23 2012 Petr Lautrbach <plautrba@redhat.com> 0.9.1-1
- upgrade
  Resolves: rhbz#829349

* Tue Sep 25 2012 Peter Vrabec <pvrabec@redhat.com> 0.9.0-1
- upgrade
  Resolves: rhbz#829349

* Wed Oct 12 2011 Peter Vrabec <pvrabec@redhat.com> 0.8.0-2
- mark provided SCAP content as example
  Resolves: #697648

* Tue Oct 11 2011 Peter Vrabec <pvrabec@redhat.com> 0.8.0-1
- upgrade
  Resolves: #697648

* Mon Jul 25 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.4-1
- upgrade. OVAL 5.8 supported
  Resolves: #697648

* Fri Mar 11 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.1-1
- upgrade, OVAL 5.6 supported
  Resolves: #642672

* Tue Feb 15 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.0-1
- upgrade, OVAL 5.6 supported
  Resolves: #642672

* Fri Jan 14 2011 Peter Vrabec <pvrabec@redhat.com> 0.6.7-1
- upgrade
  Resolves: #642672

* Wed Jul 14 2010 Peter Vrabec <pvrabec@redhat.com> 0.6.0-1
- rebase to upstream release
  Resolves: #565658, #599370

* Wed Jun 30 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.12-1
- Resolves: #565658 rebase to upstream release

* Wed May 26 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.11-1
- Resolves: #565658 rebase to upstream release

* Fri May 07 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.10-1
- Resolves: #565658 rebase to upstream release

* Fri Apr 16 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.9-1
- Resolves: #565658 rebase to upstream release

* Wed Mar 24 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.8-1
- Resolves: #565658 rebase to upstream release

* Fri Feb 26 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.7-1
- upgrade
- new utils package

* Mon Jan 04 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.6-1
- upgrade

* Tue Sep 29 2009 Peter Vrabec <pvrabec@redhat.com> 0.5.3-1
- upgrade

* Wed Aug 19 2009 Peter Vrabec <pvrabec@redhat.com> 0.5.2-1
- upgrade

* Mon Aug 03 2009 Peter Vrabec <pvrabec@redhat.com> 0.5.1-2
- add rpm-devel requirement

* Mon Aug 03 2009 Peter Vrabec <pvrabec@redhat.com> 0.5.1-1
- upgrade

* Thu Apr 30 2009 Peter Vrabec <pvrabec@redhat.com> 0.3.3-1
- upgrade

* Thu Apr 23 2009 Peter Vrabec <pvrabec@redhat.com> 0.3.2-1
- upgrade

* Sun Mar 29 2009 Peter Vrabec <pvrabec@redhat.com> 0.1.4-1
- upgrade

* Fri Mar 27 2009 Peter Vrabec <pvrabec@redhat.com> 0.1.3-2
- spec file fixes (#491892)

* Tue Mar 24 2009 Peter Vrabec <pvrabec@redhat.com> 0.1.3-1
- upgrade

* Thu Jan 15 2009 Tomas Heinrich <theinric@redhat.com> 0.1.1-1
- Initial rpm

