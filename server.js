const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 3000;

// Endpoint to check username folder existence
app.get("/check-username", (req, res) => {
    const username = req.query.username;

    // Sanitize and validate the username
    const validPattern = /^[a-zA-Z0-9_-]+$/;
    if (!validPattern.test(username)) {
        return res.status(400).json({ error: "Invalid username format." });
    }

    const folderPath = path.join(__dirname, "saves", username);
    fs.access(folderPath, fs.constants.F_OK, (err) => {
        if (err) {
            // Folder does not exist
            res.json({ exists: false });
        } else {
            // Folder exists
            res.json({ exists: true });
        }
    });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});