var dotenv = require('dotenv').config();
const fsp = require('fs').promises
const fs = require('fs');
const express = require('express');
const mongodb = require('mongodb');

const router = express.Router();

async function ensureDir(dirpath) {
    try {
        await fsp.mkdir(dirpath, {
            recursive: true
        })
    } catch (err) {
        if (err.code !== 'EEXIST') throw err
    }
}

async function mkdir(path) {
    try {
        await ensureDir(path)
        console.log(`${path} directory created`)
    } catch (err) {
        console.error(err)
    }
}

module.exports = function move(oldPath, newPath, callback) {

    fs.rename(oldPath, newPath, function (err) {
        if (err) {
            if (err.code === 'EXDEV') {
                copy();
            } else {
                callback(err);
            }
            return;
        }
        callback();
    });

    function copy() {
        var readStream = fs.createReadStream(oldPath);
        var writeStream = fs.createWriteStream(newPath);

        readStream.on('error', callback);
        writeStream.on('error', callback);

        readStream.on('close', function () {
            fs.unlink(oldPath, callback);
        });

        readStream.pipe(writeStream);
    }
}



// Get Faces
router.get('/', async (req, res) => {
    const faces = await loadFacesCollection();
    res.send(await faces.find({}).toArray());
});

// Get Face Detections
router.get('/detections', async (req, res) => {
    const faces = await loadFaceDetectionsCollection();
    res.send(await faces.find({}).toArray());
});

// Add Face
router.post('/', async (req, res) => {
    const faces = await loadFacesCollection();
    await faces.insertOne({
        text: req.body.text,
        createdAt: new Date()
    });
    res.status(201).send();
});

// Name Face
router.post('/:id', async (req, res) => {

    if (req.body.makeStranger) {

        //create a new face
        const faces = await loadFacesCollection();
        const faceDetections = await loadFaceDetectionsCollection();
        var personName = `Stranger #${await faces.find().count()+1}`
        await faces.insertOne({
            personName: personName,
            notNamed: true
        }).then(result => {
            console.log(`new face added with id:${result.insertedId}`);
            //now change the personName, notNamed and faceID of the detection
            faceDetections.findOneAndUpdate({
                _id: new mongodb.ObjectID(req.params.id)
            }, {
                $set: {
                    personName: personName,
                    notNamed: true,
                    faceID: new mongodb.ObjectID(result.insertedId)
                }
            }, {
                new: true
            }, function (err, doc) {
                console.log(`just updated the detection as well:${doc}`);
                //also gonna have to move the image in python too.
                var newFacePath = `/tesladrive/datasets/scout/train/${result.insertedId}`
                var oldFacePath = `/tesladrive/datasets/scout/train/${req.body.oldFaceID}`

                mkdir(newFacePath)
                var oldFacePathImg = `${oldFacePath}/${req.params.id}.png`
                var newFacePathImg = `${newFacePath}/${req.params.id}.png`
                //move the image


                fs.rename(oldFacePathImg, newFacePathImg, function (err) {
                    if (err) throw err
                    console.log('Successfully renamed - AKA moved!')
                    console.log(`from:${oldFacePathImg}`);
                    console.log(`to:${newFacePathImg}`);

                })


                //dont need to delete the directory  becase we know based on how the ui is set up that there is at least one more image for this face
            });
        });
        res.status(201).send();

        //assign this detection with that faceID

        //give this detection a new stranger name

        //change this detection to hasName false

    } else if (req.body.updateDetection) {
        const faces = await loadFacesCollection();
        const faceDetections = await loadFaceDetectionsCollection();
        await faceDetections.findOneAndUpdate({
            _id: new mongodb.ObjectID(req.params.id)
        }, {
            $set: {
                personName: req.body.newName,
                notNamed: false,
                faceID: new mongodb.ObjectID(req.body.newFaceID)
            }
        }, {
            new: true
        }, function (err, doc) {
            console.log(`just updated the detection:${doc}`);
            //now have to move an image around
        });
        var numDetectionsWithOldFace = await faceDetections.find({
            faceID: new mongodb.ObjectID(req.body.oldFaceID)
        }).count()
        if (numDetectionsWithOldFace > 0) {
            console.log(`have to keep the face around, there are ${numDetectionsWithOldFace} assigned to it`);
        } else {
            console.log(`we can delete the face, no other detections assigned to is`);
            faces.deleteOne({
                _id: new mongodb.ObjectID(req.body.oldFaceID)
            });
            //also gonna have to delete the training folder now 
        }

        res.status(201).send();
    } else {
        const faces = await loadFacesCollection();
        const faceDetections = await loadFaceDetectionsCollection();
        await faces.findOneAndUpdate({
            _id: new mongodb.ObjectID(req.params.id)
        }, {
            $set: {
                personName: req.body.name,
                notNamed: false
            }
        }, {
            new: true
        }, function (err, doc) {
            console.log(doc);
        });
        await faceDetections.updateMany({
            faceID: new mongodb.ObjectID(req.params.id)
        }, {
            $set: {
                personName: req.body.name,
                notNamed: false
            }
        }, function (err, doc) {
            console.log(doc);
        });
        res.status(201).send();
    }




});

// Delete Face
router.delete('/:id', async (req, res) => {
    const faces = await loadFacesCollection();
    await faces.deleteOne({
        _id: new mongodb.ObjectID(req.params.id)
    });
    res.status(200).send();
});

async function loadFacesCollection() {


    const client = await mongodb.MongoClient.connect(
        process.env.MONGO_URI, {
            useNewUrlParser: true
        }
    );

    return client.db('sds_db').collection('faces');
}

async function loadFaceDetectionsCollection() {


    const client = await mongodb.MongoClient.connect(
        process.env.MONGO_URI, {
            useNewUrlParser: true
        }
    );

    return client.db('sds_db').collection('faceDetections');
}

module.exports = router;