#!/usr/bin/env bash
# One-shot installer for the paper-writing skill (OpenAI Codex + DeepSeek Harness).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.sh | bash -s -- codex   # codex | dsh | all (default)
#   curl -fsSL https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.sh | bash -s -- all --uninstall
#
# Targets:
#   Codex : $CODEX_HOME/skills/paper-writing   (default ~/.codex/skills)
#   DSH   : ~/.agents/skills/paper-writing
#
# Re-running updates: git installs get "git pull --ff-only"; plain folders are
# backed up to <dir>.bak-<timestamp> and replaced.
set -euo pipefail

SKILL_NAME="paper-writing"
OWNER="xiaoxiaomuyu321"
REPO="paper-writing"
BRANCH="main"
CLONE_URL="https://github.com/$OWNER/$REPO.git"
TARBALL_URL="https://codeload.github.com/$OWNER/$REPO/tar.gz/refs/heads/$BRANCH"

TARGET="all"
UNINSTALL=0
for arg in "$@"; do
  case "$arg" in
    all|codex|dsh) TARGET="$arg" ;;
    --uninstall|-u) UNINSTALL=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

# Source of the skill files: a local clone if this script runs from one,
# otherwise GitHub (works when piped).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" >/dev/null 2>&1 && pwd)"
LOCAL_CLONE=""
if [ -f "$SCRIPT_DIR/SKILL.md" ] && [ -d "$SCRIPT_DIR/.git" ]; then
  LOCAL_CLONE="$SCRIPT_DIR"
fi

TMPDIR_WORK=""
cleanup() { [ -n "$TMPDIR_WORK" ] && rm -rf "$TMPDIR_WORK"; }
trap cleanup EXIT

download() { # download <url> <out>
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$1" -o "$2"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$2" "$1"
  else
    echo "need curl or wget" >&2; exit 1
  fi
}

check_installed() { # check_installed <host> <dest>
  if [ -f "$2/SKILL.md" ]; then
    echo "[$1] installed: $2"
  else
    echo "[$1] install failed: SKILL.md not found in $2" >&2; exit 1
  fi
}

install_fresh() { # install_fresh <host> <dest>
  local host="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if command -v git >/dev/null 2>&1; then
    echo "[$host] git clone -> $dest"
    if git clone -q --depth 1 -b "$BRANCH" "${LOCAL_CLONE:-$CLONE_URL}" "$dest" 2>/dev/null; then
      [ -n "$LOCAL_CLONE" ] && git -C "$dest" remote set-url origin "$CLONE_URL"
      check_installed "$host" "$dest"
      return 0
    fi
    echo "[$host] git clone failed; falling back to tarball." >&2
    rm -rf "$dest"
  fi
  echo "[$host] downloading tarball -> $dest"
  TMPDIR_WORK="$(mktemp -d)"
  download "$TARBALL_URL" "$TMPDIR_WORK/skill.tar.gz"
  tar -xzf "$TMPDIR_WORK/skill.tar.gz" -C "$TMPDIR_WORK"
  local inner
  inner="$(find "$TMPDIR_WORK" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [ -f "$inner/SKILL.md" ] || { echo "SKILL.md missing in archive" >&2; exit 1; }
  mv "$inner" "$dest"
  check_installed "$host" "$dest"
}

install_one() { # install_one <host> <dest>
  local host="$1" dest="$2"
  if [ -e "$dest" ]; then
    if [ -d "$dest/.git" ]; then
      echo "[$host] updating existing git install at $dest"
      if git -C "$dest" fetch -q origin "$BRANCH" 2>/dev/null && git -C "$dest" pull -q --ff-only 2>/dev/null; then
        echo "[$host] updated."
      else
        echo "[$host] fast-forward failed (local changes?); keeping $dest as is." >&2
      fi
    else
      local bak="$dest.bak-$(date +%Y%m%d-%H%M%S)"
      mv "$dest" "$bak"
      echo "[$host] previous plain install backed up to $bak"
      install_fresh "$host" "$dest"
    fi
  else
    install_fresh "$host" "$dest"
  fi
}

uninstall_one() { # uninstall_one <host> <dest>
  local host="$1" dest="$2"
  if [ -e "$dest" ]; then
    rm -rf "$dest"
    echo "[$host] uninstalled: $dest"
  else
    echo "[$host] not installed: $dest"
  fi
}

for t in $(case "$TARGET" in all) echo codex dsh ;; *) echo "$TARGET" ;; esac); do
  case "$t" in
    codex) DIR="$CODEX_HOME/skills/$SKILL_NAME" ;;
    dsh)   DIR="$HOME/.agents/skills/$SKILL_NAME" ;;
  esac
  if [ "$UNINSTALL" -eq 1 ]; then
    uninstall_one "$t" "$DIR"
  else
    install_one "$t" "$DIR"
  fi
done
echo "Done."
