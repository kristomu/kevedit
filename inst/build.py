#!/usr/bin/env python
"""KevEdit build script."""
from __future__ import print_function

import argparse
import errno
import logging
import os
import pwd
import subprocess
import sys

# Versions of 3rd party software to fetch
APPIMAGE_VERSION = '9'
ISPACK_VERSION = '5.5.3'
SDL_VERSION = '2.0.5'


# All build targets
TARGETS = ['appimage', 'dos', 'macos', 'windows']


# Build temp directory
WORK_DIR = os.path.abspath(os.environ.get('WORK_DIR', 'work'))

# Distribution target path
DIST_DIR = os.path.abspath(os.environ.get('DIST_DIR', 'dist'))

# Platform-specific files
PLATFORM_DIR = os.path.abspath(os.environ.get('PLATFORM_DIR', 'platform'))

# 3rd party download path
VENDOR_DIR = os.path.abspath(os.environ.get('VENDOR_DIR', 'vendor'))

# 'uid:gid' user and group IDs in a string
# TODO: what's this do on windows?
UID_GID = '{2}:{3}'.format(*pwd.getpwuid(os.getuid()))

log = logging.getLogger('build')


def main():
    """Run build script."""
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    maybe_make_dirs(WORK_DIR, DIST_DIR)
    maybe_fetch_sdl_source(SDL_VERSION)
    make_source_archive(args.version)

    source = get_source_filename(args.version)
    for target in args.targets:
        globals()['build_' + target](source, args)


def build_appimage(source, args):
    """Build Linux x86_64 AppImage to DIST_DIR."""
    maybe_fetch_appimage(APPIMAGE_VERSION)

    shell("""
        docker build
        -f Dockerfile.appimage -t kevedit/build_appimage
        --build-arg SDL_VERSION={sdl_version}
        .
        """,
        sdl_version=SDL_VERSION)
    shell("""
        docker run
        -v {work}:/work -v {dist}:/dist -v {platform}:/platform -v {vendor}:/vendor
        -u {uid_gid}
        kevedit/build_appimage /platform/linux/build_linux.sh {source} {appimage_version}
        """,
        work=WORK_DIR, dist=DIST_DIR, platform=PLATFORM_DIR, vendor=VENDOR_DIR,
        source=source, uid_gid=UID_GID, appimage_version=APPIMAGE_VERSION)
    # Need --privileged for fuse support, required by appimagetool
    shell("""
        docker run --privileged
        -v {work}:/work -v {dist}:/dist -v {vendor}:/vendor
        kevedit/build_appimage sh -c "
          /vendor/{appimage_tool} /work/appdir/KevEdit.AppDir
            /dist/KevEdit-{version}-x86_64.AppImage &&
          chown {uid_gid} /dist/KevEdit-{version}-x86_64.AppImage"
        """,
        work=WORK_DIR, dist=DIST_DIR, platform=PLATFORM_DIR, vendor=VENDOR_DIR,
        appimage_tool=get_appimagetool_filename(APPIMAGE_VERSION), uid_gid=UID_GID,
        version=args.version)


def build_macos(source, args):
    """Build macOS x86_64 .app in a .dmg archive to DIST_DIR."""
    source = get_source_filename(args.version)

    shell("""
        docker build
        -f Dockerfile.macos -t kevedit/build_macos
        --build-arg SDL_VERSION={sdl_version}
        .
        """,
        sdl_version=SDL_VERSION)
    shell("""
        docker run
        -v {work}:/work -v {dist}:/dist -v {platform}:/platform -v {vendor}:/vendor
        -u {uid_gid}
        kevedit/build_macos /platform/macos/build_macos.sh {source} {version}
        """,
        work=WORK_DIR, dist=DIST_DIR, platform=PLATFORM_DIR, vendor=VENDOR_DIR,
        source=source, uid_gid=UID_GID, version=args.version)


def build_windows(source, args):
    """Build windows x64 .exe in a self-executing installer to DIST_DIR."""
    maybe_fetch_sdl_windows_runtime(SDL_VERSION)
    maybe_fetch_ispack(ISPACK_VERSION)

    source = get_source_filename(args.version)

    shell("""
        docker build
        -f Dockerfile.windows -t kevedit/build_windows
        --build-arg SDL_VERSION={sdl_version}
        --build-arg ISPACK_VERSION={ispack_version}
        .
        """,
        sdl_version=SDL_VERSION, ispack_version=ISPACK_VERSION),
    shell("""
        docker run
        -v {work}:/work -v {dist}:/dist -v {platform}:/platform -v {vendor}:/vendor
        -u {uid_gid}
        kevedit/build_windows
        /platform/windows/build_windows.sh {source} {version} {sdl_version}
        """,
        work=WORK_DIR, dist=DIST_DIR, platform=PLATFORM_DIR, vendor=VENDOR_DIR,
        source=source, uid_gid=UID_GID, version=args.version, sdl_version=SDL_VERSION)


def build_dos(source, args):
    """Build DOS 32-bit .exe in a .zip file to DIST_DIR."""
    # TODO: maybe fetch build-djgpp

    source = get_source_filename(args.version)

    shell("""
        docker build
        -f Dockerfile.dos -t kevedit/build_dos
        .
        """)
    shell("""
        docker run
        -v {work}:/work -v {dist}:/dist -v {platform}:/platform -v {vendor}:/vendor
        -u {uid_gid}
        kevedit/build_dos /platform/dos/build_dos.sh {source} {version}
        """,
        work=WORK_DIR, dist=DIST_DIR, platform=PLATFORM_DIR, vendor=VENDOR_DIR,
        source=source, uid_gid=UID_GID, version=args.version)


def parse_args():
    """Parse command line arguments.

    :return: arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Build KevEdit for multiple platforms')
    parser.add_argument('-v', '--version', metavar='VERSION', help='KevEdit version to build')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')

    target_choices = ['all'] + TARGETS
    target_list = ', '.join(sorted(target_choices))
    parser.add_argument(
            'targets', nargs='*', metavar='TARGET', choices=target_choices, default='all',
            help='Target platforms to build: {}'.format(target_list))

    args = parser.parse_args()

    args.targets = args.targets if isinstance(args.targets, list) else [args.targets]
    if 'all' in args.targets:
        if len(args.targets) > 1:
            print('Target "all" is not allowed with other targets\n')
            parser.print_usage()
            sys.exit(1)
        args.targets = TARGETS

    if args.version is None:
        args.version = check_output('git rev-parse --verify HEAD')
        log.info('Version not specified, using current git version %s', args.version)

    return args


def maybe_fetch_sdl_source(version):
    """Fetch the SDL source code if it doesn't already exist in VENDOR_DIR.

    :param str version: SDL2 version to fetch
    """

    sdl_filename = 'SDL2-{}.tar.gz'.format(version)
    sdl_src = os.path.join(VENDOR_DIR, sdl_filename)
    sdl_sig = os.path.join(VENDOR_DIR, sdl_filename + '.sig')
    if os.path.exists(sdl_src):
        log.debug('SDL file %s already exists; will not fetch', sdl_src)
        return

    # Validate that we can fetch and check the signature first.
    validate_runs(['wget', '--version'], 'wget is required to fetch SDL')
    validate_runs(['gpg', '--version'], 'gpg is required to fetch SDL')

    log.debug('Fetching SDL source...')
    subprocess.check_call(
        ['wget', 'https://www.libsdl.org/release/' + sdl_filename, '-O', sdl_src])
    log.debug('Fetching SDL signature...')

    subprocess.check_call(
        ['wget', 'https://www.libsdl.org/release/{}.sig'.format(sdl_filename), '-O', sdl_sig])

    log.debug('Checking SDL signature...')
    subprocess.check_call(['gpg', '--verify', sdl_sig, sdl_src])
    log.info('Fetched SDL %s', version)


def maybe_fetch_sdl_windows_runtime(version):
    """Fetch the SDL windows runtime if it doesn't already exist in VENDOR_DIR.

    :param str version: SDL2 version to fetch
    """
    sdl_filename = 'SDL2-{}-win32-x64.zip'.format(version)
    sdl_zip = os.path.join(VENDOR_DIR, sdl_filename)
    if os.path.exists(sdl_zip):
        log.debug('SDL windows runtime file %s already exists; will not fetch', sdl_zip)
        return

    validate_runs(['wget', '--version'], 'wget is required to fetch SDL windows runtime')

    log.debug('Fetching SDL windows runtime...')
    subprocess.check_call(
        ['wget', 'https://www.libsdl.org/release/' + sdl_filename, '-O', sdl_zip])
    log.info('Fetched SDL windows runtime %s', version)


def maybe_fetch_ispack(version):
    """Fetch the InnoSetup packer if it doesn't already exist in VENDOR_DIR.

    :param str version: InnoSetup version to fetch
    """
    filename = 'ispack-{version}-unicode.exe'.format(version=version)
    ispack_exe = os.path.join(VENDOR_DIR, filename)
    if os.path.exists(ispack_exe):
        log.debug('ispack file %s already exists; will not fetch', ispack_exe)
        return

    validate_runs(['wget', '--version'], 'wget is required to fetch ispack')

    url = 'http://files.jrsoftware.org/ispack/{filename}'.format(filename=filename)
    log.debug('Fetching ispack exe...')
    subprocess.check_call(['wget', url, '-O', ispack_exe])
    log.info('Fetched ispack %s', version)


def maybe_fetch_appimage(version):
    """Fetch AppImage binaries if they don't exist in VENDOR_DIR.

    :param version: AppImage version to fetch
    """
    files = [{
        'input': 'appimagetool-x86_64.AppImage',
        'output': get_appimagetool_filename(version)
    }, {
        'input': 'AppRun-x86_64',
        'output': get_apprun_filename(version)
    }]
    for file in files:
        path = os.path.join(VENDOR_DIR, file['output'])
        if os.path.exists(path):
            log.debug('AppImage file %s already exists; will not fetch', path)
            continue

        validate_runs(['wget', '--version'], 'wget is required to fetch AppImage')

        url = 'https://github.com/AppImage/AppImageKit/releases/download/{version}/' \
              '{filename}'.format(version=version, filename=file['input'])
        log.debug('Fetching %s...', file['input'])
        subprocess.check_call(['wget', url, '-O', path])
        log.info('Fetched %s', file['input'])
        os.chmod(path, 0o755)


def make_source_archive(version, path=VENDOR_DIR):
    """Retrieve the selected version from git and save as a zip file.

    :param str version: version to use
    :param str path: directory to save the zip file
    """
    filename = get_source_filename(version)
    abs_path = os.path.abspath(path)

    # Run in the project root to archive all files
    log.debug('Changing directory to the project top level...')
    cwd = os.getcwd()
    root = check_output('git rev-parse --show-toplevel')
    os.chdir(root)

    log.debug('Making source archive...')
    subprocess.check_call(
        ['git', 'archive', version,
         '--format', 'zip',
         '--output', os.path.join(abs_path, filename)])

    log.debug('Restoring directory...')
    os.chdir(cwd)


def get_source_filename(version):
    """Get the KevEdit source zip filename for a given version.

    :param str version: KevEdit version
    :rtype: str
    """
    return 'kevedit-{}.zip'.format(version)


def get_appimagetool_filename(version=APPIMAGE_VERSION):
    """Get the appimagetool filename for a given version.

    :param version: AppImage version
    :rtype: str
    """
    return 'appimagetool-{}-x86_64.AppImage'.format(version)


def get_apprun_filename(version=APPIMAGE_VERSION):
    """Get the AppRun filename for a given version.

    :param version: AppImage version
    :rtype: str
    """
    return 'AppRun-{}-x86_64'.format(version)


def check_output(cmd):
    """Execute a command, check its return code, and return its output.

    The command will not be executed in a shell.

    If only one line of output is returned, the newline will be stripped.  For multi-line
    output, the newlines will be preserved.

    :param cmd: command line str or list
    :rtype: str
    """
    if isinstance(cmd, str):
        cmd = cmd.split(' ')
    result = subprocess.check_output(cmd)
    result = result.decode('utf-8')
    if result.count('\n') == 1:
        result = result.rstrip()
    return result


def shell(cmd, **kwargs):
    """Format a command line, and run it using a shell.

    :param str cmd: command line format string; newlines will be stripped.
    :param kwargs: format keyword arguments
    """
    cmd = cmd.replace('\n', '')
    cmd = cmd.format(**kwargs)
    subprocess.check_call(cmd, shell=True)


def validate_runs(command, message):
    """Validate that a command runs, exiting on failure.

    :param command: command line str or list
    :param message: error message on failure
    """
    try:
        check_output(command)
    except OSError:
        log.exception(message)
        print(message, file=sys.stderr)
        sys.exit(2)


def maybe_make_dirs(*dirs):
    """Make directories if they don't already exist.

    :param dirs: path strs
    """
    for d in dirs:
        try:
            os.mkdir(d)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


if __name__ == '__main__':
    main()
