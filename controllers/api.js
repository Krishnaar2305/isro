const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const folderPath = "./uploads";

// Count the number of files in the specified folder
const countFiles = (folderPath) => {
    try {
        return fs.readdirSync(folderPath)
            .filter(item => fs.statSync(path.join(folderPath, item)).isFile()).length;
    } catch (err) {
        console.error(`Error reading folder: ${err.message}`);
        return 0; // Default to 0 if there is an error
    }
};

let fileCount;

// Set up Multer storage configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, folderPath);
    },
    filename: (req, file, cb) => {
        fileCount = countFiles(folderPath);
        cb(null, `data${fileCount}${path.extname(file.originalname)}`); // Rename file with count
    }
});

const upload = multer({ storage }).single('datafile');

// Run the specified Python script
const runPy = (py, callback) => {
    exec(`python ${py}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);
            callback(error, null); // Pass error to callback
            return;
        }
        if (stderr) {
            console.error(`Stderr: ${stderr}`);
            callback(new Error(stderr), null); // Pass error to callback
            return;
        }
        console.log(`Successfully executed Python file.`);
        callback(null, stdout); // Pass stdout to callback
    });
};

// Upload data handler
const uploadData = (req, res) => {
    upload(req, res, (err) => {
        if (err) {
            return res.status(400).send(`Error uploading file: ${err.message}`);
        }

        console.log('File uploaded:', req.file);

        // Run the Python script and handle the callback
        runPy('./public/genCurve.py', (scriptErr, stdout) => {
            if (scriptErr) {
                return res.status(400).json({ error: 'Failed to generate graph', details: scriptErr.message });
            }

            const imgObj = {
                "message": "File uploaded successfully",
                "imagePath": `./history/img${fileCount}.png` // Adjust based on your server logic
            };
            res.status(200).json(imgObj);
        });
    });
};

module.exports = {
    uploadData  
};
