#!/bin/bash
# scripts/setup_env.sh - Environment Setup for macOS
# Syncs secrets from Google Drive and prepares the development environment.

set -e

# --- Configuration ---
SECRET_FOLDER_NAME="PersonalWebsite-Secrets"
SECRETS_FILES=(".env" "credentials.json" "token.json")

# Colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}--- Detecting Google Drive ---${NC}"

# Check common locations
# 1. macOS Filestream path
GDRIVE_BASE="/Volumes/GoogleDrive/My Drive"
# 2. Modern macOS CloudStorage path
if [ ! -d "$GDRIVE_BASE" ]; then
    GDRIVE_BASE=$(find ~/Library/CloudStorage -maxdepth 1 -name "GoogleDrive-*" 2>/dev/null | head -n 1)
    if [ -n "$GDRIVE_BASE" ]; then
        GDRIVE_BASE="$GDRIVE_BASE/My Drive"
    fi
fi

if [ ! -d "$GDRIVE_BASE" ]; then
    echo -e "${RED}Google Drive not automatically detected.${NC}"
    read -p "Please enter the path to 'My Drive': " GDRIVE_BASE
fi

GDRIVE_SECRETS_PATH="$GDRIVE_BASE/Projects/$SECRET_FOLDER_NAME"
echo -e "Using Google Drive Secrets Path: ${GREEN}$GDRIVE_SECRETS_PATH${NC}"

# --- 2. Ensure Secrets Folder exists ---
if [ ! -d "$GDRIVE_SECRETS_PATH" ]; then
    echo -e "${YELLOW}Creating secrets folder in Google Drive...${NC}"
    mkdir -p "$GDRIVE_SECRETS_PATH"
fi

# --- 3. Manage Secret Files ---
for FILE in "${SECRETS_FILES[@]}"; do
    LOCAL_PATH="$(dirname "$0")/../$FILE"
    REMOTE_PATH="$GDRIVE_SECRETS_PATH/$FILE"

    # Check if a symlink already exists
    if [ -L "$LOCAL_PATH" ]; then
        echo -e "${GRAY}✓ $FILE is already symlinked.${NC}"
        continue
    fi

    # If local file exists but not in GDrive, move it there
    if [ -f "$LOCAL_PATH" ]; then
        if [ ! -f "$REMOTE_PATH" ]; then
            echo -e "${YELLOW}Moving local $FILE to Google Drive...${NC}"
            mv "$LOCAL_PATH" "$REMOTE_PATH"
        else
            echo -e "${YELLOW}Warning: $FILE exists in both local and GDrive. Using GDrive version.${NC}"
            mv "$LOCAL_PATH" "$LOCAL_PATH.bak"
        fi
    fi

    # Create Symlink
    if [ -f "$REMOTE_PATH" ]; then
        echo -e "${CYAN}Creating symlink for $FILE...${NC}"
        ln -s "$REMOTE_PATH" "$LOCAL_PATH"
    else
         if [ "$FILE" == ".env" ]; then
             echo -e "${YELLOW}Warning: .env not found in GDrive. Initializing from env.example...${NC}"
             cp "$(dirname "$0")/../env.example" "$REMOTE_PATH"
             ln -s "$REMOTE_PATH" "$LOCAL_PATH"
             echo -e "${RED}!!! Please update your .env file in Google Drive with real keys !!!${NC}"
         else
             echo -e "${YELLOW}Missing $FILE in GDrive. Please ensure it is uploaded manually if required.${NC}"
         fi
    fi
done

# --- 4. Python Environment Setup ---
echo -e "\n${CYAN}--- Checking Python Environment ---${NC}"
VENV_PATH="$(dirname "$0")/../venv"

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
else
    echo -e "${GRAY}✓ Virtual environment exists.${NC}"
fi

# Upgrade pip and install requirements
echo -e "${YELLOW}Installing/Updating requirements...${NC}"
./venv/bin/python3 -m pip install --upgrade pip > /dev/null
./venv/bin/python3 -m pip install -r "$(dirname "$0")/../requirements.txt" > /dev/null

echo -e "\n${GREEN}✓ Setup Complete! Your environment is ready.${NC}"
