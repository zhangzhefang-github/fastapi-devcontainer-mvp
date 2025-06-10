#!/bin/bash

# FastAPI Enterprise MVP - API Testing Script
# This script tests the main API endpoints to verify functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:8501"

# Function to print colored output
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Function to test HTTP endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local headers=$4
    local data=$5
    local description=$6

    print_test "$description"
    
    local curl_cmd="curl -s -w '%{http_code}' -X $method"
    
    if [ ! -z "$headers" ]; then
        curl_cmd="$curl_cmd -H '$headers'"
    fi
    
    if [ ! -z "$data" ]; then
        curl_cmd="$curl_cmd -d '$data'"
    fi
    
    curl_cmd="$curl_cmd $API_BASE_URL$endpoint"
    
    local response=$(eval $curl_cmd)
    local status_code="${response: -3}"
    local body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        print_success "$method $endpoint - Status: $status_code"
        return 0
    else
        print_fail "$method $endpoint - Expected: $expected_status, Got: $status_code"
        echo "Response: $body"
        return 1
    fi
}

# Function to extract token from login response
extract_token() {
    local response=$1
    echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4
}

# Main testing function
run_tests() {
    local failed_tests=0
    local total_tests=0
    
    echo "🚀 Starting API Tests for FastAPI Enterprise MVP"
    echo "================================================"
    
    # Test 1: Health Check
    total_tests=$((total_tests + 1))
    if test_endpoint "GET" "/health" "200" "" "" "Health check endpoint"; then
        :
    else
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 2: Root endpoint
    total_tests=$((total_tests + 1))
    if test_endpoint "GET" "/" "200" "" "" "Root endpoint"; then
        :
    else
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 3: API documentation
    total_tests=$((total_tests + 1))
    if test_endpoint "GET" "/docs" "200" "" "" "API documentation"; then
        :
    else
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 4: OpenAPI schema
    total_tests=$((total_tests + 1))
    if test_endpoint "GET" "/api/v1/openapi.json" "200" "" "" "OpenAPI schema"; then
        :
    else
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 5: Metrics endpoint
    total_tests=$((total_tests + 1))
    if test_endpoint "GET" "/metrics" "200" "" "" "Prometheus metrics"; then
        :
    else
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 6: Login with invalid credentials
    total_tests=$((total_tests + 1))
    if test_endpoint "POST" "/api/v1/auth/login" "401" "Content-Type: application/x-www-form-urlencoded" "username=invalid&password=invalid" "Login with invalid credentials"; then
        :
    else
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 7: Access protected endpoint without token
    total_tests=$((total_tests + 1))
    if test_endpoint "GET" "/api/v1/users/me" "401" "" "" "Access protected endpoint without token"; then
        :
    else
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 8: User registration
    total_tests=$((total_tests + 1))
    local register_data='{
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "full_name": "Test User",
        "terms_accepted": true
    }'
    
    print_test "User registration"
    local register_response=$(curl -s -w '%{http_code}' -X POST \
        -H "Content-Type: application/json" \
        -d "$register_data" \
        "$API_BASE_URL/api/v1/auth/register")
    
    local register_status="${register_response: -3}"
    if [ "$register_status" = "200" ] || [ "$register_status" = "400" ]; then
        print_success "POST /api/v1/auth/register - Status: $register_status"
    else
        print_fail "POST /api/v1/auth/register - Expected: 200 or 400, Got: $register_status"
        failed_tests=$((failed_tests + 1))
    fi
    
    # Test 9: Login with demo credentials
    total_tests=$((total_tests + 1))
    print_test "Login with demo credentials"
    local login_response=$(curl -s -w '%{http_code}' -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=alice&password=123456" \
        "$API_BASE_URL/api/v1/auth/login")
    
    local login_status="${login_response: -3}"
    local login_body="${login_response%???}"
    
    if [ "$login_status" = "200" ]; then
        print_success "POST /api/v1/auth/login - Status: $login_status"
        
        # Extract token for subsequent tests
        local token=$(echo "$login_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        
        if [ ! -z "$token" ]; then
            print_info "Token extracted successfully"
            
            # Test 10: Access protected endpoint with token
            total_tests=$((total_tests + 1))
            if test_endpoint "GET" "/api/v1/users/me" "200" "Authorization: Bearer $token" "" "Access user profile with token"; then
                :
            else
                failed_tests=$((failed_tests + 1))
            fi
            
            # Test 11: Access admin endpoint
            total_tests=$((total_tests + 1))
            if test_endpoint "GET" "/api/v1/admin/users" "200" "Authorization: Bearer $token" "" "Access admin users endpoint"; then
                :
            else
                failed_tests=$((failed_tests + 1))
            fi
            
            # Test 12: Logout
            total_tests=$((total_tests + 1))
            if test_endpoint "POST" "/api/v1/auth/logout" "200" "Authorization: Bearer $token" "" "User logout"; then
                :
            else
                failed_tests=$((failed_tests + 1))
            fi
        else
            print_fail "Could not extract token from login response"
            failed_tests=$((failed_tests + 3))
            total_tests=$((total_tests + 3))
        fi
    else
        print_fail "POST /api/v1/auth/login - Expected: 200, Got: $login_status"
        print_info "Response: $login_body"
        failed_tests=$((failed_tests + 4))
        total_tests=$((total_tests + 3))
    fi
    
    echo ""
    echo "================================================"
    echo "🧪 Test Results Summary"
    echo "================================================"
    echo "Total Tests: $total_tests"
    echo "Passed: $((total_tests - failed_tests))"
    echo "Failed: $failed_tests"
    
    if [ $failed_tests -eq 0 ]; then
        print_success "All tests passed! 🎉"
        return 0
    else
        print_fail "$failed_tests test(s) failed"
        return 1
    fi
}

# Function to test frontend
test_frontend() {
    print_test "Testing frontend accessibility"
    
    local frontend_response=$(curl -s -w '%{http_code}' "$FRONTEND_URL")
    local frontend_status="${frontend_response: -3}"
    
    if [ "$frontend_status" = "200" ]; then
        print_success "Frontend is accessible at $FRONTEND_URL"
    else
        print_fail "Frontend is not accessible - Status: $frontend_status"
    fi
}

# Function to check service health
check_services() {
    echo "🔍 Checking Service Health"
    echo "=========================="
    
    # Check backend
    print_test "Backend health check"
    if curl -f -s "$API_BASE_URL/health" > /dev/null; then
        print_success "Backend is healthy"
    else
        print_fail "Backend health check failed"
    fi
    
    # Check frontend
    print_test "Frontend health check"
    if curl -f -s "$FRONTEND_URL/_stcore/health" > /dev/null; then
        print_success "Frontend is healthy"
    else
        print_fail "Frontend health check failed"
    fi
    
    echo ""
}

# Function to show service URLs
show_urls() {
    echo "🌐 Service URLs"
    echo "==============="
    echo "Backend API:      $API_BASE_URL"
    echo "API Docs:         $API_BASE_URL/docs"
    echo "Frontend:         $FRONTEND_URL"
    echo "Health Check:     $API_BASE_URL/health"
    echo "Metrics:          $API_BASE_URL/metrics"
    echo ""
}

# Main script logic
main() {
    local command=${1:-test}
    
    case $command in
        test)
            show_urls
            check_services
            run_tests
            test_frontend
            ;;
        health)
            check_services
            ;;
        urls)
            show_urls
            ;;
        help|--help|-h)
            echo "FastAPI Enterprise MVP - API Testing Script"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  test      Run all API tests (default)"
            echo "  health    Check service health only"
            echo "  urls      Show service URLs"
            echo "  help      Show this help message"
            echo ""
            ;;
        *)
            echo "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
