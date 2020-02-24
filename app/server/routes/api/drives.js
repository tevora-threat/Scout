var dotenv = require('dotenv').config();
const express = require("express");
const mongodb = require("mongodb");

const router = express.Router();

// Get Drives
router.get("/", async (req, res) => {
    const drives = await loadDrivesCollection();


    res.send(
        await drives
        .find({
            startTime: {
                $exists: true
            }
        })
        .toArray()
    );
});



async function loadDrivesCollection() {


    const client = await mongodb.MongoClient.connect(
        process.env.MONGO_URI, {
            useNewUrlParser: true
        }
    );

    return client.db("sds_db").collection("drives");
}

module.exports = router;