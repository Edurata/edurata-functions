const fs = require("fs");
const unzipper = require("unzipper");

// Handler function
async function handler(inputs) {
  const zippedFilePath = inputs.zippedFile; // Using the zipped file path from inputs
  const outputPath = zippedFilePath.replace(".zip", "_unzipped"); // Defining the output directory

  return new Promise((resolve, reject) => {
    fs.createReadStream(zippedFilePath)
      .pipe(unzipper.Extract({ path: outputPath }))
      .on("close", () => resolve({ unzipped: outputPath })) // Returning the outputPath in the 'unzipped' attribute
      .on("error", (err) => reject(err));
  });
}

/* Example function call (commented out)
handler({ zippedFile: 'path/to/your/zippedfile.zip' })
  .then((output) => console.log('Unzipped files are in:', output.unzipped))
  .catch((error) => console.error(error));
*/

module.exports = { handler };
