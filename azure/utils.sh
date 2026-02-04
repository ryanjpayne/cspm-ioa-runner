#!/bin/bash
# Utils module for Azure IOA scripts

# Function to get tags from config.ini
get_azure_tags() {
    local config_file="$(dirname "$0")/../config.ini"
    local tags=""
    
    if [ -f "$config_file" ]; then
        # Read tags from config.ini [tags] section
        # Parse the config file and extract tags
        while IFS='=' read -r key value; do
            # Skip empty lines and section headers
            if [[ -z "$key" ]] || [[ "$key" =~ ^\[.*\]$ ]]; then
                continue
            fi
            # Trim whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            # Add to tags string in Azure format
            if [ -n "$key" ] && [ -n "$value" ]; then
                if [ -z "$tags" ]; then
                    tags="$key=$value"
                else
                    tags="$tags $key=$value"
                fi
            fi
        done < <(sed -n '/^\[tags\]/,/^\[/p' "$config_file" | grep -v '^\[')
    fi
    
    # Return default tag if no tags found
    if [ -z "$tags" ]; then
        tags="app=crowdstrike-ioa-generator"
    fi
    
    echo "$tags"
}

# Export standardized Azure resource tags
export AZURE_RESOURCE_TAGS=$(get_azure_tags)
