@echo off
setlocal enabledelayedexpansion

echo 🚀 Deploying Newspaper Scraper Trigger Worker...

REM Check if wrangler is installed
wrangler --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Wrangler CLI is not installed. Please install it first:
    echo npm install -g wrangler
    pause
    exit /b 1
)

REM Check if we're logged in
wrangler whoami >nul 2>&1
if errorlevel 1 (
    echo 🔐 Please login to Cloudflare first:
    echo wrangler login
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
npm install

REM Deploy the worker
echo 🚀 Deploying worker...
wrangler deploy

echo ✅ Deployment complete!
echo.
echo 📋 Next steps:
echo 1. Set up secrets manually: wrangler secret put GITHUB_TOKEN
echo 2. Check the worker logs: wrangler tail
echo 3. Test manual trigger: curl -X POST https://your-worker-name.your-subdomain.workers.dev
echo 4. Monitor the GitHub Actions tab for triggered workflows
echo.
echo 🔧 To update the worker in the future, just run: wrangler deploy
pause 