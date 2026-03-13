# Contributing

Thanks for your interest in contributing to YouTube Automator.

## Before you start
- Open an issue for bugs, regressions, or feature proposals when possible.
- Keep pull requests focused and small.
- Do not commit secrets, OAuth tokens, generated media, or local environment files.

## Development setup
1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Create a local `.env` from `.env.example`.
4. Add your own API credentials locally only.

## Pull request guidelines
- Write clear commit messages.
- Preserve existing behavior unless the change intentionally alters it.
- Include a short summary of what changed and how it was tested.
- Update documentation when behavior or setup changes.

## Code style
- Follow existing Python style in the repository.
- Prefer small, readable functions.
- Avoid unrelated refactors in the same pull request.

## Security
If you discover a security issue, do not open a public issue. Follow the process in `SECURITY.md`.
