const simpleGit = require("simple-git");
const path = require("path");

// Handler function
async function handler(inputs) {
  const {
    repoUrl,
    path: repoPath,
    ref = "main",
    privateUser,
    privateToken,
  } = inputs;

  // Setting up the Git client
  const git = simpleGit();
  if (privateToken) {
    // Configure Git for HTTPS token-based authentication
    git
      .env("GIT_TERMINAL_PROMPT", "0")
      .env("GIT_ASKPASS", "echo")
      .env("GIT_HTTPS_USERNAME", privateUser)
      .env("GIT_HTTPS_PASSWORD", privateToken);
  }

  // Clone and checkout
  const localPath = `./cloned_repos/${path.basename(repoUrl)}`;
  await git.clone(repoUrl, localPath);
  await git.cwd(localPath);
  await git.checkout(ref);

  // Extract the specified path
  const repoCodePath = path.join(localPath, repoPath);

  // Outputs
  return { repoCode: repoCodePath };
}

// Sample function call (commented out)
// handler({
//   repoUrl: 'https://github.com/user/repo.git',
//   path: 'subdirectory',
//   ref: 'main',
//   privateToken: 'your-token'
// }).then(console.log);

module.exports = { handler };
