var dotenv = require('dotenv').config();
const express = require("express");
const mongodb = require("mongodb");

const router = express.Router();

// Get Polls
router.get("/", async (req, res) => {
  const polls = await loadPollsCollection();
  // res.send(await polls.find({}).toArray());
  //   res.send(
  //     await polls
  //       .find({})
  //       .limit(1000)
  //       .toArray()
  //   );

  res.send(
    await polls
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

// Get Drive Polls


// Delete Poll
router.delete("/:id", async (req, res) => {
  const polls = await loadPollsCollection();
  await polls.deleteOne({
    _id: new mongodb.ObjectID(req.params.id)
  });
  res.status(200).send();
});



router.get("/:id", async (req, res) => {
  const polls = await loadPollsCollection();
  // res.send(await polls.find({}).toArray());
  //   res.send(
  //     await polls
  //       .find({})
  //       .limit(1000)
  //       .toArray()
  //   );
  console.log(`the id is ${req.params.id}`)
  res.send(
    // await polls
    // .find({
    //   _id: new mongodb.ObjectID(req.params.id),

    // })
    // .toArray()
    await polls
    .find({
      driveID: new mongodb.ObjectID(req.params.id)
    })
    .toArray()
  );
});



// // Get Drive Polls
// router.get("/drives", async (req, res) => {
//   const polls = await loadPollsCollection();
//   // res.send(await polls.find({}).toArray());
//   //   res.send(
//   //     await polls
//   //       .find({})
//   //       .limit(1000)
//   //       .toArray()
//   //   );

//   res.send(
//     await polls
//     .find({
//       driveID: {
//         $exists: true
//       }
//     })
//     .toArray()
//   );
// });

// Add Poll
router.post("/", async (req, res) => {
  const polls = await loadPollsCollection();
  await polls.insertOne({
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

// Delete Poll
router.delete("/:id", async (req, res) => {
  const polls = await loadPollsCollection();
  await polls.deleteOne({
    _id: new mongodb.ObjectID(req.params.id)
  });
  res.status(200).send();
});

async function loadPollsCollection() {


  const client = await mongodb.MongoClient.connect(
    process.env.MONGO_URI, {
      useNewUrlParser: true
    }
  );

  return client.db("sds_db").collection("polls");
}

module.exports = router;