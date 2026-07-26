#!/bin/sh
# Install Frontier directly from a public GitHub repository.
#
# Examples:
#   curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh
#   curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh -s -- --agent codex
#   curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh -s -- --agent pi

set -eu

repository=${FRONTIER_REPOSITORY:-dannylee1020/frontier}
ref=${FRONTIER_REF:-main}
archive_url=${FRONTIER_ARCHIVE_URL:-https://github.com/${repository}/archive/refs/heads/${ref}.tar.gz}

fail() {
    printf '%s\n' "frontier installer: $*" >&2
    exit 1
}

command -v curl >/dev/null 2>&1 || fail "curl is required"
command -v tar >/dev/null 2>&1 || fail "tar is required"
command -v python3.12 >/dev/null 2>&1 || fail "python3.12 is required"

base_tmp=${TMPDIR:-/tmp}
tmp_dir=$(mktemp -d "${base_tmp%/}/frontier-install.XXXXXX") || fail "could not create a temporary directory"

cleanup() {
    rm -rf "$tmp_dir"
}
trap cleanup EXIT HUP INT TERM

archive_path="$tmp_dir/frontier.tar.gz"
printf '%s\n' "frontier installer: downloading $archive_url"
curl -fsSL --retry 2 --retry-delay 1 "$archive_url" -o "$archive_path" || fail "could not download $archive_url"

tar -xzf "$archive_path" -C "$tmp_dir" || fail "could not extract the repository archive"

source_dir=
for candidate in "$tmp_dir"/*; do
    if [ -f "$candidate/scripts/install.py" ]; then
        source_dir=$candidate
        break
    fi
done

[ -n "$source_dir" ] || fail "downloaded archive did not contain scripts/install.py"

exec python3.12 "$source_dir/scripts/install.py" "$@"
