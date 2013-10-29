%bcond_without	tests

Summary:	Go compiler and tools
Name:		go
Version:	1.1.2
Release:	0.1
License:	BSD
Group:		Development/Languages
#Source0Download: https://code.google.com/p/go/downloads/list
Source0:	https://go.googlecode.com/files/%{name}%{version}.src.tar.gz
# Source0-md5:	705feb2246c8ddaf820d7e171f1430c5
Patch0:		%{name}-ca-certs.patch
Patch1:		%{name}-verbose-build.patch
URL:		http://golang.org/
BuildRequires:	bash
BuildRequires:	iana-etc
BuildRequires:	inetutils-hostname
BuildRequires:	rpm-pythonprov
BuildRequires:	tzdata
Requires:	ca-certificates
ExclusiveArch:	%{ix86} %{x8664} %{arm}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_enable_debug_packages	0
%define		no_install_post_strip	1
%define		no_install_post_chrpath	1
%define		_noautoreqfiles		%{_libdir}/%{name}/src

%define		_vimdatadir	%{_datadir}/vim

%ifarch %{ix86}
%define	GOARCH 386
%endif
%ifarch %{x8664}
%define	GOARCH amd64
%endif

%description
Go is an open source programming environment that makes it easy to
build simple, reliable, and efficient software.

%package doc
Summary:	Manual for go
Group:		Documentation

%description doc
Documentation for go.

%package -n vim-syntax-%{name}
Summary:	Go syntax files for Vim
Group:		Applications/Editors
Requires:	vim-rt

%description -n vim-syntax-%{name}
Go syntax files for vim.

%prep
%setup -qc
mv go/* .
%patch0 -p1
%patch1 -p1

%build
export GOOS=linux
export GOARCH=%{GOARCH}
export GOROOT_FINAL=%{_libdir}/%{name}
export GOMAXPROCS=%{?_smp_mflags}
cd src

# from Fedora
echo -e "#!/bin/sh\n%{__cc} %{rpmcflags} %{rpmldflags} \"\$@\"" > mygcc
chmod +x mygcc
export CC="$(pwd -P)/mygcc"

bash make.bash

%if %{with tests}
%check
export GOROOT=$(pwd -P)
export PATH="$PATH":"$GOROOT"/bin
cd src
bash run.bash --no-rebuild
%endif

%install
rm -rf $RPM_BUILD_ROOT
GOROOT=$RPM_BUILD_ROOT%{_libdir}/%{name}

install -d $GOROOT/{misc,lib,src}
install -d $RPM_BUILD_ROOT%{_bindir}

# install everything into libdir (until symlink problems are fixed)
# https://code.google.com/p/go/issues/detail?id=5830
%{__cp} -av api bin doc favicon.ico include lib pkg robots.txt src \
	$RPM_BUILD_ROOT%{_libdir}/%{name}

# remove the unnecessary zoneinfo file (Go will always use the system one first)
%{__rm} -r $RPM_BUILD_ROOT%{_libdir}/%{name}/lib/time

ln -sf %{_libdir}/%{name}/bin/go $RPM_BUILD_ROOT%{_bindir}/go
ln -sf %{_libdir}/%{name}/bin/godoc $RPM_BUILD_ROOT%{_bindir}/godoc
ln -sf %{_libdir}/%{name}/bin/gofmt $RPM_BUILD_ROOT%{_bindir}/gofmt

ln -sf %{_libdir}/%{name}/pkg/tool/linux_%{GOARCH}/cgo $RPM_BUILD_ROOT%{_bindir}/cgo
ln -sf %{_libdir}/%{name}/pkg/tool/linux_%{GOARCH}/ebnflint $RPM_BUILD_ROOT%{_bindir}/ebnflint

%ifarch %{ix86}
tools="8a 8c 8g 8l"
%endif
%ifarch %{x8664}
tools="6a 6c 6g 6l"
%endif
%ifarch %{arm}
tools="5a 5c 5g 5l"
%endif
for tool in $tools; do
	ln -sf %{_libdir}/%{name}/pkg/tool/linux_%{GOARCH}/$tool $RPM_BUILD_ROOT%{_bindir}/$tool
done

VIMFILES="syntax/go.vim ftdetect/gofiletype.vim ftplugin/go/fmt.vim ftplugin/go/import.vim indent/go.vim"
for i in $VIMFILES; do
	install -Dp misc/vim/$i $RPM_BUILD_ROOT%{_vimdatadir}/$i
done

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS CONTRIBUTORS LICENSE README
%ifarch %{arm}
%attr(755,root,root) %{_bindir}/5a
%attr(755,root,root) %{_bindir}/5c
%attr(755,root,root) %{_bindir}/5g
%attr(755,root,root) %{_bindir}/5l
%endif
%ifarch %{x8664}
%attr(755,root,root) %{_bindir}/6a
%attr(755,root,root) %{_bindir}/6c
%attr(755,root,root) %{_bindir}/6g
%attr(755,root,root) %{_bindir}/6l
%endif
%ifarch %{ix86}
%attr(755,root,root) %{_bindir}/8a
%attr(755,root,root) %{_bindir}/8c
%attr(755,root,root) %{_bindir}/8g
%attr(755,root,root) %{_bindir}/8l
%endif
%attr(755,root,root) %{_bindir}/cgo
%attr(755,root,root) %{_bindir}/ebnflint
%attr(755,root,root) %{_bindir}/go
%attr(755,root,root) %{_bindir}/godoc
%attr(755,root,root) %{_bindir}/gofmt

%dir %{_libdir}/go
%dir %{_libdir}/go/bin
%dir %{_libdir}/go/pkg
%dir %{_libdir}/go/pkg/tool
%dir %{_libdir}/go/pkg/tool/linux_%{GOARCH}

%attr(755,root,root) %{_libdir}/go/bin/*
%attr(755,root,root) %{_libdir}/go/pkg/tool/linux_%{GOARCH}/*

%{_libdir}/go/include
%{_libdir}/go/lib
%{_libdir}/go/misc
%{_libdir}/go/pkg/linux_%{GOARCH}
%{_libdir}/go/pkg/obj
%{_libdir}/go/src
%{_libdir}/go/favicon.ico
%{_libdir}/go/robots.txt

%ifarch %{x8664}
%dir %{_libdir}/go/pkg/linux_%{GOARCH}_race
%{_libdir}/go/pkg/linux_%{GOARCH}_race/*.a
%{_libdir}/go/pkg/linux_%{GOARCH}_race/regexp
%{_libdir}/go/pkg/linux_%{GOARCH}_race/runtime
%{_libdir}/go/pkg/linux_%{GOARCH}_race/sync
%{_libdir}/go/pkg/linux_%{GOARCH}_race/text
%{_libdir}/go/pkg/linux_%{GOARCH}_race/unicode
%endif

%files doc
%defattr(644,root,root,755)
%doc %{_libdir}/go/api
%doc %{_libdir}/go/doc

%files -n vim-syntax-%{name}
%defattr(644,root,root,755)
%{_vimdatadir}/ftdetect/gofiletype.vim
%{_vimdatadir}/ftplugin/go
%{_vimdatadir}/indent/go.vim
%{_vimdatadir}/syntax/go.vim

