const simpleGit = require("simple-git");
const fs = require("fs");
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

  // Determine the local path for the repo
  const localPath = `./cloned_repos/${path.basename(repoUrl)}`;

  // Check if the repository already exists at the local path
  if (fs.existsSync(localPath)) {
    console.log(`Repository already exists at ${localPath}.`);
    // Additional logic can be added here if you want to pull updates or handle this scenario differently
  } else {
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
    await git.clone(repoUrl, localPath);
    console.log(`Repository cloned to ${localPath}.`);
  }

  // Change working directory to the local path
  const git = simpleGit(localPath);
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
//   privateUser: 'username',
//   privateToken: 'your-token'
// }).then(console.log);

module.exports = { handler };
