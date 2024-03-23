const nodegit = require("nodegit");
const path = require("path");
const fs = require("fs");

/**
 * Clones a Git repository to a temporary directory, supports private repositories, and checks out a specified sub-path and ref.
 * If no sub-path is specified, defaults to the root of the repository.
 * @param {Object} inputs - The inputs for the function.
 * @param {string} inputs.repoUrl - The URL of the Git repository to clone.
 * @param {string} [inputs.privateToken] - A token for accessing private repositories.
 * @param {string} [inputs.path] - A sub-path within the repository to return. Defaults to the root of the repository.
 * @param {string} [inputs.ref] - A reference within the repository to checkout.
 * @returns {Object} The output of the function.
 */
async function handler(inputs) {
  const tempDir = process.env.TMP_DIR || "/tmp";
  const cloneOptions = {};
  if (inputs.privateToken) {
    cloneOptions.fetchOpts = {
      callbacks: {
        credentials: () =>
          nodegit.Cred.userpassPlaintextNew(
            inputs.privateToken,
            "x-oauth-basic"
          ),
      },
    };
  }
  const repoPath = path.join(tempDir, `repo-${Date.now()}`);
  try {
    await nodegit.Clone(inputs.repoUrl, repoPath, cloneOptions);
    const finalPath = inputs.path ? path.join(repoPath, inputs.path) : repoPath;
    // If a ref is specified, attempt to checkout that ref.
    if (inputs.ref) {
      const repo = await nodegit.Repository.open(repoPath);
      const reference = await repo.getBranchCommit(inputs.ref);
      await nodegit.Checkout.tree(repo, reference, {
        checkoutStrategy: nodegit.Checkout.STRATEGY.FORCE,
      });
    }
    return { status: "Repository cloned successfully.", repoCode: finalPath };
  } catch (error) {
    console.error("Error cloning repository:", error);
    return { status: "Failed to clone repository.", repoCode: "" };
  }
}

module.exports = { handler };

// Example function call (commented out)
handler({
  repoUrl: "https://github.com/nodegit/nodegit",
  path: "", // Optional, defaults to the root of the repository
  ref: "master", // Optional
}).then((output) => console.log(output));
