# Contributing to Agent Workflow Builder

🎉 **Thank you for your interest in contributing to Agent Workflow Builder!** We're excited to have you join our community of developers building the future of AI agent workflows.

This document provides guidelines and information for contributors. Please read it carefully before making your first contribution.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@agent-workflow-builder.com](mailto:conduct@agent-workflow-builder.com).

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher)
- **Python** (v3.11 or higher)
- **Docker** and **Docker Compose**
- **Git**
- **Make** (optional, for using Makefile commands)

### Quick Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/agent-workflow-builder.git
   cd agent-workflow-builder
   ```
3. **Set up the development environment**:
   ```bash
   make setup
   # or manually:
   cp .env.example .env
   make install
   make dev
   ```
4. **Verify the setup** by visiting:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/docs

## 🛠️ Development Setup

### Environment Configuration

1. **Copy environment files**:
   ```bash
   cp .env.example .env
   cp frontend/.env.local.example frontend/.env.local
   cp backend/api/.env.example backend/api/.env
   ```

2. **Configure your API keys** in `.env`:
   ```bash
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   # ... other keys as needed
   ```

### Running Services

```bash
# Start all services
make dev

# Start individual services
make frontend-dev  # Frontend only
make backend-dev   # Backend API only

# View logs
make dev-logs

# Stop services
make dev-stop
```

### Database Setup

```bash
# Setup database with migrations and seed data
make db-setup

# Reset database (WARNING: Deletes all data)
make db-reset

# Run migrations only
make db-migrate
```

## 🤲 How to Contribute

### Types of Contributions

We welcome many types of contributions:

- 🐛 **Bug Reports** - Help us identify and fix issues
- ✨ **Feature Requests** - Suggest new features or improvements
- 💻 **Code Contributions** - Submit bug fixes, features, or improvements
- 📚 **Documentation** - Improve our docs, tutorials, or examples
- 🧪 **Testing** - Add tests or improve test coverage
- 🎨 **Design** - UI/UX improvements and design assets
- 🌍 **Translations** - Help make the project accessible globally

### Before You Start

1. **Check existing issues** to avoid duplicating work
2. **Create an issue** for discussion before major changes
3. **Join our Discord** for real-time collaboration
4. **Read our roadmap** to understand project direction

### Issue Guidelines

When creating issues, please:

- Use a clear and descriptive title
- Provide detailed steps to reproduce (for bugs)
- Include screenshots or recordings when helpful
- Use our issue templates when available
- Add appropriate labels

**Bug Report Template:**
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '.…'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g. macOS 12.0]
- Browser: [e.g. Chrome 95]
- Version: [e.g. 1.0.0]

## Additional Context
Any other context about the problem
```

## 🔄 Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Branch Naming Convention

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `test/description` - Test additions/changes
- `refactor/description` - Code refactoring
- `style/description` - Code style changes

### 2. Make Your Changes

- Follow our [coding standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Test Your Changes

```bash
# Run all tests
make test

# Run specific test suites
make frontend-test
make backend-test
make test-integration

# Check code quality
make lint
make format

# Check types
cd frontend && npm run type-check
```

### 4. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add drag-and-drop agent library"
git commit -m "fix: resolve connection rendering issue"
git commit -m "docs: update API documentation"
```

**Commit Types:**
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- Clear title and description
- Reference to related issues
- Screenshots/recordings for UI changes
- Checklist of changes made

### 6. PR Review Process

1. **Automated checks** must pass (CI/CD, tests, linting)
2. **Code review** by maintainers
3. **Testing** by reviewers when needed
4. **Approval** and merge by maintainers

## 🎨 Coding Standards

### Frontend (React/TypeScript)

```typescript
// Use functional components with hooks
export function WorkflowCanvas(): JSX.Element {
  const [nodes, setNodes] = useState<Node[]>([]);
  
  // Use TypeScript interfaces
  interface Node {
    id: string;
    type: NodeType;
    position: Position;
  }
  
  // Use proper naming conventions
  const handleNodeClick = useCallback((nodeId: string) => {
    // Implementation
  }, []);
  
  return (
    <div className="workflow-canvas">
      {/* JSX content */}
    </div>
  );
}
```

**Frontend Guidelines:**
- Use TypeScript for all new code
- Follow React hooks patterns
- Use Tailwind CSS for styling
- Implement proper error boundaries
- Write component tests

### Backend (Python/FastAPI)

```python
# Use type hints
from typing import List, Optional
from pydantic import BaseModel

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    definition: dict

# Use async/await for database operations
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession,
    current_user: User
) -> Workflow:
    """Create a new workflow."""
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        created_by=current_user.id
    )
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow)
    return db_workflow
```

**Backend Guidelines:**
- Use type hints everywhere
- Follow PEP 8 style guide
- Write comprehensive docstrings
- Use async/await for I/O operations
- Implement proper error handling

### General Guidelines

- **DRY Principle** - Don't Repeat Yourself
- **SOLID Principles** - Single Responsibility, Open/Closed, etc.
- **Clean Code** - Self-documenting, readable code
- **Security First** - Always consider security implications
- **Performance** - Write efficient, scalable code

## 🧪 Testing Guidelines

### Frontend Testing

```typescript
// Component testing with React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { WorkflowCanvas } from './WorkflowCanvas';

describe('WorkflowCanvas', () => {
  it('should render canvas with nodes', () => {
    render(<WorkflowCanvas />);
    expect(screen.getByTestId('workflow-canvas')).toBeInTheDocument();
  });

  it('should handle node selection', () => {
    const mockOnSelect = jest.fn();
    render(<WorkflowCanvas onNodeSelect={mockOnSelect} />);
    
    fireEvent.click(screen.getByTestId('node-1'));
    expect(mockOnSelect).toHaveBeenCalledWith('node-1');
  });
});
```

### Backend Testing

```python
# Use pytest for backend testing
import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_create_workflow(client: AsyncClient, auth_headers: dict):
    """Test workflow creation endpoint."""
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "definition": {"nodes": [], "connections": []}
    }
    
    response = await client.post(
        "/workflows/",
        json=workflow_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Workflow"
    assert "id" in data
```

### Test Coverage

- Aim for **>80% code coverage**
- Write unit tests for all new functions
- Add integration tests for API endpoints
- Include E2E tests for critical user flows

## 📚 Documentation

### Code Documentation

- Write clear docstrings for all functions and classes
- Add inline comments for complex logic
- Update README files when adding new features
- Include examples in API documentation

### User Documentation

- Update user guides for new features
- Add tutorials for complex workflows
- Keep API documentation current
- Include screenshots and videos when helpful

### Documentation Structure

```
docs/
├── api/              # API documentation
├── user-guide/       # End-user documentation
├── development/      # Developer documentation
└── architecture/     # System architecture docs
```

## 🎯 Performance Guidelines

### Frontend Performance

- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Optimize bundle size with code splitting
- Use proper image optimization

### Backend Performance

- Use database indexes appropriately
- Implement caching where beneficial
- Use async operations for I/O
- Monitor and optimize query performance

## 🔒 Security Guidelines

- Never commit secrets or API keys
- Validate all user inputs
- Use parameterized database queries
- Implement proper authentication/authorization
- Follow OWASP security guidelines

## 🌍 Internationalization

- Use i18n libraries for text strings
- Avoid hardcoded text in components
- Consider RTL language support
- Test with different locales

## 📝 Changelog

We maintain a changelog following [Keep a Changelog](https://keepachangelog.com/):

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

## 💬 Community

### Getting Help

- 💬 **Discord**: [Join our Discord server](https://discord.gg/agent-workflow-builder)
- 📧 **Email**: [support@agent-workflow-builder.com](mailto:support@agent-workflow-builder.com)
- 🐙 **GitHub Discussions**: [GitHub Discussions](https://github.com/agent-workflow-builder/discussions)
- 📚 **Documentation**: [docs.agent-workflow-builder.com](https://docs.agent-workflow-builder.com)

### Recognition

Contributors are recognized in:

- Our README contributors section
- Release notes for significant contributions
- Annual contributor spotlight
- Swag and rewards for major contributions

## 📜 License

By contributing to Agent Workflow Builder, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

---

## 🎉 Thank You!

Every contribution, no matter how small, helps make Agent Workflow Builder better for everyone. We appreciate your time and effort in helping us build the future of AI agent workflows!

**Happy coding! 🚀**