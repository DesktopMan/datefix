#!/usr/bin/python3

import argparse
import os
import sys
import datetime


def fix_directory_mtime(directory, dry_run):
    # Get list of files from path
    files = [f for f in [os.path.join(directory, f) for f in os.listdir(directory)] if os.path.isfile(f)]

    if not files:
        return False

    # Sort files in path by mtime
    files = sorted([(os.path.getmtime(f), f) for f in files])

    # Keep current atime and get mtime from the oldest file in path
    atime = os.path.getatime(directory)
    mtime_old = os.path.getmtime(directory)
    mtime_new = files[0][0]

    if mtime_new == mtime_old:
        return False

    print("%s -> %s : %s"
          % (
              datetime.datetime.fromtimestamp(mtime_old).date(),
              datetime.datetime.fromtimestamp(mtime_new).date(),
              directory)
          )

    if not dry_run:
        os.utime(directory, times=(atime, mtime_new))

    return True


def delete_file(file, dry_run):
    # Keep current parent directory atime and mtime
    parent_dir = os.path.dirname(file)
    atime = os.path.getatime(parent_dir)
    mtime = os.path.getmtime(parent_dir)

    print("Deleted : %s" % file)

    if not dry_run:
        os.unlink(file)
        os.utime(parent_dir, times=(atime, mtime))


def datefix_handler(args):
    print('datefix: Changing modification times')
    print('------------------------------------\n')

    count = 0

    for p in sorted(args.directories):
        if os.path.isdir(p):
            if fix_directory_mtime(p, args.dry_run):
                count += 1

    if count > 0:
        print('\nDone. Modified %d directories.\n' % count)
    else:
        print('Done. No changes required.\n')


def delete_handler(args):
    print('delete: Deleting files')
    print('----------------------\n')

    count = 0

    for f in sorted(args.files):
        if os.path.isfile(f):
            delete_file(f, args.dry_run)
            count += 1

    if count > 0:
        print('\nDone. Deleted %d files.\n' % count)
    else:
        print('Done. No changes required.\n')


def main():
    print('=======')
    print('Dirtool')
    print('=======')
    print()

    parser = argparse.ArgumentParser(description='Manages directories in various ways. See sub commands.')

    parser.add_argument('--dry-run', dest='dry_run', action='store_true', default=False,
                        help='Do not modify anything, only print')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_datefix = subparsers.add_parser('datefix',
                                           help='Set directory modification time with oldest file as a reference')
    parser_datefix.set_defaults(func=datefix_handler)
    parser_datefix.add_argument('directories', metavar='N', nargs='+', help='Path to directories')

    parser_delete = subparsers.add_parser('delete',
                                          help='Delete files without changing parent directory modification time')
    parser_delete.set_defaults(func=delete_handler)
    parser_delete.add_argument('files', metavar='N', nargs='+', help='Path to files')

    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.dry_run:
        print('Using dry run mode, changes are only displayed, not performed.\n')

    args.func(args)


if __name__ == "__main__":
    main()
