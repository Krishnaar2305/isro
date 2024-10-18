// routes/uploadRoutes.js

const express = require('express');
const router = express.Router();
const api = require('../controllers/api');

// POST route for file upload
router.post('/upload', api.uploadData);

module.exports = router;

