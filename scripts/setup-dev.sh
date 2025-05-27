#!/bin/bash

# Agent Workflow Builder - Development Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🚀 Agent Workflow Builder - Development Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# =============================================================================
# SYSTEM REQUIREMENTS CHECK
# =============================================================================

log_info "Checking system requirements..."

# Check Operating System
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

log_info "Detected OS: $MACHINE"

# Check required tools
REQUIRED_TOOLS=("git" "docker" "docker-compose" "node" "npm" "python3" "pip3")
MISSING_TOOLS=()

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command_exists "$tool"; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    log_error "Missing required tools: ${MISSING_TOOLS[*]}"
    log_info "Please install the missing tools and run this script again."
    log_info ""
    log_info "Installation guides:"
    log_info "- Docker: https://docs.docker.com/get-docker/"
    log_info "- Node.js: https://nodejs.org/"
    log_info "- Python: https://www.python.org/downloads/"
    exit 1
fi

log_success "All required tools are installed!"

# Check versions
log_info "Checking tool versions..."
echo "  - Docker: $(docker --version | grep -o '[0-9]*\.[0-9]*\.[0-9]*' | head -1)"
echo "  - Node.js: $(node --version)"
echo "  - npm: $(npm --version)"
echo "  - Python: $(python3 --version | grep -o '[0-9]*\.[0-9]*\.[0-9]*')"
echo "  - pip: $(pip3 --version | grep -o '[0-9]*\.[0-9]*\.[0-9]*' | head -1)"

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

log_info "Setting up environment configuration..."

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating .env file from template..."
    cp .env.example .env
    log_success ".env file created!"
    log_warning "Please edit .env file with your actual API keys and configuration"
else
    log_info ".env