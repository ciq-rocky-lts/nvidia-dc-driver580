#!/bin/sh
set -e
set -x

set_vars() {
   export VERSION=${VERSION:-550.54.14}
   export DL_SITE=${DL_SITE:-https://us.download.nvidia.com/tesla}
   export TEMP_UNPACK=${ARCH}
   export PLATFORM=Linux-${ARCH}
   export RUN_FILE=${RUN_FILE:-NVIDIA-${PLATFORM}-${VERSION}.run}
}

run_file_get() {
    printf "Downloading installer ${RUN_FILE}... "
    [[ -f $RUN_FILE ]] || wget -c -q ${DL_SITE}/${VERSION}/$RUN_FILE
    printf "OK\n"
}

run_file_extract() {
    rm -fr ${TEMP_UNPACK}
    mkdir -p ./tmp
    sh ${RUN_FILE} --extract-only --tmpdir ./tmp --target ${TEMP_UNPACK}
    rm ./tmp -rf
}

cleanup_folder() {

    printf "Cleaning up binaries... "

    cd ${TEMP_UNPACK}

    # Stuff not needed for packages:
    #   - Compiled from source
    #   - Interactive installer files
    #   - GLVND GL libraries
    #   - Internal development only libraries
    rm -fr \
        nvidia-xconfig* \
        nvidia-persistenced* \
        nvidia-modprobe* \
        libnvidia-gtk* libnvidia-wayland-client* nvidia-settings* \
        libGLESv1_CM.so.* libGLESv2.so.* libGLdispatch.so.* libOpenGL.so.* libGLX.so.* libGL.so.1* libEGL.so.1* \
        libnvidia-egl-wayland.so.* libnvidia-egl-gbm.so.* \
        libOpenCL.so.1* \
        libGL.so.${VERSION} libEGL.so.${VERSION} \
        nvidia-installer* .manifest make* mk* tls_test* libglvnd_install_checker \
        libnvidia-llvmnvgpu.so.*

    if [ "${ARCH}" == x86_64 ]; then
        rm -fr \
          32/libGLESv1_CM.so.* 32/libGLESv2.so.* 32/libGLdispatch.so.* 32/libOpenGL.so.* 32/libGLX.so.* 32/libGL.so.1* 32/libEGL.so.1* \
          32/libOpenCL.so.1* \
          32/libGL.so.${VERSION} 32/libEGL.so.${VERSION} \
          32/libnvidia-egl-wayland.so.* 32/libnvidia-egl-gbm.so.*

        cp -f *.json* 32/
    fi

    cd ..

    printf "OK\n"
}

create_tarball() {

    KMOD_COMMON=nvidia-kmod-common-${VERSION}
    USR_64=nvidia-driver-${VERSION}-${ARCH}

    mkdir ${KMOD_COMMON} ${USR_64}
    mv ${TEMP_UNPACK}/firmware ${KMOD_COMMON}/

    if [ "$ARCH" == x86_64 ]; then

        USR_32=nvidia-driver-${VERSION}-i386

        mkdir ${USR_32}
        mv ${TEMP_UNPACK}/32/* ${USR_32}/
        rm -fr ${TEMP_UNPACK}/32

    fi

    mv ${TEMP_UNPACK}/* ${USR_64}/

    rm -fr ${TEMP_UNPACK}

    # `.metadata` pins each tarball's checksum, so whoever rebuilds a version
    # next has to land on the same bytes. Left alone tar records the building
    # user, readdir order, and the moment of the build on every directory --
    # the installer creates those rather than restoring them. Clamping to the
    # installer's own mtime pins those directories and leaves every file
    # older than it untouched.
    clamp=$(stat -c %Y ${RUN_FILE})

    # One xz thread is a different encoder and a different stream. Two or more
    # agree, so a machine down to a single core still has to ask for two, and
    # --no-adjust turns a memory limit that would quietly drop xz back to one
    # into an error.
    threads=$(nproc)
    [ ${threads} -gt 1 ] || threads=2

    for tarball in ${KMOD_COMMON} ${USR_64} ${USR_32}; do

        printf "Creating tarball $tarball... "

        XZ_OPT="-T${threads} --no-adjust" tar --sort=name \
            --owner=0 --group=0 --numeric-owner \
            --mtime="@${clamp}" --clamp-mtime \
            --remove-files -cJf $tarball.tar.xz $tarball

        printf "OK\n"

    done
}

ARCH=x86_64
set_vars
run_file_get
run_file_extract
cleanup_folder
create_tarball
