# Security Policy

## Supported use
This repository is intended to be used with your own API credentials and local OAuth files.

## Reporting a vulnerability
Please do not report security vulnerabilities in public issues.

Instead, contact the maintainer privately and include:
- A description of the issue
- Reproduction steps
- Potential impact
- Any suggested mitigation

## Sensitive data handling
Never commit any of the following:
- `.env`
- `client_secret.json`
- `token.pickle`
- Raw API keys, OAuth tokens, or private credentials

If a secret is committed accidentally:
1. Revoke and rotate it immediately.
2. Remove it from git history.
3. Update any affected deployment secrets.
