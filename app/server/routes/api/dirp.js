var dotenv = require('dotenv').config();
const express = require('express');
const mongodb = require('mongodb');

const router = express.Router();

// Get Plates
// router.get('/', async (req, res) => {
//     const plates = await loadPlatesCollection();
//     res.send(await plates.find({}).toArray());
// });

// Add Plate
router.post('/', async (req, res) => {
    const dirps = await loadDirpsCollection();
    await dirps.insertOne({
        url: req.body.url,
        createdAt: new Date()
    });
    res.status(201).send();
});

// Delete Plate
// router.delete('/:id', async (req, res) => {
//     const plates = await loadPlatesCollection();
//     await plates.deleteOne({
//         _id: new mongodb.ObjectID(req.params.id)
//     });
//     res.status(200).send();
// });

async function loadDirpsCollection() {


    const client = await mongodb.MongoClient.connect(
        process.env.MONGO_URI, {
            useNewUrlParser: true
        }
    );

    return client.db('sds_db').collection('dirps');
}

module.exports = router;