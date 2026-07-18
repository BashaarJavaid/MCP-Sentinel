"""Remove stale MCP Sentinel probe containers."""

from sentinel.dynamic.sandbox import reap_orphans


def main() -> None:
    reap_orphans()


if __name__ == "__main__":
    main()
