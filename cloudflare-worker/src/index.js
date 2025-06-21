export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // Only allow POST requests for triggering the workflow
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      // Trigger the GitHub Actions workflow
      const response = await triggerGitHubWorkflow(env);
      
      return new Response(JSON.stringify(response), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (error) {
      console.error('Error triggering workflow:', error);
      
      return new Response(JSON.stringify({ 
        error: 'Failed to trigger workflow',
        details: error.message 
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
  },

  // Scheduled function that runs every 30 minutes
  async scheduled(event, env, ctx) {
    try {
      console.log('Scheduled trigger executing at:', new Date().toISOString());
      await triggerGitHubWorkflow(env);
      console.log('Workflow triggered successfully');
    } catch (error) {
      console.error('Scheduled trigger failed:', error);
    }
  },
};

async function triggerGitHubWorkflow(env) {
  const { GITHUB_TOKEN, GITHUB_REPO, GITHUB_OWNER, WORKFLOW_ID } = env;
  
  if (!GITHUB_TOKEN || !GITHUB_REPO || !GITHUB_OWNER || !WORKFLOW_ID) {
    throw new Error('Missing required environment variables');
  }

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_ID}/dispatches`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `token ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
      'User-Agent': 'Cloudflare-Worker/1.0',
    },
    body: JSON.stringify({
      ref: 'main', // or your default branch
      inputs: {
        // You can add custom inputs here if needed
        triggered_by: 'cloudflare-worker-scheduler',
        timestamp: new Date().toISOString(),
      },
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`GitHub API error: ${response.status} ${response.statusText} - ${errorText}`);
  }

  return {
    success: true,
    message: 'Workflow triggered successfully',
    timestamp: new Date().toISOString(),
  };
} 