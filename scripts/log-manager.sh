#!/bin/bash

# FastAPI Enterprise MVP - Log Management Tool
# This script provides utilities for managing application logs

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}📋 $1${NC}"
}

print_step() {
    echo -e "${BLUE}▶️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

LOG_DIR="logs"

# Function to check if logs directory exists
check_logs_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        print_warning "Logs directory not found. Creating..."
        mkdir -p "$LOG_DIR"
    fi
}

# Function to show log files
show_log_files() {
    print_header "Available Log Files"
    echo ""
    
    if [ ! -d "$LOG_DIR" ] || [ -z "$(ls -A $LOG_DIR 2>/dev/null)" ]; then
        print_warning "No log files found in $LOG_DIR"
        return
    fi
    
    echo "📁 Log Directory: $LOG_DIR"
    echo ""
    
    for file in "$LOG_DIR"/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(du -h "$file" | cut -f1)
            modified=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1 || date -r "$file" "+%Y-%m-%d %H:%M:%S")
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            
            echo "📄 $filename"
            echo "   Size: $size | Lines: $lines | Modified: $modified"
            echo ""
        fi
    done
}

# Function to tail logs
tail_logs() {
    local log_type=$1
    local lines=${2:-50}
    
    check_logs_dir
    
    case $log_type in
        "all")
            print_step "Tailing all log files (last $lines lines each)..."
            if [ -f "$LOG_DIR/app.log" ]; then
                echo ""
                print_header "Application Log (app.log)"
                tail -n "$lines" "$LOG_DIR/app.log"
            fi
            if [ -f "$LOG_DIR/error.log" ]; then
                echo ""
                print_header "Error Log (error.log)"
                tail -n "$lines" "$LOG_DIR/error.log"
            fi
            if [ -f "$LOG_DIR/app.json" ]; then
                echo ""
                print_header "JSON Log (app.json)"
                tail -n "$lines" "$LOG_DIR/app.json" | jq . 2>/dev/null || tail -n "$lines" "$LOG_DIR/app.json"
            fi
            ;;
        "app")
            if [ -f "$LOG_DIR/app.log" ]; then
                print_step "Tailing application log..."
                tail -n "$lines" "$LOG_DIR/app.log"
            else
                print_error "Application log file not found"
            fi
            ;;
        "error")
            if [ -f "$LOG_DIR/error.log" ]; then
                print_step "Tailing error log..."
                tail -n "$lines" "$LOG_DIR/error.log"
            else
                print_error "Error log file not found"
            fi
            ;;
        "json")
            if [ -f "$LOG_DIR/app.json" ]; then
                print_step "Tailing JSON log..."
                tail -n "$lines" "$LOG_DIR/app.json" | jq . 2>/dev/null || tail -n "$lines" "$LOG_DIR/app.json"
            else
                print_error "JSON log file not found"
            fi
            ;;
        "performance")
            if [ -f "$LOG_DIR/performance.log" ]; then
                print_step "Tailing performance log..."
                tail -n "$lines" "$LOG_DIR/performance.log" | jq . 2>/dev/null || tail -n "$lines" "$LOG_DIR/performance.log"
            else
                print_error "Performance log file not found"
            fi
            ;;
        *)
            print_error "Unknown log type: $log_type"
            echo "Available types: all, app, error, json, performance"
            ;;
    esac
}

# Function to follow logs in real-time
follow_logs() {
    local log_type=$1
    
    check_logs_dir
    
    case $log_type in
        "all")
            print_step "Following all log files in real-time..."
            if command -v multitail >/dev/null 2>&1; then
                multitail "$LOG_DIR"/*.log 2>/dev/null || tail -f "$LOG_DIR"/*.log 2>/dev/null
            else
                tail -f "$LOG_DIR"/*.log 2>/dev/null
            fi
            ;;
        "app")
            if [ -f "$LOG_DIR/app.log" ]; then
                print_step "Following application log..."
                tail -f "$LOG_DIR/app.log"
            else
                print_error "Application log file not found"
            fi
            ;;
        "error")
            if [ -f "$LOG_DIR/error.log" ]; then
                print_step "Following error log..."
                tail -f "$LOG_DIR/error.log"
            else
                print_error "Error log file not found"
            fi
            ;;
        "json")
            if [ -f "$LOG_DIR/app.json" ]; then
                print_step "Following JSON log..."
                tail -f "$LOG_DIR/app.json"
            else
                print_error "JSON log file not found"
            fi
            ;;
        *)
            print_error "Unknown log type: $log_type"
            echo "Available types: all, app, error, json"
            ;;
    esac
}

# Function to search logs
search_logs() {
    local pattern=$1
    local log_type=${2:-"all"}
    local context=${3:-3}
    
    check_logs_dir
    
    if [ -z "$pattern" ]; then
        print_error "Search pattern is required"
        return 1
    fi
    
    print_step "Searching for pattern: '$pattern' in $log_type logs"
    echo ""
    
    case $log_type in
        "all")
            for file in "$LOG_DIR"/*.log "$LOG_DIR"/*.json; do
                if [ -f "$file" ]; then
                    filename=$(basename "$file")
                    matches=$(grep -c "$pattern" "$file" 2>/dev/null || echo "0")
                    if [ "$matches" -gt 0 ]; then
                        print_success "Found $matches matches in $filename:"
                        grep -n -C "$context" "$pattern" "$file" 2>/dev/null | head -20
                        echo ""
                    fi
                fi
            done
            ;;
        *)
            file="$LOG_DIR/$log_type.log"
            if [ ! -f "$file" ]; then
                file="$LOG_DIR/$log_type.json"
            fi
            
            if [ -f "$file" ]; then
                matches=$(grep -c "$pattern" "$file" 2>/dev/null || echo "0")
                if [ "$matches" -gt 0 ]; then
                    print_success "Found $matches matches:"
                    grep -n -C "$context" "$pattern" "$file" 2>/dev/null
                else
                    print_warning "No matches found"
                fi
            else
                print_error "Log file not found: $file"
            fi
            ;;
    esac
}

# Function to analyze logs
analyze_logs() {
    print_header "Log Analysis Report"
    echo ""
    
    check_logs_dir
    
    # Basic statistics
    print_step "Log File Statistics:"
    echo ""
    
    total_size=0
    total_lines=0
    
    for file in "$LOG_DIR"/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size_bytes=$(stat -c%s "$file" 2>/dev/null || echo "0")
            size_human=$(du -h "$file" | cut -f1)
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            
            total_size=$((total_size + size_bytes))
            total_lines=$((total_lines + lines))
            
            echo "📄 $filename: $size_human ($lines lines)"
        fi
    done
    
    total_size_human=$(echo "$total_size" | awk '{
        if ($1 > 1024*1024*1024) printf "%.1fGB", $1/1024/1024/1024
        else if ($1 > 1024*1024) printf "%.1fMB", $1/1024/1024
        else if ($1 > 1024) printf "%.1fKB", $1/1024
        else printf "%dB", $1
    }')
    
    echo ""
    echo "📊 Total: $total_size_human ($total_lines lines)"
    echo ""
    
    # Error analysis
    if [ -f "$LOG_DIR/error.log" ]; then
        print_step "Recent Errors (last 10):"
        echo ""
        tail -10 "$LOG_DIR/error.log" 2>/dev/null | while read -r line; do
            echo "🔴 $line"
        done
        echo ""
    fi
    
    # Performance analysis
    if [ -f "$LOG_DIR/app.log" ]; then
        print_step "Performance Insights:"
        echo ""
        
        # Count log levels
        info_count=$(grep -c "INFO" "$LOG_DIR/app.log" 2>/dev/null || echo "0")
        warning_count=$(grep -c "WARNING" "$LOG_DIR/app.log" 2>/dev/null || echo "0")
        error_count=$(grep -c "ERROR" "$LOG_DIR/app.log" 2>/dev/null || echo "0")
        
        echo "📈 Log Levels:"
        echo "   INFO: $info_count"
        echo "   WARNING: $warning_count"
        echo "   ERROR: $error_count"
        echo ""
        
        # Recent slow operations
        slow_ops=$(grep -i "slow\|timeout\|duration.*[0-9][0-9][0-9][0-9]" "$LOG_DIR/app.log" 2>/dev/null | tail -5)
        if [ ! -z "$slow_ops" ]; then
            print_step "Recent Slow Operations:"
            echo "$slow_ops"
            echo ""
        fi
    fi
}

# Function to clean old logs
clean_logs() {
    local days=${1:-7}
    
    print_step "Cleaning logs older than $days days..."
    
    check_logs_dir
    
    # Find and remove old log files
    old_files=$(find "$LOG_DIR" -name "*.log.*" -o -name "*.json.*" -mtime +$days 2>/dev/null)
    
    if [ -z "$old_files" ]; then
        print_success "No old log files found"
        return
    fi
    
    echo "Files to be removed:"
    echo "$old_files"
    echo ""
    
    read -p "Are you sure you want to delete these files? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo "$old_files" | xargs rm -f
        print_success "Old log files removed"
    else
        print_warning "Operation cancelled"
    fi
}

# Function to archive logs
archive_logs() {
    local archive_name="logs_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    print_step "Creating log archive: $archive_name"
    
    check_logs_dir
    
    if [ -z "$(ls -A $LOG_DIR 2>/dev/null)" ]; then
        print_warning "No log files to archive"
        return
    fi
    
    tar -czf "$archive_name" "$LOG_DIR"
    
    if [ $? -eq 0 ]; then
        print_success "Archive created: $archive_name"
        
        # Optionally clean current logs
        read -p "Do you want to clean current log files? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            rm -f "$LOG_DIR"/*.log "$LOG_DIR"/*.json
            print_success "Current log files cleaned"
        fi
    else
        print_error "Failed to create archive"
    fi
}

# Main function
main() {
    local command=${1:-help}
    
    case $command in
        "list"|"ls")
            show_log_files
            ;;
        "tail")
            tail_logs "${2:-all}" "${3:-50}"
            ;;
        "follow"|"f")
            follow_logs "${2:-all}"
            ;;
        "search")
            search_logs "$2" "$3" "$4"
            ;;
        "analyze")
            analyze_logs
            ;;
        "clean")
            clean_logs "$2"
            ;;
        "archive")
            archive_logs
            ;;
        "help"|"--help"|"-h")
            echo "FastAPI Enterprise MVP - Log Management Tool"
            echo ""
            echo "Usage: $0 [COMMAND] [OPTIONS]"
            echo ""
            echo "Commands:"
            echo "  list, ls              List all log files with details"
            echo "  tail [TYPE] [LINES]   Show last N lines of logs (default: all, 50)"
            echo "  follow, f [TYPE]      Follow logs in real-time (default: all)"
            echo "  search PATTERN [TYPE] [CONTEXT] Search for pattern in logs"
            echo "  analyze               Analyze logs and show statistics"
            echo "  clean [DAYS]          Clean logs older than N days (default: 7)"
            echo "  archive               Archive current logs and optionally clean"
            echo "  help                  Show this help message"
            echo ""
            echo "Log Types:"
            echo "  all                   All log files (default)"
            echo "  app                   Application logs"
            echo "  error                 Error logs only"
            echo "  json                  JSON formatted logs"
            echo "  performance           Performance logs"
            echo ""
            echo "Examples:"
            echo "  $0 tail app 100       Show last 100 lines of app.log"
            echo "  $0 follow error       Follow error.log in real-time"
            echo "  $0 search \"ERROR\" app 5  Search for ERROR in app logs with 5 lines context"
            echo "  $0 clean 3            Clean logs older than 3 days"
            echo ""
            ;;
        *)
            print_error "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
