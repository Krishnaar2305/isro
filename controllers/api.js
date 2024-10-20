const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const folderPath = "./uploads";

// Count the number of files in the specified folder
// const countFiles = (folderPath) => {
//     try {
//         return fs.readdirSync(folderPath)
//             .filter(item => fs.statSync(path.join(folderPath, item)).isFile()).length;
//     } catch (err) {
//         console.error(`Error reading folder: ${err.message}`);
//         return 0; // Default to 0 if there is an error
//     }
// };

// let fileCount;

// Set up Multer storage configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, folderPath);
    },
    filename: (req, file, cb) => {
        cb(null, `data${path.extname(file.originalname)}`); // Rename file with count
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
        runPy('./python/stats.py', (scriptErr, stdout) => {
            if (scriptErr) {
                return res.status(400).json({ error: 'Failed to generate graph', details: scriptErr.message });
            }

            const parsedData = JSON.parse(stdout);
            console.log(parsedData)
            const imgObj = {
                "message": "File uploaded successfully",
                "originalCurve": `./curves/originalCurve${parsedData.now}.png`,
                "smoothenedCurve": `./curves/smoothenedCurve${parsedData.now}.png`,
                "peaksCurve": `./curves/peaksCurve${parsedData.now}.png`,
                "data": parsedData
            };
            res.status(200).json(imgObj);
        });
    });
};

// const getNumber = (req, res) =>{
//     const num = countFiles(folderPath);
//     res.status(200).json({num})
// }

module.exports = {
    uploadData,
};
