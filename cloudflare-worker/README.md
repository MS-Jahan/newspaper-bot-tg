# Newspaper Scraper Trigger - Cloudflare Worker

This Cloudflare Worker automatically triggers your GitHub Actions workflow every 30 minutes using the GitHub API.

## Features

- **Scheduled Execution**: Runs every 30 minutes using Cloudflare's cron triggers
- **Manual Trigger**: Can also be triggered via HTTP POST request
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Handles cross-origin requests properly

## Setup Instructions

### 1. Prerequisites

- A Cloudflare account
- Node.js and npm installed
- Wrangler CLI installed: `npm install -g wrangler`

### 2. GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with the following permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)

### 3. Get Workflow ID

You need to find your workflow ID. You can do this by:

1. Going to your repository's Actions tab
2. Clicking on the "newspaper_scraper_periodic" workflow
3. Looking at the URL, it will be something like: `https://github.com/username/repo/actions/workflows/main-periodic.yaml`
4. The workflow ID is the filename: `main-periodic.yaml`

### 4. Deploy the Worker

1. Navigate to the cloudflare-worker directory:
   ```bash
   cd cloudflare-worker
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Login to Cloudflare:
   ```bash
   wrangler login
   ```

4. Set the required secrets:
   ```bash
   wrangler secret put GITHUB_TOKEN
   wrangler secret put GITHUB_OWNER
   wrangler secret put GITHUB_REPO
   wrangler secret put WORKFLOW_ID
   ```

   When prompted, enter:
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `GITHUB_OWNER`: Your GitHub username
   - `GITHUB_REPO`: `newspaper-bot-tg`
   - `WORKFLOW_ID`: `main-periodic.yaml`

5. Deploy the worker:
   ```bash
   wrangler deploy
   ```

### 5. Verify Setup

1. Check the worker logs:
   ```bash
   wrangler tail
   ```

2. Test manual trigger (optional):
   ```bash
   curl -X POST https://your-worker-name.your-subdomain.workers.dev
   ```

## Configuration

### Cron Schedule

The worker is configured to run every 30 minutes. To change this, edit the `wrangler.toml` file:

```toml
[triggers]
crons = ["*/30 * * * *"]  # Every 30 minutes
```

Common cron patterns:
- `"0 */2 * * *"` - Every 2 hours
- `"0 9 * * *"` - Daily at 9 AM
- `"0 9 * * 1-5"` - Weekdays at 9 AM

### Environment Variables

The following environment variables are required:

- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_OWNER`: GitHub username
- `GITHUB_REPO`: Repository name
- `WORKFLOW_ID`: Workflow file name (e.g., `main-periodic.yaml`)

## Monitoring

### View Logs

```bash
wrangler tail
```

### Check Worker Status

Visit your worker's URL to see if it's running:
```
https://your-worker-name.your-subdomain.workers.dev
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check your GitHub token permissions
2. **404 Not Found**: Verify the workflow ID and repository name
3. **Scheduler not running**: Check the cron expression in `wrangler.toml`

### Debug Mode

To run the worker locally for testing:

```bash
wrangler dev
```

## Security Notes

- Keep your GitHub token secure
- The worker only accepts POST requests for manual triggers
- CORS is configured to allow all origins (modify as needed for production)

## Cost

Cloudflare Workers are very cost-effective:
- Free tier: 100,000 requests/day
- Paid tier: $5/month for 10 million requests
- Cron triggers count as requests

For a 30-minute schedule, you'll use about 1,440 requests per day (well within the free tier). 