#!/bin/bash

# 🌳 AI Tree Personality System - Quick Start Script
# This script sets up and tests the AI features

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🌳 AI Tree Personality System Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if backend is running
check_backend() {
    echo -e "${BLUE}Checking backend...${NC}"
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Backend not running${NC}"
        echo -e "${YELLOW}Start it with: cd backend && python -m uvicorn app.main:app --reload${NC}"
        return 1
    fi
}

# Install backend dependencies
install_backend_deps() {
    echo -e "\n${BLUE}Installing backend dependencies...${NC}"
    cd "$BACKEND_DIR"
    
    if pip install -q google-generativeai elevenlabs 2>/dev/null; then
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ Some dependencies failed to install${NC}"
    fi
    
    cd "$SCRIPT_DIR"
}

# Check environment variables
check_env() {
    echo -e "\n${BLUE}Checking environment variables...${NC}"
    
    if [ -f "$SCRIPT_DIR/.env" ]; then
        if grep -q "GEMINI_API_KEY" "$SCRIPT_DIR/.env" && grep -q "ELEVENLABS_API_KEY" "$SCRIPT_DIR/.env"; then
            echo -e "${GREEN}✓ .env file has required API keys${NC}"
            return 0
        fi
    fi
    
    echo -e "${YELLOW}⚠ Missing API keys in .env${NC}"
    echo -e "${YELLOW}Make sure .env has:${NC}"
    echo "  GEMINI_API_KEY=..."
    echo "  ELEVENLABS_API_KEY=..."
    return 1
}

# Run database migration
run_migration() {
    echo -e "\n${BLUE}Checking database...${NC}"
    
    # This is just a check - actual migration needs manual setup
    echo -e "${YELLOW}Note: Manual database migration may be required${NC}"
    echo -e "${YELLOW}See DATABASE_MIGRATION_AI.md for details${NC}"
}

# Run tests
run_tests() {
    echo -e "\n${BLUE}Running AI feature tests...${NC}"
    
    if [ ! -f "$SCRIPT_DIR/test_ai_features.py" ]; then
        echo -e "${RED}✗ test_ai_features.py not found${NC}"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    python test_ai_features.py
}

# Main menu
show_menu() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}What would you like to do?${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo "1) Install dependencies"
    echo "2) Check environment"
    echo "3) Check backend connection"
    echo "4) Run full test suite"
    echo "5) View documentation"
    echo "6) Show all commands"
    echo "0) Exit"
    echo ""
    read -p "Enter choice [0-6]: " choice
}

show_commands() {
    echo -e "\n${BLUE}Quick Commands:${NC}"
    echo ""
    echo "Start backend:"
    echo "  cd backend && python -m uvicorn app.main:app --reload"
    echo ""
    echo "Start frontend:"
    echo "  cd frontend && npm run dev"
    echo ""
    echo "Run tests:"
    echo "  python test_ai_features.py"
    echo ""
    echo "Database migration:"
    echo "  psql -U postgres -d petri < DATABASE_MIGRATION_AI.md"
    echo ""
    echo "View documentation:"
    echo "  cat AI_PERSONALITY_SYSTEM.md"
    echo "  cat DATABASE_MIGRATION_AI.md"
    echo "  cat AI_IMPLEMENTATION_COMPLETE.md"
}

# Process menu choice
process_choice() {
    case $1 in
        1)
            install_backend_deps
            ;;
        2)
            check_env
            ;;
        3)
            if check_backend; then
                echo -e "${GREEN}Backend is ready!${NC}"
            else
                echo -e "${RED}Backend connection failed${NC}"
                echo "Start backend with: cd backend && python -m uvicorn app.main:app --reload"
            fi
            ;;
        4)
            if check_backend; then
                run_tests
            else
                echo -e "${RED}Cannot run tests - backend not running${NC}"
            fi
            ;;
        5)
            if command -v less &> /dev/null; then
                less AI_PERSONALITY_SYSTEM.md
            else
                cat AI_PERSONALITY_SYSTEM.md
            fi
            ;;
        6)
            show_commands
            ;;
        0)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
}

# Main loop
main() {
    # Initial checks
    install_backend_deps
    
    # Interactive menu
    while true; do
        show_menu
        process_choice "$choice"
    done
}

# Run main if called directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main
fi
