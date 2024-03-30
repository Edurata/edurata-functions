const fs = require("fs");
const archiver = require("archiver");

// Handler function
async function handler(inputs) {
  const { file } = inputs;
  const output = fs.createWriteStream(`${file}.zip`);
  const archive = archiver("zip", {
    zlib: { level: 9 }, // Compression level
  });

  return new Promise((resolve, reject) => {
    archive.on("error", (err) => reject(err)).pipe(output);

    archive.file(file, { name: file.name });
    archive.finalize();

    output.on("close", () => resolve({ zipped: `${file}.zip` }));
  });
}

/* Example function call (commented out)
handler({ file: { path: 'path/to/your/file', name: 'yourfile.txt' }})
  .then((output) => console.log('Zipped file:', output.zipped))
  .catch((error) => console.error(error));
*/

module.exports = { handler };
