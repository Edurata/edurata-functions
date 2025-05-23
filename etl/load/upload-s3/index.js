const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const { Upload } = require("@aws-sdk/lib-storage");
const { fromEnv } = require("@aws-sdk/credential-provider-env");
const fs = require("fs");

// Function to upload data to S3
async function handler(inputs) {
  const s3Client = new S3Client({
    credentials: fromEnv(),
    region: process.env.AWS_REGION || "eu-central-1",
  });

  const { bucket_name, files } = inputs;
  let success = true;
  console.log("bucket_name", bucket_name);
  for (const file of files) {
    console.log("file", file);
    const params = {
      Bucket: bucket_name,
      Key: file.key,
    };

    try {
      if (file.content) {
        params.Body = file.content;
        await s3Client.send(new PutObjectCommand(params));
      } else if (file.path) {
        const upload = new Upload({
          client: s3Client,
          params: { ...params, Body: fs.createReadStream(file.path) },
        });

        await upload.done();
      } else {
        success = false;
        continue;
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      throw error; // This will ensure the job fails
    }
  }

  return { success };
}

// Sample function call (commented out)
// handler({
//   bucket_name: 'your-bucket-name',
//   files: [
//     { path: './test/testfile.txt', key: 'example2.txt' }
//   ]
// });

module.exports = { handler };
