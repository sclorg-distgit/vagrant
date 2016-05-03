%{?scl:%scl_package vagrant}
%{!?scl:%global pkg_name %{name}}

%global enable_tests 0

# Try to get bash completion dir, but provide fallback when the autodetection fails.
%global bashcompletion_dir %(pkg-config --variable=completionsdir bash-completion 2> /dev/null || echo %{_root_sysconfdir}/bash_completion.d)

%global vagrant_spec_commit 9bba7e1228379c0a249a06ce76ba8ea7d276afbe

# Determine the right place for RPM macros
# /etc/rpm for RHEL 6 compatibility
%global rpmmacrodir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] ||
d=/etc/rpm; echo $d)

Name: %{?scl_prefix}vagrant
Version: 1.8.1
Release: 2%{?dist}
Summary: Build and distribute virtualized development environments
Group: Development/Languages
License: MIT
URL: http://vagrantup.com
Source0: https://github.com/mitchellh/%{pkg_name}/archive/v%{version}/%{pkg_name}-%{version}.tar.gz
# Upstream binstub with adjusted paths, the offical way how to run vagrant
Source1: binstub
# The library has no official release yet. But since it is just test
# dependency, it should be fine to include the source right here.
Source2: https://github.com/mitchellh/%{pkg_name}-spec/archive/%{vagrant_spec_commit}/%{pkg_name}-spec-%{vagrant_spec_commit}.tar.gz
# Monkey-patching needed for Vagrant to work until the respective patches
# for RubyGems and Bundler are in place
Source3: patches.rb
Source4: macros.vagrant

# The load directive is supported since RPM 4.12, i.e. F21+. The build process
# fails on older Fedoras.
#%%{?load:%{SOURCE4}}

# For RHEL 6 and RHEL 7 builds:
%{lua: 
  function source_macros(file)
    local macro = nil
    for line in io.lines(file) do
      if not macro and line:match("^%%") then
        macro = line:match("^%%(.*)$")
        line = nil
      end
      if macro then
        if line and macro:match("^.-%s*\\%s*$") then
          macro = macro .. '\n' .. line
        end
        if not macro:match("^.-%s*\\%s*$") then
          rpm.define(macro)
          macro = nil
        end
      end
    end
  end
  source_macros(rpm.expand("%{SOURCE4}"))
}


Patch0: vagrant-1.8.1-fix-dependencies.patch

# Install plugins in isolation
# https://github.com/mitchellh/vagrant/pull/5877
Patch1: vagrant-1.8.1-disable-winrm-tests.patch
# Don't use biosdevname if missing in Fedora guest
Patch3: vagrant-1.7.4-dont-require-biosdevname-fedora.patch

# Fixes vagrant plugin install error with recent RubyGems.
# https://bugzilla.redhat.com/show_bug.cgi?id=1330208
# https://github.com/mitchellh/vagrant/pull/7198
Patch4: vagrant-1.8.1-Fixes-specification-rb-undefined-method-group-by-for-nilclass.patch

# Until we have scl-utils that generates this
Requires: %{?scl_prefix}runtime
Requires: %{?scl_prefix_ruby}ruby(release)
Requires: %{?scl_prefix_ruby}ruby(rubygems) >= 1.3.6
# Explicitly specify MRI, since Vagrant does not work with JRuby ATM.
Requires: %{?scl_prefix_ruby}ruby
# rb-inotify should be installed by listen, but this dependency was removed
# in Fedora's package.
Requires: %{?scl_prefix}rubygem(rb-inotify)
Requires: %{?scl_prefix_ruby}rubygem(bundler) >= 1.5.2
Requires: %{?scl_prefix_ruby}rubygem(bundler) < 1.10.5
Requires: %{?scl_prefix}rubygem(hashicorp-checkpoint) >= 0.1.1
Requires: %{?scl_prefix}rubygem(hashicorp-checkpoint) < 0.2
Requires: %{?scl_prefix}rubygem(childprocess) >= 0.5.0
Requires: %{?scl_prefix}rubygem(childprocess) < 0.6
Requires: %{?scl_prefix_ror}rubygem(erubis) >= 2.7.0
Requires: %{?scl_prefix_ror}rubygem(erubis) < 2.8
Requires: %{?scl_prefix_ror}rubygem(i18n) >= 0.6.0
Requires: %{?scl_prefix}rubygem(listen) >= 3.0.2
Requires: %{?scl_prefix}rubygem(listen) < 3.1
Requires: %{?scl_prefix}rubygem(log4r) >= 1.1.9
Requires: %{?scl_prefix}rubygem(log4r) < 1.1.11
Requires: %{?scl_prefix}rubygem(net-ssh) >= 2.6.6
Requires: %{?scl_prefix}rubygem(net-ssh) < 2.10
Requires: %{?scl_prefix}rubygem(net-scp) >= 1.1.0
Requires: %{?scl_prefix}rubygem(nokogiri) >= 1.6
Requires: %{?scl_prefix}rubygem(net-sftp) >= 2.1
Requires: %{?scl_prefix}rubygem(net-sftp) < 2.2
Requires: %{?scl_prefix}rubygem(rest-client) >= 1.6.0
Requires: %{?scl_prefix}rubygem(rest-client) < 2.0

Requires: bsdtar
Requires: curl

Requires(pre): shadow-utils

%if 0%{?enable_tests}
BuildRequires: bsdtar
BuildRequires: %{?scl_prefix_ruby}ruby
BuildRequires: %{?scl_prefix}rubygem(listen)
BuildRequires: %{?scl_prefix}rubygem(childprocess)
BuildRequires: %{?scl_prefix}rubygem(hashicorp-checkpoint)
BuildRequires: %{?scl_prefix}rubygem(log4r)
BuildRequires: %{?scl_prefix}rubygem(net-ssh)
BuildRequires: %{?scl_prefix}rubygem(net-scp)
BuildRequires: %{?scl_prefix}rubygem(nokogiri)
BuildRequires: %{?scl_prefix_ror}rubygem(i18n)
BuildRequires: %{?scl_prefix_ror}rubygem(erubis)
BuildRequires: %{?scl_prefix}rubygem(rb-inotify)
BuildRequires: %{?scl_prefix_ror}rubygem(rspec) < 3
BuildRequires: %{?scl_prefix_ruby}rubygem(bundler)
BuildRequires: %{?scl_prefix}rubygem(net-sftp)
BuildRequires: %{?scl_prefix}rubygem(rest-client)
BuildRequires: %{?scl_prefix}rubygem(webmock)
BuildRequires: %{?scl_prefix}rubygem(fake_ftp)
%endif

%if 0%{?rhel} >= 7
BuildRequires: pkgconfig(bash-completion)
%else
BuildRequires: pkgconfig
%endif

BuildArch: noarch

%description
Vagrant is a tool for building and distributing virtualized development
environments.

%package doc
Summary: Documentation for %{pkg_name}
Group: Documentation
Requires: %{?scl_prefix}%{pkg_name} = %{version}-%{release}
BuildArch: noarch

%description doc
Documentation for %{pkg_name}.

%prep
%setup -n %{pkg_name}-%{version} -q

%patch0 -p1
%patch1 -p1
%patch4 -p1

%build

%install
mkdir -p %{buildroot}%{vagrant_dir}
cp -pa ./* \
        %{buildroot}%{vagrant_dir}/

find %{buildroot}%{vagrant_dir}/bin -type f | xargs chmod a+x

rm %{buildroot}%{vagrant_dir}/{CHANGELOG,CONTRIBUTING,README}.md
rm %{buildroot}%{vagrant_dir}/LICENSE

# Provide executable similar to upstream:
# https://github.com/mitchellh/vagrant-installers/blob/master/substrate/modules/vagrant_installer/templates/vagrant.erb
install -D -m 755 %{SOURCE1} %{buildroot}%{_bindir}/vagrant
sed -i 's|@vagrant_dir@|%{vagrant_dir}|' %{buildroot}%{_bindir}/vagrant
sed -i 's|@vagrant_plugin_conf_dir@|%{vagrant_plugin_conf_dir}|' %{buildroot}%{_bindir}/vagrant
# Set up proper GEM_PATH
GEM_PATH=/opt/rh/%{scl_ruby}/root/usr/share/gems:/opt/rh/%{scl_ror}/root/usr/share/gems:/opt/rh/%{scl}/root/usr/share/gems:/opt/rh/%scl/root/usr/share/vagrant/gems
sed -i -e "s|@gem_path@|$GEM_PATH|" %{buildroot}%{_bindir}/vagrant

# auto-completion
install -D -m 0644 %{buildroot}%{vagrant_dir}/contrib/bash/completion.sh \
  %{buildroot}%{bashcompletion_dir}/%{pkg_name}
sed -i '/#!\// d' %{buildroot}%{bashcompletion_dir}/%{pkg_name}

# create the global home dir
install -d -m 755 %{buildroot}%{vagrant_plugin_conf_dir}

# Install the monkey-patch file and load it from Vagrant after loading RubyGems
cp %{SOURCE3}  %{buildroot}%{vagrant_dir}/lib/vagrant
sed -i -e "11irequire 'vagrant/patches'" %{buildroot}%{vagrant_dir}/lib/vagrant.rb

# Install Vagrant macros
mkdir -p %{buildroot}%{rpmmacrodir}
install -m 644 %{SOURCE4} %{buildroot}%{rpmmacrodir}/macros.%{pkg_name}%{?scl:.%{scl}}
sed -i "s/%%{pkg_name}/%{pkg_name}/" %{buildroot}%{rpmmacrodir}/macros.%{pkg_name}%{?scl:.%{scl}}

# Make sure the plugins.json exists when we define
# it as a ghost file further down - will not be packaged.
touch %{buildroot}%{vagrant_plugin_conf_dir}/plugins.json

# Prepare vagrant plugins directory structure.
for i in \
  %{vagrant_plugin_instdir} \
  %{vagrant_plugin_cache} \
  %{vagrant_plugin_spec} \
  %{vagrant_plugin_docdir}
do
  mkdir -p `dirname %{buildroot}$i`
done

%check
%if 0%{?enable_tests}
# Unpack the vagrant-spec and adjust the directory name.
rm -rf ../vagrant-spec
tar xvzf %{S:2} -C ..
mv ../vagrant-spec{-%{vagrant_spec_commit},}

# Remove the git reference, which is useless in our case.
sed -i '/git/ s/^/#/' ../vagrant-spec/vagrant-spec.gemspec

# Insert new test dependencies
sed -i '25 i\ spec.add_dependency "webmock"' ../vagrant-spec/vagrant-spec.gemspec
sed -i '26 i\ spec.add_dependency "fake_ftp"' ../vagrant-spec/vagrant-spec.gemspec

# TODO: winrm is not in Fedora yet.
rm -rf test/unit/plugins/communicators/winrm
sed -i '/it "eager loads WinRM" do/,/^      end$/ s/^/#/' test/unit/vagrant/machine_test.rb
sed -i '/it "should return the specified communicator if given" do/,/^    end$/ s/^/#/' test/unit/vagrant/machine_test.rb

# We have RSpec 2.11 is ror scl, but tests works only with 2.14 or higher
#sed -i 's/"rspec", "~> 2\.14"/"rspec", "~> 2\.11"/' ../vagrant-spec/vagrant-spec.gemspec
# Download newer rspec for Copr build
%{?scl:scl enable %{scl} - << \EOF}
gem install rspec --version 2.14
bundle --local
%{?scl:EOF}

# Test suite must be executed in order.
%{?scl:scl enable %{scl} - << \EOF}
ruby -rbundler/setup -I.:lib -e 'Dir.glob("test/unit/**/*_test.rb").sort.each &method(:require)'
%{?scl:EOF}
%endif

%pre
getent group vagrant >/dev/null || groupadd -r vagrant
 

%files
%doc LICENSE
%{_bindir}/%{pkg_name}
%dir %{vagrant_dir}
%exclude %{vagrant_dir}/.*
%exclude %{vagrant_dir}/Vagrantfile
%{vagrant_dir}/bin
# TODO: Make more use of contribs.
%{vagrant_dir}/contrib
%exclude %{vagrant_dir}/contrib/bash
%{vagrant_dir}/vagrant.gemspec
%{vagrant_dir}/keys
%{vagrant_dir}/lib
%{vagrant_dir}/plugins
%exclude %{vagrant_dir}/scripts
%{vagrant_dir}/templates
%{vagrant_dir}/version.txt
%exclude %{vagrant_dir}/website
# TODO: This is suboptimal and may break, but can't see much better way ...
# TODO: This won't work on RHEL6
#%%dir %{dirname:%{bashcompletion_dir}}
%dir %{bashcompletion_dir}
%{bashcompletion_dir}/%{pkg_name}
%dir %{vagrant_plugin_conf_dir}
%ghost %attr(0664, root, root) %{vagrant_plugin_conf_dir}/plugins.json
%{rpmmacrodir}/macros.%{pkg_name}%{?scl:.%{scl}}

# Explicitly include Vagrant plugins directory strucure to avoid accidentally
# packaged content.
%dir %{vagrant_plugin_dir}
%dir %{vagrant_plugin_dir}/gems
%dir %{vagrant_plugin_dir}/cache
%dir %{vagrant_plugin_dir}/specifications
%dir %{vagrant_plugin_dir}/doc

%files doc
%doc CONTRIBUTING.md CHANGELOG.md README.md
%{vagrant_dir}/Gemfile
%{vagrant_dir}/Rakefile
%{vagrant_dir}/tasks
%{vagrant_dir}/test
%{vagrant_dir}/vagrant-spec.config.example.rb

%changelog
* Tue May 03 2016 Tomas Hrcka <thrcka@redhat.com> - 1.8.1-2
- New upstream release 

* Tue Sep 08 2015 Josef Stribny <jstribny@redhat.com> - 1.7.4-3
- Remove locking of C extentions versions

* Mon Sep 07 2015 Josef Stribny <jstribny@redhat.com> - 1.7.4-2
- Fix dependencies

* Mon Sep 07 2015 Josef Stribny <jstribny@redhat.com> - 1.7.4-1
- Update to 1.7.4
- Patch: install plugins in isolation

* Thu Aug 06 2015 Vít Ondruch <vondruch@redhat.com> - 1.7.2-6
- Provide fallback back-completion location for RHEL6.
- Resolves: rhbz#1250318

* Tue Jul 21 2015 Vít Ondruch <vondruch@redhat.com> - 1.7.2-5
- Apply the patch cleanly.

* Fri Jun 12 2015 Josef Stribny <jstribny@redhat.com> - 1.7.2-4
- Requires pkgconfig on RHEL 6

* Fri Jun 12 2015 Josef Stribny <jstribny@redhat.com> - 1.7.2-3
- Update spec for rh-vagrant1 and disable tests for now

* Mon Mar 02 2015 Josef Stribny <jstribny@redhat.com> - 1.7.2-2
- Add missing runtime dependencies for 1.7.2

* Thu Feb 19 2015 Josef Stribny <jstribny@redhat.com> - 1.7.2-1
- Update to Vagrant 1.7.2
- Prepare and own plugin directory structure

* Mon Dec 15 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-23
- Fix RPM macro dir for RHEL 6

* Mon Dec 15 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-22
- Add explicit dep on vagrant1-runtime

* Thu Dec 04 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-21
- Run gem install within scl enable
- Edit file list to reach RHEL6 compatibility

* Thu Dec 04 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-20
- Ask on config(bash-completion) on RHEL6
- Fix version requirement of nokogiri and ruby-libvirt

* Wed Dec 03 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-19
- Fix vagrant plugin path in GEM_PATH

* Wed Dec 03 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-18
- Set up GEM_PATH for SCL
- Fix Ruby path in macros.vagrant
- List vagrant plugin dir correctly
- Enable test again

* Fri Nov 28 2014 Tomas Hrcka <thrcka@redhat.com> - 1.6.5-17
- Install macros scl way
 
* Thu Nov 27 2014 Tomas Hrcka <thrcka@redhat.com> - 1.6.5-16
- Disable tests for now.
 
* Thu Nov 27 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-15
- Add SCL macros

* Wed Nov 26 2014 Vít Ondruch <vondruch@redhat.com> - 1.6.5-14
- Drop -devel sub-package.

* Tue Nov 25 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-13
- Create -devel sub-package

* Mon Nov 24 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-12
- Include monkey-patching for RubyGems and Bundler for now

* Wed Oct 22 2014 Vít Ondruch <vondruch@redhat.com> - 1.6.5-11
- Make vagrant non-rubygem package.

* Tue Oct 14 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-10
- rebuilt

* Tue Oct 07 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-9
- Register vagrant-libvirt automatically

* Tue Sep 30 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-8
- Set libvirt as a default provider

* Tue Sep 23 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-7
- Require core dependencies for vagrant-libvirt beforehand

* Mon Sep 22 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-6
- Fix SSL cert path for the downloader

* Tue Sep 16 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-5
- rebuilt

* Tue Sep 16 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-4
- rebuilt

* Sat Sep 13 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-3
- Include libvirt requires for now

* Wed Sep 10 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-2
- Add missing deps on Bundler and hashicorp-checkpoint

* Mon Sep 08 2014 Josef Stribny <jstribny@redhat.com> - 1.6.5-1
* Update to 1.6.5

* Mon Sep 08 2014 Josef Stribny <jstribny@redhat.com> - 1.6.3-2
- Clean up
- Update to 1.6.3

* Fri Oct 18 2013  <adrahon@redhat.com> - 1.3.3-1.1
- Misc bug fixes, no separate package for docs, /etc/vagrant management

* Tue Sep 24 2013  <adrahon@redhat.com> - 1.3.3-1
- Initial package
