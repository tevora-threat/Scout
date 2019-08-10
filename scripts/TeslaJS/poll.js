"use strict";

const cron = require("node-cron");
const fs = require('fs');

var request = require('request');
require('colors');
var program = require('commander');
var framework = require('./sampleFramework.js');
const mongoose = require("mongoose");
mongoose.connect(
    "mongodb://CHANGEME(USERNAME):CHANGEME(PASSWORD)@localhost:27017/CHANGEME(DBNAME)?authSource=admin", {
        useNewUrlParser: true
    }
);

const Poll = mongoose.model(
    "Poll", {
        ts: Date,
        heading: Number,
        location: {
            type: {
                type: String,
                enum: ["Point"],
                required: true
            },
            coordinates: {
                type: [Number],
                required: true
            }
        },
        locAvail: Boolean,
        nativeType: String,
        power: Number,
        status: String,
        speed: Number,
        driveID: mongoose.Schema.Types.ObjectId
    },
    "polls",
);

const Drive = mongoose.model(
    "Drive", {
        startTime: Date,
        startHeading: Number,
        startLocation: {
            type: {
                type: String,
                enum: ["Point"],
                required: true
            },
            coordinates: {
                type: [Number],
                required: true
            }
        },
        endtime: Date,
        endHeading: Number,
        endLocation: {
            type: {
                type: String,
                enum: ["Point"],
                required: false
            },
            coordinates: {
                type: [Number],
                required: false
            }
        }
    },
    "drives",
);


program
    .option('-u, --username [string]', 'username (needed only if token not cached)')
    .option('-p, --password [string]', 'password (needed only if token not cached)')
    .option('-g, --geocode', 'geocode the street address')
    .option('-i, --index <n>', 'vehicle index (first car by default)', parseInt)
    .option('-U, --uri [string]', 'URI of test server (e.g. http://127.0.0.1:3000)')
    .parse(process.argv);

var theTime = Date.now()
var sample = new framework.SampleFramework(program, sampleMain);
cron.schedule("*/1 * * * * *", function () {
    sample.run();
});



var lastState = ""
var lastDrive = ""

function sampleMain(tjs, options) {
    tjs.driveState(options, function (err, drive_state) {
        if (drive_state) {
            console.log(drive_state);


            var state = drive_state.shift_state || "Parked";
            var speed = drive_state.speed || "0";


            if (lastState === 'Parked' && state != 'Parked') {

                lastState = state;

                const newDrive = new Drive({
                    startTime: new Date(parseInt(drive_state.gps_as_of.toString())),
                    startHeading: drive_state.heading.toString(),
                    startLocation: {
                        type: "Point",
                        coordinates: [drive_state.latitude.toString(), drive_state.longitude.toString()]
                    }
                });
                newDrive.save().then(() => {
                    lastDrive = newDrive._id


                    console.log(`Saved:\n${newDrive._id}`)
                    const newPoll = new Poll({
                        ts: new Date(parseInt(drive_state.gps_as_of.toString())),
                        // ts: parseInt(theLog.ts),
                        heading: drive_state.heading.toString(),
                        location: {
                            type: "Point",
                            coordinates: [drive_state.latitude.toString(), drive_state.longitude.toString()]
                        },
                        locAvail: drive_state.native_location_supported.toString(),
                        nativeType: drive_state.native_type.toString(),
                        power: drive_state.power.toString(),
                        status: state,
                        speed: speed,
                        driveID: newDrive._id
                    });

                    newPoll.save().then(() => console.log(`Saved:\n${newPoll}`));


                });


            } else if ((lastState != 'Parked' && lastState != "") && state === 'Parked') {
                lastState = state;

                Drive.updateOne({
                    _id: lastDrive
                }, {
                    endTime: new Date(parseInt(drive_state.gps_as_of.toString())),
                    endHeading: drive_state.heading.toString(),
                    endLocation: {
                        type: "Point",
                        coordinates: [drive_state.latitude.toString(), drive_state.longitude.toString()]
                    }
                }, (err) => {}).then(() => {
                    const newPoll = new Poll({
                        ts: new Date(parseInt(drive_state.gps_as_of.toString())),
                        heading: drive_state.heading.toString(),
                        location: {
                            type: "Point",
                            coordinates: [drive_state.latitude.toString(), drive_state.longitude.toString()]
                        },
                        locAvail: drive_state.native_location_supported.toString(),
                        nativeType: drive_state.native_type.toString(),
                        power: drive_state.power.toString(),
                        status: state,
                        speed: speed,
                        driveID: lastDrive
                    });

                    newPoll.save().then(() => {
                        console.log(`Saved:\n${newPoll}`)
                        lastDrive = ""
                    });
                });





            } else {


                lastState = state

                if (state != "Parked") {
                    const newPoll = new Poll({
                        ts: new Date(parseInt(drive_state.gps_as_of.toString())),
                        heading: drive_state.heading.toString(),
                        location: {
                            type: "Point",
                            coordinates: [drive_state.latitude.toString(), drive_state.longitude.toString()]
                        },
                        locAvail: drive_state.native_location_supported.toString(),
                        nativeType: drive_state.native_type.toString(),
                        power: drive_state.power.toString(),
                        status: state,
                        speed: speed,
                        driveID: lastDrive
                    });

                    newPoll.save().then(() => {
                        console.log(`Saved:\n${newPoll}`)
                    });
                } else {
                    const newPoll = new Poll({
                        ts: new Date(parseInt(drive_state.gps_as_of.toString())),
                        heading: drive_state.heading.toString(),
                        location: {
                            type: "Point",
                            coordinates: [drive_state.latitude.toString(), drive_state.longitude.toString()]
                        },
                        locAvail: drive_state.native_location_supported.toString(),
                        nativeType: drive_state.native_type.toString(),
                        power: drive_state.power.toString(),
                        status: state,
                        speed: speed
                    });

                    newPoll.save().then(() => {
                        console.log(`Saved:\n${newPoll}`)
                    });
                }

            }



            console.log("\nState: " + state.green);

            if (drive_state.speed) {
                var str = drive_state.speed || 0;
                console.log("Speed: " + str.green);
            }


        } else {
            console.log(err.red);
        }
    });
}