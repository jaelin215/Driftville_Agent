# Pull Request

## Title
<!-- Short, imperative: "Chore: Updated README with multi-OS support" -->
<!-- Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context. List any dependencies that are required for this change. -->


Fixes # (issue)

<!-- (Optional) Please provide a loom video for visual changes to speed up reviews
 Loom Video: https://www.loom.com/
-->

## Issue(s)
<!-- Link one or more issues, e.g., Fixes # (issue) -->

## Summary
<!-- 2–3 sentences: What problem does this PR solve? Why now? -->

## Scope
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] Chore (refactoring code, technical debt, workflow improvements)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactor (does not change functionality, e.g. code style improvements, linting)
- [ ] Documentation update (e.g. README.md)

## Changes
<!-- Bullet points of key changes; keep technical and concise -->
- 
- 
- 

## Acceptance Criteria
<!-- Copy from ticket(s) and mark each as met -->
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## How I Tested
<!-- What you ran and what you verified. Mention datasets/fixtures and outcomes. -->
- Unit tests: `poetry run pytest -q`
- Lint/format: `poetry run isort . && poetry run black . && poetry run flake8 .`
- Manual checks / screenshots noted below.

## Screenshots / Artifacts (optional)
<!-- Paste images or link logs/artifacts when useful -->

## API / DB Impact
- **API changes**: <!-- endpoints added/changed/removed; include request/response schema diffs -->
- **DB changes**: <!-- migrations or schema updates; backward-compat notes -->

## Follow-ups / Dependencies
<!-- Upstream/downstream tickets affected, TODOs intentionally deferred -->
- 

## Checklist
- [ ] Code compiles and passes CI locally (format → quality → tests)
- [ ] Added/updated tests for new logic and edge cases
- [ ] Updated docs / README where relevant
- [ ] No secrets or credentials committed
