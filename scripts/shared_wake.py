#!/usr/bin/env python3
"""Apply the verified KlipperScreen DPMS overlay fix, only on matching code."""
import argparse
import ast
from datetime import datetime
from pathlib import Path
import shutil

OLD = """        elif state != functions.DPMS_State.On:
            if not self.screensaver.is_showing():
                self.screensaver.show()
        return True
"""
NEW = """        elif state != functions.DPMS_State.On:
            if not self.screensaver.is_showing():
                self.screensaver.show()
        elif self.screensaver.is_showing():
            # Also dismiss the overlay after another display wakes DPMS.
            self.screensaver.close()
        return True
"""


def patched_source(source):
    tree = ast.parse(source)
    methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
               and n.name == "check_dpms_state"]
    if len(methods) != 1:
        raise ValueError("Cannot identify one check_dpms_state method; no changes made")
    method = methods[0]
    for node in ast.walk(method):
        if isinstance(node, ast.If) and ast.unparse(node.test) == "self.screensaver.is_showing()":
            if any(isinstance(n, ast.Call) and ast.unparse(n.func) == "self.screensaver.close"
                   for statement in node.body for n in ast.walk(statement)):
                return source, False
    segment = "".join(source.splitlines(keepends=True)[method.lineno - 1:method.end_lineno])
    if OLD.rstrip() not in segment or source.count(OLD) != 1:
        raise ValueError("KlipperScreen differs from the verified version; no changes made")
    updated = source.replace(OLD, NEW, 1)
    compile(updated, "screen.py", "exec")
    return updated, True


NOTIFY = '        # KSC_WAKE_FIFO_V1: notify the camera viewer without polling for wake.\n        try:\n            import os\n            import stat\n            ksc_runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")\n            ksc_pipe = os.path.join(ksc_runtime, "KlipperScreenCam", "wake.fifo")\n            ksc_fd = os.open(ksc_pipe, os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW)\n            try:\n                if stat.S_ISFIFO(os.fstat(ksc_fd).st_mode):\n                    os.write(ksc_fd, b"wake\\n")\n            finally:\n                os.close(ksc_fd)\n        except OSError:\n            pass  # The camera viewer may be stopped or not installed.\n'


def notified_source(source):
    tree = ast.parse(source)
    methods = [method for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == "ScreenSaver" for method in node.body
               if isinstance(method, ast.FunctionDef) and method.name == "close"]
    if len(methods) != 1:
        raise ValueError("Cannot identify ScreenSaver.close; no changes made")
    method = methods[0]
    lines = source.splitlines(keepends=True)
    segment = "".join(lines[method.lineno - 1:method.end_lineno])
    if "KSC_WAKE_FIFO_V1" in segment:
        return source, False
    anchor = "        self.screen.lock_screen.relock()"
    if segment.count(anchor) != 1:
        raise ValueError("ScreenSaver.close differs from the verified version; no changes made")
    segment = segment.replace(anchor, anchor + "\n" + NOTIFY.rstrip(), 1)
    updated = "".join(lines[:method.lineno - 1]) + segment + "".join(lines[method.end_lineno:])
    compile(updated, "screensaver.py", "exec")
    return updated, True


def apply(directory, write=False):
    directory = Path(directory).expanduser()
    targets = [(directory / "screen.py", patched_source),
               (directory / "ks_includes/widgets/screensaver.py", notified_source)]
    plans = []
    # Validate both files before touching either of them.
    for path, transform in targets:
        if path.is_symlink():
            raise ValueError("Refusing to patch a symlink")
        source = path.read_text(encoding="utf-8")
        updated, needed = transform(source)
        if needed:
            plans.append((path, updated))
        else:
            print("Shared wake integration already present:", path)
    if not plans:
        return []
    if not write:
        for path, _ in plans:
            print("Shared wake integration can be applied:", path)
        return []
    suffix = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backups = []
    for path, _ in plans:
        backup = path.with_name(path.name + ".before-ksc-shared-wake-" + suffix)
        with backup.open("xb") as stream:
            stream.write(path.read_bytes())
        shutil.copystat(path, backup)
        backups.append(backup)
    for path, updated in plans:
        path.write_text(updated, encoding="utf-8")
        print("Shared wake integration applied:", path)
    for backup in backups:
        print("Backup:", backup)
    print("Restart KlipperScreen at a suitable time to load this change.")
    return backups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path.home() / "KlipperScreen")
    parser.add_argument("--apply", action="store_true", help="Apply with backup; default is check only")
    args = parser.parse_args()
    try:
        apply(args.directory, args.apply)
    except (OSError, ValueError, SyntaxError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
