#!/bin/bash

#############################################################################
# CrowdStrike IOA Runner - Interactive Bootstrap Script
# 
# This script provides an interactive menu to run IOA (Indicator of Attack)
# scripts for AWS, Azure, and GCP cloud providers.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/ryanjpayne/cspm-ioa-runner/refs/heads/main/ioa-runner.sh | bash
#   OR
#   bash ioa-runner.sh
#
# Compatible with: AWS CloudShell, Azure Cloud Shell, GCP Cloud Shell
#############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://raw.githubusercontent.com/ryanjpayne/cspm-ioa-runner/refs/heads/main"
INSTALL_DIR="$HOME/ioa-scripts"
GITHUB_RAW_BASE="https://raw.githubusercontent.com/ryanjpayne/cspm-ioa-runner/refs/heads/main"

#############################################################################
# Helper Functions
#############################################################################

print_header() {
    echo -e "${RED}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                  CrowdStrike IOA Runner                   ║"
    echo "║             Cloud Security Posture Management             ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

#############################################################################
# Environment Detection
#############################################################################

detect_environment() {
    print_info "Detecting cloud environment..."
    
    if [ -n "$AWS_EXECUTION_ENV" ] || [ -n "$AWS_CLOUDSHELL" ]; then
        echo "AWS CloudShell"
    elif [ -n "$AZURE_HTTP_USER_AGENT" ] || [ -d "/usr/cloudshell" ]; then
        echo "Azure Cloud Shell"
    # elif [ -n "$DEVSHELL_PROJECT_ID" ] || [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
    #     echo "GCP Cloud Shell"
    else
        echo "Local/Unknown"
    fi
}

#############################################################################
# Dependency Installation
#############################################################################

check_python() {
    if command -v python3 &> /dev/null; then
        print_success "Python 3 is installed"
        return 0
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

check_pip() {
    if command -v pip3 &> /dev/null; then
        print_success "pip3 is installed"
        return 0
    else
        print_warning "pip3 is not installed, attempting to install..."
        return 1
    fi
}

install_python_dependencies() {
    print_info "Installing Python dependencies..."
    
    if ! check_python; then
        print_error "Python 3 is required but not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Install pip if not available
    if ! check_pip; then
        python3 -m ensurepip --default-pip 2>/dev/null || true
    fi
    
    # Install requirements.txt (boto3 for AWS)
    pip3 install -r "$INSTALL_DIR/requirements.txt" 2>/dev/null
    
    print_success "Python dependencies installed"
}

check_cloud_cli() {
    local csp=$1
    
    case $csp in
        aws)
            if command -v aws &> /dev/null; then
                print_success "AWS CLI is installed"
                return 0
            else
                print_warning "AWS CLI is not installed"
                return 1
            fi
            ;;
        azure)
            if command -v az &> /dev/null; then
                print_success "Azure CLI is installed"
                return 0
            else
                print_warning "Azure CLI is not installed"
                return 1
            fi
            ;;
        # gcp)
        #     if command -v gcloud &> /dev/null; then
        #         print_success "GCP CLI is installed"
        #         return 0
        #     else
        #         print_warning "GCP CLI is not installed"
        #         return 1
        #     fi
        #     ;;
    esac
}

#############################################################################
# File Download Functions
#############################################################################

setup_directory() {
    print_info "Setting up directory structure..."
    
    mkdir -p "$INSTALL_DIR"/{aws,azure,gcp}
    cd "$INSTALL_DIR"
    
    print_success "Directory structure created at $INSTALL_DIR"
}

copy_runner_script() {
    print_info "Installing IOA Runner script..."
    
    # Get the absolute path of the currently running script
    local current_script=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
    local target_script="$INSTALL_DIR/ioa-runner.sh"
    
    # Skip if we're already running from the install directory
    if [ "$current_script" = "$target_script" ]; then
        print_success "IOA Runner already running from install directory"
        return 0
    fi
    
    # Copy the runner script itself to the install directory
    # Handle both direct execution and piped execution from curl
    if [ -f "$0" ] && [ "$0" != "bash" ] && [ "$0" != "-bash" ]; then
        cp "$0" "$INSTALL_DIR/ioa-runner.sh"
        chmod +x "$INSTALL_DIR/ioa-runner.sh"
        print_success "IOA Runner installed to $INSTALL_DIR/ioa-runner.sh"
    else
        # If piped from curl, download it directly
        download_file "$GITHUB_RAW_BASE/ioa-runner.sh" "$INSTALL_DIR/ioa-runner.sh"
        chmod +x "$INSTALL_DIR/ioa-runner.sh"
        print_success "IOA Runner downloaded to $INSTALL_DIR/ioa-runner.sh"
    fi
}

download_file() {
    local url=$1
    local dest=$2
    
    if command -v curl &> /dev/null; then
        curl -sSL "$url" -o "$dest" 2>/dev/null
    elif command -v wget &> /dev/null; then
        wget -q "$url" -O "$dest" 2>/dev/null
    else
        print_error "Neither curl nor wget is available"
        return 1
    fi
    
    return 0
}

download_aws_scripts() {
    print_info "Downloading AWS IOA scripts..."
    
    local aws_scripts=(
        "aws_ioa_204.py"
        "aws_ioa_206.py"
        "aws_ioa_207_209_210_213.py"
        "aws_ioa_211_212_214.py"
        "aws_ioa_215.py"
        "aws_ioa_216.py"
        "aws_ioa_217.py"
        "aws_ioa_221.py"
        "aws_ioa_223.py"
        "aws_ioa_225_251.py"
        "aws_ioa_228.py"
        "aws_ioa_229.py"
        "aws_ioa_234.py"
        "aws_ioa_235_258_259_264.py"
        "aws_ioa_236.py"
        "aws_ioa_238.py"
        "aws_ioa_246.py"
        "aws_ioa_249_253.py"
        "aws_ioa_250.py"
        "aws_ioa_254.py"
        "aws_ioa_255.py"
        "aws_ioa_256.sh"
        "aws_ioa_257.py"
        "utils.py"
    )
    
    for script in "${aws_scripts[@]}"; do
        download_file "$GITHUB_RAW_BASE/aws/$script" "$INSTALL_DIR/aws/$script"
        chmod +x "$INSTALL_DIR/aws/$script"
    done
    
    print_success "AWS scripts downloaded"
}

download_azure_scripts() {
    print_info "Downloading Azure IOA scripts..."
    
    local azure_scripts=(
        "azure_ioa_243.sh"
        "azure_ioa_303.sh"
        "azure_ioa_309.sh"
        "azure_ioa_317.sh"
        "azure_ioa_318.sh"
        "azure_ioa_321_322.sh"
        "azure_ioa_323.sh"
        "azure_ioa_391.sh"
        "azure_ioa_395.sh"
        "azure_ioa_518.sh"
        "utils.sh"
    )
    
    for script in "${azure_scripts[@]}"; do
        download_file "$GITHUB_RAW_BASE/azure/$script" "$INSTALL_DIR/azure/$script"
        chmod +x "$INSTALL_DIR/azure/$script"
    done
    
    print_success "Azure scripts downloaded"
}

# PLACEHOLDER FOR WHEN GCP IOAS ARE RELEASED
# download_gcp_scripts() {
#     print_info "Downloading GCP IOA scripts..."
#     # Currently no GCP scripts, but structure is ready
#     print_warning "No GCP scripts available yet"
# }

download_config_files() {
    print_info "Downloading configuration files..."
    
    download_file "$GITHUB_RAW_BASE/config.ini" "$INSTALL_DIR/config.ini"
    download_file "$GITHUB_RAW_BASE/requirements.txt" "$INSTALL_DIR/requirements.txt"
    
    print_success "Configuration files downloaded"
}

#############################################################################
# Menu Functions
#############################################################################

show_main_menu() {
    clear
    print_header
    
    local env=$(detect_environment)
    echo -e "${CYAN}Environment: ${NC}$env"
    echo -e "${CYAN}Install Directory: ${NC}$INSTALL_DIR"
    echo ""
    echo -e "${YELLOW}Select Cloud Service Provider:${NC}"
    echo ""
    echo "  1) AWS (Amazon Web Services)"
    echo "  2) Azure (Microsoft Azure)"
    # echo "  3) GCP (Google Cloud Platform)"
    echo ""
    echo "  0) Exit"
    echo ""
    echo -n "Enter your choice [0-2]: "
}

show_aws_menu() {
    clear
    print_header
    echo -e "${YELLOW}AWS IOA Scripts:${NC}"
    echo ""
    echo "  1)  204 - Cross-User IAM LoginProfile modification"
    echo "  2)  206 - IAM User Access Key created"
    echo "  3)  207/209/210/213 - IAM Policy modifications"
    echo "  4)  211/212/214 - IAM Role modifications"
    echo "  5)  215 - IAM User created"
    echo "  6)  216 - IAM Group modifications"
    echo "  7)  217 - S3 Bucket Policy modified"
    echo "  8)  221 - EC2 Security Group modified"
    echo "  9)  223 - EC2 Instance launched"
    echo "  10) 225/251 - Lambda Function modifications"
    echo "  11) 228 - RDS Instance modifications"
    echo "  12) 229 - CloudTrail logging disabled"
    echo "  13) 234 - KMS Key Policy modified"
    echo "  14) 235/258/259/264 - S3 Bucket modifications"
    echo "  15) 236 - VPC modifications"
    echo "  16) 238 - Route53 modifications"
    echo "  17) 246 - ECS Task Definition registered"
    echo "  18) 249/253 - SNS/SQS modifications"
    echo "  19) 250 - DynamoDB Table modifications"
    echo "  20) 254 - Secrets Manager modifications"
    echo "  21) 255 - Systems Manager modifications"
    echo "  22) 256 - CloudFormation Stack operations"
    echo "  23) 257 - EKS Cluster modifications"
    echo ""
    echo "  0) Back to main menu"
    echo ""
    echo -n "Enter your choice: "
}

show_azure_menu() {
    clear
    print_header
    echo -e "${YELLOW}Azure IOA Scripts:${NC}"
    echo ""
    echo "  1)  243 - Event Hub namespace deleted"
    echo "  2)  303 - User MFA disabled"
    echo "  3)  309 - Storage Account Networking changed to All Networks"
    echo "  4)  317 - Secret added to an application registration"
    echo "  5)  318 - Certificate added to an application registration"
    echo "  6)  321/322 - Virtual Machine Network Security Group modifications"
    echo "  7)  323 - Virtual Machine manually deleted"
    echo "  8)  391 - Event Hub deleted"
    echo "  9)  395 - Conditional Access policy deleted"
    echo "  10) 518 - Virtual Machine disk exported by user"
    echo ""
    echo "  0) Back to main menu"
    echo ""
    echo -n "Enter your choice: "
}

# show_gcp_menu() {
#     clear
#     print_header
#     echo -e "${YELLOW}GCP IOA Scripts:${NC}"
#     echo ""
#     print_warning "No GCP IOA scripts available yet"
#     echo ""
#     echo "  0) Back to main menu"
#     echo ""
#     echo -n "Enter your choice: "
# }

#############################################################################
# Script Execution Functions
#############################################################################

get_script_summary() {
    local script_path=$1
    local summary=""
    
    # Extract the docstring or comments from the script
    if [[ $script_path == *.py ]]; then
        summary=$(python3 -c "
import sys
with open('$script_path', 'r') as f:
    content = f.read()
    # Extract docstring
    if '\"\"\"' in content:
        start = content.find('\"\"\"') + 3
        end = content.find('\"\"\"', start)
        if end > start:
            print(content[start:end].strip())
" 2>/dev/null)
    else
        # For shell scripts, extract the comment block
        summary=$(sed -n "/^: '/,/^'/p" "$script_path" | sed "1d;\$d" 2>/dev/null)
    fi
    
    echo "$summary"
}

show_script_summary() {
    local script_file=$1
    local script_path="$INSTALL_DIR/aws/$script_file"
    
    if [ ! -f "$script_path" ]; then
        script_path="$INSTALL_DIR/azure/$script_file"
    fi
    
    clear
    print_header
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Script Summary${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Script:${NC} $script_file"
    echo ""
    
    local summary=$(get_script_summary "$script_path")
    if [ -n "$summary" ]; then
        echo -e "${YELLOW}Description:${NC}"
        echo ""
        echo "$summary"
    else
        echo -e "${YELLOW}Description:${NC} No description available"
    fi
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${RED}⚠ WARNING:${NC} This script will create and delete resources in your account."
    echo -e "${RED}           Ensure you have appropriate permissions and understand the impact.${NC}"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

run_aws_script() {
    local script_num=$1
    local script_file=""
    local profile=""
    
    case $script_num in
        1) script_file="aws_ioa_204.py" ;;
        2) script_file="aws_ioa_206.py" ;;
        3) script_file="aws_ioa_207_209_210_213.py" ;;
        4) script_file="aws_ioa_211_212_214.py" ;;
        5) script_file="aws_ioa_215.py" ;;
        6) script_file="aws_ioa_216.py" ;;
        7) script_file="aws_ioa_217.py" ;;
        8) script_file="aws_ioa_221.py" ;;
        9) script_file="aws_ioa_223.py" ;;
        10) script_file="aws_ioa_225_251.py" ;;
        11) script_file="aws_ioa_228.py" ;;
        12) script_file="aws_ioa_229.py" ;;
        13) script_file="aws_ioa_234.py" ;;
        14) script_file="aws_ioa_235_258_259_264.py" ;;
        15) script_file="aws_ioa_236.py" ;;
        16) script_file="aws_ioa_238.py" ;;
        17) script_file="aws_ioa_246.py" ;;
        18) script_file="aws_ioa_249_253.py" ;;
        19) script_file="aws_ioa_250.py" ;;
        20) script_file="aws_ioa_254.py" ;;
        21) script_file="aws_ioa_255.py" ;;
        22) script_file="aws_ioa_256.sh" ;;
        23) script_file="aws_ioa_257.py" ;;
        *) 
            print_error "Invalid script selection"
            return 1
            ;;
    esac
    
    # Show summary and get confirmation
    show_script_summary "$script_file"
    
    echo -n "Do you want to continue? (y/N): "
    read confirm </dev/tty
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Script execution cancelled"
        echo ""
        echo -n "Press Enter to return to menu..."
        read </dev/tty
        return 0
    fi
    
    echo ""
    echo -n "Enter AWS profile name (or press Enter for 'default'): "
    read profile </dev/tty
    profile=${profile:-default}
    
    echo ""
    print_info "Running $script_file with profile: $profile"
    echo ""
    
    cd "$INSTALL_DIR/aws"
    
    if [[ $script_file == *.py ]]; then
        python3 "$script_file" "$profile"
    else
        bash "$script_file" "$profile"
    fi
    
    local exit_code=$?
    echo ""
    
    if [ $exit_code -eq 0 ]; then
        print_success "Script completed successfully"
    else
        print_error "Script failed with exit code: $exit_code"
    fi
    
    echo ""
    echo -n "Press Enter to continue..."
    read </dev/tty
}

run_azure_script() {
    local script_num=$1
    local script_file=""
    
    case $script_num in
        1) script_file="azure_ioa_243.sh" ;;
        2) script_file="azure_ioa_303.sh" ;;
        3) script_file="azure_ioa_309.sh" ;;
        4) script_file="azure_ioa_317.sh" ;;
        5) script_file="azure_ioa_318.sh" ;;
        6) script_file="azure_ioa_321_322.sh" ;;
        7) script_file="azure_ioa_323.sh" ;;
        8) script_file="azure_ioa_391.sh" ;;
        9) script_file="azure_ioa_395.sh" ;;
        10) script_file="azure_ioa_518.sh" ;;
        *) 
            print_error "Invalid script selection"
            return 1
            ;;
    esac
    
    # Show summary and get confirmation
    show_script_summary "$script_file"
    
    echo -n "Do you want to continue? (y/N): "
    read confirm </dev/tty
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Script execution cancelled"
        echo ""
        echo -n "Press Enter to return to menu..."
        read </dev/tty
        return 0
    fi
    
    echo ""
    print_info "Running $script_file"
    echo ""
    
    cd "$INSTALL_DIR/azure"
    bash "$script_file"
    
    local exit_code=$?
    echo ""
    
    if [ $exit_code -eq 0 ]; then
        print_success "Script completed successfully"
    else
        print_error "Script failed with exit code: $exit_code"
    fi
    
    echo ""
    echo -n "Press Enter to continue..."
    read </dev/tty
}

#############################################################################
# Main Program Flow
#############################################################################

initialize() {
    print_header
    
    local env=$(detect_environment)
    print_info "Detected environment: $env"
    
    # Check if already initialized
    if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/.initialized" ]; then
        print_success "IOA scripts already initialized"
        echo ""
        echo -n "Re-download scripts? (y/N): "
        read response </dev/tty
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            return 0
        fi
    fi
    
    echo ""
    print_info "Initializing IOA Runner..."
    
    # Setup directory structure
    setup_directory
    
    # Copy/download the runner script itself
    copy_runner_script
    
    # Download scripts based on environment or all
    echo ""
    echo -n "Download scripts for all cloud providers? (Y/n): "
    read download_all </dev/tty
    
    if [[ "$download_all" =~ ^[Nn]$ ]]; then
        echo ""
        echo "Select cloud provider to download scripts for:"
        echo "  1) AWS"
        echo "  2) Azure"
        #echo "  3) GCP"
        echo -n "Enter choice: "
        read csp_choice </dev/tty
        
        case $csp_choice in
            1) download_aws_scripts ;;
            2) download_azure_scripts ;;
            #3) download_gcp_scripts ;;
            *) print_error "Invalid choice" ;;
        esac
    else
        download_aws_scripts
        download_azure_scripts
        #download_gcp_scripts
    fi
    
    # Download config files
    download_config_files
    
    # Install Python dependencies
    echo ""
    install_python_dependencies
    
    # Mark as initialized
    touch "$INSTALL_DIR/.initialized"
    
    echo ""
    print_success "Initialization complete!"
    echo ""
    echo -n "Press Enter to continue to main menu..."
    read </dev/tty
}

main_loop() {
    while true; do
        show_main_menu
        read choice </dev/tty
        
        case $choice in
            1)
                # AWS Menu
                if ! check_cloud_cli "aws"; then
                    echo ""
                    print_warning "AWS CLI not detected. Some scripts may not work properly."
                    echo -n "Continue anyway? (y/N): "
                    read continue </dev/tty
                    if [[ ! "$continue" =~ ^[Yy]$ ]]; then
                        continue
                    fi
                fi
                
                while true; do
                    show_aws_menu
                    read aws_choice </dev/tty
                    
                    if [ "$aws_choice" = "0" ]; then
                        break
                    elif [ "$aws_choice" -ge 1 ] && [ "$aws_choice" -le 23 ]; then
                        run_aws_script "$aws_choice"
                    else
                        print_error "Invalid choice"
                        sleep 2
                    fi
                done
                ;;
            2)
                # Azure Menu
                if ! check_cloud_cli "azure"; then
                    echo ""
                    print_warning "Azure CLI not detected. Scripts will not work."
                    echo -n "Press Enter to continue..."
                    read </dev/tty
                    continue
                fi
                
                while true; do
                    show_azure_menu
                    read azure_choice </dev/tty
                    
                    if [ "$azure_choice" = "0" ]; then
                        break
                    elif [ "$azure_choice" -ge 1 ] && [ "$azure_choice" -le 10 ]; then
                        run_azure_script "$azure_choice"
                    else
                        print_error "Invalid choice"
                        sleep 2
                    fi
                done
                ;;
            # 3)
            #     # GCP Menu
            #     show_gcp_menu
            #     read gcp_choice </dev/tty
            #     ;;
            0)
                echo ""
                print_info "Exiting IOA Runner. Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                sleep 2
                ;;
        esac
    done
}

#############################################################################
# Entry Point
#############################################################################

main() {
    # Initialize on first run
    initialize
    
    # Start main menu loop
    main_loop
}

# Run main function
main
