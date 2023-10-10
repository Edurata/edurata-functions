import * as AWS from "aws-sdk";

export async function uploadFileToS3(
  filePath: string,
  bucketName: string,
  key: string
): Promise<void> {
  const s3 = new AWS.S3();

  const params: AWS.S3.PutObjectRequest = {
    Bucket: bucketName,
    Key: key,
    Body: require("fs").createReadStream(filePath),
  };

  try {
    await s3.upload(params).promise();
    console.log(`File uploaded successfully to S3: s3://${bucketName}/${key}`);
  } catch (err) {
    console.error("Error uploading file to S3:", err);
    throw err;
  }
}
