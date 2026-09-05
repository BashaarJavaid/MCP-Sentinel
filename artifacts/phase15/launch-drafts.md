# Phase 15 launch drafts — owner revises and publishes

Prepared 2026-09-04. These are unpublished maker drafts, not submitted posts.
Product readiness gates in [README.md](README.md) have passed; the public
1.2.1 release and both Action proofs are linked in [publication.json](publication.json).
List reviews may remain pending while announcements publish; Phase 15 cannot
close until both selected list PRs merge and all three announcements are accessible.

## Claims and destinations

Lead with four Docker-isolated probes, OWASP Agentic Top 10 mappings, validated
SARIF for GitHub code scanning, and replay of recorded GPT responses. Current
positive evidence is the [1.2.1 installed-wheel replay](replay/report.json): all
11 rule IDs, ten confirmed findings and one `needs_review` finding. The Docker
probes executed during this rehearsal; GPT responses came from existing captures.
Current cost is zero; recorded origin cost is historical, not new spend.

The [pinned real-server scan](public/walkthrough.json) has zero findings and skips
SENT-001 because permissions are absent. It proves repeatability and discloses
coverage, not that the Git server is secure. The new exact-tag/alias Action checks
passed on the clean fixture and prove integration, not positive alert creation.
For historical positive upload evidence cite [v0.1.0, 2026-07-21](../phase4-action-evidence.md)
and its [public run](https://github.com/BashaarJavaid/mcp-sentinel-action-demo/actions/runs/29874088698).

Canonical links to check again at publication:

- [PyPI 1.2.1](https://pypi.org/project/portunusmcp-sentinel/1.2.1/)
- [Marketplace](https://github.com/marketplace/actions/mcp-sentinel)
- [Documentation](https://bashaarjavaid.github.io/MCP-Sentinel/)
- [Walkthrough](https://bashaarjavaid.github.io/MCP-Sentinel/walkthrough/)
- [Source](https://github.com/BashaarJavaid/MCP-Sentinel)
- [Changelog](https://github.com/BashaarJavaid/MCP-Sentinel/blob/main/CHANGELOG.md)
- [Demo, 2:45, older MCP Sentinel v0.1.0 branding and historical alerts](https://www.youtube.com/watch?v=0myxPyTDx2c&t=3s)
- [Security policy](https://github.com/BashaarJavaid/MCP-Sentinel/security/policy)
- [Private report](https://github.com/BashaarJavaid/MCP-Sentinel/security/advisories/new)

Supported tiers: rules-only Python/TypeScript needs no credentials or Docker;
static plus GPT requires an operator-supplied key; full probing requires Docker
and a supported local Python target. TypeScript is static-only; JavaScript,
TSX, workspace analysis, imported handlers/schemas, cross-file TypeScript flow,
and Node execution are unsupported. Hosts: Python 3.10–3.13; dynamic targets:
Python 3.10–3.12. Replay works only with the bundled fixture captures.

## TensorBlock/awesome-mcp-servers

Read [Add or Improve an Entry](https://github.com/TensorBlock/awesome-mcp-servers#add-or-improve-an-entry)
and the [security category](https://github.com/TensorBlock/awesome-mcp-servers/blob/main/docs/security.md).
The README asks for a category markdown bullet, duplicate search, and PR; do
not edit generated catalog/profile files. The security category already contains
scanner CLI tooling, but acceptance of Sentinel's tooling scope belongs to its
maintainers. Do not claim Sentinel exposes MCP tools, a transport, or an endpoint.

Owner submission steps:

1. Fork the repository and create branch `add-portunusmcp-sentinel` from current main.
2. Search the repository for `BashaarJavaid/MCP-Sentinel` and `PortunusMCP Sentinel`.
   If already present, return for a scope decision instead of submitting a duplicate.
3. Add this single bullet to `docs/security.md`, preserving the surrounding style:

```markdown
- [BashaarJavaid/MCP-Sentinel](https://github.com/BashaarJavaid/MCP-Sentinel): Build-time scanner tooling for local MCP server source, with Python/TypeScript static checks, Docker-isolated Python probes, OWASP Agentic Top 10 mappings, and SARIF output. Install: `pipx install portunusmcp-sentinel`. MIT.
```

4. Open a PR against `TensorBlock/awesome-mcp-servers:main`, title
   `Add PortunusMCP Sentinel security scanner tooling`.
5. Body: “I maintain PortunusMCP Sentinel. This adds scanner tooling to the security
   category. It is a CLI/GitHub Action, not an MCP server endpoint. The runnable
   package, coverage boundaries, and pinned walkthrough are linked from the repo.”
6. Supply the PR URL for verification. If reviewers reject tooling or request a
   destination change, bring that decision back to the owner; do not replace this list.

## AIM-Intelligence/awesome-mcp-security

The [contribution guide](https://github.com/AIM-Intelligence/awesome-mcp-security/blob/main/CONTRIBUTING.md)
requests a PR and refers to the
[Awesome manifesto](https://github.com/sindresorhus/awesome/blob/main/awesome.md).
The current `README.md` has a **Tools** section with link, hyphen, description.

1. Fork the repository; branch from its default branch as `add-portunusmcp-sentinel`.
2. Search for the same project URL/name to avoid duplicates.
3. Append under **Tools**, before **Articles and Blog Posts**:

```markdown
- [PortunusMCP Sentinel](https://github.com/BashaarJavaid/MCP-Sentinel) - Build-time MCP security scanner with static Python/TypeScript analysis, Docker-isolated Python probes, OWASP Agentic Top 10 mappings, and SARIF reports. Includes recorded GPT review replay for its bundled demo.
```

4. Open a PR titled `Add PortunusMCP Sentinel to security tools`. Disclose authorship
   and link the runnable package and walkthrough. Submit only this focused entry.
5. Return the PR URL and later the merge URL; rejection or requested scope changes
   return to the owner.

## Show HN

Check [Show HN guidelines](https://news.ycombinator.com/showhn.html) and
[HN guidelines](https://news.ycombinator.com/newsguidelines.html) immediately before
posting. Submit the runnable product URL, not the walkthrough as the product.

Title: **Show HN: PortunusMCP Sentinel – Scan MCP servers before release**

URL: https://github.com/BashaarJavaid/MCP-Sentinel

Maker comment draft:

> I built PortunusMCP Sentinel for MCP server maintainers who want evidence before
> shipping. Its Python sandbox runs four fixed probes in isolated Docker containers;
> findings carry OWASP Agentic Top 10 mappings and export as SARIF for GitHub code scanning.
>
> Try `pipx install portunusmcp-sentinel==1.2.1`, then
> `sentinel scan /path/to/server --static-only --allow-degraded`. That path reads
> Python or supported TypeScript source without running it and needs no API key.
> Candidates remain unconfirmed without review. Full Python scans add GPT review
> and Docker; `sentinel demo --replay-review` runs fresh fixture probes using recorded
> GPT responses, with no new model calls.
>
> I documented an untouched, pinned official Git-server scan here:
> https://bashaarjavaid.github.io/MCP-Sentinel/walkthrough/
> It produced zero findings and one skipped rule; that is not a clean bill of health.
> I'd like maintainers to try it and share a minimal reproduction for missed patterns,
> false positives, or unclear reports. Sensitive reports go through the repo's private form.

Owner: revise in your own voice, submit through HN's Submit page with the title
and product URL, add your maker comment, and return the item URL. No vote requests.

## r/mcp

Recheck [community rules](https://www.reddit.com/r/mcp/about/rules/).
The rules allow disclosed self-promotion, require the showcase tag, disallow
waitlists, and prohibit AI-generated promotional slop. **Do not paste this draft
unchanged: the owner must rewrite it personally and check current rules.**

Title: **I built PortunusMCP Sentinel to scan MCP server source before release**

Flair/tag: **showcase** (verify the exact available spelling in the post UI).

Personal rewrite starting point:

> I'm the maker of PortunusMCP Sentinel, an MIT-licensed CLI and GitHub Action.
> The part I'd like feedback on is evidence: four isolated Docker probes for Python
> servers, OWASP mappings, and SARIF that fits GitHub code scanning.
>
> Install with `pipx install portunusmcp-sentinel==1.2.1`. You can start with
> `sentinel scan /path/to/server --static-only --allow-degraded` without credentials.
> Python and bounded TypeScript static checks are supported; dynamic probing is
> Python-only. The bundled demo replays recorded GPT responses while running Docker
> probes again. It does not make new GPT calls.
>
> Source: https://github.com/BashaarJavaid/MCP-Sentinel
> Reproducible scan and its limitations:
> https://bashaarjavaid.github.io/MCP-Sentinel/walkthrough/
>
> If you maintain a server, please try a scan and tell me which finding or missing
> pattern you can reproduce. I can use minimal examples more than general praise.

Owner posts after revision, then provides the accessible post URL.

## Glama-linked Discord community

Start at [Glama's MCP community link](https://glama.ai/mcp), which resolved via
`https://glama.ai/discord` to [invite C3eCXhYWtJ](https://discord.com/invite/C3eCXhYWtJ)
on 2026-09-04. The invite alone does not establish an eligible posting channel.

**Owner action required:** join/open the linked community, read server and channel
rules, confirm an eligible showcase channel, and revise the draft. If none exists,
return for a destination or scope change. No channel is assumed and nothing is posted.

> I made PortunusMCP Sentinel, a CLI/GitHub Action for MCP maintainers. It combines
> Docker-isolated Python probes, OWASP mappings, and SARIF reports. The bundled
> replay uses recorded GPT responses while executing fresh probes.
> `pipx install portunusmcp-sentinel==1.2.1`
> Rules-only scans need no key or Docker; TypeScript is static-only.
> Repo: https://github.com/BashaarJavaid/MCP-Sentinel
> Walkthrough: https://bashaarjavaid.github.io/MCP-Sentinel/walkthrough/
> I'd appreciate reproducible false positives, missed patterns, or confusing output
> from a scan of your server. I'm the author; sensitive reports belong in the private form.

Return the server/channel identification, applicable rules, and message permalink
for verification. If the community requires membership to view messages, record
that access limit rather than calling it anonymously public.
