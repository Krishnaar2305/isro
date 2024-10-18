const multer = require('multer');
const path = require('path');
const fs = require('fs')

const storage = multer.diskStorage({
    destination:(req, file, cb) => {
        cb(null, 'Isro/uploads/'); // Set upload directory
    },
    filename: (req, file, cb) =>  {
        cb(null, Date.now() + path.extname(file.originalname)); // Rename file with timestamp
    }
});

const upload = multer({ storage }).single('datafile');

const uploadData = (req, res) => {
    upload(req, res, function(err){
        try {
            console.log('File uploaded:', req.file);
            // You can now access the uploaded file in req.file
            // res.send('File uploaded successfully.');
            res.redirect("/")
        } catch (err) {
            res.status(400).send(`Error uploading file ${err.message}`);
        }
    });
};


module.exports = {
    uploadData
};