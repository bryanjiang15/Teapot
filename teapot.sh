#!/bin/bash

# Teapot Platform - Unified Server Management Script
# Usage: ./teapot.sh [start|stop|restart|status] [all|backend|frontend|teapot-api|creator-api]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create logs directory if it doesn't exist
mkdir -p logs

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

get_pid_from_port() {
    lsof -ti:$1 2>/dev/null || echo ""
}

kill_process() {
    local pid=$1
    if ps -p $pid > /dev/null 2>&1; then
        kill $pid 2>/dev/null
        sleep 1
        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
        return 0
    fi
    return 1
}

kill_port() {
    local port=$1
    local pid=$(get_pid_from_port $port)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}Stopping process on port $port (PID: $pid)...${NC}"
        kill_process $pid
        echo -e "${GREEN}   ✓ Stopped process on port $port${NC}"
        return 0
    fi
    return 1
}

# ============================================================================
# Start Functions
# ============================================================================

start_teapot_api() {
    echo -e "${GREEN}🚀 Starting TeapotAPI (port 8000)...${NC}"
    
    if check_port 8000; then
        echo -e "${RED}   ❌ Port 8000 already in use${NC}"
        return 1
    fi
    
    cd TeapotAPI
    python run.py > ../logs/teapot-api.log 2>&1 &
    local pid=$!
    cd ..
    
    echo -e "${GREEN}   ✓ TeapotAPI started (PID: $pid)${NC}"
    sleep 2
    return 0
}

start_creator_api() {
    echo -e "${GREEN}🚀 Starting CreatorAPI (port 8001)...${NC}"
    
    if check_port 8001; then
        echo -e "${RED}   ❌ Port 8001 already in use${NC}"
        return 1
    fi
    
    cd CreatorAPI
    python -c "
import uvicorn
from tcg_api import app
uvicorn.run(app, host='0.0.0.0', port=8001)
" > ../logs/creator-api.log 2>&1 &
    local pid=$!
    cd ..
    
    echo -e "${GREEN}   ✓ CreatorAPI started (PID: $pid)${NC}"
    sleep 2
    return 0
}

start_frontend() {
    echo -e "${GREEN}🚀 Starting Frontend (port 5173)...${NC}"
    
    if check_port 5173; then
        echo -e "${RED}   ❌ Port 5173 already in use${NC}"
        return 1
    fi
    
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    local pid=$!
    cd ..
    
    echo -e "${GREEN}   ✓ Frontend started (PID: $pid)${NC}"
    sleep 2
    return 0
}

start_backend() {
    echo -e "${BLUE}🔍 Checking required ports...${NC}"
    local port_conflict=0
    
    if check_port 8000; then
        echo -e "${RED}❌ Port 8000 is already in use${NC}"
        port_conflict=1
    fi
    if check_port 8001; then
        echo -e "${RED}❌ Port 8001 is already in use${NC}"
        port_conflict=1
    fi
    
    if [ $port_conflict -eq 1 ]; then
        exit 1
    fi
    
    start_teapot_api
    start_creator_api
}

start_all() {
    echo -e "${BLUE}🔍 Checking required ports...${NC}"
    local port_conflict=0
    
    if check_port 8000; then
        echo -e "${RED}❌ Port 8000 is already in use${NC}"
        port_conflict=1
    fi
    if check_port 8001; then
        echo -e "${RED}❌ Port 8001 is already in use${NC}"
        port_conflict=1
    fi
    if check_port 5173; then
        echo -e "${RED}❌ Port 5173 is already in use${NC}"
        port_conflict=1
    fi
    
    if [ $port_conflict -eq 1 ]; then
        echo -e "${YELLOW}Run './teapot.sh stop all' to stop conflicting processes${NC}"
        exit 1
    fi
    
    start_teapot_api
    start_creator_api
    start_frontend
    
    echo ""
    echo -e "${GREEN}✨ All servers started successfully!${NC}"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${YELLOW}📍 Server URLs:${NC}"
    echo -e "   Frontend:    ${GREEN}http://localhost:5173${NC}"
    echo -e "   TeapotAPI:   ${GREEN}http://localhost:8000${NC} (docs: /docs)"
    echo -e "   CreatorAPI:  ${GREEN}http://localhost:8001${NC} (docs: /docs)"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}📝 Logs: 'logs/' directory${NC}"
    echo -e "${YELLOW}🛑 Stop: './teapot.sh stop all'${NC}"
    echo -e "${BLUE}💡 View logs: 'tail -f logs/*.log'${NC}"
}

# ============================================================================
# Stop Functions
# ============================================================================

stop_teapot_api() {
    echo -e "${YELLOW}Stopping TeapotAPI (port 8000)...${NC}"
    if kill_port 8000; then
        return 0
    else
        echo -e "${YELLOW}   TeapotAPI not running${NC}"
        return 1
    fi
}

stop_creator_api() {
    echo -e "${YELLOW}Stopping CreatorAPI (port 8001)...${NC}"
    if kill_port 8001; then
        return 0
    else
        echo -e "${YELLOW}   CreatorAPI not running${NC}"
        return 1
    fi
}

stop_frontend() {
    echo -e "${YELLOW}Stopping Frontend (port 5173)...${NC}"
    if kill_port 5173; then
        return 0
    else
        echo -e "${YELLOW}   Frontend not running${NC}"
        return 1
    fi
}

stop_backend() {
    stop_teapot_api
    stop_creator_api
}

stop_all() {
    stop_teapot_api
    stop_creator_api
    stop_frontend
    
    echo ""
    echo -e "${GREEN}✓ All servers stopped successfully!${NC}"
}

# ============================================================================
# Status Functions
# ============================================================================

check_service_status() {
    local name=$1
    local port=$2
    
    if check_port $port; then
        local pid=$(get_pid_from_port $port)
        echo -e "   ${GREEN}●${NC} $name - ${GREEN}Running${NC} (port $port, PID: $pid)"
        return 0
    else
        echo -e "   ${RED}○${NC} $name - ${RED}Stopped${NC} (port $port)"
        return 1
    fi
}

show_status() {
    local target=$1
    
    case $target in
        all)
            echo -e "${BLUE}Teapot Platform Status:${NC}"
            echo ""
            check_service_status "TeapotAPI " 8000
            check_service_status "CreatorAPI" 8001
            check_service_status "Frontend  " 5173
            ;;
        backend)
            echo -e "${BLUE}Backend Services Status:${NC}"
            echo ""
            check_service_status "TeapotAPI " 8000
            check_service_status "CreatorAPI" 8001
            ;;
        frontend)
            check_service_status "Frontend" 5173
            ;;
        teapot-api)
            check_service_status "TeapotAPI" 8000
            ;;
        creator-api)
            check_service_status "CreatorAPI" 8001
            ;;
        *)
            show_status all
            ;;
    esac
    echo ""
}

# ============================================================================
# Main Script Logic
# ============================================================================

show_usage() {
    echo "Teapot Platform - Server Management"
    echo ""
    echo "Usage: ./teapot.sh [command] [target]"
    echo ""
    echo "Commands:"
    echo "  start     Start server(s)"
    echo "  stop      Stop server(s)"
    echo "  restart   Restart server(s)"
    echo "  status    Show server status"
    echo ""
    echo "Targets:"
    echo "  all         All servers (TeapotAPI + CreatorAPI + Frontend)"
    echo "  backend     Backend servers (TeapotAPI + CreatorAPI)"
    echo "  frontend    Frontend only"
    echo "  teapot-api  TeapotAPI only"
    echo "  creator-api CreatorAPI only"
    echo ""
    echo "Examples:"
    echo "  ./teapot.sh start all         # Start everything"
    echo "  ./teapot.sh stop all          # Stop everything"
    echo "  ./teapot.sh restart backend   # Restart backend servers"
    echo "  ./teapot.sh status            # Show status of all services"
    echo "  ./teapot.sh start teapot-api  # Start only TeapotAPI"
    echo ""
}

# Parse command line arguments
COMMAND=${1:-}
TARGET=${2:-all}

if [ -z "$COMMAND" ]; then
    show_usage
    exit 0
fi

case $COMMAND in
    start)
        print_header "   Starting Teapot Platform Servers   "
        case $TARGET in
            all)
                start_all
                ;;
            backend)
                start_backend
                echo ""
                echo -e "${GREEN}✨ Backend servers started!${NC}"
                echo -e "${YELLOW}URLs: ${GREEN}http://localhost:8000${NC} | ${GREEN}http://localhost:8001${NC}"
                ;;
            frontend)
                start_frontend
                echo ""
                echo -e "${GREEN}✨ Frontend started!${NC}"
                echo -e "${YELLOW}URL: ${GREEN}http://localhost:5173${NC}"
                ;;
            teapot-api)
                start_teapot_api
                echo ""
                echo -e "${GREEN}✨ TeapotAPI started!${NC}"
                echo -e "${YELLOW}URL: ${GREEN}http://localhost:8000${NC}"
                ;;
            creator-api)
                start_creator_api
                echo ""
                echo -e "${GREEN}✨ CreatorAPI started!${NC}"
                echo -e "${YELLOW}URL: ${GREEN}http://localhost:8001${NC}"
                ;;
            *)
                echo -e "${RED}Unknown target: $TARGET${NC}"
                show_usage
                exit 1
                ;;
        esac
        ;;
    
    stop)
        print_header "   Stopping Teapot Platform Servers   "
        case $TARGET in
            all)
                stop_all
                ;;
            backend)
                stop_backend
                echo ""
                echo -e "${GREEN}✓ Backend servers stopped!${NC}"
                ;;
            frontend)
                stop_frontend
                echo ""
                echo -e "${GREEN}✓ Frontend stopped!${NC}"
                ;;
            teapot-api)
                stop_teapot_api
                echo ""
                echo -e "${GREEN}✓ TeapotAPI stopped!${NC}"
                ;;
            creator-api)
                stop_creator_api
                echo ""
                echo -e "${GREEN}✓ CreatorAPI stopped!${NC}"
                ;;
            *)
                echo -e "${RED}Unknown target: $TARGET${NC}"
                show_usage
                exit 1
                ;;
        esac
        ;;
    
    restart)
        print_header "   Restarting Teapot Platform Servers "
        echo -e "${YELLOW}Stopping services...${NC}"
        case $TARGET in
            all)
                stop_all
                echo ""
                echo -e "${YELLOW}Starting services...${NC}"
                start_all
                ;;
            backend)
                stop_backend
                echo ""
                echo -e "${YELLOW}Starting services...${NC}"
                start_backend
                echo ""
                echo -e "${GREEN}✨ Backend servers restarted!${NC}"
                ;;
            frontend)
                stop_frontend
                echo ""
                echo -e "${YELLOW}Starting service...${NC}"
                start_frontend
                echo ""
                echo -e "${GREEN}✨ Frontend restarted!${NC}"
                ;;
            teapot-api)
                stop_teapot_api
                echo ""
                echo -e "${YELLOW}Starting service...${NC}"
                start_teapot_api
                echo ""
                echo -e "${GREEN}✨ TeapotAPI restarted!${NC}"
                ;;
            creator-api)
                stop_creator_api
                echo ""
                echo -e "${YELLOW}Starting service...${NC}"
                start_creator_api
                echo ""
                echo -e "${GREEN}✨ CreatorAPI restarted!${NC}"
                ;;
            *)
                echo -e "${RED}Unknown target: $TARGET${NC}"
                show_usage
                exit 1
                ;;
        esac
        ;;
    
    status)
        show_status $TARGET
        ;;
    
    help|--help|-h)
        show_usage
        ;;
    
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
