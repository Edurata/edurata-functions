const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const fs = require("fs");

const s3Client = new S3Client();

async function uploadFile(bucketName, fileKey, filePath) {
  try {
    const fileContent = fs.readFileSync(filePath);

    const putObjectParams = {
      Bucket: bucketName,
      Key: fileKey,
      Body: fileContent,
    };

    const data = await s3Client.send(new PutObjectCommand(putObjectParams));
    console.log(`File uploaded successfully: ${fileKey}`, data);
  } catch (err) {
    console.error("Error", err);
  }
}

async function uploadMultipleFiles(bucketName, files) {
  for (const file of files) {
    await uploadFile(bucketName, file.key, file.path);
  }
}

export const handler = async (event) => {
  const bucketName = event.bucketName;
  const filesToUpload = event.files;

  try {
    await uploadMultipleFiles(bucketName, filesToUpload);
  } catch (err) {
    console.error(err);
    return { success: false };
  }
  return { success: true };
};

const bucketName = "your-bucket-name";
const filesToUpload = ["path/to/local/file1.txt", "path/to/local/file2.txt"];

// handler({ bucketName, filesToUpload });
