var dotenv = require('dotenv').config();
const express = require('express');
const mongodb = require('mongodb');
const router = express.Router();

console.log(process.env.MONGO_URI);


// Get Plates
router.get('/', async (req, res) => {
    var plates = await loadPlatesCollection();
    const plateDetections = await loadPlateDetectionsCollection();
    var platesToCheckDetections = await plates.find({}).toArray()

    await platesToCheckDetections.forEach(plate => {
        console.log(plate._id);

        plate.numDetections = plateDetections.find({
            plateID: new mongodb.ObjectID(plate._id)
        }).sort({
            ts: 1
        }).toArray().length

        console.log(plateDetections.find({
            plateID: new mongodb.ObjectID(plate._id)
        }).sort({
            _id: 1
        }).toArray());

    });
    // console.log(plateDetections.find({
    //   plateID: new mongodb.ObjectID(plate._id)
    // }).sort({
    //     ts: 1
    // }).toArray().length);

    // res.send(await plates.find({}).toArray());
    res.send(platesToCheckDetections);


});

// Get Plate Detections for recent(limit to 50)
router.get('/detections', async (req, res) => {
    const plates = await loadPlateDetectionsCollection();
    res.send(await plates.find().sort({
        _id: 1
    }).limit(50).toArray());

});

// Get All Plate Detections
router.get('/alldetections', async (req, res) => {
    const plates = await loadPlateDetectionsCollection();
    res.send(await plates.find().sort({
        _id: 1
    }).toArray());
});

// Get Plate Detections DeDuped)
router.get('/alldetectionsdd', async (req, res) => {
    const plates = await loadPlateDetectionsCollection();
    var prePlates = await plates.find().sort({
        _id: 1
    }).toArray()
    var prePlatesCount = await plates.find().count()
    var prePlates2 = await prePlates
    console.log(prePlatesCount);

    var lastPlate = {}
    var lastPlate2 = {
        test: false
    }
    var postPlates = []
    await prePlates2.forEach(detection => {
        // postPlates.push(detection)
        // console.log(`pDetection:${detection}`);
        console.log(`lastPlate == ${Object.keys(lastPlate).length}`);
        console.log(`lastPlate2 == ${Object.keys(lastPlate2).length}`);


        if (Object.keys(lastPlate).length > 0) {


            //check if this plateContent is the same as the last one
            if (detection.plateContent === lastPlate.plateContent) {
                //same plate, has enough time gone by?
                if (detection.ts - lastPlate.ts > 60) {
                    postPlates.push(detection)
                    lastPlate = detection
                    console.log(`pushing valid detection:${detection}`);
                }
            } else {
                postPlates.push(detection)
                lastPlate = detection
                console.log(`pushing valid detection:${detection}`);
            }



        } else {

            //first time running, nothing to compare to
            lastPlate = detection
            postPlates.push(detection)
            console.log(`pushing valid detection:${detection}`);

        }

    });
    res.send(postPlates);

});

// Get specific plate detections

router.get('/detections/:id', async (req, res) => {
    const faces = await loadPlateDetectionsCollection();
    res.send(await faces.find({
        plateID: new mongodb.ObjectID(req.params.id)
    }).sort({
        ts: 1
    }).toArray());


    // .find({
    //   _id: new mongodb.ObjectID(req.params.id)
    // })
    // .toArray()

});


// Add Plate
router.post('/', async (req, res) => {
    const plates = await loadPlatesCollection();
    await plates.insertOne({
        text: req.body.text,
        createdAt: new Date()
    });
    res.status(201).send();
});

// Delete Plate
router.delete('/:id', async (req, res) => {
    const plates = await loadPlatesCollection();
    await plates.deleteOne({
        _id: new mongodb.ObjectID(req.params.id)
    });
    res.status(200).send();
});

async function loadPlatesCollection() {


    const client = await mongodb.MongoClient.connect(
        process.env.MONGO_URI, {
            useNewUrlParser: true
        }
    );

    return client.db('sds_db').collection('plates');
}

async function loadPlateDetectionsCollection() {

    const client = await mongodb.MongoClient.connect(
        process.env.MONGO_URI, {
            useNewUrlParser: true
        }
    );
    return client.db('sds_db').collection('plateDetections');


}

module.exports = router;