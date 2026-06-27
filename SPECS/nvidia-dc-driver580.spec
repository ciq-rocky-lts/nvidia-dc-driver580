%global debug_package %{nil}
%global __strip /bin/true
%global __brp_ldconfig %{nil}
%define _build_id_links none
# To allow firmware to be noarch
%define _binaries_in_noarch_packages_terminate_build 0

# This should be set to 1 for whichever major version is considered the latest release and 0 for all other builds.  If set to 1,
# a -latest package will be built that contains exactly the same files and scripts that are in the base package
%define is_latest_release 0

# Used for major-version meta package.
%define major_version 580

# nvidia-persistenced version (seems to be kept in sync with desktop driver, but doesn't change frequently, so this shouldn't be an issue)
# The rpm will have the driver version rather than the upstream version.  I'm not super happy about it, but the alternatives are to either push
# persistenced into a separate package or run the risk of duplicate NEVRAs being generated.
%define persistenced_version %{major_version}.159.03

# Package name without major version namespace
%define name_no_version nvidia-dc-driver

# Upstream epoch
%define upstream_epoch 3

%define fabricarch %{_arch}
%ifarch aarch64
%define fabricarch sbsa
%endif

%global _systemd_util_dir %{_prefix}/lib/systemd

Name:           %{name_no_version}%{major_version}
Version:        %{major_version}.159.03
Release:        1%{?dist}
Summary:        NVIDIA's proprietary display driver for NVIDIA Datacenter graphic cards (major version %{major_version})
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html
ExclusiveArch:  %{ix86} x86_64 aarch64

Source0:        nvidia-driver-%{version}-i386.tar.xz
Source1:        nvidia-driver-%{version}-x86_64.tar.xz
Source2:        nvidia-driver-%{version}-aarch64.tar.xz
Source3:        nvidia-kmod-common-%{version}.tar.xz
Source4:        https://github.com/NVIDIA/nvidia-persistenced/archive/refs/tags/%{persistenced_version}/nvidia-persistenced-%{persistenced_version}.tar.gz
Source5:        https://developer.download.nvidia.com/compute/nvidia-driver/redist/fabricmanager/linux-x86_64/fabricmanager-linux-x86_64-%{version}-archive.tar.xz
Source6:        https://developer.download.nvidia.com/compute/nvidia-driver/redist/fabricmanager/linux-sbsa/fabricmanager-linux-sbsa-%{version}-archive.tar.xz
Source7:        https://developer.download.nvidia.com/compute/nvidia-driver/redist/libnvsdm/linux-x86_64/libnvsdm-linux-x86_64-%{version}-archive.tar.xz
Source8:        https://developer.download.nvidia.com/compute/nvidia-driver/redist/imex/linux-x86_64/imex-linux-x86_64-%{version}-archive.tar.xz
Source9:        https://developer.download.nvidia.com/compute/nvidia-driver/redist/imex/linux-sbsa/imex-linux-sbsa-%{version}-archive.tar.xz
Source10:       https://developer.download.nvidia.com/compute/nvidia-driver/redist/libnvidia_nscq/linux-x86_64/libnvidia_nscq-linux-x86_64-%{version}-archive.tar.xz
Source11:       https://developer.download.nvidia.com/compute/nvidia-driver/redist/libnvidia_nscq/linux-sbsa/libnvidia_nscq-linux-sbsa-%{version}-archive.tar.xz

Source30:       70-nvidia.preset
Source31:       10-nvidia.conf
Source32:       alternate-install-present
Source33:       nvidia-persistenced.service
Source34:       70-nvidia-persistenced.preset

Source40:       com.nvidia.driver.metainfo.xml
Source41:       parse-supported-gpus.py
Source42:       com.nvidia.driver.png
Source43:       nvidia-uvm.conf

Source90:       nvidia-generate-tarballs.sh
Source91:       nvidia-generate-tarballs-aarch64.sh

%ifarch x86_64 aarch64
BuildRequires:  gcc
BuildRequires:  libtirpc-devel
BuildRequires:  m4
BuildRequires:  libappstream-glib
BuildRequires:  python3
%endif
BuildRequires:  systemd-rpm-macros

%define global_requires_name() %{expand:\
Requires:       %{name_no_version}%1-gpu%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       %{name_no_version}%1-cuda%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       %{name_no_version}-there-can-be-only-one
Conflicts:      (%{name_no_version}-there-can-be-only-one without %{name_no_version}%1)
}

%global_requires_name %{major_version}

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with recent NVIDIA chipsets.

For the full product support list, please consult the release notes for driver
version %{version}.


%define global_requires_gpu() %{expand:\
Requires:       %{name_no_version}%1-gpu-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
%if 0%{?rhel} < 10
Requires:       xorg-x11-server-Xorg%{?_isa}
%endif
%{?systemd_requires}

Provides:       nvidia-driver = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      nvidia-driver
Provides:       %{name_no_version}-gpu-there-can-be-only-one
Conflicts:      (%{name_no_version}-gpu-there-can-be-only-one without %{name_no_version}%1-gpu)
Provides:       nvidia-drivers
Conflicts:      nvidia-x11-drv
Conflicts:      nvidia-x11-drv-470xx
Conflicts:      xorg-x11-drv-nvidia
Conflicts:      xorg-x11-drv-nvidia-470xx
}

%package gpu
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards (major version %{major_version})
%global_requires_gpu %{major_version}

%description gpu
This package provides the GPU integration components for %{name}.


# Workaround because of Peridot issues when multiple versions of the same noarch package are created
%ifarch x86_64
%define global_requires_firmware() %{expand:\
BuildArch:      noarch
Provides:       nvidia-kmod-common = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      nvidia-kmod-common
Requires:       kmod-custom(nvidia-dc-cuda%1) = %{version}
}

%package -n nvidia-dc-firmware%{major_version}
Summary:        Firwmare for NVIDIA GPUs
%global_requires_firmware %{major_version}

%description -n nvidia-dc-firmware%{major_version}
This package provides the NVIDIA GPU firmware for %{name}.
%endif


%define global_requires_gpu_libs() %{expand:\
Provides:       nvidia-driver-libs = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      nvidia-driver-libs
Requires:       egl-gbm%{?_isa} >= 1.1.2
Requires:       egl-wayland%{?_isa} >= 1.1.13.1
Requires:       nvidia-dc-firmware%1 = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libvdpau%{?_isa} >= 0.5
Requires:       libglvnd%{?_isa} >= 1.0
Requires:       libglvnd-egl%{?_isa} >= 1.0
Requires:       libglvnd-gles%{?_isa} >= 1.0
Requires:       libglvnd-glx%{?_isa} >= 1.0
Requires:       libglvnd-opengl%{?_isa} >= 1.0
Requires:       libnvidia-dc%1-ml%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       vulkan-loader

Provides:       egl-x11
Conflicts:      egl-x11
Conflicts:      nvidia-x11-drv-libs
Conflicts:      nvidia-x11-drv-470xx-libs
Conflicts:      xorg-x11-drv-nvidia-libs
Conflicts:      xorg-x11-drv-nvidia-470xx-libs
# Funky boolean dependency to ensure that, if any CUDA driver is installed, it's ours
Conflicts:      (nvidia-driver-cuda-libs without %{name_no_version}%1-cuda-libs = %{?epoch:%{epoch}:}%{version}-%{release})
Suggests:       %{name_no_version}%1-cuda-libs = %{?epoch:%{epoch}:}%{version}-%{release}
}

%package gpu-libs
Summary:        GPU Libraries for %{name}
%global_requires_gpu_libs %{major_version}

%description gpu-libs
This package provides the shared GPU libraries for %{name}.


%define global_requires_cuda_libs() %{expand:\
Provides:       nvidia-driver-cuda-libs = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      nvidia-driver-cuda-libs
Provides:       %{name_no_version}-cuda-libs-there-can-be-only-one
Conflicts:      (%{name_no_version}-cuda-libs-there-can-be-only-one without %{name_no_version}%1-cuda-libs)
Provides:       nvidia-driver-devel = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      nvidia-driver-devel
Provides:       %{name_no_version}%1-devel = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libnvidia-dc%1-ml%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       nvidia-dc-firmware%1 = %{?epoch:%{epoch}:}%{version}-%{release}
%ifarch x86_64 aarch64
Requires:       libnvidia-dc%1-cfg%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
%endif

Conflicts:      xorg-x11-drv-nvidia-cuda-libs
Conflicts:      xorg-x11-drv-nvidia-470xx-cuda-libs
# Funky boolean dependency to ensure that, if any NVIDIA driver is installed, it's ours
Conflicts:      (nvidia-driver-libs without %{name_no_version}%1-gpu-libs = %{?epoch:%{epoch}:}%{version}-%{release})
Suggests:       %{name_no_version}%1-gpu-libs = %{?epoch:%{epoch}:}%{version}-%{release}
}

%package cuda-libs
Summary:        Libraries for %{name}-cuda
%global_requires_cuda_libs %{major_version}

%description cuda-libs
This package provides the CUDA libraries for %{name}-cuda.


%define global_requires_fbc() %{expand:\
Provides:       libnvidia-fbc = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      libnvidia-fbc
Provides:       nvidia-driver-NvFBCOpenGL = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
# Loads libnvidia-encode.so at runtime
Requires:       %{name_no_version}%1-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
}

%package -n libnvidia-dc%{major_version}-fbc
Summary:        NVIDIA OpenGL-based Framebuffer Capture libraries
%global_requires_fbc %{major_version}

%description -n libnvidia-dc%{major_version}-fbc
This library provides a high performance, low latency interface to capture and
optionally encode the composited framebuffer of an X screen. NvFBC are private
APIs that are only available to NVIDIA approved partners for use in remote
graphics scenarios.


%define global_requires_ml() %{expand:\
Provides:       libnvidia-ml = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      libnvidia-ml
Provides:       cuda-nvml = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Provides:       nvidia-driver-NVML = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
}

%package -n libnvidia-dc%{major_version}-ml
Summary:        NVIDIA Management Library (NVML)
%global_requires_ml %{major_version}

%description -n libnvidia-dc%{major_version}-ml
A C-based API for monitoring and managing various states of the NVIDIA GPU
devices. It provides a direct access to the queries and commands exposed via
nvidia-smi. The run-time version of NVML ships with the NVIDIA display driver,
and the SDK provides the appropriate header, stub libraries and sample
applications. Each new version of NVML is backwards compatible and is intended
to be a platform for building 3rd party applications.


%ifarch x86_64 aarch64

%define global_requires_cfg() %{expand:\
Provides:       libnvidia-cfg = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      libnvidia-cfg
}

%package -n libnvidia-dc%{major_version}-cfg
Summary:        NVIDIA Config public interface (nvcfg)
%global_requires_cfg %{major_version}

%description -n libnvidia-dc%{major_version}-cfg
This package contains the private libnvidia-cfg runtime library which is used by
other driver components.


%define global_requires_cuda() %{expand:\
Provides:       nvidia-driver-cuda = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      nvidia-driver-cuda
Requires:       %{name_no_version}%1-cuda-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       nvidia-dc-persistenced%1%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       opencl-filesystem
Requires:       ocl-icd

Conflicts:      xorg-x11-drv-nvidia-cuda
Conflicts:      xorg-x11-drv-nvidia-470xx-cuda
}

%package cuda
Summary:        CUDA integration for %{name}
%global_requires_cuda %{major_version}

%description cuda
This package provides the CUDA integration components for %{name}.


%define global_requires_persistenced() %{expand:\
License:        GPLv2+
Requires:       libnvidia-dc%1-cfg%{?_isa} >= %{?epoch:%{epoch}:}%{version}-%{release}
%{?systemd_requires}
Provides:       nvidia-persistenced = %{?upstream_epoch:%{upstream_epoch}:}%{version}-%{release}
Conflicts:      nvidia-persistenced
}

%package -n nvidia-dc-persistenced%{major_version}
Summary:        A daemon to maintain persistent software state in the NVIDIA Datacenter driver
%global_requires_persistenced %{major_version}

%description -n nvidia-dc-persistenced%{major_version}
The nvidia-persistenced utility is used to enable persistent software state in
the NVIDIA driver. When persistence mode is enabled, the daemon prevents the
driver from releasing device state when the device is not in use. This can
improve the startup time of new clients in this scenario.


%define global_requires_fabricmanager() %{expand:\
Requires:       %{name_no_version}%1-cuda = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       nvidia-dc-nvlsm
%{?systemd_requires}

Provides:       nvidia-fabric-manager-there-can-be-only-one
Conflicts:      (nvidia-fabric-manager-there-can-be-only-one without nvidia-dc-fabric-manager%1)
Provides:       nvidia-fabric-manager-%{major_version} = %{version}-%{release}
Conflicts:      nvidia-fabric-manager-%{major_version}
Provides:       nvidia-fabric-manager = %{version}-%{release}
Conflicts:      nvidia-fabric-manager
Provides:       cuda-drivers-fabricmanager-%{major_version} = %{version}-%{release}
Conflicts:      cuda-drivers-fabricmanager-%{major_version}
Provides:       cuda-drivers-fabricmanager = %{version}-%{release}
Conflicts:      cuda-drivers-fabricmanager
}

%package -n nvidia-dc-fabric-manager%{major_version}
Summary:        Fabric Manager for NVSwitch based systems
%global_requires_fabricmanager %{major_version}

%description -n nvidia-dc-fabric-manager%{major_version}
Fabric Manager for NVIDIA NVSwitch based systems.


%define global_requires_fabricmanager_devel() %{expand:\
Requires:       nvidia-dc-fabric-manager%1%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

Provides:       nvidia-fabric-manager-devel-%{major_version} = %{version}-%{release}
Conflicts:      nvidia-fabric-manager-devel-%{major_version}
Provides:       nvidia-fabric-manager-devel = %{version}-%{release}
Conflicts:      nvidia-fabric-manager-devel
}

%package -n nvidia-dc-fabric-manager%{major_version}-devel
Summary:        Fabric Manager API headers and associated library
%global_requires_fabricmanager_devel %{major_version}

%description -n nvidia-dc-fabric-manager%{major_version}-devel
Fabric Manager API headers and associated library


%ifarch x86_64
%define global_requires_libnvsdm() %{expand:\
Requires:       %{name_no_version}%1-cuda = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       libibmad-devel
Requires:       libibumad-devel
Requires:       libmnl-devel

Provides:       nvidia-libnvsdm-there-can-be-only-one
Conflicts:      (nvidia-libnvsdm-there-can-be-only-one without nvidia-dc-libnvsdm%1)
Provides:       libnvsdm-%{major_version} = %{version}-%{release}
Conflicts:      libnvsdm-%{major_version}
Provides:       libnvsdm = %{version}-%{release}
Conflicts:      libnvsdm
}

%package -n nvidia-dc-libnvsdm%{major_version}
Summary:        NVSwitch Configuration and Query library
%global_requires_libnvsdm %{major_version}

%description -n nvidia-dc-libnvsdm%{major_version}
NVIDIA NVSDM library provides telemetry from QM switches.
%endif


%define global_requires_imex() %{expand:\
Requires:       %{name_no_version}%1-cuda = %{?epoch:%{epoch}:}%{version}-%{release}
%{?systemd_requires}
# Requires systemd-udev to ensure that /usr/lib/sysctl.d exists
Requires:       systemd-udev
Requires:       openssl >= 3.0.0

Provides:       nvidia-imex-there-can-be-only-one
Conflicts:      (nvidia-imex-there-can-be-only-one without nvidia-dc-imex%1)
Provides:       nvidia-imex-%{major_version} = %{version}-%{release}
Conflicts:      nvidia-imex-%{major_version}
Provides:       nvidia-imex = %{version}-%{release}
Conflicts:      nvidia-imex
}

%package -n nvidia-dc-imex%{major_version}
Summary:        NVIDIA Imex
%global_requires_imex %{major_version}

%description -n nvidia-dc-imex%{major_version}
NVIDIA Imex process is a privileged/system client of RM and will facilitate the mapping of GPU memory(over NVLink) between GPUs via the memory import and export mechanisms.


%define global_requires_nscq() %{expand:\
Requires:       %{name_no_version}%1-cuda = %{?epoch:%{epoch}:}%{version}-%{release}

Provides:       libnvidia-nscq-there-can-be-only-one
Conflicts:      (libnvidia-nscq-there-can-be-only-one without libnvidia-dc-nscq%1)
Provides:       libnvidia-nscq-%{major_version} = %{version}-%{release}
Conflicts:      libnvidia-nscq-%{major_version}
Provides:       libnvidia-nscq = %{version}-%{release}
Conflicts:      libnvidia-nscq
}

%package -n libnvidia-dc-nscq%{major_version}
Summary:        NVSwitch Configuration and Query library
%global_requires_nscq %{major_version}

%description -n libnvidia-dc-nscq%{major_version}
NVIDIA NVSwitch Configuration and Query (NSCQ) library provides a
stable driver API used by DCGM for monitoring NVSwitch devices.
%endif


%if %{is_latest_release}
%package -n %{name_no_version}-latest
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards (latest major version)
%global_requires_name -- -latest

%description -n %{name_no_version}-latest
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with recent NVIDIA chipsets.

For the full product support list, please consult the release notes for driver
version %{version}.


%package -n %{name_no_version}-latest-gpu
Summary:        NVIDIA's proprietary display driver for NVIDIA graphic cards (latest major version)
%global_requires_gpu -- -latest
Obsoletes:      nvidia-driver <= %{?upstream_epoch:%{upstream_epoch}:}%{version}

%description -n %{name_no_version}-latest-gpu
This package provides the GPU integration components for %{name_no_version}-latest.


# Workaround because of Peridot issues when multiple versions of the same noarch package are created
%ifarch x86_64
%package -n nvidia-dc-firmware-latest
Summary:        Firwmare for NVIDIA GPUs
%global_requires_firmware -- -latest
Obsoletes:      nvidia-kmod-common <= %{?upstream_epoch:%{upstream_epoch}:}%{version}

%description -n nvidia-dc-firmware-latest
This package provides the NVIDIA GPU firmware for %{name_no_version}-latest.
%endif


%package -n %{name_no_version}-latest-gpu-libs
Summary:        GPU Libraries for %{name_no_version}-latest
%global_requires_gpu_libs -- -latest
Obsoletes:      nvidia-driver-libs <= %{?upstream_epoch:%{upstream_epoch}:}%{version}
Obsoletes:      egl-x11

%description -n %{name_no_version}-latest-gpu-libs
This package provides the shared GPU libraries for %{name_no_version}-latest.


%package -n %{name_no_version}-latest-cuda-libs
Summary:        Libraries for %{name_no_version}-latest-cuda
%global_requires_cuda_libs -- -latest
Obsoletes:      nvidia-driver-cuda-libs <= %{?upstream_epoch:%{upstream_epoch}:}%{version}
Obsoletes:      nvidia-driver-devel <= %{?upstream_epoch:%{upstream_epoch}:}%{version}

%description -n %{name_no_version}-latest-cuda-libs
This package provides the CUDA libraries for %{name_no_version}-latest-cuda.


%package -n libnvidia-dc-latest-fbc
Summary:        NVIDIA OpenGL-based Framebuffer Capture libraries
%global_requires_fbc -- -latest
Obsoletes:      libnvidia-fbc <= %{?upstream_epoch:%{upstream_epoch}:}%{version}
Obsoletes:      nvidia-driver-NvFBCOpenGL <= %{?upstream_epoch:%{upstream_epoch}:}%{version}

%description -n libnvidia-dc-latest-fbc
This library provides a high performance, low latency interface to capture and
optionally encode the composited framebuffer of an X screen. NvFBC are private
APIs that are only available to NVIDIA approved partners for use in remote
graphics scenarios.


%package -n libnvidia-dc-latest-ml
Summary:        NVIDIA Management Library (NVML)
%global_requires_ml -- -latest
Obsoletes:      libnvidia-ml <= %{?upstream_epoch:%{upstream_epoch}:}%{version}
Obsoletes:      nvidia-driver-NVML < %{?upstream_epoch:%{upstream_epoch}:}%{version}

%description -n libnvidia-dc-latest-ml
A C-based API for monitoring and managing various states of the NVIDIA GPU
devices. It provides a direct access to the queries and commands exposed via
nvidia-smi. The run-time version of NVML ships with the NVIDIA display driver,
and the SDK provides the appropriate header, stub libraries and sample
applications. Each new version of NVML is backwards compatible and is intended
to be a platform for building 3rd party applications.


%ifarch x86_64 aarch64

%package -n libnvidia-dc-latest-cfg
Summary:        NVIDIA Config public interface (nvcfg)
%global_requires_cfg -- -latest
Obsoletes:      libnvidia-cfg <= %{?upstream_epoch:%{upstream_epoch}:}%{version}

%description -n libnvidia-dc-latest-cfg
This package contains the private libnvidia-cfg runtime library which is used by
other driver components.


%package -n %{name_no_version}-latest-cuda
Summary:        CUDA integration for %{name_no_version}-latest
%global_requires_cuda -- -latest
Obsoletes:      nvidia-driver-cuda <= %{?upstream_epoch:%{upstream_epoch}:}%{version}
Provides:       nvidia-accelerated-graphics-driver = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       nvidia-accelerated-graphics-driver%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      nvidia-accelerated-graphics-driver <= %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      nvidia-accelerated-graphics-driver.%{_arch} <= %{?epoch:%{epoch}:}%{version}-%{release}

%description -n %{name_no_version}-latest-cuda
This package provides the CUDA integration components for %{name_no_version}-latest.


%package -n nvidia-dc-persistenced-latest
Summary:        A daemon to maintain persistent software state in the NVIDIA Datacenter driver
%global_requires_persistenced -- -latest
Obsoletes:      nvidia-persistenced <= %{?upstream_epoch:%{upstream_epoch}:}%{version}

%description -n nvidia-dc-persistenced-latest
The nvidia-persistenced utility is used to enable persistent software state in
the NVIDIA driver. When persistence mode is enabled, the daemon prevents the
driver from releasing device state when the device is not in use. This can
improve the startup time of new clients in this scenario.


%package -n nvidia-dc-fabric-manager-latest
Summary:        Fabric Manager for NVSwitch based systems
%global_requires_fabricmanager -- -latest
Obsoletes:      nvidia-fabric-manager-%{major_version} <= %{version}
Obsoletes:      nvidia-fabric-manager <= %{version}
Obsoletes:      cuda-drivers-fabricmanager-%{major_version} <= %{version}
Obsoletes:      cuda-drivers-fabricmanager <= %{version}

%description -n nvidia-dc-fabric-manager-latest
Fabric Manager for NVIDIA NVSwitch based systems.


%package -n nvidia-dc-fabric-manager-latest-devel
Summary:        Fabric Manager API headers and associated library
%global_requires_fabricmanager_devel -- -latest
Obsoletes:      nvidia-fabric-manager-devel-%{major_version} <= %{version}
Obsoletes:      nvidia-fabric-manager-devel <= %{version}

%description -n nvidia-dc-fabric-manager-latest-devel
Fabric Manager API headers and associated library


%ifarch x86_64
%package -n nvidia-dc-libnvsdm-latest
Summary:        NVSwitch Configuration and Query library
%global_requires_libnvsdm -- -latest
Obsoletes:      libnvsdm-%{major_version} <= %{version}
Obsoletes:      libnvsdm <= %{version}

%description -n nvidia-dc-libnvsdm-latest
NVIDIA NVSDM library provides telemetry from QM switches.
%endif


%package -n nvidia-dc-imex-latest
Summary:        NVIDIA Imex
%global_requires_imex -- -latest
Obsoletes:      nvidia-imex-%{major_version} <= %{version}
Obsoletes:      nvidia-imex <= %{version}

%description -n nvidia-dc-imex-latest
NVIDIA Imex process is a privileged/system client of RM and will facilitate the mapping of GPU memory(over NVLink) between GPUs via the memory import and export mechanisms.


%package -n libnvidia-dc-nscq-latest
Summary:        NVSwitch Configuration and Query library
%global_requires_nscq -- -latest
Obsoletes:      libnvidia-nscq-%{major_version} <= %{version}
Obsoletes:      libnvidia-nscq <= %{version}

%description -n libnvidia-dc-nscq-latest
NVIDIA NVSwitch Configuration and Query (NSCQ) library provides a
stable driver API used by DCGM for monitoring NVSwitch devices.
%endif
%endif


%prep
%setup -q -T -b 3 -n nvidia-kmod-common-%{version}

%ifarch x86_64 aarch64
%setup -q -T -b 4 -n nvidia-persistenced-%{persistenced_version}
sed -i -e '/+= -O0 -g/d' utils.mk
%endif

%ifarch %{ix86}
%setup -q -n nvidia-driver-%{version}-i386
%endif

%ifarch x86_64
%setup -q -T -b 7 -n libnvsdm-linux-x86_64-%{version}-archive
%setup -q -T -b 5 -n fabricmanager-linux-x86_64-%{version}-archive
%setup -q -T -b 8 -n imex-linux-x86_64-%{version}-archive
%setup -q -T -b 10 -n libnvidia_nscq-linux-x86_64-%{version}-archive
%setup -q -T -b 1 -n nvidia-driver-%{version}-x86_64
%endif

%ifarch aarch64
%setup -q -T -b 6 -n fabricmanager-linux-sbsa-%{version}-archive
%setup -q -T -b 9 -n imex-linux-sbsa-%{version}-archive
%setup -q -T -b 11 -n libnvidia_nscq-linux-sbsa-%{version}-archive
%setup -q -T -b 2 -n nvidia-driver-%{version}-aarch64
%endif

%ifarch x86_64
%if 0%{?rhel} == 8
rm -f libnvidia-pkcs11-openssl3.so.%{version}
%else
rm -f libnvidia-pkcs11.so.%{version}
%endif
%endif

# Create symlinks for shared objects
ldconfig -vn .

# Required for building gstreamer 1.0 NVENC plugins
ln -sf libnvidia-encode.so.%{version} libnvidia-encode.so

# Required for building ffmpeg 3.1 Nvidia CUVID
ln -sf libnvcuvid.so.%{version} libnvcuvid.so

# Required for building against CUDA
ln -sf libcuda.so.%{version} libcuda.so


%build
%ifarch x86_64 aarch64
cd ../nvidia-persistenced-%{persistenced_version}
export CFLAGS="%{optflags} -I%{_includedir}/tirpc"
%make_build \
    DEBUG=1 \
    LIBS="-ldl -ltirpc" \
    NV_VERBOSE=1 \
    PREFIX=%{_prefix} \
    STRIP_CMD=true
%endif


%install
# EGL loader
install -p -m 0644 -D 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json

# EGL external platform
install -p -m 0644 -D 20_nvidia_xcb.json %{buildroot}%{_datadir}/egl/egl_external_platform.d/20_nvidia_xcb.json
install -p -m 0644 -D 20_nvidia_xlib.json %{buildroot}%{_datadir}/egl/egl_external_platform.d/20_nvidia_xlib.json

# Vulkan loader
install -p -m 0644 -D nvidia_icd.json %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
sed -i -e 's|libGLX_nvidia|%{_libdir}/libGLX_nvidia|g' %{buildroot}%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json

%ifarch x86_64
# Vulkan SC loader and compiler
install -p -m 0644 -D nvidia_icd_vksc.json %{buildroot}%{_datadir}/vulkansc/icd.d/nvidia_icd.%{_target_cpu}.json
sed -i -e 's|libnvidia-vksc-core|%{_libdir}/libnvidia-vksc-core|g' %{buildroot}%{_datadir}/vulkansc/icd.d/nvidia_icd.%{_target_cpu}.json
install -p -m 0755 -D nvidia-pcc %{buildroot}%{_bindir}/nvidia-pcc
%endif

# Unique libraries
mkdir -p %{buildroot}%{_libdir}/vdpau/
cp -a lib*GL*_nvidia.so* libcuda*.so* libnv*.so* %{buildroot}%{_libdir}/
cp -a libvdpau_nvidia.so* %{buildroot}%{_libdir}/vdpau/

%if 0%{?fedora} || 0%{?rhel} >= 9
# GBM loader
mkdir -p %{buildroot}%{_libdir}/gbm/
ln -sf ../libnvidia-allocator.so.%{version} %{buildroot}%{_libdir}/gbm/nvidia-drm_gbm.so
%endif

%ifarch x86_64
# NGX Proton/Wine library
mkdir -p %{buildroot}%{_libdir}/nvidia/wine/
cp -a *.dll %{buildroot}%{_libdir}/nvidia/wine/
%endif

%ifarch x86_64 aarch64
# alternate-install-present file triggers runfile warning
install -m 0755 -d %{buildroot}/usr/lib/nvidia/
install -p -m 0644 %{SOURCE32} %{buildroot}/usr/lib/nvidia/

# Empty?
mkdir -p %{buildroot}%{_sysconfdir}/nvidia/

# OpenCL config
install -p -m 0755 -D nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/nvidia.icd

# Binaries
mkdir -p %{buildroot}%{_bindir}
install -p -m 0755 nvidia-{debugdump,smi,cuda-mps-control,cuda-mps-server,bug-report.sh,ngx-updater,powerd} %{buildroot}%{_bindir}

# Man pages
mkdir -p %{buildroot}%{_mandir}/man1/
install -p -m 0644 nvidia-{smi,cuda-mps-control}*.gz %{buildroot}%{_mandir}/man1/

# X stuff
install -p -m 0644 -D %{SOURCE31} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
install -p -m 0755 -D nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/nvidia_drv.so
install -p -m 0755 -D libglxserver_nvidia.so.%{version} %{buildroot}%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so

# NVIDIA specific configuration files
mkdir -p %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-key-documentation \
    %{buildroot}%{_datadir}/nvidia/
install -p -m 0644 nvidia-application-profiles-%{version}-rc \
    %{buildroot}%{_datadir}/nvidia/

# NVIDIA uvm
install -p -m 0644 -D %{SOURCE43} %{buildroot}%{_modulesloaddir}/nvidia-uvm.conf

# OptiX
install -p -m 0644 nvoptix.bin %{buildroot}%{_datadir}/nvidia/

# Systemd units and script for suspending/resuming
install -p -m 0644 -D %{SOURCE34} %{buildroot}%{_systemd_util_dir}/system-preset/70-nvidia-persistenced.preset
install -p -m 0644 -D %{SOURCE30} %{buildroot}%{_systemd_util_dir}/system-preset/70-nvidia.preset
mkdir -p %{buildroot}%{_unitdir}/
install -p -m 0644 systemd/system/*.service %{buildroot}%{_unitdir}/
install -p -m 0755 systemd/nvidia-sleep.sh %{buildroot}%{_bindir}/
install -p -m 0755 -D systemd/system-sleep/nvidia %{buildroot}%{_systemd_util_dir}/system-sleep/nvidia
install -p -m 0644 -D nvidia-dbus.conf %{buildroot}%{_datadir}/dbus-1/system.d/nvidia-dbus.conf

# Ignore powerd binary exiting if hardware is not present
# We should check for information in the DMI table
sed -i -e 's/ExecStart=/ExecStart=-/g' %{buildroot}%{_unitdir}/nvidia-powerd.service

# Vulkan layer
install -p -m 0644 -D nvidia_layers.json %{buildroot}%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json

# install AppData and add modalias provides
install -p -m 0644 -D %{SOURCE40} %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
%{SOURCE41} supported-gpus/supported-gpus.json %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
mkdir -p %{buildroot}%{_datadir}/pixmaps/
cp %{SOURCE42} %{buildroot}%{_datadir}/pixmaps/

# nvsandboxutils configuration
install -p -m 0644 -D sandboxutils-filelist.json %{buildroot}%{_datadir}/nvidia/files.d/sandboxutils-filelist.json

# Workaround because of Peridot issues when multiple versions of the same noarch package are created
%ifarch x86_64
# Install firmware
mkdir -p %{buildroot}/usr/lib/firmware/nvidia/%{version}
install -p -m 0444 ../nvidia-kmod-common-%{version}/firmware/gsp_{ga,tu}10x.bin %{buildroot}/usr/lib/firmware/nvidia/%{version}/
%endif

cd ../nvidia-persistenced-%{persistenced_version}
%make_install \
    NV_VERBOSE=1 \
    PREFIX=%{_prefix} \
    STRIP_CMD=true
mkdir -p %{buildroot}%{_sharedstatedir}/nvidia-persistenced
# Systemd unit files
install -p -m 644 -D %{SOURCE33} %{buildroot}%{_unitdir}/nvidia-persistenced.service

# FabricManager
cd ../fabricmanager-linux-%{fabricarch}-%{version}-archive
install -p -m 0644 -D -t %{buildroot}%{_sysconfdir} etc/fabricmanager.cfg
install -p -m 0755 -D -t %{buildroot}%{_bindir} bin/*
install -p -m 0644 -D -t %{buildroot}%{_includedir} include/*
install -p -m 0755 -D -t %{buildroot}%{_sbindir} sbin/*
install -p -m 0755 -D -t %{buildroot}%{_libdir} lib/*
install -p -m 0644 -D -t %{buildroot}%{_unitdir} systemd/*
mkdir -p %{buildroot}%{_datadir}
cp -a share/* %{buildroot}%{_datadir}
# Config files should go in /etc, but this is where NVIDIA expects to see them, so
# create symlinks to the actual files in /etc
mkdir -p %{buildroot}%{_datadir}/nvidia/nvswitch
ln -s ../../../../etc/fabricmanager.cfg %{buildroot}%{_datadir}/nvidia/nvswitch/fabricmanager.cfg
# No need for the installer to be packaged
rm -f %{buildroot}%{_sbindir}/fm_run_package_installer.sh
# Update location of config files and nvlsm binary in script and systemd service
sed -i 's@/opt/nvidia/nvlsm/sbin@/usr/sbin@g' %{buildroot}%{_bindir}/nvidia-fabricmanager-start.sh %{buildroot}%{_unitdir}/nvidia-fabricmanager.service
sed -i 's@/usr/share/nvidia/nvswitch/fabricmanager.cfg@/etc/fabricmanager.cfg@g' %{buildroot}%{_bindir}/nvidia-fabricmanager-start.sh %{buildroot}%{_unitdir}/nvidia-fabricmanager.service

# libnvsdm
%ifarch x86_64
cd ../libnvsdm-linux-x86_64-%{version}-archive
install -p -m 0755 -D -t %{buildroot}%{_bindir} bin/*
install -p -m 0644 -D -t %{buildroot}%{_includedir} include/*
install -p -m 0755 -D -t %{buildroot}%{_libdir} lib/*
%endif

# Imex
cd ../imex-linux-%{fabricarch}-%{version}-archive
install -p -m 0644 -D -t %{buildroot}%{_sysconfdir}/nvidia-imex etc/nvidia-imex/config.cfg
install -p -m 0755 -D -t %{buildroot}%{_bindir} usr/bin/*
install -p -m 0644 -D -t %{buildroot}%{_unitdir} usr/lib/systemd/system/*
mkdir -p %{buildroot}%{_usr}/lib/sysctl.d
cat << EOF > %{buildroot}%{_usr}/lib/sysctl.d/50-reserve-imex-port.conf
# This file is used to reserve the IMEX port for the NVIDIA IMEX service.
#
# Please make any changes in /etc/sysctl.d as this file will be overwritten
# on package updates.

net.ipv4.ip_local_reserved_ports = 50000,50005
net.ipv6.ip_local_reserved_ports = 50000,50005
EOF

# libnvidia_nscq
cd ../libnvidia_nscq-linux-%{fabricarch}-%{version}-archive
install -p -m 0755 -D -t %{buildroot}%{_libdir} lib/*
%endif


%ifarch x86_64 aarch64
%check
appstream-util validate --nonet %{buildroot}%{_metainfodir}/com.nvidia.driver.metainfo.xml
%endif


%ifarch x86_64 aarch64
%define global_scriptlets() %{expand:\
# Normally, these run at %%post, but we run them at %%posttrans to handle the situation
# where a user replaces the package using `dnf install nvidia-driver<major> --allowerasing`.
# Previously, the %%post for the new package would run before the %%preun for the removed
# package, leaving the systemd units disabled.
%posttrans -n %{name_no_version}%1
%systemd_post nvidia-hibernate.service
%systemd_post nvidia-powerd.service
%systemd_post nvidia-resume.service
%systemd_post nvidia-suspend.service
%systemd_post nvidia-suspend-then-hibernate.service

%posttrans -n nvidia-dc-persistenced%1
%systemd_post nvidia-persistenced.service

%posttrans -n nvidia-dc-fabric-manager%1
%systemd_post nvidia-fabricmanager.service

%posttrans -n nvidia-dc-imex%1
%systemd_post nvidia-imex.service

%preun -n %{name_no_version}%1
%systemd_preun nvidia-hibernate.service
%systemd_preun nvidia-powerd.service
%systemd_preun nvidia-resume.service
%systemd_preun nvidia-suspend.service
%systemd_preun nvidia-suspend-then-hibernate.service

%preun -n nvidia-dc-persistenced%1
%systemd_preun nvidia-persistenced.service

%preun -n nvidia-dc-fabric-manager%1
%systemd_preun nvidia-fabricmanager.service

%preun -n nvidia-dc-imex%1
%systemd_preun nvidia-imex.service

%postun -n %{name_no_version}%1
%systemd_postun nvidia-hibernate.service
%systemd_postun nvidia-powerd.service
%systemd_postun nvidia-resume.service
%systemd_postun nvidia-suspend.service
%systemd_postun nvidia-suspend-then-hibernate.service

%postun -n nvidia-dc-persistenced%1
%systemd_postun nvidia-persistenced.service

%postun -n nvidia-dc-fabric-manager%1
%systemd_postun nvidia-fabricmanager.service

%postun -n nvidia-dc-imex%1
%systemd_postun nvidia-imex.service
}
%global_scriptlets %{major_version}

%if %{is_latest_release}
%global_scriptlets -- -latest
%endif
%endif


%define files_gpu() %{expand:\
%license LICENSE
%doc NVIDIA_Changelog README.txt html supported-gpus/supported-gpus.json
%dir %{_sysconfdir}/nvidia
%dir %{_datadir}/nvidia
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/10-nvidia.conf
%{_bindir}/nvidia-bug-report.sh
%{_bindir}/nvidia-ngx-updater
%ifarch x86_64
%{_bindir}/nvidia-pcc
%endif
%{_bindir}/nvidia-powerd
%{_bindir}/nvidia-sleep.sh
%{_metainfodir}/com.nvidia.driver.metainfo.xml
%{_datadir}/dbus-1/system.d/nvidia-dbus.conf
%{_datadir}/nvidia/nvidia-application-profiles*
%{_datadir}/pixmaps/com.nvidia.driver.png
%{_libdir}/xorg/modules/extensions/libglxserver_nvidia.so
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%{_prefix}/lib/nvidia/alternate-install-present
%{_systemd_util_dir}/system-preset/70-nvidia.preset
%{_systemd_util_dir}/system-sleep/nvidia
%{_unitdir}/nvidia-hibernate.service
%{_unitdir}/nvidia-powerd.service
%{_unitdir}/nvidia-resume.service
%{_unitdir}/nvidia-suspend.service
%{_unitdir}/nvidia-suspend-then-hibernate.service
}


%define files_cuda() %{expand:\
%license LICENSE
%doc NVIDIA_Changelog README.txt html supported-gpus/supported-gpus.json
%dir %{_datadir}/nvidia
%dir %{_datadir}/nvidia/files.d
%{_sysconfdir}/OpenCL/vendors/*
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_modulesloaddir}/nvidia-uvm.conf
%{_datadir}/nvidia/files.d/sandboxutils-filelist.json
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-smi.*
}


%define files_cfg() %{expand:\
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
}


%define files_firmware() %{expand:\
%license LICENSE
%{_prefix}/lib/firmware/nvidia/%{version}
}


%define files_persistenced() %{expand:\
%license ../nvidia-persistenced-%{persistenced_version}/COPYING
%{_bindir}/nvidia-persistenced
%{_mandir}/man1/nvidia-persistenced.1.*
%{_sharedstatedir}/nvidia-persistenced
%{_systemd_util_dir}/system-preset/70-nvidia-persistenced.preset
%{_unitdir}/nvidia-persistenced.service
}


%define files_gpu_libs() %{expand:\
%{_datadir}/egl/egl_external_platform.d/20_nvidia_xcb.json
%{_datadir}/egl/egl_external_platform.d/20_nvidia_xlib.json
%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%{_datadir}/vulkan/icd.d/nvidia_icd.%{_target_cpu}.json
%if 0%{?fedora} || 0%{?rhel} >= 9
%dir %{_libdir}/gbm
%{_libdir}/gbm/nvidia-drm_gbm.so
%endif
%{_libdir}/libEGL_nvidia.so.0
%{_libdir}/libEGL_nvidia.so.%{version}
%{_libdir}/libGLESv1_CM_nvidia.so.1
%{_libdir}/libGLESv1_CM_nvidia.so.%{version}
%{_libdir}/libGLESv2_nvidia.so.2
%{_libdir}/libGLESv2_nvidia.so.%{version}
%{_libdir}/libGLX_nvidia.so.0
%{_libdir}/libGLX_nvidia.so.%{version}
%{_libdir}/libnvidia-allocator.so.1
%{_libdir}/libnvidia-allocator.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-egl-xcb.so.1
%{_libdir}/libnvidia-egl-xcb.so.1.0.5
%{_libdir}/libnvidia-egl-xlib.so.1
%{_libdir}/libnvidia-egl-xlib.so.1.0.5
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-glvkspirv.so.%{version}
%{_libdir}/libnvidia-gpucomp.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%ifarch x86_64 aarch64
%{_datadir}/nvidia/nvoptix.bin
%{_datadir}/vulkan/implicit_layer.d/nvidia_layers.json
%{_libdir}/libnvidia-api.so.1
%{_libdir}/libnvidia-ngx.so.1
%{_libdir}/libnvidia-ngx.so.%{version}
%{_libdir}/libnvidia-rtcore.so.%{version}
%{_libdir}/libnvoptix.so.1
%{_libdir}/libnvoptix.so.%{version}
%endif
%ifarch x86_64
%{_datadir}/vulkansc/icd.d/nvidia_icd.%{_target_cpu}.json
%{_libdir}/libnvidia-present.so.%{version}
%{_libdir}/libnvidia-vksc-core.so.1
%{_libdir}/libnvidia-vksc-core.so.%{version}
%dir %{_libdir}/nvidia
%dir %{_libdir}/nvidia/wine
%{_libdir}/nvidia/wine/*.dll
%endif
}


%define files_cuda_libs() %{expand:\
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-encode.so
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-nvvm.so.4
%{_libdir}/libnvidia-nvvm.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%{_libdir}/libnvidia-opticalflow.so.1
%{_libdir}/libnvidia-opticalflow.so.%{version}
%{_libdir}/libnvidia-ptxjitcompiler.so.1
%{_libdir}/libnvidia-ptxjitcompiler.so.%{version}
%ifarch x86_64 aarch64
%{_libdir}/libcudadebugger.so.1
%{_libdir}/libcudadebugger.so.%{version}
%{_libdir}/libnvidia-nvvm70.so.4
%{_libdir}/libnvidia-sandboxutils.so.1
%{_libdir}/libnvidia-sandboxutils.so.%{version}
%endif
%ifarch x86_64
%if 0%{?rhel} == 8
%{_libdir}/libnvidia-pkcs11.so.%{version}
%else
%{_libdir}/libnvidia-pkcs11-openssl3.so.%{version}
%endif
%endif
}


%define files_fbc() %{expand:\
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}
}


%define files_ml() %{expand:\
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}
}


%define files_fabricmanager() %{expand:\
%license ../fabricmanager-linux-%{fabricarch}-%{version}-archive/LICENSE
%license ../fabricmanager-linux-%{fabricarch}-%{version}-archive/third-party-notices.txt
%doc ../fabricmanager-linux-%{fabricarch}-%{version}-archive/etc/fabricmanager_multinode.cfg
%config(noreplace) %{_sysconfdir}/fabricmanager.cfg
%{_bindir}/nvswitch-audit
%{_bindir}/nv-fabricmanager
%{_bindir}/nvidia-fabricmanager-start.sh
%{_datadir}/nvidia/nvswitch
%{_libdir}/libnvfm.so.1
%{_unitdir}/nvidia-fabricmanager.service
}


%define files_fabricmanager_devel() %{expand:\
%{_libdir}/libnvfm.so
%{_includedir}/nv_fm_*
}


%define files_libnvsdm() %{expand:\
%license ../libnvsdm-linux-x86_64-%{version}-archive/LICENSE
%license ../libnvsdm-linux-x86_64-%{version}-archive/usr/share/doc/third-party-notices.txt
%{_bindir}/nvsdm_cli
%{_includedir}/nvsdm.h
%{_libdir}/libnvsdm.so*
}


%define files_imex() %{expand:\
%license ../imex-linux-%{fabricarch}-%{version}-archive/LICENSE
%license ../imex-linux-%{fabricarch}-%{version}-archive/usr/share/doc/third-party-notices.txt
%dir %{_sysconfdir}/nvidia-imex
%config(noreplace) %{_sysconfdir}/nvidia-imex/config.cfg\
%{_bindir}/nvidia-imex-ctl
%{_bindir}/nvidia-imex
%{_unitdir}/nvidia-imex.service
%{_usr}/lib/sysctl.d/50-reserve-imex-port.conf
}


%define files_nscq() %{expand:\
%license ../libnvidia_nscq-linux-%{fabricarch}-%{version}-archive/LICENSE
%{_libdir}/libnvidia-nscq.so*
}


%ifarch x86_64 aarch64
%files

%files gpu
%files_gpu

%files cuda
%files_cuda

%files -n libnvidia-dc%{major_version}-cfg
%files_cfg

# Workaround because of Peridot issues when multiple versions of the same noarch package are created
%ifarch x86_64
%files -n nvidia-dc-firmware%{major_version}
%files_firmware
%endif

%files -n nvidia-dc-persistenced%{major_version}
%files_persistenced

%files -n nvidia-dc-fabric-manager%{major_version}
%files_fabricmanager

%files -n nvidia-dc-fabric-manager%{major_version}-devel
%files_fabricmanager_devel

%ifarch x86_64
%files -n nvidia-dc-libnvsdm%{major_version}
%files_libnvsdm
%endif

%files -n nvidia-dc-imex%{major_version}
%files_imex

%files -n libnvidia-dc-nscq%{major_version}
%files_nscq
%endif

%files gpu-libs
%files_gpu_libs

%files cuda-libs
%files_cuda_libs

%files -n libnvidia-dc%{major_version}-fbc
%files_fbc

%files -n libnvidia-dc%{major_version}-ml
%files_ml

%if %{is_latest_release}
%ifarch x86_64 aarch64
%files -n %{name_no_version}-latest

%files -n %{name_no_version}-latest-gpu
%files_gpu

%files -n %{name_no_version}-latest-cuda
%files_cuda

%files -n libnvidia-dc-latest-cfg
%files_cfg

# Workaround because of Peridot issues when multiple versions of the same noarch package are created
%ifarch x86_64
%files -n nvidia-dc-firmware-latest
%files_firmware
%endif

%files -n nvidia-dc-persistenced-latest
%files_persistenced

%files -n nvidia-dc-fabric-manager-latest
%files_fabricmanager

%files -n nvidia-dc-fabric-manager-latest-devel
%files_fabricmanager_devel

%ifarch x86_64
%files -n nvidia-dc-libnvsdm-latest
%files_libnvsdm
%endif

%files -n nvidia-dc-imex-latest
%files_imex

%files -n libnvidia-dc-nscq-latest
%files_nscq
%endif

%files -n %{name_no_version}-latest-gpu-libs
%files_gpu_libs

%files -n %{name_no_version}-latest-cuda-libs
%files_cuda_libs

%files -n libnvidia-dc-latest-fbc
%files_fbc

%files -n libnvidia-dc-latest-ml
%files_ml

%endif


%changelog
* Wed May 06 2026 Pratham Patel <ppatel@ciq.com> - 580.159.03-1
- Update to 580.159.03

* Wed Feb 25 2026 Jonathan Dieter <jdieter@ciq.com> - 580.126.20-1
- Update to 580.126.20

* Wed Feb 11 2026 Jonathan Dieter <jdieter@ciq.com> - 580.126.16-1
- Update to 580.126.16

* Thu Jan 29 2026 David Gomez <dgomez@ciq.com> - 580.126.09-2
- Add nvidia-uvm.conf and mark as not latest

* Fri Jan 16 2026 Pratham Patel <ppatel@ciq.com> - 580.126.09-1
- Update to 580.126.09

* Mon Nov 24 2025 Jonathan Dieter <jdieter@ciq.com> - 580.105.08-1
- Update to 580.105.08

* Tue Oct 07 2025 Jonathan Dieter <jdieter@ciq.com> - 580.95.05-1
- Update to 580.95.05

* Fri Sep 05 2025 Jonathan Dieter <jdieter@ciq.com> - 580.82.07-1
- Update to 580.82.07
- Mark as latest release

* Fri Aug 29 2025 Jonathan Dieter <jdieter@ciq.com> - 580.65.06-2
- Until this has been more thoroughly tested, don't mark this as latest

* Mon Aug 04 2025 Jonathan Dieter <jdieter@ciq.com> - 580.65.06-1
- Initial release of 580
- Ensure that IMEX ports aren't handed out as ephemeral ports
