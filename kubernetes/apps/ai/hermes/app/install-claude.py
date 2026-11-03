"""Install pinned Claude artifacts on the Hermes PVC before the gateway starts."""

import hashlib
import os
from pathlib import Path
import platform
import shutil
import tarfile
import tempfile
import time
import urllib.request


CLAUDE_VERSION = "2.1.317"
# Published in the release's manifest.json at downloads.claude.ai.
CLAUDE_SHA256 = {
    "x86_64": ("linux-x64", "eb224419e344575faa4a1f39b290b649425a10cd5ee2ef1d003480cd9ae57eb0"),
    "aarch64": ("linux-arm64", "563a0d60ad0c223d9415768210997acb0f7134ea51dc3c238e88bc2e18ddeefa"),
}
# Claude Subscription DirectSDK 0.3.4, pinned to the reviewed catalog commit.
PLUGIN_COMMIT = "1b9102c7c4211b9622680fe6e2b78246634cbc1d"
PLUGIN_SHA256 = "4c87517b726c7a49f5551e9ca95ea42dbaf39f2fbd8feb3ff7694c67828aa5a6"
PLUGIN_NAME = "claude-subscription-directsdk-experimental"
PLUGIN_DIRECTORY = "claude-subscription-directsdk"


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def download(url, destination, expected):
    """Keep verified downloads across pod replacements; publish only complete files."""
    if destination.is_file() and digest(destination) == expected:
        print(f"Using cached {destination.name}", flush=True)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
                candidate = Path(temporary) / destination.name
                with urllib.request.urlopen(url, timeout=60) as response, candidate.open("wb") as output:
                    shutil.copyfileobj(response, output)
                if digest(candidate) != expected:
                    raise ValueError(f"Checksum mismatch for {destination.name}")
                os.replace(candidate, destination)
            print(f"Installed verified {destination.name}", flush=True)
            return
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2)


def link(target, destination):
    """Switch managed versions without replacing an unrelated user installation."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not destination.is_symlink():
        raise RuntimeError(f"Refusing to replace unmanaged path: {destination}")
    if destination.is_symlink() and destination.resolve() == target.resolve():
        return
    temporary = destination.with_name(destination.name + ".new")
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(target)
    os.replace(temporary, destination)


def main():
    os.umask(0o077)
    home = Path(os.environ["HERMES_HOME"])
    managed = home / ".local/share/hermes-managed"
    target_platform, checksum = CLAUDE_SHA256[platform.machine()]
    binary = managed / "claude" / CLAUDE_VERSION / target_platform / "claude"
    download(
        f"https://downloads.claude.ai/claude-code-releases/{CLAUDE_VERSION}/{target_platform}/claude",
        binary,
        checksum,
    )
    binary.chmod(0o755)
    link(binary, home / ".local/bin/claude")

    archive = managed / "downloads" / f"claude-plugin-{PLUGIN_COMMIT}.tar.gz"
    download(
        f"https://codeload.github.com/NousResearch/hermes-official-plugins/tar.gz/{PLUGIN_COMMIT}",
        archive,
        PLUGIN_SHA256,
    )
    installed = managed / "plugins" / PLUGIN_COMMIT
    if not installed.is_dir():
        installed.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=installed.parent) as temporary:
            prefix = f"hermes-official-plugins-{PLUGIN_COMMIT}/{PLUGIN_DIRECTORY}"
            with tarfile.open(archive, "r:gz") as source:
                members = [m for m in source.getmembers() if m.name.startswith(prefix + "/")]
                source.extractall(temporary, members=members, filter="data")
            extracted = Path(temporary) / prefix
            for required in ("plugin.yaml", "__init__.py", "directsdk.py"):
                if not (extracted / required).is_file():
                    raise RuntimeError(f"Plugin archive is missing {required}")
            os.replace(extracted, installed)
    link(installed, home / "plugins" / PLUGIN_NAME)

    # Claude Code owns and refreshes its credentials; never seed or overwrite them.
    auth = home / ".claude"
    auth.mkdir(mode=0o700, exist_ok=True)
    auth.chmod(0o700)
    print(f"Claude Code {CLAUDE_VERSION} and plugin {PLUGIN_COMMIT[:7]} ready", flush=True)


if __name__ == "__main__":
    main()
