const fs = require("fs");
const path = require("path");
const archiver = require("archiver");

// Handler function
async function handler(inputs) {
  const { file: filePath } = inputs;
  const output = fs.createWriteStream(`${path.basename(filePath)}.zip`);
  const archive = archiver("zip", {
    zlib: { level: 9 }, // Compression level
  });

  return new Promise((resolve, reject) => {
    output.on("close", () =>
      resolve({ zipped: `${path.basename(filePath)}.zip` })
    );
    output.on("error", (err) => reject(err));

    archive.pipe(output);

    if (fs.statSync(filePath).isFile()) {
      // If the provided path is a file, add it to the archive
      archive.file(filePath, { name: path.basename(filePath) });
    } else {
      // If the provided path is a directory, add all files from the directory to the root of the archive
      archive.directory(filePath, false);
    }

    archive.finalize();
  });
}

// Export the handler function
module.exports = { handler };
