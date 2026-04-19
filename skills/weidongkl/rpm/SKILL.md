# RPM Expert 技能 - RPM 包管理专家（完整版）

## 技能描述 | Skill Description

**名称 | Name:** rpm  
**版本 | Version:** 3.1.0  
**作者 | Author:** OS Build Agent (OBS Expert)  
**领域 | Domain:** RPM Package Management (Red Hat/Fedora/CentOS/openSUSE/openEuler)

专业级 RPM 包管理技能，提供全面的 RPM 包管理、构建、验证、签名、依赖分析、构建系统集成和自动化构建功能。

Advanced-level RPM Package Management skill with comprehensive package management, building, verification, signing, dependency analysis, build system integration, and automated building.

**依赖 | Dependencies:** 无（独立技能）  
**扩展 | Extensions:** openeuler-rpm (openEuler 专项扩展)

---

## ⭐ 核心特性 | Key Features

### 1. Spec 文件分析与优化 | Spec File Analysis & Optimization
- ✅ 自动检测 spec 文件问题 | Auto-detect spec file issues
- ✅ 提供优化建议 | Provide optimization suggestions
- ✅ 符合官方打包指南 | Comply with official packaging guidelines
- ✅ openEuler 专用检查 | openEuler-specific checks

### 2. 多构建系统支持 | Multi-Build System Support
- Autotools, CMake, Meson, SCons, Makefile
- Python (setup.py, pyproject.toml, setuptools)
- Node.js (npm), Java (Maven, Gradle)
- Ruby (Gem), PHP (Composer)

### 3. 自动化构建 | Automated Building
- 本地构建 | Local building
- Mock 构建 | Mock building
- OBS 构建 | OBS building
- CI/CD 集成 | CI/CD integration

### 4. 包验证与测试 | Package Verification & Testing
- RPMLint 集成 | RPMLint integration
- 签名验证 | Signature verification
- 文件完整性检查 | File integrity check
- 运行时测试 | Runtime testing

### 5. 依赖管理 | Dependency Management
- 自动依赖生成 | Auto dependency generation
- 依赖解析 | Dependency resolution
- 依赖冲突检测 | Dependency conflict detection
- 反向依赖查询 | Reverse dependency query

### 6. 宏系统深入理解 | Macro System Deep Dive
- 宏定义与展开 | Macro definition & expansion
- 宏调试 | Macro debugging
- 宏文档查询 | Macro documentation
- 宏覆盖 | Macro override

### 7. 构建环境管理 | Build Environment Management
- 构建容器化 | Build containerization
- 构建隔离 | Build isolation
- 构建缓存 | Build caching
- 构建优化 | Build optimization

### 8. openEuler 专项支持 | openEuler-Specific Support
- openEuler 打包规范 | openEuler packaging standards
- openEuler 包拆分规则 | openEuler package splitting rules
- openEuler 验收检查 | openEuler acceptance checklist
- openEuler 自定义宏 | openEuler custom macros

---

## 📁 本文档结构 | Document Structure

### 1️⃣ 核心能力 | Core Capabilities
- Spec 文件分析与优化
- 多构建系统支持
- 自动化构建
- 包验证与测试
- 依赖管理
- 宏系统深入理解
- 构建环境管理
- openEuler 专项支持

### 2️⃣ RPM 基础功能 | RPM Basic Functions
- RPM 查询 | RPM Query
- RPM 创建 | RPM Creation
- RPM 验证 | RPM Verification
- RPM 签名 | RPM Signing
- 依赖分析 | Dependency Analysis
- Spec 文件检查 | Spec File Linting
- 宏管理 | Macro Management
- 数据库管理 | Database Management

### 3️⃣ Spec 文件最佳实践 | Spec File Best Practices
- 标准模板 | Standard Template
- Spec 文件结构说明 | Spec Structure
- 常见模式 | Common Patterns

### 4️⃣ 构建系统支持 | Build System Support
- Autotools | Autotools
- CMake | CMake
- Meson | Meson
- Python | Python
- Node.js | Node.js

### 5️⃣ 高级功能 | Advanced Features
- 构建环境管理 | Build Environment Management
- CI/CD 集成 | CI/CD Integration
- openEuler 专项支持 | openEuler-Specific Support

### 6️⃣ 工作流与模板 | Workflows & Templates
- RPM 构建工作流 | RPM Build Workflow
- openEuler 构建工作流 | openEuler Build Workflow
- Spec 文件模板 | Spec File Templates

---

## 📋 RPM 基础功能 | RPM Basic Functions

### 1️⃣ RPM 查询 | RPM Query

#### 查询已安装包 | Query Installed Packages

```bash
# 查询所有已安装包 | Query all installed packages
rpm -qa

# 查询特定包 | Query specific package
rpm -qi httpd

# 查询包文件列表 | Query package files
rpm -ql httpd

# 查询包依赖 | Query package dependencies
rpm -qR httpd

# 查询包提供 | Query package provides
rpm -q --provides httpd

# 查询 changelog/脚本/触发器 | Query changelog/scripts/triggers
rpm -q --changelog httpd
rpm -q --scripts httpd
rpm -q --triggers httpd

# 查询文件归属 | Query file ownership
rpm -qf /etc/httpd/conf/httpd.conf

# 查询配置文件 | Query config files
rpm -qc httpd

# 查询文档文件 | Query documentation files
rpm -qd httpd
```

#### 查询 RPM 文件 | Query RPM Files

```bash
# 查询 RPM 文件信息 | Query RPM file info
rpm -qip ./httpd-2.4.57-1.rpm

# 查询 RPM 文件依赖 | Query RPM file dependencies
rpm -qp --requires ./httpd-2.4.57-1.rpm

# 查询 RPM 文件提供 | Query RPM file provides
rpm -qp --provides ./httpd-2.4.57-1.rpm

# 查询 RPM 文件脚本 | Query RPM file scripts
rpm -qp --scripts ./httpd-2.4.57-1.rpm
```

#### 查询已安装包详情 | Query Installed Package Details

```bash
# 查询包详细信息 | Query package details
rpm -qi package-name

# 查询包安装时间 | Query package installation time
rpm -qi package-name | grep "Install Date"

# 查询包签发者 | Query package vendor
rpm -qi package-name | grep "Vendor"

# 查询包签名 | Query package signature
rpm -qi package-name | grep "Signature"
```

### 2️⃣ RPM 创建 | RPM Creation

#### 设置构建环境 | Set Up Build Environment

```bash
# 安装构建工具 | Install build tools
dnf install -y rpm-build rpmdevtools

# 设置构建目录 | Set up build directories
rpmdev-setuptree

# 检查目录结构 | Check directory structure
tree ~/rpmbuild/
```

#### 创建 Spec 文件 | Create Spec File

```bash
# 使用模板创建 spec 文件 | Create spec file with template
rpmdev-newspec -o mypackage.spec mypackage

# 使用最小模板 | Use minimal template
rpmdev-newspec -t minimal mypackage.spec

# 使用 Python 模板 | Use Python template
rpmdev-newspec -t python mypackage.spec

# 使用 C 模板 | Use C template
rpmdev-newspec -t c mypackage.spec
```

#### 构建 SRPM | Build SRPM

```bash
# 从 spec 文件构建 SRPM | Build SRPM from spec
rpmbuild -bs mypackage.spec

# 从 spec 文件构建 SRPM 并指定源码目录 | Build SRPM with custom sources
rpmbuild -bs --define "_sourcedir /path/to/sources" mypackage.spec

# 使用 osc 构建 SRPM | Build SRPM with osc
osc build -- srpm
```

#### 构建 RPM | Build RPM

```bash
# 构建二进制 RPM | Build binary RPM
rpmbuild -bb mypackage.spec

# 构建 SRPM + RPM | Build SRPM + RPM
rpmbuild -ba mypackage.spec

# 使用 mock 构建 (推荐) | Build with mock (recommended)
mock -r fedora-39-x86_64 mypackage.spec

# 使用 build 工具 (openSUSE) | Build with build tool (openSUSE)
build --root=/path/to/root mypackage.spec

# 使用 osc 构建 | Build with osc
osc build
```

### 3️⃣ RPM 验证 | RPM Verification

```bash
# 验证所有包 | Verify all packages
rpm -Va

# 验证特定包 | Verify specific package
rpm -V httpd

# 验证配置文件 | Verify config files
rpm -Vf /etc/httpd/conf/httpd.conf

# 验证并显示详细信息 | Verify with details
rpm -Vv httpd
```

#### 验证结果代码 | Verification Result Codes

```
S: 文件大小不匹配 | File size mismatch
M: 模式不匹配 | Mode mismatch (permissions/filetype)
5: MD5 校验和不匹配 | MD5 digest mismatch
D: 设备号不匹配 | Device number mismatch
L: 符号链接不正确 | Symbolic link incorrect
U: 用户不匹配 | User mismatch
G: 组不匹配 | Group mismatch
T: 修改时间不匹配 | File mtime mismatch
c: 配置文件 | Config file
d: 文档文件 | Documentation file
g: ghost file | Ghost file
```

### 4️⃣ RPM 签名 | RPM Signing

```bash
# 签名 RPM 包 | Sign RPM package
rpm --addsign ./mypackage-1.0-1.x86_64.rpm

# 重新签名 | Resign
rpm --resign ./mypackage-1.0-1.x86_64.rpm

# 删除签名 | Delete signature
rpm --delsign ./mypackage-1.0-1.x86_64.rpm

# 检查签名 | Check signature
rpm -K ./mypackage-1.0-1.x86_64.rpm

# 导入 GPG 密钥 | Import GPG key
rpm --import RPM-GPG-KEY-example

# 列出 GPG 密钥 | List GPG keys
rpm -qa gpg-pubkey*
```

### 5️⃣ 依赖分析 | Dependency Analysis

```bash
# 查找提供命令的包 | Find package providing command
rpm -qf $(which command)

# 查找提供文件的包 | Find package providing file
rpm -qf /path/to/file

# 查找提供依赖的包 | Find package providing dependency
rpm -q --whatprovides libexample.so

# 查找依赖某包的包 | Find packages requiring this package
rpm -q --whatrequires httpd

# 检查未满足依赖 | Check unsatisfied dependencies
rpm -qp --requires ./package.rpm

# 解析依赖 | Resolve dependencies
dnf whatprovides libexample.so
# or
yum whatprovides libexample.so

# 列出包的反向依赖 | List reverse dependencies
rpm -q --recommends httpd
```

### 6️⃣ Spec 文件检查 | Spec File Linting

#### 使用 RPMLint | Using RPMLint

```bash
# 检查 spec 文件 | Check spec file
rpmlint mypackage.spec

# 检查 RPM 文件 | Check RPM file
rpmlint ./mypackage-1.0-1.x86_64.rpm

# 检查并显示详细信息 | Check with detailed info
rpmlint -v mypackage.spec

# 检查并显示解释 | Check with explanation
rpmlint -I mypackage.spec

# 检查并输出 JSON | Check with JSON output
rpmlint --output json mypackage.spec
```

#### 常见 RPMLint 错误 | Common RPMLint Errors

```
# 错误 | Errors
mypackage.spec: W: summary-not-capitalized
  Summary should start with a capital letter

mypackage.spec: W: no-description
  Package has no %description

mypackage.spec: W: no-changelogname
  Changelog should have packager name and email

mypackage.spec: E: invalid-license GPL
  License not found in standard license list

mypackage.spec: E: spurious-executable-permission
  File has executable permission but is not a script

# 警告 | Warnings
mypackage-1.0-1.x86_64.rpm: W: shared-lib-calls-exit
  shared library calls exit() or=_exit()

mypackage-1.0-1.x86_64.rpm: W: dangling-symlink
  Symlink points to non-existent file
```

### 7️⃣ 宏管理 | Macro Management

```bash
# 列出所有宏 | List all macros
rpm --showrc

# 列出特定宏 | List specific macro
rpm --eval '%{_topdir}'

# 展开宏 | Expand macro
rpm --eval '%{name}'

# 定义宏 | Define macro
echo '%_my_macro value' >> ~/.rpmmacros

# 查看宏文件 | View macro files
cat /usr/lib/rpm/macros

# 检查 spec 文件中的宏 | Check macros in spec file
rpmspec -E mypackage.spec
```

### 8️⃣ 数据库管理 | Database Management

```bash
# 重建 RPM 数据库 | Rebuild RPM database
rpm --rebuilddb

# 验证数据库 | Verify database
rpm --verifydb

# 清理数据库 | Clean database
rpm --clean

# 初始化数据库 | Initialize database
rpm --initdb

# 导出数据库 | Export database
rpm -qa --dump > rpmdb-export.txt

# 导入数据库 | Import database
rpm --import RPM-GPG-KEY*
```

---

## ⚙️ Spec 文件最佳实践 | Spec File Best Practices

### 标准模板 | Standard Template

```spec
Name:           mypackage
Version:        1.0.0
Release:        0%{?dist}
Summary:        Package summary here

License:        MIT
URL:            https://example.com
Source0:        %{url}/releases/%{name}-%{version}.tar.gz
# Source0:      https://github.com/user/repo/releases/download/%{version}/%{name}-%{version}.tar.gz

# BuildArch:    noarch  # 仅用于无架构依赖的包
# BuildArch:    x86_64  # 仅用于特定架构

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig

# AutoReq:      no      # 可选：禁用自动依赖
Requires:       glibc >= 2.17

# patches 补丁
# Patch0:       fix-build.patch

%description
Detailed package description goes here.
Multiple lines are supported.
Multiple paragraphs are supported.

%prep
%autosetup -p1
# or | 或
# %setup -q
# %patch0 -p1

%build
%configure
%make_build

%install
%make_install

# %check 阶段：运行单元测试
%check
%make_test
# or | 或
# make test

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}*.1*
%{_datadir}/%{name}/

%changelog
* Thu Apr 16 2026 Your Name <your@email.com> - 1.0.0-1
- Update to 1.0.0
- Fix build with modern cmake
- Add unit tests

* Fri Mar 22 2024 Your Name <your@email.com> - 0.9.0-1
- Initial package
```

### Spec 文件结构说明 | Spec Structure

| 部分 | 说明 | Description |
|------|------|-------------|
| **Preamble** | 元数据部分，定义包的基本信息 | Metadata section |
| **Name** | 包名，必须与 spec 文件名一致 | Package name |
| **Version** | 上游版本号 | Upstream version |
| **Release** | 发布号，初始为 0%{?dist} | Release number |
| **Summary** | 简短描述 | Short description |
| **License** | 许可证 | License |
| **URL** | 项目主页 | Project URL |
| **Source0** | 源码包路径/URL | Source package |
| **BuildArch** | 构建架构 | Build architecture |
| **BuildRequires** | 构建时依赖 | Build-time dependencies |
| **Requires** | 运行时依赖 | Runtime dependencies |
| **%prep** | 准备阶段：解压、打补丁 | Preparation |
| **%build** | 构建阶段：编译 | Build |
| **%install** | 安装阶段：安装到 buildroot | Install |
| **%check** | 测试阶段：运行测试 | Tests |
| **%files** | 文件列表 | File list |
| **%changelog** | 变更日志 | Changelog |

---

## 🔧 构建系统支持 | Build System Support

### Autotools | Autotools

```spec
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool

%prep
%autosetup -p1

%build
%configure
%make_build

%install
%make_install

%check
make test
```

### CMake | CMake

```spec
BuildRequires:  cmake
BuildRequires:  make

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install

%check
%ctest
```

### Meson | Meson

```spec
BuildRequires:  meson
BuildRequires:  ninja-build

%prep
%autosetup -p1

%build
%meson
%ninja_build

%install
%ninja_install

%check
%ninja_test
```

### Python | Python

```spec
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%pyproject_build_wheel
%pyproject_install

%install
%pyproject_make_binary

%check
%pyproject_check
```

### Node.js | Node.js

```spec
BuildRequires:  nodejs
BuildRequires:  npm

%prep
%autosetup -p1 -n package

%build
npm install --production=false
npm run build

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -r . %{buildroot}%{_datadir}/%{name}/

%files
%license LICENSE
%doc README.md
%{_datadir}/%{name}/
```

---

## 🚀 高级功能 | Advanced Features

### 构建环境管理 | Build Environment Management

#### Mock 构建 | Mock Building

```bash
# 安装 mock | Install mock
dnf install -y mock

# 初始化构建环境 | Initialize build environment
mock -r fedora-39-x86_64 --init

# 构建 SRPM | Build SRPM
mock -r fedora-39-x86_64 --buildsrpm --spec mypackage.spec --sources .

# 构建 RPM | Build RPM
mock -r fedora-39-x86_64 --rebuild mypackage-1.0-1.fc39.src.rpm

# 使用自定义配置 | Use custom configuration
mock -r fedora-39-x86_64 --configdir ./configs/ --rebuild mypackage.rpm

# 查看构建日志 | View build logs
mock -r fedora-39-x86_64 --tail-log

# 清理构建环境 | Clean build environment
mock -r fedora-39-x86_64 --clean
```

#### OBS 构建 | OBS Building

```bash
# 检出 OBS 项目 | Checkout OBS project
osc checkout <project>

# 检出 OBS 包 | Checkout OBS package
osc checkout <project> <package>

# 构建本地包 | Build local package
osc build

# 构建特定架构 | Build for specific architecture
osc build <repo> <arch>

# 构建 SRPM | Build SRPM
osc sr

# 查看构建结果 | View build results
osc results

# 重新构建 | Rebuild
osc rebuild <repo> <arch>

# 提交包 | Submit package
osc commit

# 创建提交请求 | Create submit request
osc sr <source_project> <source_package> <target_project> <target_package>
```

### CI/CD 集成 | CI/CD Integration

#### GitHub Actions 示例 | GitHub Actions Example

```yaml
# .github/workflows/build.yml
name: Build RPM

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install RPM tools
        run: |
          sudo apt-get update
          sudo apt-get install -y rpm-build rpmdevtools rpmlint
      
      - name: Setup build environment
        run: |
          rpmdev-setuptree
          cp -r . ~/rpmbuild/SOURCES/
          cp *.spec ~/rpmbuild/SPECS/
      
      - name: Lint spec file
        run: rpmlint ~/rpmbuild/SPECS/*.spec
      
      - name: Build SRPM
        run: rpmbuild -bs ~/rpmbuild/SPECS/*.spec
      
      - name: Build RPM
        run: rpmbuild -bb ~/rpmbuild/SPECS/*.spec
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: rpm-packages
          path: ~/rpmbuild/RPMS/
```

---

## 🏗️ openEuler 专项支持 | openEuler-Specific Support

### openEuler 打包规范 | openEuler Packaging Standards

openEuler 遵守 [Linux 基础标准 (LSB)](http://www.linuxbase.org/) 和 [Linux 文件系统层级标准 (FHS)](http://www.pathname.com/fhs/)。

openEuler follows the [Linux Base Standard (LSB)](http://www.linuxbase.org/) and [Filesystem Hierarchy Standard (FHS)](http://www.pathname.com/fhs/).

**打包原则:** 不做复杂的拆分，将软件拆分为基本固定的 5 个 RPM 包，保持包的简洁。

**Packaging Principle:** Avoid complex splitting, package software into 5 basic RPM packages, keeping packages simple.

### openEuler 包拆分规则 | openEuler Package Splitting Rules

| 分类 | 包名 | 包含内容 | 关键点 |
|------|------|----------|--------|
| **主包** | 与软件源码包同名 | 1、命令、配置、so<br/>2、license、copyright、readme<br/>3、man、info手册 | 可通过 Provides、Obsoletes 兼容其他 OS |
| **libs包** | 软件包名-libs | 1、对外提供的动态库、命令 | 分离功能与能力，避免循环依赖 |
| **devel包** | 软件包名-devel | 1、头文件<br/>2、Example<br/>3、tests用例<br/>4、开发内容 | devel 包需 Requires 主包 |
| **static包** | 软件包名-static | 1、静态库.a<br/>2、静态版本 | 可使用宏控制 |
| **help包** | 软件包名-help | 二次开发文档、手册 | **文档大时才拆分** |

### openEuler 专用宏 | openEuler Custom Macros

```bash
# 删除 rpath
%disable_rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool \
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

# 删除 .la 和 .a 文件
%delete_la_and_a
find $RPM_BUILD_ROOT -type f -name "*.la" -delete \
find $RPM_BUILD_ROOT -type f -name "*.a" -delete

# 删除 .la 文件
%delete_la
find $RPM_BUILD_ROOT -type f -name "*.la" -delete

# 删除 chrpath
%chrpath_delete
find $RPM_BUILD_ROOT/ -type f -exec file {} ';' | grep "<ELF>" | awk -F ':' '{print $1}' | xargs chrpath --delete {}

# help 子包定义
%package_help
%package        help \
Summary:        Documents for %{name} \
Buildarch:      noarch \
Requires:               man info

%description help \
Man pages and other related documents for %{name}.

# info 工具
%install_info()
/sbin/install-info %1 %{_infodir}/dir || :

%install_info_rm()
/sbin/install-info --remove %1 %{_infodir}/dir || :
```

### openEuler 构建工作流 | openEuler Build Workflow

详见 [openeuler-rpm 技能](./openeuler-rpm/SKILL.md) 获取完整的 openEuler 专项支持和模板。

For complete openEuler-specific support and templates, see the [openeuler-rpm skill](./openeuler-rpm/SKILL.md).

---

## ⚠️ openEuler 专用规范 | openEuler-Specific Standards

### 来源可靠 | Source Reliability

- **不要内嵌预编译好的二进制文件或库文件**
- **避免多个上游项目捆绑到一个软件包**
- 软件应该是开源软件
- spec 文件要适配 openEuler
- 黑名单软件**必须不能**引入

### 架构支持 | Architecture Support

- 尽量支持 aarch64 和 x86_64 架构
- 架构强相关内容通过 `%ifarch` 宏控制
- 无架构内容构建成 noarch 包
- 使用 `ExcludeArch:` 或 `ExclusiveArch:` 控制

### openEuler changelog 格式 | openEuler Changelog Format

```spec
* Tue Apr 7 2020 openEuler Buildteam <buildteam@openeuler.org> - 10.33-3
- Type: CVES/Bugfix/Feature
- ID: CVE-2019-20454
- SUG: NA
- DESC: fix CVE-2019-20454
```

### openEuler 检视原则 | openEuler Review Guidelines

**必须项（MUST） | MUSTs:**
- ✅ 使用 rpmlint 工具检查
- ✅ 包命名符合 openEuler 规则
- ✅ License 字段匹配实际许可证
- ✅ spec 文件英语撰写
- ✅ 源代码匹配 spec 中 URL
- ✅ ExcludeArch 列出不支持架构
- ✅ BuildRequires 包含所有依赖
- ✅ 使用 %find_lang 处理区域设置
- ✅ 不将单一文件打包到多个 rpm
- ✅ 安装到 prefix（/usr）相对路径
- ✅ 正确设置文件权限
- ✅ devel 包：`Requires: %{name} = %{version}-%{release}`
- ✅ rpm 包文件名是有效的 UTF-8

---

## 📋 RPM 快速参考 | RPM Quick Reference

**快速开始 | Quick Start:**

```bash
# 1. 创建 spec 文件 | Create spec file
rpmdev-newspec -o mypackage.spec mypackage

# 2. 编辑 spec 文件 | Edit spec file
vim mypackage.spec

# 3. 构建 | Build
rpmbuild -ba mypackage.spec

# 4. 检查 | Check
rpmlint mypackage.spec
```

**Spec 文件核心部分 | Spec File Core Sections:**

| 部分 | 说明 | Example |
|------|------|---------|
| Preamble | 元数据 | Name, Version, Release, BuildRequires |
| %prep | 准备阶段 | %autosetup -p1 |
| %build | 构建阶段 | %configure / %cmake / %meson |
| %install | 安装阶段 | %make_install / %cmake_install |
| %check | 测试阶段 | %make_test / %ctest |
| %files | 文件列表 | %{_bindir}/%{name} |
| %changelog | 变更日志 | * Date Packager - Version |

**构建系统选择 | Build System Selection:**

```spec
# Autotools | Autotools
BuildRequires: autoconf, automake, libtool
%prep: %autosetup -p1
%build: %configure && %make_build
%install: %make_install

# CMake | CMake
BuildRequires: cmake
%prep: %autosetup -p1
%build: %cmake && %cmake_build
%install: %cmake_install

# Meson | Meson
BuildRequires: meson, ninja-build
%prep: %autosetup -p1
%build: %meson && %ninja_build
%install: %ninja_install

# Python | Python
BuildRequires: python3-devel, python3-setuptools
%prep: %autosetup -p1 -n %{name}-%{version}
%build: %pyproject_build_wheel && %pyproject_install
%install: %pyproject_make_binary
```

**常用宏 | Common Macros:**

| 宏 | 路径 | Path |
|------|------|-------------|
| `%{_bindir}` | /usr/bin |
| `%{_libdir}` | /usr/lib[64] |
| `%{_datadir}` | /usr/share |
| `%{_sysconfdir}` | /etc |
| `%{_docdir}` | /usr/share/doc |
| `%{_mandir}` | /usr/share/man |
| `%{_topdir}` | ~/rpmbuild |

**故障排除 | Troubleshooting:**

```bash
# 构建失败 | Build Failed
rpmbuild -vv -ba mypackage.spec

# RPMLint 检查 | RPMLint Check
rpmlint mypackage.spec
rpmlint -I mypackage.spec  # with explanation

# 依赖问题 | Dependency Issues
dnf whatprovides libexample.so
```

---

## 📚 参考资料 | References

### 官方文档 | Official Documentation

- [RPM 官方文档](https://rpm.org/documentation.html)
- [RPM 打包指南](https://rpm-packaging-guide.github.io/)
- [Fedora 打包指南](https://docs.fedoraproject.org/en-US/packaging-guidelines/)
- [openSUSE 打包指南](https://en.opensuse.org/openSUSE:Packaging_guidelines)
- [openEuler 打包指南](https://openeuler.org/zh/documentations/docs/packaging-guidelines.html)

### 构建系统 | Build Systems

- [GNU Autotools](https://www.gnu.org/software/automake/manual/autoconf/)
- [CMake](https://cmake.org/documentation/)
- [Meson](https://mesonbuild.com/)
- [Makefile](https://www.gnu.org/software/make/manual/)

### 工具 | Tools

- [rpmlint](https://github.com/rpmlint/rpmlint)
- [mock](https://github.com/rpmlint/mock)
- [osc](https://github.com/openSUSE/osc)
- [rpmdevtools](https://github.com/rpm-software-management/rpmdevtools)

---

## 🔧 命令参考 | Command Reference

| 命令 | 描述 | Description |
|------|------|-------------|
| `rpm -qa` | 查询所有已安装包 | Query all installed |
| `rpm -qi` | 包信息 | Package info |
| `rpm -ql` | 包文件列表 | Package files |
| `rpm -qR` | 包依赖 | Package requires |
| `rpm -qc` | 配置文件 | Config files |
| `rpm -qd` | 文档文件 | Documentation files |
| `rpm -qf` | 文件归属 | File ownership |
| `rpm -V` | 验证包 | Verify package |
| `rpm -Va` | 验证所有包 | Verify all |
| `rpm -K` | 检查签名 | Check signature |
| `rpm --addsign` | 签名包 | Sign package |
| `rpm --import` | 导入密钥 | Import key |
| `rpm --rebuilddb` | 重建数据库 | Rebuild database |
| `rpmbuild -ba` | 构建 SRPM+RPM | Build SRPM+RPM |
| `rpmbuild -bs` | 构建 SRPM | Build SRPM |
| `rpmbuild -bb` | 构建 RPM | Build RPM |
| `rpmlint` | 检查 spec/RPM | Lint spec/RPM |
| `osc build` | OBS 构建 | OBS build |
| `osc sr` | OBS 提交请求 | OBS SR |

---

## 📖 最佳实践 | Best Practices

### 1. Spec 文件编写 | Spec File Writing

- ✅ 使用 `%autosetup` 代替手动 `%setup`
- ✅ 使用 `%buildroot` 代替 `$RPM_BUILD_ROOT`
- ✅ 使用标准宏如 `%{_bindir}`, `%{_datadir}`
- ✅ 遵循 openSUSE/Fedora/openEuler 打包指南
- ✅ 提供详细的 changelog 条目
- ✅ 使用 `%check` 阶段运行单元测试
- ✅ 优先使用 `%pyproject_*` 宏用于 Python 包
- ✅ 使用 `%cmake_*` 宏用于 CMake 项目
- ✅ 定期运行 `rpmlint` 检查 spec 文件
- ✅ openEuler: 使用专用 changelog 格式

### 2. 构建优化 | Build Optimization

- ✅ 使用并行构建 `make %{?_smp_mflags}`
- ✅ 使用 mock 或 OBS 进行干净构建
- ✅ 清理构建环境中的临时文件
- ✅ 使用 `BuildRequires` 明确声明构建依赖
- ✅ 使用 `Requires` 明确声明运行时依赖
- ✅ 避免使用 `AutoReq: no` 除非必要
- ✅ 使用 `%{?dist}` 标签区分发行版
- ✅ openEuler: 使用专用宏清理构建产物

### 3. 质量控制 | Quality Control

- ✅ 运行 `rpmlint` 检查 spec 文件
- ✅ 验证签名和校验和
- ✅ 测试安装和卸载
- ✅ 检查依赖完整性
- ✅ 验证文件权限和所有权
- ✅ 检查文档和文档文件
- ✅ 运行单元测试通过 `make test`
- ✅ openEuler: 运行 make check 自测用例

---

## 📅 版本历史 | Changelog

### v3.1.0 (2026-04-17) ⭐⭐⭐ 新增功能 | New Features

- **RPM 快速参考：** 添加 RPM 快速参考章节
- **Quick Start：** 提供快速开始指南
- **Build System 选择表：** 添加构建系统选择表
- **宏参考表：** 添加常用宏参考表

### v3.0.0 (2026-04-17) ⭐⭐⭐ 重大更新 | Major Update

- **功能合并：** 整合 rpm-expert 的全部功能
- **全新结构：** 重新组织文档结构，清晰分类
- **openEuler 支持：** 添加 openEuler 专项支持章节
- **工作流指导：** 提供完整的 RPM 和 openEuler 构建工作流
- **模板示例：** 添加完整的 Spec 文件模板和示例

### v2.0.0 (2026-04-16)
- 更新 spec 文件模板以符合最新最佳实践
- 添加现代构建系统支持：CMake, Meson, PyProject
- 添加 RPMLint 集成和常见错误解释
- 优化宏使用说明和示例
- 添加 OBS 工作流最佳实践
- 更新故障排除部分

### v1.0.0 (2026-03-23)
- 初始版本，完整的 RPM 管理支持
- 中英文双语文档

---

## 📄 许可证 | License

MIT License - 与 OpenClaw AgentSkills 规范兼容  
MIT License - Compatible with OpenClaw AgentSkills specification
