#!/usr/bin/env python
"""Setup a Zephyr toolchain."""

import argparse
import hashlib
import shutil
import subprocess
import sys

from pathlib import Path


WEST_CONFIG = r"""[manifest]
path = zephyr
file = west.yml
"""


def _update_hash(hash_o, file_path):
    with open(file_path, 'rb') as f:
        hash_o.update(f.read())


def _exists(file_path):
    if file_path.exists():
        return True
    print(f"{file_path.absolute()} does not exist.")
    return False


def check(args):
    work_dir = Path(args.working_dir)
    west_config = work_dir / ".west" / "config"
    zephyr_dir = work_dir / "zephyr"
    west_yml = zephyr_dir / "west.yml"
    west_orig_hash = work_dir / ".west" / "west.sha256"

    if not _exists(west_config):
        return 1
    if not zephyr_dir.samefile(Path(args.rtos_dir)):
        print(f'{zephyr_dir.absolute()} does not point to the '
              'correct Zephyr directory.')
        return 2
    if not _exists(west_yml):
        return 3
    if not _exists(west_orig_hash):
        return 4

    west_hash = hashlib.new('sha256')
    _update_hash(west_hash, west_yml)
    _update_hash(west_hash, west_config)
    with open(west_orig_hash) as f:
        orig_hash = f.read()
        if orig_hash != west_hash.hexdigest():
            print("Hash of west config does not match")
            return 5

    return 0


def init(args):
    if check(args) == 0:
        return 0
    work_dir = Path(args.working_dir)
    work_dir.mkdir(exist_ok=True)

    # delete all contents
    for fi in work_dir.iterdir():
        if fi.is_dir() and not fi.is_symlink():
            shutil.rmtree(fi)
        else:
            fi.unlink()

    # west files
    west_dir = work_dir / ".west"
    west_dir.mkdir()
    with open(west_dir / "config", "w") as f:
        f.write(WEST_CONFIG)

    # zephyr symlink
    rtos_dir = Path(args.rtos_dir)
    assert rtos_dir.is_dir()
    (work_dir / "zephyr").symlink_to(rtos_dir)

    env = dict([x.split("=") for x in args.west_env.split(" ")])
    subprocess.run(
        [sys.executable, args.west_path, "update"],
        env=env, cwd=work_dir, check=True
    )

    # hash file about the current config
    west_hash = hashlib.new('sha256')
    _update_hash(west_hash, work_dir / 'zephyr' / 'west.yml')
    _update_hash(west_hash, work_dir / '.west' / 'config')
    with open(work_dir / '.west' / 'west.sha256', 'w') as f:
        f.write(west_hash.hexdigest())

    return 0


def main():
    actions = {"check": check, "init": init}
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument(
        "action", choices=actions.keys(),
        help="Action that should be performed."
    )
    parser.add_argument(
        "--rtos-dir", required=True, help="Path to the Zephyr RTOS repo."
    )
    parser.add_argument(
        "--working-dir", required=True, help="Path to the Zephyr toolchain."
    )
    parser.add_argument("--west-path", help="Path to the west tool.")
    parser.add_argument("--west-env", help="Environment for executing west.")
    args = parser.parse_args()
    return actions[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
