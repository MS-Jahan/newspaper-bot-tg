#!/bin/bash

# Newspaper Scraper Trigger - Deployment Script
# This script helps deploy the Cloudflare Worker

set -e

echo "🚀 Deploying Newspaper Scraper Trigger Worker..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI is not installed. Please install it first:"
    echo "npm install -g wrangler"
    exit 1
fi

# Check if we're logged in
if ! wrangler whoami &> /dev/null; then
    echo "🔐 Please login to Cloudflare first:"
    echo "wrangler login"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if secrets are already set
echo "🔍 Checking if secrets are configured..."

# Function to check if a secret exists
check_secret() {
    local secret_name=$1
    if ! wrangler secret list 2>/dev/null | grep -q "$secret_name"; then
        return 1
    fi
    return 0
}

# Check and set secrets
secrets=("GITHUB_TOKEN" "GITHUB_OWNER" "GITHUB_REPO" "WORKFLOW_ID")

for secret in "${secrets[@]}"; do
    if ! check_secret "$secret"; then
        echo "🔑 Setting secret: $secret"
        echo "Please enter the value for $secret:"
        read -s value
        echo "$value" | wrangler secret put "$secret"
    else
        echo "✅ Secret $secret already configured"
    fi
done

# Deploy the worker
echo "🚀 Deploying worker..."
wrangler deploy

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Check the worker logs: wrangler tail"
echo "2. Test manual trigger: curl -X POST https://your-worker-name.your-subdomain.workers.dev"
echo "3. Monitor the GitHub Actions tab for triggered workflows"
echo ""
echo "🔧 To update the worker in the future, just run: wrangler deploy" 