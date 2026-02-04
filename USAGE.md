# CrowdStrike IOA Runner Usage Guide

This guide provides detailed instructions on how to use the IOA Runner interactive menu system.

## Table of Contents
- [Getting Started](#getting-started)
- [Main Menu](#main-menu)
- [AWS Scripts](#aws-scripts)
- [Azure Scripts](#azure-scripts)
- [GCP Scripts](#gcp-scripts)
- [Best Practices](#best-practices)
- [Common Workflows](#common-workflows)

## Getting Started

### First Time Setup

1. Run the bootstrap script:
```bash
curl -sSL https://raw.githubusercontent.com/ryanjpayne/cspm-ioa-runner/refs/heads/main/ioa-runner.sh | bash
```

2. The script will:
   - Detect your environment
   - Create `$HOME/ioa-scripts` directory
   - Download all IOA scripts
   - Install Python dependencies
   - Display the main menu

### Subsequent Runs

After initial setup, you can run the script from anywhere:

```bash
bash $HOME/ioa-scripts/ioa-runner.sh
```

Or navigate to the directory:
```bash
cd $HOME/ioa-scripts
bash ioa-runner.sh
```

## Main Menu

When you launch the IOA Runner, you'll see:

```
╔═════════════════════════════════════════════════════════════╗
║                    CrowdStrike IOA Runner                   ║
║              Cloud Security Posture Management              ║
╚═════════════════════════════════════════════════════════════╝

Environment: AWS CloudShell
Install Directory: /home/cloudshell-user/ioa-scripts

Select Cloud Service Provider:

  1) AWS (Amazon Web Services)
  2) Azure (Microsoft Azure)
  3) GCP (Google Cloud Platform)

  0) Exit

Enter your choice [0-3]:
```

### Navigation
- Enter a number (0-3) to select an option
- Press `0` to exit at any time
- Press `0` in sub-menus to return to the main menu

## AWS Scripts

### Accessing AWS Menu

1. From the main menu, select `1` for AWS
2. If AWS CLI is not detected, you'll be warned but can continue
3. The AWS IOA menu will display all 23 available scripts

### Running an AWS Script

1. Select a script number (1-23)
2. When prompted, enter your AWS profile name:
   - Press Enter for default profile
   - Or type a specific profile name (e.g., `production`, `dev`)
3. The script will execute and display output
4. Press Enter when complete to return to the AWS menu

### Example: Running IOA 204

```
Enter your choice: 1

Enter AWS profile name (or press Enter for 'default'): demo-profile

ℹ Running aws_ioa_204.py with profile: demo-profile

[Script output appears here...]

✓ Script completed successfully

Press Enter to continue...
```

## Azure Scripts

### Accessing Azure Menu

1. From the main menu, select `2` for Azure
2. Azure CLI must be installed and authenticated
3. The Azure IOA menu will display available scripts

### Running an Azure Script

1. Select a script number
2. The script will execute immediately (no profile prompt)
3. View the output
4. Press Enter to return to the Azure menu

### Example: Running IOA 321/322

```
Enter your choice: 1

ℹ Running azure_ioa_321_322.sh

Creating Resource Group CSPM_TESTING_321_322
[Script output appears here...]

✓ Script completed successfully

Press Enter to continue...
```

## GCP Scripts

GCP scripts are coming soon. The menu structure is ready for when scripts are added.

## Script Descriptions

Each IOA Script includes a usage block with pattern details.  Please review this and the script body for details about what resources will be created and deleted and what CLI commands are used.

## Best Practices

### Before Running Scripts

1. **Verify Authentication**
   - AWS: Run `aws sts get-caller-identity` to verify credentials
   - Azure: Run `az account show` to verify login
   - GCP: Run `gcloud auth list` to verify authentication

2. **Check Permissions**
   - Ensure you have necessary permissions to create/modify resources
   - Review the script's operations before running

3. **Use Test Environments**
   - Always run in non-production environments
   - Verify CrowdStrike CSPM is monitoring the account

4. **Review Script Documentation**
   - Check individual script comments for specific requirements
   - Note any manual cleanup steps that may be needed

### During Script Execution

1. **Monitor Output**
   - Watch for error messages
   - Note any resources created
   - Check for completion messages

2. **Don't Interrupt**
   - Let scripts complete fully
   - Interrupting may leave resources in inconsistent state

3. **Note Resource Names**
   - Scripts often create resources with specific names
   - You may need these for manual cleanup if script fails

### After Running Scripts

1. **Verify in CrowdStrike Console**
   - Check that IOAs were triggered
   - Review detection details
   - Verify timeline of events

2. **Check Resource Cleanup**
   - Scripts are designed to clean up automatically
   - Verify no unexpected resources remain
   - Manually clean up if script was interrupted

3. **Review Costs**
   - Some operations may incur charges
   - Check cloud provider billing

## Troubleshooting During Use

### Script Fails to Run

**Check:**
- Cloud CLI is installed and configured
- You have necessary permissions
- Profile name is correct (for AWS)
- You're authenticated to the cloud provider

### Script Hangs

**Actions:**
- Wait for timeout (scripts have built-in timeouts)
- Check cloud provider console for stuck operations
- If necessary, press Ctrl+C and manually clean up resources

### Can't Return to Menu

**Solution:**
- Press Enter when prompted
- If stuck, press Ctrl+C to exit
- Restart the script

## Advanced Usage

### Running Specific Scripts Directly

If you know which script you want to run:

```bash
# AWS script
cd $HOME/ioa-scripts/aws
python3 aws_ioa_204.py your-profile-name

# Azure script
cd $HOME/ioa-scripts/azure
bash azure_ioa_321_322.sh
```

### Customizing the Runner

Edit `ioa-runner.sh` to:
- Change installation directory
- Modify GitHub repository URL
