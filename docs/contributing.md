# Contributing to BROskiPets

Contributions are welcome from everyone — whether you're fixing a typo, adding a new EEP, or shipping a major feature. This doc explains how to contribute effectively.

---

## Before You Start

- Check [open issues](https://github.com/welshDog/BROskiPets-LLM-dNFT/issues) — someone may already be working on your idea
- For significant changes, open an issue first to discuss the approach
- Read [docs/style.md](style.md) before writing code

---

## Workflow

### 1 — Fork and clone

```bash
# Fork via GitHub UI, then:
git clone https://github.com/YOUR_USERNAME/BROskiPets-LLM-dNFT.git
cd BROskiPets-LLM-dNFT
git remote add upstream https://github.com/welshDog/BROskiPets-LLM-dNFT.git
```

### 2 — Create a branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:

| Prefix | When to use |
|--------|------------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `test/` | Adding/fixing tests |
| `chore/` | Build scripts, CI, tooling |
| `refactor/` | Code restructuring, no behaviour change |

### 3 — Make your changes

Follow the style guide in [docs/style.md](style.md).

### 4 — Run tests

Both test suites must pass before opening a PR:

```bash
# Python
python -m pytest tests/ -v

# Solidity
cd contracts && forge test -v
```

If you added new code, add corresponding tests. PRs without tests for new functionality will be asked to add them.

### 5 — Commit

Write clear, concise commit messages:

```bash
# Good
git commit -m "fix: prevent evolve() from blocking first evolution on new tokens"
git commit -m "feat: add upload_metadata_to_ipfs() with Redis CID caching"
git commit -m "docs: add FastAPI endpoint reference to api.md"

# Not helpful
git commit -m "fix stuff"
git commit -m "wip"
git commit -m "updates"
```

**Commit message format:**

```
<type>: <short description (max 72 chars)>

[optional body — explain WHY, not WHAT]
```

Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `security`

### 6 — Push and open a PR

```bash
git push origin feat/your-feature-name
```

Then open a pull request on GitHub. Fill in the PR template:

- **What does this PR do?** — one paragraph summary
- **Why?** — motivation or issue link
- **How was it tested?** — test output or manual steps
- **Breaking changes?** — yes/no; if yes, describe the impact

---

## What Makes a Good PR

- **Small and focused** — one feature or fix per PR. Reviewers will thank you.
- **Tests included** — new behaviour needs tests; bug fixes need a test that would have caught the bug
- **No unrelated changes** — don't fix typos or refactor code that isn't related to your PR's purpose
- **Passing CI** — both test suites green before requesting review

---

## Types of Contributions

### Bug fixes

1. Open an issue describing the bug (or reference existing)
2. Write a failing test that reproduces the bug
3. Fix the code
4. Confirm the test now passes
5. Open a PR

### New EEPs

The squad is currently capped at 78 (`MAX_SUPPLY` in the contract). New EEPs require a governance decision. Open an issue tagged `[EEP proposal]` with:

- Name and species
- Role and power
- Proposed rarity (with justification)
- How it maps to a real capability in the HyperCode ecosystem

### Documentation improvements

Documentation PRs are always welcome. No test suite requirement — just open a PR.

### Security issues

**Do not open a public issue for security vulnerabilities.**

Email [security@eepvengers.xyz](mailto:security@eepvengers.xyz) with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

You will receive a response within 48 hours.

---

## Code Review

All PRs require at least one review from a maintainer. Feedback is given as inline comments. Address all comments before the PR can be merged.

**Response time:** maintainers aim to review within 5 business days. If you haven't heard back after a week, leave a comment on the PR.

---

## Setting Up Your Dev Environment

See [docs/development.md](development.md) for the full setup guide.

**Quick version:**

```bash
python -m venv .venv && source .venv/bin/activate
pip install redis httpx pytest fakeredis

# Contract tooling
curl -L https://foundry.paradigm.xyz | bash && foundryup
cd contracts && forge install
```

---

## Style Guide

See [docs/style.md](style.md) for the full guide.

**Key rules:**

- Python: follow PEP 8, use `black` for formatting, `ruff` for linting
- Solidity: OpenZeppelin style, NatSpec on all public functions, custom errors preferred
- Comments: explain *why*, not *what* — the code already says what
- No emojis in code (docs are fine)

---

## Questions?

- Open a [GitHub Discussion](https://github.com/welshDog/BROskiPets-LLM-dNFT/discussions)
- Tag an issue with `question`

Built by a dyslexic tinkerer from Wales — all contributors welcome, all skill levels, all backgrounds.
