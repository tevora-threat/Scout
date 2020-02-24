<template>
  <v-container>
    <v-layout justify-center></v-layout>
    <v-layout v-if="!notTesting">
      <v-flex xs12>
        <l-map
          :zoom="zoom"
          ref="myMap"
          :center="center"
          :options="mapOptions"
          style="height: 100%!important;"
          @update:center="centerUpdate"
          @update:zoom="zoomUpdate"
          class="mapBoi"
        >
          <l-tile-layer :url="url" :attribution="attribution" />
        </l-map>

        <v-layout row wrap>
          <v-btn
            v-if="!showAll"
            color="red darken-1"
            fab
            dark
            absolute
            @click="backToAll"
            top
            outlined
            right
            style="top:10%;"
          >
            <v-icon>close</v-icon>
          </v-btn>

          <!-- start of structure -->
          <v-flex xs12 style="padding-left:24px!important;padding-right:24px!important;">
            <v-layout row wrap>
              <v-flex xs3>All Detected Faces</v-flex>
              <v-flex xs6></v-flex>
            </v-layout>

            <!-- we need to change height if search bar not showing -->
            <v-card
              v-bind:class="{singleClassFace:(!showAll&&singleEvent.type==='face'),singleClassPlate:(!showAll&&singleEvent.type==='plate'),searchClass:showAll}"
              style="overflow-x:hidden!important; overflow-y:auto!important;border-radius:6px!important;"
              color="rgb(255, 255, 255, 0.9)"
            >
              <v-container
                fluid
                grid-list-lg
                style="padding-left:0px!important;padding-right:0px!important;padding-bottom:0!important;"
              >
                <v-card-title>
                  <h1>All Detected Faces</h1>

                  <v-spacer></v-spacer>
                  <v-text-field
                    v-model="search"
                    append-icon="search"
                    label="Search"
                    single-line
                    hide-details
                  ></v-text-field>
                </v-card-title>

                <v-data-table
                  style="font-size:20px!important;"
                  :headers="headers"
                  :footer-props="{
    'items-per-page-options': [10, 20, 30, 40, 50]
  }"
                  :items-per-page="30"
                  :items="faces"
                  :sort-by="['numDetections']"
                  sort-desc
                  :search="search"
                >
                  <template v-slot:item.personName="{ item }">
                    <h4 @click="clickedRecent(item)">{{item.personName}}</h4>
                  </template>
                  <template
                    v-slot:item.firstSeen="{ item }"
                  >{{item.firstSeen | moment("dddd, MMMM D YYYY hh:mm a")}}</template>
                  <template
                    v-slot:item.lastSeen="{ item }"
                  >{{item.lastSeen | moment("dddd, MMMM D YYYY hh:mm a")}}</template>
                  <template v-slot:item.status="{ item }">
                    <h4
                      @click="clickedRecent(item)"
                      v-if="item.status==='High Risk'"
                      style="color:#cc0000"
                    >{{item.status}}</h4>
                    <h4 @click="clickedRecent(item)" v-else>{{item.status}}</h4>
                  </template>
                </v-data-table>
              </v-container>
            </v-card>
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import PlateService from "../service/PlateService.js";
import FaceService from "../service/FaceService.js";
import PollService from "../service/PollService.js";
import Vue2LeafletRotatedMarker from "vue2-leaflet-rotatedmarker";
import Vue2LeafletMarkerCluster from "vue2-leaflet-markercluster";

import LMovingMarker from "vue2-leaflet-movingmarker";

import {
  LMap,
  LTileLayer,
  LMarker,
  LPopup,
  LTooltip,
  LIcon
} from "vue2-leaflet";
import { icon, latLngBounds } from "leaflet";

function rand(n) {
  let max = n + 0.1;
  let min = n - 0.1;
  return Math.random() * (max - min) + min;
}
export default {
  components: {
    "l-rotated-marker": Vue2LeafletRotatedMarker,
    "l-moving-marker": LMovingMarker,
    "l-marker": LMarker,
    "l-popup": LPopup,
    "l-icon": LIcon,
    "v-marker-cluster": Vue2LeafletMarkerCluster
  },
  name: "AllFaces",

  data: () => ({
    faceDetections: [],
    persons: {},
    oldLength: 0,
    dialog: false,
    nameSet: false,
    doIKnow: null,

    clusterOptions: {},
    headers: [
      {
        text: "Name",
        align: "left",
        sortable: false,
        value: "personName"
      },
      { text: "Age", value: "age" },
      { text: "Gender", value: "gender" },
      { text: "#/Detections", value: "numDetections", align: "left" },
      { text: "First Seen", value: "firstSeen" },
      { text: "Last Seen", value: "lastSeen" },
      { text: "Status", value: "status" }
    ],
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
    polls: [],
    faces: [],
    zoom: 13,
    center: L.latLng(33.695898, -117.740997),
    url:
      "https://api.mapbox.com/styles/v1/tev43478638w46/cjtsk7iaj1oll1fnz5gxgd1dh/tiles/256/{z}/{x}/{y}?access_token=CHANGEME(MapBoxAccessToken)",
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
  async created() {
    try {
      console.log("pollservicetry");
      this.polls = await PollService.getPolls();
      var drives = [];
      var newDrive = [];
      console.log(drives);
    } catch (err) {
      this.error = err.message;
      console.log(err.message);
    }
    try {
      console.log("plateservicetry");

      this.plates = await PlateService.getPlates();

      this.plates.forEach(plate => {
        console.log(plate);
      });
    } catch (err) {
      this.error = err.message;
    }
    try {
      console.log("get all face detections");

      this.faceDetections = await FaceService.getDetections();
      this.faceDetections.sort((a, b) => {
        if (a.ts === b.ts) {
          // If two elements have same number, then the one who has larger rating.average wins
          return b._id - a._id;
        } else {
          // If two elements have different number, then the one who has larger number wins
          return b.ts - a.ts;
        }
      });
    } catch (err) {
      this.error = err.message;
    }
    try {
      this.faces = await FaceService.getFaces();
      this.faces.forEach(face => {
        console.log(face);
        const faceIDs = [face._id];
        face.numDetections = this.faceDetections.filter(i =>
          faceIDs.includes(i.faceID)
        ).length;
        face.firstSeen = this.faceDetections.filter(i =>
          faceIDs.includes(i.faceID)
        )[face.numDetections - 1].ts;
        face.lastSeen = this.faceDetections.filter(i =>
          faceIDs.includes(i.faceID)
        )[0].ts;
        if (!face.gender) {
          face.gender = "-";
          face.age = "-";
          // plate.vmodel = '-'
        } else {
          console.log("gender:", face.gender);
        }
      });
      console.log(
        L.latLng(
          this.faces[0].location.coords[0],
          this.faces[0].location.coords[1]
        )
      );
    } catch (err) {
      this.error = err.message;
    }
    for (let i = 0; i < 40; i++) {
      this.randomFaces.push({
        id: i,
        latlng: L.latLng(CHANGEME), //CHANGEME
        text: "Hello " + i
      });
    }
    for (let i = 0; i < 200; i++) {
      this.randomPlates.push({
        id: i,
        latlng: L.latLng(CHANGEME), //CHANGEME
        text: "Hello " + i
      });
    }

    //
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

  watch: {},
  methods: {
    clickedRecent(item) {
      console.log(item);

      console.log("clicked one");

      var vm = this;
      vm.$router.push({
        name: "Recent",
        params: { search: item.personName, faceID: item._id }
      });
    },
    addedName() {
      this.backToAll();
      this.detected.forEach(event => {
        TEMP;
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
        // Display the current position of the video in a p element with id="demo"
        // document.getElementById("demo").innerHTML = vid.currentTime;
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
    toNewFace(id) {},
    handleMarkerClick(l) {
      l.yaw += 20;
      console.log(l.yaw);

      this.$refs.movingMarkerRef.mapObject.slideTo([20, 20], {
        duration: 2000,
        keepAtCenter: true
      });
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
      this.showInfo = true;
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
      this.$refs.myMap.mapObject.flyTo();
      this.$refs.myMap.mapObject.getBounds();
      this.clusterOptions = { disableClusteringAtZoom: 16 };
    });
  }
};
</script>

<style>
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";
table.v-table tbody td {
  font-size: 20px !important;
  padding-top: 14px !important;
}

th.column {
  font-size: 20px !important;
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
  font-family: Gotham, sans-serif !important;
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
td.text-left,
td.text-start {
  padding-top: 8px !important;
  font-size: 18px !important;
}

label.v-label,
.v-input .v-label {
  height: 42px !important;
}
@media only screen and (min-width: 1904px) {
  .container {
    max-width: 1985px;
  }
}

.negPower {
  transform: rotate(180deg);
}
</style>

