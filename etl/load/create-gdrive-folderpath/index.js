const axios = require('axios');

// Function to authenticate with Google Drive API
async function authenticate() {
    const token = process.env.GOOGLE_DRIVE_API_TOKEN; // Store your access token as an environment variable
    return token;
}

// Function to check if a folder exists
async function checkFolderExists(folderName, parentId, accessToken) {
    const query = `name='${folderName}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '${parentId}' in parents`;
    const response = await axios.get('https://www.googleapis.com/drive/v3/files', {
        params: {
            q: query,
            fields: 'files(id, name)'
        },
        headers: {
            Authorization: `Bearer ${accessToken}`
        }
    });
    return response.data.files.length > 0 ? response.data.files[0] : null;
}

// Function to create a folder
async function createFolder(folderName, parentId, accessToken) {
    const response = await axios.post(
        'https://www.googleapis.com/drive/v3/files',
        {
            name: folderName,
            mimeType: 'application/vnd.google-apps.folder',
            parents: [parentId]
        },
        {
            headers: {
                Authorization: `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        }
    );
    return response.data;
}

// Function to ensure folder path exists
async function ensureFolderPath(folderPath, accessToken) {
    const folders = folderPath.split('/');
    let parentId = 'root'; // Start with the root folder

    for (const folderName of folders) {
        let folder = await checkFolderExists(folderName, parentId, accessToken);
        if (!folder) {
            folder = await createFolder(folderName, parentId, accessToken);
            console.log(`Created folder: ${folderName}`);
        } else {
            console.log(`Folder already exists: ${folderName}`);
        }
        parentId = folder.id; // Move to the next folder's parent ID
    }
}

async function handler(inputs) {
    try {
        const { folder_path } = inputs;
        const accessToken = await authenticate();

        await ensureFolderPath(folder_path, accessToken);

        return { message: "Folder path created or verified successfully." };
    } catch (error) {
        console.error('Error creating folder path:', error.response ? error.response.data : error.message);
        return { message: "An error occurred while creating the folder path." };
    }
}

// Sample function call
// handler({ folder_path: 'hello/foo/bar' }).then(console.log).catch(console.error);

module.exports = { handler };
