---
applyTo: '**'
---

# MyML.NetApp Pull Request Description Guidelines (C#/.NET)

## PR Title Format

Follow the convention: `<type>(<scope>): <subject>`

Examples:
- `feat(model): add confidence interval calculation to ModelBuilder`
- `fix(console): handle missing model file in Predict`
- `refactor(lib): move training logic to shared library`

## PR Description Structure

```markdown
## Purpose

[Clearly explain what this PR accomplishes and why it is needed. Reference any business or technical requirements.]

## Changes

- [Bullet point list of specific changes]
- [Highlight C#/.NET code, project, or solution structure changes]
- [Note any configuration, NuGet, or environment changes]

## Related Issues

Fixes #123 Related to #456

## Testing Performed

- [Describe manual and automated test steps]
- [List new or updated xUnit/NUnit/MSTest tests]
- [Include test coverage or edge cases addressed]
- [Mention if you ran `dotnet test` and results]

## Screenshots

[If UI/console output changes, include before/after screenshots or sample output]

## Deployment Notes

- [Flag any .NET version, NuGet, or environment variable changes]
- [Note if new build steps, scripts, or migrations are required]
- [Mention backward compatibility or breaking changes]

## Additional Context

[Any other information that would be helpful to reviewers, such as design decisions, trade-offs, or links to documentation]

```

## Key Components to Include

### Purpose Section
- Clearly state the problem being solved
- Explain why these changes are needed (e.g., code quality, maintainability, new feature)
- Reference requirements or user stories if applicable

### Changes Section
- Use bullet points for clarity
- Group related changes (e.g., model, tests, CI/CD)
- Highlight significant C#/.NET code changes (e.g., new classes, refactoring, dependency injection)
- Note new or removed NuGet dependencies, project references, or solution structure changes

### Testing Section
- List specific test cases covered (unit, integration, edge cases)
- Note if you added/updated xUnit/NUnit/MSTest tests
- Mention if you ran `dotnet test` and if all tests pass
- Include code coverage improvements if relevant
- Mention any manual testing (e.g., running the console app)

### Deployment Notes
- Flag changes that require .NET SDK/runtime updates
- Note new or changed environment variables, config files, or build scripts
- Highlight potential backward compatibility issues
- Mention if a new model file or data migration is required

## Example Good PR Description

```markdown
## Purpose

Improve error handling in the prediction workflow and add test coverage for missing model scenarios.

## Changes

- Add exception handling to `ModelBuilder.Predict` for missing model file
- Add xUnit test to verify `Predict` throws `FileNotFoundException`
- Update README with troubleshooting steps for missing model
- Refactor test data to ensure multiclass scenarios are always valid

## Related Issues

Fixes #42

## Testing Performed

- Added/ran xUnit tests for missing model file
- Ran `dotnet test` (all tests passing)
- Manually tested console app for error message when model is missing

## Screenshots

N/A (no UI changes)

## Deployment Notes

- No breaking changes
- Ensure `MLModel.zip` is present in the correct directory for production use

## Additional Context

- See [CHANGELOG.md](../../CHANGELOG.md) for a summary of all recent changes
```
