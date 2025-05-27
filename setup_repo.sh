#!/bin/bash

# Agent Workflow Builder - Repository Setup Script
# This script creates the complete directory structure and empty files

echo "🚀 Setting up Agent Workflow Builder Repository..."

# Create main directories
directories=(
    # Root directories
    "frontend"
    "backend"
    "docs"
    "scripts"
    "deploy"
    "tests"
    "examples"
    
    # Frontend structure
    "frontend/src"
    "frontend/src/components"
    "frontend/src/components/Canvas"
    "frontend/src/components/AgentLibrary"
    "frontend/src/components/WorkflowNodes"
    "frontend/src/components/Connections"
    "frontend/src/components/Toolbar"
    "frontend/src/components/ConfigPanels"
    "frontend/src/components/Common"
    "frontend/src/hooks"
    "frontend/src/utils"
    "frontend/src/services"
    "frontend/src/store"
    "frontend/src/types"
    "frontend/src/assets"
    "frontend/src/assets/icons"
    "frontend/src/assets/images"
    "frontend/public"
    
    # Backend API structure
    "backend/api"
    "backend/api/routes"
    "backend/api/middleware"
    "backend/api/models"
    "backend/api/schemas"
    "backend/api/services"
    "backend/api/utils"
    "backend/api/config"
    
    # Agent Engine
    "backend/agent-engine"
    "backend/agent-engine/core"
    "backend/agent-engine/frameworks"
    "backend/agent-engine/frameworks/langchain"
    "backend/agent-engine/frameworks/crewai"
    "backend/agent-engine/frameworks/autogen"
    "backend/agent-engine/tools"
    "backend/agent-engine/memory"
    "backend/agent-engine/executors"
    
    # Workflow Engine
    "backend/workflow-engine"
    "backend/workflow-engine/parser"
    "backend/workflow-engine/scheduler"
    "backend/workflow-engine/runner"
    "backend/workflow-engine/monitoring"
    
    # Shared services
    "backend/shared"
    "backend/shared/database"
    "backend/shared/auth"
    "backend/shared/logging"
    "backend/shared/messaging"
    "backend/shared/storage"
    
    # Integration services
    "backend/integrations"
    "backend/integrations/llm-providers"
    "backend/integrations/databases"
    "backend/integrations/cloud-services"
    "backend/integrations/apis"
    
    # Database
    "database"
    "database/migrations"
    "database/seeds"
    "database/schemas"
    
    # Docker and deployment
    "deploy/docker"
    "deploy/kubernetes"
    "deploy/terraform"
    "deploy/helm"
    
    # Documentation
    "docs/api"
    "docs/architecture"
    "docs/user-guide"
    "docs/development"
    "docs/deployment"
    
    # Tests
    "tests/frontend"
    "tests/backend"
    "tests/integration"
    "tests/e2e"
    "tests/fixtures"
    
    # Examples and templates
    "examples/workflows"
    "examples/agents"
    "examples/integrations"
)

# Create all directories
echo "📁 Creating directory structure..."
for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo "  ✓ Created: $dir"
done

# Root files
root_files=(
    "README.md"
    ".gitignore"
    "LICENSE"
    "CONTRIBUTING.md"
    "CHANGELOG.md"
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "Makefile"
    ".env.example"
    ".github/workflows/ci.yml"
    ".github/workflows/deploy.yml"
    ".github/ISSUE_TEMPLATE/bug_report.md"
    ".github/ISSUE_TEMPLATE/feature_request.md"
    ".github/pull_request_template.md"
)

# Frontend files
frontend_files=(
    "frontend/package.json"
    "frontend/package-lock.json"
    "frontend/tsconfig.json"
    "frontend/tailwind.config.js"
    "frontend/next.config.js"
    "frontend/Dockerfile"
    "frontend/.env.local.example"
    "frontend/public/favicon.ico"
    "frontend/public/manifest.json"
    
    # Components
    "frontend/src/components/Canvas/WorkflowCanvas.tsx"
    "frontend/src/components/Canvas/CanvasToolbar.tsx"
    "frontend/src/components/Canvas/MiniMap.tsx"
    "frontend/src/components/Canvas/GridBackground.tsx"
    
    "frontend/src/components/AgentLibrary/AgentLibrary.tsx"
    "frontend/src/components/AgentLibrary/CategoryList.tsx"
    "frontend/src/components/AgentLibrary/AgentCard.tsx"
    "frontend/src/components/AgentLibrary/SearchBar.tsx"
    "frontend/src/components/AgentLibrary/FilterPanel.tsx"
    
    "frontend/src/components/WorkflowNodes/BaseNode.tsx"
    "frontend/src/components/WorkflowNodes/LLMNode.tsx"
    "frontend/src/components/WorkflowNodes/ToolNode.tsx"
    "frontend/src/components/WorkflowNodes/CrewAINode.tsx"
    "frontend/src/components/WorkflowNodes/LangChainNode.tsx"
    
    "frontend/src/components/Connections/Connection.tsx"
    "frontend/src/components/Connections/ConnectionManager.tsx"
    "frontend/src/components/Connections/ConnectionPoint.tsx"
    
    "frontend/src/components/Toolbar/MainToolbar.tsx"
    "frontend/src/components/Toolbar/ExecutionControls.tsx"
    "frontend/src/components/Toolbar/WorkflowActions.tsx"
    
    "frontend/src/components/ConfigPanels/NodeConfigPanel.tsx"
    "frontend/src/components/ConfigPanels/WorkflowSettings.tsx"
    "frontend/src/components/ConfigPanels/EnvironmentVariables.tsx"
    "frontend/src/components/ConfigPanels/ConnectionManager.tsx"
    
    "frontend/src/components/Common/Modal.tsx"
    "frontend/src/components/Common/Button.tsx"
    "frontend/src/components/Common/Input.tsx"
    "frontend/src/components/Common/Dropdown.tsx"
    "frontend/src/components/Common/LoadingSpinner.tsx"
    
    # Hooks
    "frontend/src/hooks/useWorkflow.ts"
    "frontend/src/hooks/useNodes.ts"
    "frontend/src/hooks/useConnections.ts"
    "frontend/src/hooks/useWebSocket.ts"
    "frontend/src/hooks/useAuth.ts"
    
    # Services
    "frontend/src/services/api.ts"
    "frontend/src/services/websocket.ts"
    "frontend/src/services/auth.ts"
    "frontend/src/services/workflow.ts"
    "frontend/src/services/agents.ts"
    
    # Utils
    "frontend/src/utils/canvas.ts"
    "frontend/src/utils/validation.ts"
    "frontend/src/utils/constants.ts"
    "frontend/src/utils/helpers.ts"
    
    # Store
    "frontend/src/store/index.ts"
    "frontend/src/store/workflowSlice.ts"
    "frontend/src/store/authSlice.ts"
    "frontend/src/store/uiSlice.ts"
    
    # Types
    "frontend/src/types/workflow.ts"
    "frontend/src/types/agent.ts"
    "frontend/src/types/api.ts"
    "frontend/src/types/user.ts"
    
    # Main files
    "frontend/src/App.tsx"
    "frontend/src/index.tsx"
    "frontend/src/index.css"
)

# Backend API files
backend_api_files=(
    "backend/api/main.py"
    "backend/api/requirements.txt"
    "backend/api/Dockerfile"
    "backend/api/.env.example"
    
    # Routes
    "backend/api/routes/__init__.py"
    "backend/api/routes/workflows.py"
    "backend/api/routes/agents.py"
    "backend/api/routes/auth.py"
    "backend/api/routes/executions.py"
    "backend/api/routes/templates.py"
    "backend/api/routes/integrations.py"
    
    # Models
    "backend/api/models/__init__.py"
    "backend/api/models/workflow.py"
    "backend/api/models/user.py"
    "backend/api/models/execution.py"
    "backend/api/models/template.py"
    
    # Schemas
    "backend/api/schemas/__init__.py"
    "backend/api/schemas/workflow.py"
    "backend/api/schemas/agent.py"
    "backend/api/schemas/execution.py"
    "backend/api/schemas/user.py"
    
    # Services
    "backend/api/services/__init__.py"
    "backend/api/services/workflow_service.py"
    "backend/api/services/agent_service.py"
    "backend/api/services/execution_service.py"
    "backend/api/services/auth_service.py"
    
    # Middleware
    "backend/api/middleware/__init__.py"
    "backend/api/middleware/auth.py"
    "backend/api/middleware/cors.py"
    "backend/api/middleware/logging.py"
    "backend/api/middleware/rate_limit.py"
    
    # Config
    "backend/api/config/__init__.py"
    "backend/api/config/database.py"
    "backend/api/config/settings.py"
    "backend/api/config/logging.py"
    
    # Utils
    "backend/api/utils/__init__.py"
    "backend/api/utils/validators.py"
    "backend/api/utils/helpers.py"
    "backend/api/utils/exceptions.py"
)

# Agent Engine files
agent_engine_files=(
    "backend/agent-engine/__init__.py"
    "backend/agent-engine/requirements.txt"
    "backend/agent-engine/Dockerfile"
    
    # Core
    "backend/agent-engine/core/__init__.py"
    "backend/agent-engine/core/agent_factory.py"
    "backend/agent-engine/core/orchestrator.py"
    "backend/agent-engine/core/executor.py"
    "backend/agent-engine/core/registry.py"
    
    # Frameworks
    "backend/agent-engine/frameworks/__init__.py"
    "backend/agent-engine/frameworks/langchain/__init__.py"
    "backend/agent-engine/frameworks/langchain/agent.py"
    "backend/agent-engine/frameworks/langchain/tools.py"
    "backend/agent-engine/frameworks/langchain/memory.py"
    
    "backend/agent-engine/frameworks/crewai/__init__.py"
    "backend/agent-engine/frameworks/crewai/crew.py"
    "backend/agent-engine/frameworks/crewai/agent.py"
    "backend/agent-engine/frameworks/crewai/task.py"
    
    "backend/agent-engine/frameworks/autogen/__init__.py"
    "backend/agent-engine/frameworks/autogen/agent.py"
    "backend/agent-engine/frameworks/autogen/conversation.py"
    
    # Tools
    "backend/agent-engine/tools/__init__.py"
    "backend/agent-engine/tools/web_tools.py"
    "backend/agent-engine/tools/database_tools.py"
    "backend/agent-engine/tools/file_tools.py"
    "backend/agent-engine/tools/api_tools.py"
    
    # Memory
    "backend/agent-engine/memory/__init__.py"
    "backend/agent-engine/memory/vector_store.py"
    "backend/agent-engine/memory/conversation.py"
    "backend/agent-engine/memory/embeddings.py"
    
    # Executors
    "backend/agent-engine/executors/__init__.py"
    "backend/agent-engine/executors/local_executor.py"
    "backend/agent-engine/executors/docker_executor.py"
    "backend/agent-engine/executors/k8s_executor.py"
)

# Workflow Engine files
workflow_engine_files=(
    "backend/workflow-engine/__init__.py"
    "backend/workflow-engine/requirements.txt"
    "backend/workflow-engine/Dockerfile"
    
    # Parser
    "backend/workflow-engine/parser/__init__.py"
    "backend/workflow-engine/parser/workflow_parser.py"
    "backend/workflow-engine/parser/node_parser.py"
    "backend/workflow-engine/parser/validator.py"
    
    # Scheduler
    "backend/workflow-engine/scheduler/__init__.py"
    "backend/workflow-engine/scheduler/task_scheduler.py"
    "backend/workflow-engine/scheduler/dependency_resolver.py"
    "backend/workflow-engine/scheduler/queue_manager.py"
    
    # Runner
    "backend/workflow-engine/runner/__init__.py"
    "backend/workflow-engine/runner/workflow_runner.py"
    "backend/workflow-engine/runner/node_runner.py"
    "backend/workflow-engine/runner/execution_context.py"
    
    # Monitoring
    "backend/workflow-engine/monitoring/__init__.py"
    "backend/workflow-engine/monitoring/metrics.py"
    "backend/workflow-engine/monitoring/logging.py"
    "backend/workflow-engine/monitoring/health_check.py"
)

# Shared services files
shared_files=(
    "backend/shared/__init__.py"
    "backend/shared/requirements.txt"
    
    # Database
    "backend/shared/database/__init__.py"
    "backend/shared/database/connection.py"
    "backend/shared/database/models.py"
    "backend/shared/database/migrations.py"
    
    # Auth
    "backend/shared/auth/__init__.py"
    "backend/shared/auth/jwt_handler.py"
    "backend/shared/auth/permissions.py"
    "backend/shared/auth/oauth.py"
    
    # Logging
    "backend/shared/logging/__init__.py"
    "backend/shared/logging/logger.py"
    "backend/shared/logging/formatters.py"
    
    # Messaging
    "backend/shared/messaging/__init__.py"
    "backend/shared/messaging/rabbitmq.py"
    "backend/shared/messaging/redis.py"
    "backend/shared/messaging/websocket.py"
    
    # Storage
    "backend/shared/storage/__init__.py"
    "backend/shared/storage/s3.py"
    "backend/shared/storage/local.py"
    "backend/shared/storage/gcs.py"
)

# Integration files
integration_files=(
    "backend/integrations/__init__.py"
    "backend/integrations/requirements.txt"
    
    # LLM Providers
    "backend/integrations/llm-providers/__init__.py"
    "backend/integrations/llm-providers/openai_client.py"
    "backend/integrations/llm-providers/anthropic_client.py"
    "backend/integrations/llm-providers/google_client.py"
    "backend/integrations/llm-providers/local_client.py"
    
    # Databases
    "backend/integrations/databases/__init__.py"
    "backend/integrations/databases/postgresql.py"
    "backend/integrations/databases/mongodb.py"
    "backend/integrations/databases/redis.py"
    "backend/integrations/databases/vector_db.py"
    
    # Cloud Services
    "backend/integrations/cloud-services/__init__.py"
    "backend/integrations/cloud-services/aws.py"
    "backend/integrations/cloud-services/gcp.py"
    "backend/integrations/cloud-services/azure.py"
    
    # APIs
    "backend/integrations/apis/__init__.py"
    "backend/integrations/apis/slack.py"
    "backend/integrations/apis/github.py"
    "backend/integrations/apis/jira.py"
    "backend/integrations/apis/discord.py"
)

# Database files
database_files=(
    "database/README.md"
    "database/init.sql"
    
    # Migrations
    "database/migrations/001_initial_schema.sql"
    "database/migrations/002_add_templates.sql"
    "database/migrations/003_add_executions.sql"
    
    # Seeds
    "database/seeds/users.sql"
    "database/seeds/templates.sql"
    "database/seeds/agent_categories.sql"
    
    # Schemas
    "database/schemas/workflow_schema.sql"
    "database/schemas/user_schema.sql"
    "database/schemas/execution_schema.sql"
)

# Docker and deployment files
deploy_files=(
    "deploy/docker/Dockerfile.api"
    "deploy/docker/Dockerfile.agent-engine"
    "deploy/docker/Dockerfile.workflow-engine"
    "deploy/docker/Dockerfile.frontend"
    "deploy/docker/docker-compose.prod.yml"
    
    # Kubernetes
    "deploy/kubernetes/namespace.yaml"
    "deploy/kubernetes/api-deployment.yaml"
    "deploy/kubernetes/agent-engine-deployment.yaml"
    "deploy/kubernetes/frontend-deployment.yaml"
    "deploy/kubernetes/postgres-deployment.yaml"
    "deploy/kubernetes/redis-deployment.yaml"
    "deploy/kubernetes/ingress.yaml"
    "deploy/kubernetes/secrets.yaml"
    
    # Terraform
    "deploy/terraform/main.tf"
    "deploy/terraform/variables.tf"
    "deploy/terraform/outputs.tf"
    "deploy/terraform/modules/vpc/main.tf"
    "deploy/terraform/modules/eks/main.tf"
    "deploy/terraform/modules/rds/main.tf"
    
    # Helm
    "deploy/helm/Chart.yaml"
    "deploy/helm/values.yaml"
    "deploy/helm/templates/deployment.yaml"
    "deploy/helm/templates/service.yaml"
    "deploy/helm/templates/configmap.yaml"
)

# Documentation files
doc_files=(
    "docs/README.md"
    "docs/architecture/system-overview.md"
    "docs/architecture/database-design.md"
    "docs/architecture/api-design.md"
    "docs/architecture/security.md"
    
    "docs/api/authentication.md"
    "docs/api/workflows.md"
    "docs/api/agents.md"
    "docs/api/executions.md"
    "docs/api/websockets.md"
    
    "docs/user-guide/getting-started.md"
    "docs/user-guide/creating-workflows.md"
    "docs/user-guide/agent-configuration.md"
    "docs/user-guide/templates.md"
    "docs/user-guide/troubleshooting.md"
    
    "docs/development/setup.md"
    "docs/development/contributing.md"
    "docs/development/testing.md"
    "docs/development/debugging.md"
    
    "docs/deployment/docker.md"
    "docs/deployment/kubernetes.md"
    "docs/deployment/cloud-providers.md"
    "docs/deployment/monitoring.md"
)

# Test files
test_files=(
    "tests/README.md"
    "tests/pytest.ini"
    "tests/jest.config.js"
    
    # Frontend tests
    "tests/frontend/components/Canvas.test.tsx"
    "tests/frontend/components/AgentLibrary.test.tsx"
    "tests/frontend/hooks/useWorkflow.test.ts"
    "tests/frontend/services/api.test.ts"
    
    # Backend tests
    "tests/backend/test_workflows.py"
    "tests/backend/test_agents.py"
    "tests/backend/test_executions.py"
    "tests/backend/test_auth.py"
    
    # Integration tests
    "tests/integration/test_workflow_execution.py"
    "tests/integration/test_agent_communication.py"
    
    # E2E tests
    "tests/e2e/workflow-creation.spec.ts"
    "tests/e2e/agent-execution.spec.ts"
    
    # Fixtures
    "tests/fixtures/workflows.json"
    "tests/fixtures/agents.json"
    "tests/fixtures/users.json"
)

# Example files
example_files=(
    "examples/README.md"
    
    # Workflow examples
    "examples/workflows/data-processing-pipeline.json"
    "examples/workflows/customer-support-automation.json"
    "examples/workflows/devops-deployment.json"
    "examples/workflows/content-generation.json"
    
    # Agent examples
    "examples/agents/custom-code-agent.py"
    "examples/agents/langchain-rag-agent.py"
    "examples/agents/crewai-team-setup.py"
    
    # Integration examples
    "examples/integrations/slack-integration.py"
    "examples/integrations/github-automation.py"
    "examples/integrations/database-sync.py"
)

# Script files
script_files=(
    "scripts/setup-dev.sh"
    "scripts/build.sh"
    "scripts/deploy.sh"
    "scripts/backup-db.sh"
    "scripts/migrate-db.sh"
    "scripts/seed-data.sh"
    "scripts/run-tests.sh"
)

# Combine all file arrays
all_files=(
    "${root_files[@]}"
    "${frontend_files[@]}"
    "${backend_api_files[@]}"
    "${agent_engine_files[@]}"
    "${workflow_engine_files[@]}"
    "${shared_files[@]}"
    "${integration_files[@]}"
    "${database_files[@]}"
    "${deploy_files[@]}"
    "${doc_files[@]}"
    "${test_files[@]}"
    "${example_files[@]}"
    "${script_files[@]}"
)

# Create all files
echo "📄 Creating files..."
for file in "${all_files[@]}"; do
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$file")"
    
    # Create empty file
    touch "$file"
    echo "  ✓ Created: $file"
done

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

# Create .gitkeep files for empty directories
echo "📌 Adding .gitkeep files for empty directories..."
find . -type d -empty -exec touch {}/.gitkeep \;

# Create basic .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
build/
dist/
.next/

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# Temporary files
tmp/
temp/

# Cache
.cache/
EOF

# Create basic README.md
echo "📋 Creating README.md..."
cat > README.md << 'EOF'
# Agent Workflow Builder

A powerful visual workflow builder for AI agents supporting LangChain, CrewAI, and custom agent frameworks.

## Features

- 🎨 Visual drag-and-drop workflow builder
- 🤖 Multi-framework agent support (LangChain, CrewAI, AutoGen)
- 🔗 Extensive integration library
- ⚡ Real-time execution monitoring
- 🔒 Enterprise-grade security
- ☁️ Cloud-native deployment

## Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd agent-workflow-builder

# Setup development environment
./scripts/setup-dev.sh

# Start services
docker-compose up -d

# Access the application
open http://localhost:3000
```

## Architecture

- **Frontend**: React/Next.js with TypeScript
- **Backend**: FastAPI (Python) + Express.js (Node.js)
- **Agent Engine**: Multi-framework agent execution
- **Database**: PostgreSQL + Redis + Vector DB
- **Deployment**: Docker + Kubernetes

## Documentation

- [Getting Started](docs/user-guide/getting-started.md)
- [API Documentation](docs/api/)
- [Architecture Overview](docs/architecture/system-overview.md)
- [Development Guide](docs/development/setup.md)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
EOF

echo ""
echo "🎉 Repository setup complete!"
echo ""
echo "📁 Directory structure created with ${#directories[@]} directories"
echo "📄 ${#all_files[@]} empty files created"
echo ""
echo "Next steps:"
echo "1. Initialize git repository: git init"
echo "2. Add remote origin: git remote add origin <your-repo-url>"
echo "3. Setup development environment: ./scripts/setup-dev.sh"
echo "4. Start building your agent workflow platform! 🚀"
echo ""