%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define relabel_files() \
restorecon -R /usr/bin/oscap /usr/libexec/openscap; \

Name:           openscap
Version:        1.2.17
Release:        2%{?dist}
Summary:        Set of open source libraries enabling integration of the SCAP line of standards
Group:          System Environment/Libraries
License:        LGPLv2+
URL:            http://www.open-scap.org/
Source0:        https://github.com/OpenSCAP/openscap/releases/download/%{version}/%{name}-%{version}.tar.gz
Patch1:		openscap-1.2.17-filehash58_probe_test.patch
Patch100:   eurolinux.patch 
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  swig libxml2-devel libxslt-devel perl-XML-Parser
BuildRequires:  rpm-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  pcre-devel
BuildRequires:  libacl-devel
BuildRequires:  libselinux-devel libcap-devel
BuildRequires:  libblkid-devel
BuildRequires:  bzip2-devel
%if %{?_with_check:1}%{!?_with_check:0}
BuildRequires:  perl-XML-XPath
%endif
Requires(post):   /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
OpenSCAP is a set of open source libraries providing an easier path
for integration of the SCAP line of standards. SCAP is a line of standards
managed by NIST with the goal of providing a standard language
for the expression of Computer Network Defense related information.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libxml2-devel
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        python
Summary:        Python bindings for %{name}
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
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
Obsoletes:      openscap-selinux

%description    scanner
The %{name}-scanner package contains oscap command-line tool. The oscap
is configuration and vulnerability scanner, capable of performing
compliance checking using SCAP content.

%package        utils
Summary:        OpenSCAP Utilities
Group:          Applications/System
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       rpmdevtools rpm-build
Requires:       %{name}-containers = %{version}-%{release}

%description    utils
The %{name}-utils package contains command-line tools build on top
of OpenSCAP library. Historically, openscap-utils included oscap
tool which is now separated to %{name}-scanner sub-package.


%package        extra-probes
Summary:        SCAP probes
Group:          Applications/System
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  openldap-devel
BuildRequires:  GConf2-devel
#BuildRequires:  opendbx - for sql

%description    extra-probes
The %{name}-extra-probes package contains additional probes that are not
commonly used and require additional dependencies.

%package        engine-sce
Summary:        Script Check Engine plug-in for OpenSCAP
Group:          Applications/System
Requires:       %{name}%{?_isa} = %{version}-%{release}

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

%package        containers
Summary:        Utils for scanning containers
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-scanner
BuildArch:      noarch

%description    containers
Tool for scanning Atomic containers.


%prep
%setup -q
%patch1 -p1 -b .filehash58_probe_test
%patch100 -p1 

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

# remove content for another OS
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-rhel6-oval.xml
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-rhel6-xccdf.xml
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

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog NEWS README.md
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
%{_libexecdir}/openscap/probe_symlink
%{_libexecdir}/openscap/probe_sysctl
%{_libexecdir}/openscap/probe_system_info
%{_libexecdir}/openscap/probe_systemdunitdependency
%{_libexecdir}/openscap/probe_systemdunitproperty
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
%doc docs/{html,examples}/
%{_libdir}/libopenscap.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/openscap
%exclude %{_includedir}/openscap/sce_engine_api.h

%files engine-sce-devel
%defattr(-,root,root,-)
%{_libdir}/libopenscap_sce.so
%{_includedir}/openscap/sce_engine_api.h

%files scanner
%{_bindir}/oscap
%{_mandir}/man8/oscap.8.gz
%{_bindir}/oscap-chroot
%{_mandir}/man8/oscap-chroot.8.gz
%{_sysconfdir}/bash_completion.d

%files utils
%defattr(-,root,root,-)
%doc docs/oscap-scan.cron
%{_mandir}/man8/*
%exclude %{_mandir}/man8/oscap.8.gz
%exclude %{_mandir}/man8/oscap-docker.8.gz
%exclude %{_mandir}/man8/oscap-chroot.8.gz
%{_bindir}/*
%exclude %{_bindir}/oscap
%exclude %{_bindir}/oscap-docker
%exclude %{_bindir}/oscap-chroot


%files extra-probes
%{_libexecdir}/openscap/probe_ldap57
%{_libexecdir}/openscap/probe_gconf

%files engine-sce
%{_libdir}/libopenscap_sce.so.*

%files containers
%defattr(-,root,root,-)
%{_bindir}/oscap-docker
%{_mandir}/man8/oscap-docker.8.gz
%{python_sitelib}/oscap_docker_python/*


%changelog
* Wed Dec 12 2018 Aleksander Baranowski <aleksander.baranowski@euro-linux.com>
- Patched for EuroLinux

* Tue Aug 14 2018 Matěj Týč <matyc@redhat.com> - 1.2.17-2
- Patched to include tests for filehash58 probe.

* Wed Jul 11 2018 Matěj Týč <matyc@redhat.com> - 1.2.17-1
- Rebased to the 1.2.17 upstream release (#1564900).
- Fixed the offline scanning (#1547107, #1556988).
- HTML Guide user experience improvements.
- New options in HTML report "Group By" menu.
- oscap-ssh supports --oval-results.
- For more news, see https://github.com/OpenSCAP/openscap/releases/tag/1.2.17

* Tue Feb 06 2018 Watson Yuuma Sato <wsato@redhat.com> - 1.2.16-6
- Cleanup temporary images created by oscap-docker (#1454637)

* Tue Jan 23 2018 Jan Černý <jcerny@redhat.com> - 1.2.16-5
- Revert warnings by default in oscap tool (#1537089)

* Mon Jan 15 2018 Watson Yuuma Sato <wsato@redhat.com> - 1.2.16-4
- Fix requirement on openscap-containers

* Tue Jan 09 2018 Watson Yuuma Sato <wsato@redhat.com> - 1.2.16-3
- Update bash completion (#1505517)
- Align bash role header with output of help command (#1439813)

* Mon Nov 20 2017 Matěj Týč <matyc@redhat.com> - 1.2.16-2
- moved oscap-docker to newly created openscap-containers.
- moved man of oscap-chroot to oscap-scanner.

* Tue Nov 14 2017 Matěj Týč <matyc@redhat.com> - 1.2.16-1
- upgrade to the latest upstream release
- moved oscap-chroot to openscap-scanner because it's a thin wrapper script with no dependencies

* Mon Aug 28 2017 Jan Černý <jcerny@redhat.com> - 1.2.15-1
- upgrade to the latest upstream release
- short profile names can be used instead of long IDs
- new option --rule allows to evaluate only a single rule
- new option --fix-type in "oscap xccdf generate fix" allows choosing
  remediation script type without typing long URL
- "oscap info" shows profile titles
- OVAL details in HTML report are easier to read
- HTML report is smaller because unselected rules are removed
- HTML report supports NIST 800-171 and CJIS
- remediation scripts contain headers with useful information (#1439813)
- remediation scripts report progress when they run
- basic support for Oracle Linux (CPEs, runlevels)
- remediation scripts can be generated from datastreams that contain
  multiple XCCDF benchmarks
- basic support for OVAL 5.11.2 (only schemas, no features)
- enabled offline RPM database in rpminfo probe
- added Fedora 28 CPE
- fixed oscap-docker with Docker >= 2.0
- fixed behavior of sysctl probe to be consistent with sysctl tool
- fixed generating remediation scripts
- severity of tailored rules is not discarded
- fixed errors in RPM probes initialization
- oscap-docker shows all warnings reported by oscap
- fixed pkgconfig file

* Fri May 19 2017 Martin Preisler <mpreisle@redhat.com> - 1.2.14-2
- RPM probes to return not applicable on non-rpm systems (#1447629)
- fixed sysctl tests on s390x architecture (#1447649)
- Revert warning by default in oscap tool, our message categories are not ready for it (#1447341)

* Tue Mar 21 2017 Jan Černý <jcerny@redhat.com> - 1.2.14-1
- Upgrade to the latest upstream release
- Detailed information about ARF files in 'oscap info'
- Generating remediation scripts from ARF
- HTML report UX improvements
- Fixed CPE dictionary to identify RHEVH as RHEL7 (#1420038)
- Fixed systemd probes crashes inside containers (#1431186)
- Fixed output on terminals with white background (#1365911)
- Error handling in oscap-vm (#1391754)
- Fixed SCE stderr stalling (#1420811)
- Fixed absolute filepath parsing in OVAL (#1312831, #1312824)
- Fixed segmentation faults in RPM probes (#1414303, #1414312)
- Fixed missing header in result-oriented Ansible remediations

* Thu Jan 05 2017 Martin Preisler <mpreisle@redhat.com> - 1.2.13-1
- Upgrade to the latest upstream release
- Added --thin-results CLI override to oscap xccdf eval
- Added --without-syschar CLI override to oscap xccdf eval
- Remediations are not filtered by applicability
- Fixed segmentation faults in XCCDF and OVAL processing
- Added a warning on generating an ARF from XCCDF 1.1

* Wed Nov 16 2016 Martin Preisler <mpreisle@redhat.com> - 1.2.12-1
- Upgrade to the latest upstream release
- improved HTML report by referencing links
- fixed validity errors in ARF files
- fixed CVE parsing
- fixed injecting xccdf:check-content-ref references in ARF results
- fixed oscap-docker incompliance reporting (#1387248)
- fixed oscap-docker man page (#1387166)

* Mon Nov 14 2016 Martin Preisler <mpreisle@redhat.com> - 1.2.11-1
- upgrade to the latest upstream release

* Mon Sep 05 2016 Jan Černý <jcerny@redhat.com> - 1.2.10-2
- fix oscap-docker to follow the proxy settings (#1351952)

* Thu Jun 30 2016 Jan Černý <jcerny@redhat.com> - 1.2.10-1
- upgrade to the latest upstream release

* Tue May 31 2016 Martin Preisler <mpreisle@redhat.com> - 1.2.9-7
- fixed dates in the changelog
- changed Release to 7 to avoid conflicts

* Tue May 31 2016 Martin Preisler <mpreisle@redhat.com> - 1.2.9-4
- worked around a change in behavior in argparse between different versions of python2 (#1278147)

* Thu May 05 2016 Martin Preisler <mpreisle@redhat.com> - 1.2.9-3
- fixed loading SDS session multiple times (#1250072)

* Tue Apr 26 2016 Jan Černý <jcerny@redhat.com> - 1.2.9-2
- fix specfile

* Mon Apr 25 2016 Jan Černý <jcerny@redhat.com> - 1.2.9-1
- upgrade to the latest upstream release

* Fri Jul 24 2015 Martin Preisler <mpreisle@redhat.com> - 1.2.5-3
- add a patch for scap-as-rpm to generate SRPM correctly (#1242893)

* Fri Jul 24 2015 Martin Preisler <mpreisle@redhat.com> - 1.2.5-2
- add a patch to support RHSA identifiers in HTML report and guide (#1243808)

* Mon Jul 06 2015 Šimon Lukašík <slukasik@redhat.com> - 1.2.5-1
- upgrade to the latest upstream release

* Mon Jun 22 2015 Šimon Lukašík <slukasik@redhat.com> - 1.2.4-1
- upgrade to the latest upstream release
- drop openscap-selinux sub-package

* Tue Jan 20 2015 Šimon Lukašík <slukasik@redhat.com> - 1.1.1-3
- USGCB, schematron: var_ref missing when var_check exported (#1182242)

* Thu Jan 08 2015 Šimon Lukašík <slukasik@redhat.com> - 1.1.1-2
- STIG-generated results contain var_ref without var_check (#1159289)
- Probes failed to stop by USR1 signal as specified (#1165139)

* Fri Sep 26 2014 Šimon Lukašík <slukasik@redhat.com> - 1.1.1-1
- upgrade to the latest upstream release

* Wed Sep 03 2014 Šimon Lukašík <slukasik@redhat.com> - 1.1.0-1
- upgrade
- introduce openscap-scanner sub-package (#1115105)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1.0.3-2
- Mass rebuild 2014-01-24

* Tue Jan 14 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.3-1
- upgrade
- This upstream release addresses: #1052142

* Fri Jan 10 2014 Šimon Lukašík <slukasik@redhat.com> - 1.0.2-1
- upgrade
- This upstream release addresses: #1018291, #1029879, #1026833

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.0.1-2
- Mass rebuild 2013-12-27

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

* Fri Nov 15 2013 Šimon Lukašík <slukasik@redhat.com> - 0.9.13-7
- do not obsolete openscap-conten just drop it (#1028706)
  scap-security-guide will bring the Obsoletes tag

* Thu Nov 14 2013 Šimon Lukašík <slukasik@redhat.com> - 0.9.13-6
- only non-noarch packages should be requiring specific architecture

* Sat Nov 09 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-5
- specify architecture when requiring base package

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-4
- specify dependency between engine and devel sub-package

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-3
- correct openscap-utils dependencies

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-2
- drop openscap-content package (use scap-security-guide instead)

* Fri Nov 08 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.13-1
- upgrade

* Thu Sep 26 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.12-2
- Start building SQL probes for Fedora

* Wed Sep 11 2013 Šimon Lukašík <slukasik@redhat.com> 0.9.12-1
- upgrade

* Thu Jul 18 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.11-1
- upgrade

* Mon Jul 15 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.10-1
- upgrade

* Mon Jun 17 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.8-1
- upgrade

* Fri Apr 26 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.7-1
- upgrade
- add openscap-selinux sub-package

* Wed Apr 24 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.6-1
- upgrade

* Wed Mar 20 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.5-1
- upgrade

* Mon Mar 04 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.4.1-1
- upgrade

* Tue Feb 26 2013 Petr Lautrbach <plautrba@redhat.com> 0.9.4-1
- upgrade

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Dec 17 2012 Petr Lautrbach <plautrba@redhat.com> 0.9.3-1
- upgrade

* Wed Nov 21 2012 Petr Lautrbach <plautrba@redhat.com> 0.9.2-1
- upgrade

* Mon Oct 22 2012 Petr Lautrbach <plautrba@redhat.com> 0.9.1-1
- upgrade

* Tue Sep 25 2012 Peter Vrabec <pvrabec@redhat.com> 0.9.0-1
- upgrade

* Mon Aug 27 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.5-1
- upgrade

* Tue Aug 07 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.4-1
- upgrade

* Tue Jul 31 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.3-2
- fix Profile and  @hidden issue

* Mon Jul 30 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.3-1
- upgrade

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jun 08 2012 Petr Pisar <ppisar@redhat.com> - 0.8.2-2
- Perl 5.16 rebuild

* Fri Mar 30 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.2-1
- upgrade

* Tue Feb 21 2012 Peter Vrabec <pvrabec@redhat.com> 0.8.1-1
- upgrade

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 0.8.0-3
- Rebuild against PCRE 8.30

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Oct 11 2011 Peter Vrabec <pvrabec@redhat.com> 0.8.0-1
- upgrade

* Mon Jul 25 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.4-1
- upgrade

* Thu Jul 21 2011 Petr Sabata <contyk@redhat.com> - 0.7.3-3
- Perl mass rebuild

* Wed Jul 20 2011 Petr Sabata <contyk@redhat.com> - 0.7.3-2
- Perl mass rebuild

* Fri Jun 24 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.3-1
- upgrade

* Fri Jun 17 2011 Marcela Mašláňová <mmaslano@redhat.com> - 0.7.2-3
- Perl mass rebuild

* Fri Jun 10 2011 Marcela Mašláňová <mmaslano@redhat.com> - 0.7.2-2
- Perl 5.14 mass rebuild

* Wed Apr 20 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.2-1
- upgrade

* Fri Mar 11 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.1-1
- upgrade

* Thu Feb 10 2011 Peter Vrabec <pvrabec@redhat.com> 0.7.0-1
- upgrade

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Peter Vrabec <pvrabec@redhat.com> 0.6.8-1
- upgrade

* Fri Jan 14 2011 Peter Vrabec <pvrabec@redhat.com> 0.6.7-1
- upgrade

* Wed Oct 20 2010 Peter Vrabec <pvrabec@redhat.com> 0.6.4-1
- upgrade

* Tue Sep 14 2010 Peter Vrabec <pvrabec@redhat.com> 0.6.3-1
- upgrade

* Fri Aug 27 2010 Peter Vrabec <pvrabec@redhat.com> 0.6.2-1
- upgrade

* Wed Jul 14 2010 Peter Vrabec <pvrabec@redhat.com> 0.6.0-1
- upgrade

* Wed May 26 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.11-1
- upgrade

* Fri May 07 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.10-1
- upgrade

* Fri Apr 16 2010 Peter Vrabec <pvrabec@redhat.com> 0.5.9-1
- upgrade

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

