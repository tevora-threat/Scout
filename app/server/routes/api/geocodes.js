var dotenv = require('dotenv').config();
const express = require("express");
const mongodb = require("mongodb");

const router = express.Router();

// Get Geocodes
router.get("/", async (req, res) => {
  const geocodes = await loadGeocodesCollection();
  // res.send(await geocodes.find({}).toArray());
  //   res.send(
  //     await geocodes
  //       .find({})
  //       .limit(1000)
  //       .toArray()
  //   );

  res.send(
    await geocodes
    .find({
      status: "D",
      speed: {
        $gte: 15,
        $lte: 65
      }
    })
    .limit(100)
    .toArray()
  );
});

// Get Drive Geocodes


// Delete Geocode
router.delete("/:id", async (req, res) => {
  const geocodes = await loadGeocodesCollection();
  await geocodes.deleteOne({
    _id: new mongodb.ObjectID(req.params.id)
  });
  res.status(200).send();
});



router.get("/:id", async (req, res) => {
  const geocodes = await loadGeocodesCollection();
  // res.send(await geocodes.find({}).toArray());
  //   res.send(
  //     await geocodes
  //       .find({})
  //       .limit(1000)
  //       .toArray()
  //   );
  console.log(`the id is ${req.params.id}`)
  res.send(
    // await geocodes
    // .find({
    //   _id: new mongodb.ObjectID(req.params.id),

    // })
    // .toArray()
    await geocodes
    .find({
      _id: new mongodb.ObjectID(req.params.id)
    })
    .toArray()


  );
  console.log(await geocodes
    .find({
      _id: new mongodb.ObjectID(req.params.id)
    })
    .toArray());


});



// // Get Drive Geocodes
// router.get("/drives", async (req, res) => {
//   const geocodes = await loadGeocodesCollection();
//   // res.send(await geocodes.find({}).toArray());
//   //   res.send(
//   //     await geocodes
//   //       .find({})
//   //       .limit(1000)
//   //       .toArray()
//   //   );

//   res.send(
//     await geocodes
//     .find({
//       driveID: {
//         $exists: true
//       }
//     })
//     .toArray()
//   );
// });

// Add Geocode
router.post("/", async (req, res) => {
  const geocodes = await loadGeocodesCollection();
  await geocodes.insertOne({
    createdAt: new Date(),
    lat: req.body.lat,
    lon: req.body.lon,
    ts: req.body.ts,
    locAvail: req.body.locAvail,
    nativeType: req.body.nativeType,
    power: req.body.power,
    heading: req.body.heading,
    speed: req.body.speed,
    status: req.body.status
  });
  res.status(201).send();
});

// Delete Geocode
router.delete("/:id", async (req, res) => {
  const geocodes = await loadGeocodesCollection();
  await geocodes.deleteOne({
    _id: new mongodb.ObjectID(req.params.id)
  });
  res.status(200).send();
});

async function loadGeocodesCollection() {


  const client = await mongodb.MongoClient.connect(
    process.env.MONGO_URI, {
      useNewUrlParser: true
    }
  );

  return client.db("sds_db").collection("geocodes");
}

module.exports = router;