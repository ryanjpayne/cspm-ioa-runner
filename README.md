# CrowdStrike CSPM Real-time Visibility and Detection Demo

Python based demo developed by CrowdStrike for triggering Indicators of Attack (IOAs) based on policy definitions.

## 🚀 Quick Start

The IOA Runner is a single shell script that provides an interactive menu for running CrowdStrike IOA (Indicator of Attack) scripts across AWS, Azure, and GCP cloud providers.

### One-Line Installation

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_ORG/ioa-scripts/main/ioa-runner.sh | bash
```

**Note:** Replace `YOUR_ORG` with your GitHub organization/username before using.

### Manual Installation

1. Download the script:
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_ORG/ioa-scripts/main/ioa-runner.sh -o ioa-runner.sh
```

2. Make it executable:
```bash
chmod +x ioa-runner.sh
```

3. Run the script:
```bash
./ioa-runner.sh
```

## Supported Environments

The IOA Runner is designed to work in the following environments:

- ✅ **AWS CloudShell** - Fully supported
- ✅ **Azure Cloud Shell** - Fully supported  
- ✅ **GCP Cloud Shell** - Fully supported
- ✅ **Local Linux/macOS** - Fully supported
- ⚠️ **Windows** - Use WSL (Windows Subsystem for Linux) or Git Bash

## Prerequisites

### Required
- **Bash shell** (version 4.0 or higher)
- **Python 3** (version 3.6 or higher)
- **curl** or **wget** (for downloading scripts)

### Cloud Provider CLIs (or access to the respective CloudShell)
- **AWS CLI** - For running AWS IOA scripts
- **Azure CLI** - For running Azure IOA scripts
- **GCP CLI (gcloud)** - For running GCP IOA scripts

### Python Dependencies
The script will automatically install:
- `boto3` (for AWS operations)

## How It Works

1. **Initialization Phase**
   - Detects your cloud environment (AWS CloudShell, Azure Cloud Shell, GCP Cloud Shell, or local)
   - Creates directory structure at `$HOME/ioa-scripts`
   - Downloads IOA scripts from GitHub repository
   - Installs Python dependencies
   - Marks installation as complete

2. **Interactive Menu**
   - Select cloud service provider (AWS, Azure, or GCP)
   - Choose from available IOA scripts for that provider
   - Script executes with appropriate parameters
   - View results and return to menu

3. **Script Execution**
   - For AWS: Prompts for AWS profile name (defaults to 'default')
   - For Azure: Uses current Azure CLI authentication
   - For GCP: Uses current gcloud authentication
   - Runs the selected IOA script
   - Displays success/failure status

## Directory Structure

After installation, the following structure is created:

```
$HOME/ioa-scripts/
├── READMEs
├── config.ini           # Configuration file
├── requirements.txt     # Python dependencies
├── aws/                 # AWS IOA scripts
│   ├── aws_ioa_204.py
│   ├── aws_ioa_206.py
│   └── ...
├── azure/               # Azure IOA scripts
│   ├── azure_ioa_321_322.sh
│   └── azure_ioa_323.sh
│   └── ...
└── gcp/                 # GCP IOA scripts (coming soon)
```

## Usage Examples

### Running in AWS CloudShell

```bash
# One-line install and run
curl -sSL https://raw.githubusercontent.com/YOUR_ORG/ioa-scripts/main/ioa-runner.sh | bash

# The script will:
# 1. Detect CloudShell environment
# 2. Download all scripts
# 3. Install dependencies
# 4. Show interactive menu
# 5. Select CSP → Choose IOA script → Enter profile name (AWS)
```

See [Detailed Usage](/USAGE.md) for instructions on how to use the IOA Runner interactive menu system.

## Available IOA Scripts

### AWS (23 scripts)
- Policy 204 - Cross-User IAM LoginProfile modification
- Policy 206 - IAM User Access Key created
- Policy 207/209/210/213 - IAM Policy modifications
- Policy 211/212/214 - IAM Role modifications
- Policy 215 - IAM User created
- Policy 216 - IAM Group modifications
- Policy 217 - S3 Bucket Policy modified
- Policy 221 - EC2 Security Group modified
- Policy 223 - EC2 Instance launched
- Policy 225/251 - Lambda Function modifications
- Policy 228 - RDS Instance modifications
- Policy 229 - CloudTrail logging disabled
- Policy 234 - KMS Key Policy modified
- Policy 235/258/259/264 - S3 Bucket modifications
- Policy 236 - VPC modifications
- Policy 238 - Route53 modifications
- Policy 246 - ECS Task Definition registered
- Policy 249/253 - SNS/SQS modifications
- Policy 250 - DynamoDB Table modifications
- Policy 254 - Secrets Manager modifications
- Policy 255 - Systems Manager modifications
- Policy 256 - CloudFormation Stack operations
- Policy 257 - EKS Cluster modifications

### Azure (10 scripts)
- Policy 243 - Event Hub namespace deleted
- Policy 303 - User MFA disabled
- Policy 309 - Storage Account Networking changed to All Networks
- Policy 317 - Secret added to an application registration
- Policy 318 - Certificate added to an application registration
- Policy 321/322 - Virtual Machine Network Security Group modifications
- Policy 323 - Azure Resource modifications
- Policy 391 - Event Hub deleted
- Policy 395 - Conditional Access policy deleted
- Policy 518 - Virtual Machine disk exported by user

### GCP
- Coming soon

## Uninstallation

To remove the IOA Runner and all downloaded scripts:

```bash
rm -rf $HOME/ioa-scripts
```

## Security Considerations

- The script downloads files from GitHub - ensure you trust the source
- IOA scripts create/modify cloud resources - review scripts before running
- Scripts may incur cloud provider costs
- Always run in a test/demo environment


## Support

## License
