    def merge(self, env: dict[str, Value], branches: list[dict[str, Value]]) -> None:
        first, *rest = branches or [{}]
        for name in set().union(*(branch.keys() for branch in branches)):
            root = name.removeprefix("#record:")
            initial = (
                Value(key=root)
                if name.startswith("#record:") and root in self.objects
                else UNKNOWN_VALUE
            )
            value = first.get(name, initial)
            if (
                not name.startswith("#guard:")
                and (
                    value.sources
                    or not (
                        value.contained
                        or value.checked_path_parent
                        or value.option_safe
                        or value.url_checks
                    )
                )
                and all(
                    (other := branch.get(name, initial)) is value or other == value
                    for branch in rest
                )
            ):
                # Reuse unchanged state as the Python flow does. Guard markers
                # and source-free safety claims still use their normal merge.
                env[name] = value
                continue
            values = [branch.get(name, initial) for branch in branches]
            env[name] = (
                Value(contained=all(value.contained for value in values))
                if name.startswith("#guard:")
                else self.combined(values)
            )
