# Contributing to DexAgent

Thank you for your interest in contributing to DexAgent! This document provides guidelines and instructions for contributing to the project.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our code of conduct:
- Be respectful and inclusive
- Use welcoming and constructive language
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:
- Git installed and configured
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- PostgreSQL 15+ (if not using Docker)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/dex_agent.git
   cd dex_agent
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Development Environment**
   ```bash
   make dev
   ```

4. **Verify Setup**
   ```bash
   make test-all
   ```

## 📋 Development Workflow

### 1. Issue Management

All contributions should be linked to a Jira issue or GitHub issue:

- **For new features**: Create an epic in Jira first
- **For bugs**: Create a bug report with reproduction steps
- **For improvements**: Create an improvement ticket with clear requirements

### 2. Branch Strategy

Use descriptive branch names that include the issue key:

```bash
# Feature branches
git checkout -b feature/DX-123-user-authentication

# Bug fix branches
git checkout -b bugfix/DX-124-login-validation

# Hotfix branches
git checkout -b hotfix/DX-125-security-patch
```

### 3. Commit Guidelines

Follow conventional commit format with Jira issue keys:

```bash
git commit -m "DX-123: Add user authentication feature

- Implement JWT token generation
- Add password hashing with bcrypt
- Create user registration endpoint
- Add authentication middleware"
```

**Commit Message Format:**
- **Subject**: `DX-XXX: Brief description (50 chars max)`
- **Body**: Detailed explanation of changes (wrap at 72 chars)
- **Footer**: References to issues, breaking changes

### 4. Code Standards

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters
- Use Black for code formatting
- Use isort for import sorting

```bash
# Format code
black apps/backend/
isort apps/backend/

# Lint code
flake8 apps/backend/
mypy apps/backend/
```

#### TypeScript/JavaScript (Frontend)
- Follow ESLint configuration
- Use Prettier for code formatting
- Use TypeScript for type safety
- Follow React best practices

```bash
# Format and lint
cd apps/frontend
npm run lint
npm run format
```

#### General Standards
- Write self-documenting code
- Add comments for complex logic
- Include docstrings for public functions
- Keep functions small and focused
- Use meaningful variable names

## 🧪 Testing Requirements

All contributions must include appropriate tests:

### Test Coverage Requirements
- **Minimum Coverage**: 80% for new code
- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test API endpoints and workflows
- **E2E Tests**: Test complete user journeys

### Running Tests

```bash
# Run all tests
make test-all

# Run specific test suites
make test-frontend      # Playwright E2E tests
make test-backend       # Python API tests
make test-integration   # Full integration tests

# Run with coverage
make test-coverage
```

### Writing Tests

#### Backend Tests (pytest)
```python
def test_user_authentication():
    """Test user authentication endpoint."""
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### Frontend Tests (Playwright)
```typescript
test('user can login successfully', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid=email]', 'admin@example.com');
  await page.fill('[data-testid=password]', 'password123');
  await page.click('[data-testid=login-button]');
  await expect(page).toHaveURL('/dashboard');
});
```

## 📝 Documentation

### Required Documentation
- **API Changes**: Update API_REFERENCE.md
- **Architecture Changes**: Update ARCHITECTURE_GUIDE.md
- **New Features**: Update README.md and relevant docs
- **Code Documentation**: Add docstrings and comments

### Documentation Standards
- Use clear, concise language
- Include code examples
- Provide complete setup instructions
- Update table of contents
- Include screenshots for UI changes

## 🔍 Code Review Process

### 1. Self-Review Checklist
Before submitting a PR, ensure:
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No sensitive information in code
- [ ] Performance impact considered
- [ ] Security implications reviewed

### 2. Pull Request Guidelines

#### PR Title Format
```
DX-123: Brief description of changes
```

#### PR Description Template
```markdown
## Summary
Brief description of the changes and their purpose.

## Jira Issue
- Link to Jira issue: [DX-123](link-to-jira-issue)

## Changes Made
- List of specific changes
- Technical details
- Impact on existing functionality

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact assessed
```

### 3. Review Process
1. **Automated Checks**: CI/CD pipeline must pass
2. **Peer Review**: At least one approved review required
3. **Testing Validation**: All tests must pass
4. **Documentation Review**: Ensure docs are current
5. **Security Review**: Assess security implications

## 🚀 Release Process

### Version Numbering
We use Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps
1. **Create Release Branch**: `release/vX.Y.Z`
2. **Update Version Numbers**: Update all relevant files
3. **Update CHANGELOG**: Document all changes
4. **Testing**: Complete release testing
5. **Create Release PR**: Merge to main
6. **Tag Release**: Create Git tag with version
7. **Deploy**: Deploy to production
8. **Monitor**: Monitor release and rollback if needed

## 🎯 Contribution Types

### 🐛 Bug Fixes
- Include reproduction steps
- Add regression tests
- Update documentation if needed
- Reference original issue

### ✨ New Features
- Start with Jira epic/story
- Include comprehensive tests
- Update documentation
- Consider backward compatibility

### 📚 Documentation
- Keep consistency with existing docs
- Include code examples
- Update navigation if needed
- Verify all links work

### 🔧 Refactoring
- Maintain existing functionality
- Include performance benchmarks
- Update relevant tests
- Document architectural changes

### 🚀 Performance Improvements
- Include benchmarks and metrics
- Document performance impact
- Add performance tests
- Consider scalability implications

## 🛠️ Development Tips

### Useful Commands
```bash
# Development workflow
make dev                    # Start development environment
make logs                   # View service logs
make status                 # Check service status
make restart               # Restart all services

# Testing workflow
make test-watch            # Run tests in watch mode
make test-debug           # Run tests with debugging
make lint                 # Run all linters
make format               # Format all code

# Database operations
make db-reset             # Reset database
make db-migrate           # Run migrations
make db-backup            # Backup database

# Docker operations
make docker-clean         # Clean Docker resources
make docker-rebuild       # Rebuild all containers
```

### IDE Setup

#### VS Code Extensions
- Python
- Pylance
- TypeScript and JavaScript Language Features
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- GitLens
- Docker

#### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./apps/backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## 🆘 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Project Documentation**: Comprehensive guides and references
- **Code Comments**: Inline documentation and explanations

### Mentorship Program
New contributors can request mentorship:
1. Comment on a "good first issue"
2. Tag @maintainers for guidance
3. Join our community discussions
4. Attend virtual office hours (if available)

## 🎉 Recognition

Contributors are recognized through:
- **Contributor List**: Listed in project documentation
- **Release Notes**: Mentioned in changelog
- **Social Media**: Highlighted on project social accounts
- **Badges**: Contributor badges on GitHub profile

## 📋 Issue Labels

Understanding our label system:

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to docs |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `question` | Further information is requested |
| `wontfix` | This will not be worked on |
| `duplicate` | This issue or pull request already exists |
| `invalid` | This doesn't seem right |

## 🔐 Security

### Reporting Security Issues
- **DO NOT** create public issues for security vulnerabilities
- Email security concerns to: security@dexagent.com
- Include detailed reproduction steps
- We will respond within 48 hours

### Security Guidelines
- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP security practices
- Encrypt sensitive data in transit and at rest

---

Thank you for contributing to DexAgent! Your contributions help make this project better for everyone. 🚀