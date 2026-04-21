# Contributing

Thank you for your interest in BROskiPets!

The full contribution guide is in [docs/contributing.md](docs/contributing.md).

**Quick start:**

```bash
# Fork, clone, create a branch
git checkout -b feat/your-feature

# Make changes, then run tests
python -m pytest tests/ -v
cd contracts && forge test

# Commit and push
git push origin feat/your-feature
# Open a PR on GitHub
```

**Rules:**
- Both test suites must pass (Python: 108, Solidity: 16)
- New functionality needs tests
- Follow the style guide: [docs/style.md](docs/style.md)
- One feature per PR

**Security issues:** email [security@eepvengers.xyz](mailto:security@eepvengers.xyz) — do not open public issues for vulnerabilities.
