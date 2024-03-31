const fs = require("fs");
const path = require("path");
const archiver = require("archiver");

// Handler function
async function handler(inputs) {
  const { file: filePath } = inputs;
  const output = fs.createWriteStream(`${filePath}.zip`);
  const archive = archiver("zip", {
    zlib: { level: 9 }, // Compression level
  });

  return new Promise((resolve, reject) => {
    output.on("close", () => resolve({ zipped: `${filePath}.zip` }));
    output.on("error", (err) => reject(err));

    archive.pipe(output);

    if (fs.statSync(filePath).isFile()) {
      // If the provided path is a file, add it to the archive
      archive.file(filePath, { name: path.basename(filePath) });
    } else {
      // If the provided path is a directory, add all files and directories in it to the archive
      const items = fs.readdirSync(filePath);
      items.forEach((item) => {
        const itemPath = path.join(filePath, item);
        archive.directory(itemPath, path.basename(itemPath));
      });
    }

    archive.finalize();
  });
}

/* Example function call (commented out)
handler({ filePath: 'path/to/your/fileOrFolder' })
  .then((output) => console.log('Zipped:', output.zipped))
  .catch((error) => console.error(error));
*/

module.exports = { handler };
