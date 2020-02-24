<template>
  <v-layout v-if="!notTesting">
    <v-flex xs12>
      <l-map
        :zoom="zoom"
        ref="myMap"
        :center="center"
        :options="mapOptions"
        @update:center="centerUpdate"
        @update:zoom="zoomUpdate"
        class="halfHeightMap"
      >
        <l-tile-layer :url="url" :attribution="attribution" />

        <l-polyline
          v-for="drive in allDrives"
          :key="drive[0]._id"
          :lat-lngs="parseDrives(drive)"
          color="#3399ff"
          weight="8"
        ></l-polyline>

        <l-moving-marker
          ref="movingMarkerRef"
          :lat-lng="currentDrive.latlng"
          :duration="currentDrive.duration"
          :rotationAngle="currentDrive.heading"
          keepAtCenter
          :icon="icon1"
        ></l-moving-marker>
      </l-map>

      <v-layout justify-space-between column fill-height>
        <v-flex xs6 style="min-height:100%!important;">
          <v-container>
            <v-layout row wrap>
              <v-flex xs3>
                <v-text-field
                  style="margin-top: 12px!important;display:none!important;"
                  v-if="showAll"
                  solo
                  label="Search"
                  v-model="search"
                  prepend-inner-icon="search"
                  append-icon="keyboard_arrow_right"
                  class="roundCard"
                ></v-text-field>

                <v-btn
                  color="white darken-4"
                  fab
                  dark
                  absolute
                  @click="doubleSpeed()"
                  top
                  outlined
                  right
                  style="top:58%;left:1.5%"
                >
                  <v-icon>mdi-update</v-icon>
                </v-btn>
              </v-flex>
              <v-spacer></v-spacer>
              <v-flex style="padding-top:12px!important;" xs3>
                <!-- we need to change height if search bar not showing -->
                <v-card
                  style="overflow-x:hidden!important; overflow-y:auto!important;border-radius:6px!important;"
                  color="rgb(255, 255, 255, 0.9)"
                >
                  <v-container
                    fluid
                    grid-list-lg
                    style="padding-left:0px!important;padding-right:0px!important;padding-bottom:0!important;"
                  >
                    <center>
                      <br />
                      <h2 v-if="showAll">{{detection.plateContent}}</h2>
                      <h3
                        v-if="showAll"
                      >{{detection.vyear}} {{detection.vmake}} {{detection.vmodel}}</h3>
                      <h2 v-if="showAll">{{detection.street}} {{detection.city}}</h2>
                      <h3 v-if="showAll">{{detection.ts|moment("dddd, MMMM Do | h:mmA")}}</h3>
                      <h1
                        style="padding-top:64px!important;"
                        class="display-4"
                      >{{currentDrive.speed}}</h1>
                    </center>
                    <v-layout row wrap>
                      <v-flex xs3>
                        <center>
                          <h2 style="margin-top:-32px!important;color:gray">
                            P R N
                            <span style="color:black;">D</span>
                          </h2>
                        </center>
                      </v-flex>
                      <v-flex xs6>
                        <center>
                          <h2 style="margin-top:-32px!important;">MPH</h2>
                        </center>
                      </v-flex>
                      <v-flex xs3></v-flex>
                      <v-flex xs6 style="padding-right:0px!important;">
                        <v-progress-linear
                          background-color="green"
                          rounded
                          height="4"
                          class="negPower"
                          style="background:rgba(0, 0, 0, 0.17);"
                          :buffer-value="currentDrive.negPower"
                        ></v-progress-linear>
                      </v-flex>
                      <v-flex xs6 style="padding-left:0px!important;">
                        <v-progress-linear
                          :buffer-value="currentDrive.posPower"
                          background-color="black"
                          style="background:rgba(0, 0, 0, 0.17);"
                          rounded
                          height="4"
                        ></v-progress-linear>
                      </v-flex>
                    </v-layout>
                  </v-container>
                </v-card>
              </v-flex>
            </v-layout>
          </v-container>
        </v-flex>
        <v-flex xs6 style="bottom:0px!important;margin-top: -184px!important;">
          <v-layout row wrap>
            <v-flex xs4>
              <video
                style="width:100%!important;"
                muted
                :src="grabVideo(detection.videoFileName,'left',detection.secondsIntoVideo)"
                type="video/mp4"
              ></video>
            </v-flex>
            <v-flex xs4>
              <video
                style="width:100%!important;"
                muted
                :src="grabVideo(detection.videoFileName,'middle',detection.secondsIntoVideo)"
                type="video/mp4"
              ></video>
            </v-flex>
            <v-flex xs4>
              <video
                style="width:100%!important;"
                muted
                :src="grabVideo(detection.videoFileName,'right',detection.secondsIntoVideo)"
                type="video/mp4"
              ></video>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import { Icon, LatLng } from "leaflet";

import iconUrl from "leaflet/dist/images/marker-icon.png";


import PlateService from "../service/PlateService.js";
import FaceService from "../service/FaceService.js";
import PollService from "../service/PollService.js";
import DriveService from "../service/DriveService.js";
import Vue2LeafletRotatedMarker from "vue2-leaflet-rotatedmarker";
import Vue2LeafletMarkerCluster from "vue2-leaflet-markercluster";
import L from "leaflet";
import {
  LMap,
  LTileLayer,
  LIconDefault,
  LPopup,
  LMarker,
  LIcon
} from "vue2-leaflet";
import LMovingMarker from "../Vue2LeafletMovingMarker";



import { icon, latLngBounds } from "leaflet";

function rand(n) {
  let max = n + 0.1;
  let min = n - 0.1;
  return Math.random() * (max - min) + min;
}
export default {

  components: {
    "v-marker": LMarker,

    "v-rotated-marker": Vue2LeafletRotatedMarker,
    LMap,
    LTileLayer,
    LIconDefault,
    LPopup,
    LMovingMarker,
    location
  },
  name: "TesMap",

  data: () => ({
    nextFrame: null,
    detection: {},
    leftVideo: "",
    rightVideo: "",
    middleVideo: "",
    twoSpeed: false,
    currentFrame: 0,
    stepDuration: 1000,
    icon2: new Icon({ iconUrl }),
    icon1: new Icon({
      iconSize: [50, 50],
      iconAnchor: [25, 25],
      iconUrl: require(`../assets/arrow_rounded_reg.png`),
      iconRetinaUrl: require(`../assets/arrow_rounded.png`)
    }),
    currentDrive: {
      frame: 0,
      latlng: L.latLng(33.693684, -117.852491),
      heading: 219,
      speed: null,
      duration: 1000,
      power: 0,
      negPower: 0,
      posPower: 0,
      gear: null
    },
    movelocations: [],

    allDrives: [],
    nameSet: false,
    doIKnow: null,

    clusterOptions: {},

    negPower: 10,
    posPower: 0,
    currentSpeed: 46,
    showVideo: false,
    configKonva: {
      width: 200,
      height: 200
    },
    configCircle: {
      x: 100,
      y: 100,
      radius: 70,
      fill: "rgba(0,255,0,0.0)",
      stroke: "black",
      strokeWidth: 4
    },
    vidName: "",
    sheet: false,
    singleEvent: {},
    showAll: true,
    showPolyLine: false,
    search: "",
    faceIcon: L.icon({
      iconUrl: "../assets/face_icon.png",
      iconSize: [56, 71],
      iconAnchor: [28, 70]
    }),
    faceLightIcon: L.icon({
      iconUrl: "../assets/face_icon.png",
      iconSize: [56, 71],
      iconAnchor: [28, 70]
    }),
    detected: [],
    clipDetails: [],

    model: null,
    isLoading: false,

    plates: [],
    randomFaces: [],
    randomPlates: [],
    drives: [],
    drives2: [],
    locations: [],
    test: "",
    polyline: {
      latlngs: [],
      color: "green"
    },
    dateRanges: [
      "Last 12 Hours",
      "Last 24 Hours",
      "Last 7 Days",
      "Last 30 Days"
    ],
    showVid: false,

    petHidden: false,
    similarImages: [],
    notTesting: false,
    faceHidden: false,
    plateHidden: false,
    showSearch: true,
    currentInfo: {},
    showInfo: false,
    //plates: [],
    polls: [],
    faces: [],
    zoom: 16,
    center: L.latLng(33.695898, -117.740997),
    
    url:
      "https://api.mapbox.com/styles/v1/tev43478638w46/cjtsk7iaj1oll1fnz5gxgd1dh/tiles/256/{z}/{x}/{y}?access_token=CHANGEME(MapBoxAccessToken)",
    /
    attribution:
      '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',

    currentZoom: 9,
    currentCenter: L.latLng(33.695898, -117.740997),
    showParagraph: false,
    mapOptions: {
      zoomSnap: 1,
      bounds: null
    }
  }),
  beforeDestroy() {
    clearInterval(this.nextFrame);
  },
  async created() {
    var vm = this;
    if (vm.$route.params.detection) {
      console.log(
        `should be replaying detection ${vm.$route.params.detection._id}`
      );
      vm.detection = vm.$route.params.detection;
      vm.currentDrive.latlng = L.latLng(
        vm.detection.location.coordinates[1],
        vm.detection.location.coordinates[0]
      );
      vm.currentDrive.rotationAngle = vm.detection.heading;

      console.log(`detection occured at:${vm.detection.ts}`);
      console.log(`detection pollID is:${vm.detection.pollID}`);

      //drive data
      vm.allDrives.push(await PollService.getDrivePolls(vm.detection.driveID));

      console.log(`this.allDrives is now:${vm.allDrives}`);
      var pollTSs = vm.allDrives[0].map(function(item) {
        return item["_id"];
      });
      console.log(pollTSs);

      console.log(
        `index of the matching poll is ${pollTSs.indexOf(vm.detection.pollID)}`
      );
      vm.currentDrive.frame = pollTSs.indexOf(vm.detection.pollID) - 3;
      vm.currentDrive.duration = 1000;
      console.log(vm.allDrives);
    }

    function startPlaying() {
      // Get all videos.
      var videos = document.querySelectorAll("video");

      // Create a promise to wait all videos to be loaded at the same time.
      // When all of the videos are ready, call resolve().
      var promise = new Promise(function(resolve) {
        
        resolve();
      });

      // Play all videos one by one only when all videos are ready to be played.
      promise.then(function() {
        videos.forEach(function(v) {
          
          v.play();
        });
      });
    }

    setTimeout(() => startPlaying(), 3000);

    var vm = this;
    vm.currentDrive.heading = 219;
    this.moveMarker(this.currentFrame);

    
  },
  directives: {
    insertBox(canvasElement, binding) {
      var ctx = canvasElement.getContext("2d");
      var image = new Image();
      
      var img = document.getElementById("tesimg");

      image.onload = () => {
        ctx.drawImage(image, 0, 0);

        ctx.beginPath();
        ctx.rect(50, 50, 100, 100);
        ctx.lineWidth = 2;
        ctx.strokeStyle = "yellow";
        ctx.stroke();
      };
    }
  },
  methods: {
    grabVideo(filePreName, location, secondsIn) {

      String.prototype.rsplit = function(sep, maxsplit) {
        var split = this.split(sep);
        return maxsplit
          ? [split.slice(0, -maxsplit).join(sep)].concat(split.slice(-maxsplit))
          : split;
      };
      var videoAgnostic = filePreName
        .rsplit("-", 1)[0]
        .split("/")
        .pop();
      console.log(videoAgnostic);

      switch (location) {
        case "left":
          return `https://10.6.6.13/video/${videoAgnostic}-left_repeater.mp4#t=${
            secondsIn - 3 < 0 ? 0 : secondsIn - 3
          }`;
          break;
        case "middle":
          return `https://10.6.6.13/video/${videoAgnostic}-front.mp4#t=${
            secondsIn - 3 < 0 ? 0 : secondsIn - 3
          }`;
          break;
        case "right":
          return `https://10.6.6.13/video/${videoAgnostic}-right_repeater.mp4#t=${
            secondsIn - 3 < 0 ? 0 : secondsIn - 3
          }`;
          break;
        default:
          break;
      }
    },

    doubleSpeed() {
      var videos = document.querySelectorAll("video");
      videos.forEach(function(v) {
        v.currentTime += 10;
      });
      this.currentDrive.frame += 10;

    },

    moveMarker(currentFrame) {
      var vm = this;

      this.nextFrame = setInterval(() => {
        
        console.log(`my stepDuration is:${vm.stepDuration}`);

        var newHeading = this.allDrives[0][this.currentDrive.frame].heading;
        this.currentDrive.heading = newHeading;
        console.log(this.currentDrive.heading);
        var newSpeed = this.allDrives[0][this.currentDrive.frame].speed;
        var newGear = this.allDrives[0][this.currentDrive.frame].status;
        this.currentDrive.gear = newGear;

        this.currentDrive.speed = newSpeed;
        console.log(this.currentDrive.speed);
        if (newSpeed === 0) {
          newSpeed = 1;
        } else if (newSpeed > 60) {
          newSpeed = 60;
        }
        var newDuration = 1000 * (60 / newSpeed);
        this.currentDrive.duration = newDuration;
        console.log(this.currentDrive.duration);

        var newPower = this.allDrives[0][this.currentDrive.frame].power;
        this.currentDrive.power = newPower;

        if (newPower > 0) {
          vm.currentDrive.negPower = 0;
          //   vm.currentDrive.posPower = newPower;
          vm.currentDrive.posPower = newPower;
        } else if (newPower < 0) {
          vm.currentDrive.negPower = -1 * newPower;
          vm.currentDrive.posPower = 0;
        } else {
          vm.currentDrive.negPower = 0;
          vm.currentDrive.posPower = 0;
        }

        var newCoord = L.latLng(
          this.allDrives[0][this.currentDrive.frame].location.coordinates[1],
          this.allDrives[0][this.currentDrive.frame].location.coordinates[0]
        );
        this.currentDrive.latlng = newCoord;
        console.log(newCoord);

        this.currentDrive.frame++;
        console.log(this.currentDrive.frame);
      }, this.stepDuration);
    },

    randomColor() {
      const r = () => Math.floor(256 * Math.random());

      return `rgb(${r()}, ${r()}, ${r()})`;
    },
    parseDrives(drive) {
      var prettyDrive = [];
      drive.forEach(drivePoll => {
        var newArray = [
          drivePoll.location.coordinates[1],
          drivePoll.location.coordinates[0]
        ];
        prettyDrive.push(newArray);
      });
      return prettyDrive;
    },

    addedName() {
      this.backToAll();
      this.detected.forEach(event => {
TEMP
      });
      this.nameSet = true;
    },
    logCoords(coords) {
      console.log(`[${coords[0]},${coords[1]}],`);

    },
    resetImg() {
      var vm = this;
      if (vm.singleEvent.ogImg) {
        vm.singleEvent.imgUrl = vm.singleEvent.ogImg;
      }
    },
    previewImg(imgUrl) {
      var vm = this;
      console.log("mouseover");

      if (!vm.singleEvent.ogImg) {
        vm.singleEvent.ogImg = vm.singleEvent.imgUrl;
      }

      vm.singleEvent.imgUrl = imgUrl;
    },
    vidPlaying() {
      var vm = this;
      var vid = document.getElementById("singleVideo");
      vid.ontimeupdate = function() {
        myFunction();
      };

      function myFunction() {
        
        var theSecond = parseInt(vid.currentTime);
        console.log(`current time:${theSecond}`);
        var currentSpec = vm.clipDetails[theSecond];
        vm.currentSpeed = currentSpec.speed;
        if (currentSpec.power > 0) {
          vm.negPower = 0;
          vm.posPower = currentSpec.power;
        } else if (currentSpec.power < 0) {
          vm.negPower = -1 * currentSpec.power;
          vm.posPower = 0;
        } else {
          vm.negPower = 0;
          vm.posPower = 0;
        }
      }

      function myFunction2() {
        var theSecond = parseInt(vid.currentTime);
        var newHeading = this.allDrives[0][theSecond].heading;
        this.currentDrive.heading = newHeading;
        console.log(this.currentDrive.heading);
        var newSpeed = this.allDrives[0][theSecond].speed;
        var newGear = this.allDrives[0][theSecond].status;
        this.currentDrive.gear = newGear;

        this.currentDrive.speed = newSpeed;
        console.log(this.currentDrive.speed);
        if (newSpeed === 0) {
          newSpeed = 1;
        } else if (newSpeed > 60) {
          newSpeed = 60;
        }
        var newDuration = 1000 * (60 / newSpeed);
        this.currentDrive.duration = newDuration;
        console.log(this.currentDrive.duration);

        var newPower = this.allDrives[0][theSecond].power;
        this.currentDrive.power = newPower;

        if (newPower > 0) {
          vm.currentDrive.negPower = 0;
          vm.currentDrive.posPower = newPower;
        } else if (newPower < 0) {
          vm.currentDrive.negPower = -1 * newPower;
          vm.currentDrive.posPower = 0;
        } else {
          vm.currentDrive.negPower = 0;
          vm.currentDrive.posPower = 0;
        }

        var newCoord = L.latLng(
          this.allDrives[0][theSecond].location.coordinates[1],
          this.allDrives[0][theSecond].location.coordinates[0]
        );
        this.currentDrive.latlng = newCoord;
        console.log(newCoord);

        this.currentDrive.frame++;
        console.log(theSecond);
      }
    },
    showWholeTrip(event) {
      var vm = this;
      vm.showVideo = false;


      const bounds = latLngBounds(this.drives2);

      
      this.$refs.myMap.mapObject.flyToBounds(bounds, 15);
      this.negPower = 0;
      this.posPower = 45;
    },
    tryVideo(event) {
      var vm = this;
      if (event.vidUrl) {
        vm.vidName = event.vidUrl;
      }
      this.showVideo = true;
      var newcoord = event.coords[1] + 0.015;
      this.$refs.myMap.mapObject.flyTo(L.latLng(newcoord, event.coords[0]), 15);
    },
    toNewFace(id) {
      
    },
    
    playVid() {
      this.showVideo = true;
    },
    honkboi() {
      FaceService.getFaces();
    },
    zoomUpdate(zoom) {
      this.currentZoom = zoom;
    },
    moveCenter(center) {
      // mapObject.flyTo(L.latLng(center[0], center[1]));
      this.singleEvent = center;
      //centers the marker
      this.$refs.myMap.mapObject.flyTo(
        L.latLng(center.coords[1], center.coords[0]),
        15
      );

      

      const bounds = latLngBounds(this.drives2);

      

      this.showAll = false;
      this.detected.forEach(event => {
        event.showSingle = false;
      });
      center.showSingle = true;
      if (this.singleEvent.type === "plate") {
        this.showPolyLine = true;
      }
    },
    centerUpdate(center) {
      console.log("center update");
      console.log(this.currentCenter);

      this.currentCenter = center;
      console.log(this.currentCenter);
    },
    maxCard(id) {
      this.centerUpdate(
        L.latLng(this.plates[id].coords[1], this.plates[id].coords[0])
      );
    },
    showLongText() {
      this.showParagraph = !this.showParagraph;
    },
    innerClick(plate) {
      this.currentInfo = plate;
      // this.showSearch = false;
      this.showInfo = true;
      // alert("Click!");
    },
    backToAll() {
      this.showAll = true;
      this.showVideo = false;
      this.showPolyLine = false;
    },
    popClosed() {
      console.log("popClosed");

      var vm = this;
      vm.showInfo = false;
      vm.showVideo = false;
      vm.currentInfo = {};
    }
  },
  computed: {
    filteredList() {
      return this.detected.filter(event => {
        return (
          event.title.toLowerCase().includes(this.search.toLowerCase()) ||
          event.makeModel.toLowerCase().includes(this.search.toLowerCase())
        );
      });
    },
    dynamicSize() {
      return [this.iconSize, this.iconSize * 1.15];
    },
    dynamicAnchor() {
      return [this.iconSize / 2, this.iconSize * 1.15];
    }
  },
  mounted() {
    setInterval(() => {
      var vm = this;
      var newPlates = [];
      
    }, 100);
    this.$nextTick(() => {
      
      this.$refs.movingMarkerRef.slideTo();
      this.$refs.myMap.mapObject.flyTo();
      this.$refs.myMap.mapObject.slideTo();
      this.$refs.myMap.mapObject.getBounds();
      this.clusterOptions = { disableClusteringAtZoom: 16 };
    });
  }
  
};
</script>

<style>
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";

.singleClassFace {
  height: calc(100vh - 220px);
}
.singleClassNamedFace {
  height: calc(100vh - 365px);
}
.singleClassPlate {
  height: calc(100vh - 405px);
}
.searchClass {
  height: calc(100vh - 200px);
}
.sub {
  font-size: 18px;
}
.v-input--selection-controls.v-input .v-label {
  padding-top: 10px !important;
}

.v-input--selection-controls {
  /* margin-top:-16px!important; */
}
.v-text-field input {
  margin-top: 12px !important;
  font-size: 18px !important;
}
input {
  line-height: 44px !important;
  font-size: 18px !important;
}
.v-label {
  line-height: 35px !important;
  font-size: 18px !important;
}
.v-select__selection--comma,
.v-select__selection {
  margin-bottom: 0 !important;
}
body,
p,
h1,
h2,
h3,
h4,
h5,
h6 {
  text-rendering: optimizeSpeed;
}

body {
  font-family: Gotham, sans-serif;
}

h1 {
  font-weight: 700;
}

.v-list__tile__title {
  text-align: center !important;
}

.leaflet-control-zoom {
  display: none !important;
}

.leaflet-popup-content {
  width: auto !important;
}
.roundCard {
  border-radius: 8px !important;
  background-color: rgba(255, 255, 255, 0.75) !important;
}

.roundCard .v-input__slot {
  border-radius: 8px !important;
  background-color: rgba(255, 255, 255, 0.85) !important;
}

.roundCard2,
.v-menu__content {
  border-radius: 8px !important;
  /* background-color: rgba(255, 255, 255, 0.75) !important; */
}

.roundCard2 .v-input__slot {
  border-radius: 8px !important;
  /* background-color: rgba(255, 255, 255, 0.85) !important; */
}

.clearBack {
  border-radius: 8px !important;
  background-color: rgba(255, 255, 255, 0) !important;
}
</style>
<style scoped>
@media only screen and (min-width: 1904px) {
  .container {
    max-width: 1985px;
  }
}

.negPower {
  transform: rotate(180deg);
}
</style>
<style scoped>
.halfHeightMap {
  min-height: 64% !important;
  min-width: 1024px !important;

  /* Set up proportionate scaling */
  width: 100% !important;
  height: auto !important;

  /* Set up positioning */
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
}
</style>



