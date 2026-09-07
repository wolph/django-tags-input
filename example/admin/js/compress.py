#!/usr/bin/env python
import optparse
import os
import subprocess
import sys
from typing import Any

here: str = os.path.dirname(__file__)


def main() -> None:
    usage: str = 'usage: %prog [file1..fileN]'
    description: str = (
        'With no file paths given this script will automatically '
        'compress all jQuery-based files of the admin app. Requires the Google'
        ' Closure Compiler library and Java version 6 or later.'
    )
    parser: optparse.OptionParser = optparse.OptionParser(
        usage, description=description
    )
    parser.add_option(
        '-c',
        dest='compiler',
        default='~/bin/compiler.jar',
        help='path to Closure Compiler jar file',
    )
    parser.add_option(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
    )
    parser.add_option(
        '-q',
        '--quiet',
        action='store_false',
        dest='verbose',
    )
    options: Any
    args: list[str]
    (options, args) = parser.parse_args()

    compiler: str = os.path.expanduser(str(options.compiler))
    if not os.path.exists(compiler):
        sys.exit(
            f'Google Closure compiler jar file {compiler} not found. '
            'Please use the -c option to specify the path.'
        )

    if not args:
        if options.verbose:
            sys.stdout.write(
                'No filenames given; defaulting to admin scripts\n'
            )
        args = [
            os.path.join(here, f)
            for f in [
                'actions.js',
                'collapse.js',
                'inlines.js',
                'prepopulate.js',
            ]
        ]

    for arg in args:
        if not arg.endswith('.js'):
            arg = arg + '.js'
        to_compress: str = os.path.expanduser(arg)
        if os.path.exists(to_compress):
            base_name: str = ''.join(arg.rsplit('.js'))
            to_compress_min: str = f'{base_name}.min.js'
            cmd: str = (
                f'java -jar {compiler} --js {to_compress} '
                f'--js_output_file {to_compress_min}'
            )
            if options.verbose:
                sys.stdout.write(f'Running: {cmd}\n')
            subprocess.call(cmd.split())
        else:
            sys.stdout.write(
                f'File {to_compress} not found. Sure it exists?\n'
            )


if __name__ == '__main__':
    main()
