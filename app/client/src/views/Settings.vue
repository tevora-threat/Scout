<template>
  <v-container>
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
          <v-flex xs12>
            <v-layout row wrap>
              <v-flex xs3>All Detected Plates</v-flex>
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
                <v-layout justify-center>
                  <v-dialog v-model="teslaToken" persistent max-width="600">
                    <v-card>
                      <v-toolbar color="red darken-1" dark>
                        <v-toolbar-title style="padding-top:20px!important;">
                          <h1 style="padding-top: 8px!important;">Tesla Token Refresh</h1>
                        </v-toolbar-title>
                        <v-spacer></v-spacer>

                        <v-btn @click="teslaToken = false" flat>CLOSE</v-btn>
                      </v-toolbar>
                      <v-card-title class>
                        <h5
                          style="padding-top:4px!important;"
                        >Request a new token below using your Tesla account credentials. These will not be stored.</h5>
                      </v-card-title>
                      <v-container>
                        <v-layout row wrap justify-space-around>
                          <v-flex xs5>
                            <v-text-field
                              style="margin-top: 12px!important;"
                              solo
                              label="Email Address"
                              v-model="tempEmail"
                            ></v-text-field>
                          </v-flex>
                          <v-flex xs5>
                            <v-text-field
                              style="margin-top: 12px!important;"
                              solo
                              type="password"
                              label="Password"
                              v-model="tempPass"
                            ></v-text-field>
                          </v-flex>
                          <v-flex xs4></v-flex>
                          <v-flex xs4>
                            <v-btn
                              style="line-height: 44px;margin-top:12px;height:46px!important;"
                              round
                              color="red darken-1"
                              dark
                              @click="loginRefresh(tempEmail,tempPassword)"
                            >
                              <span style="margin-top:6px!important;">Refresh Token</span>
                            </v-btn>
                          </v-flex>
                          <v-flex xs4></v-flex>
                        </v-layout>
                      </v-container>
                      <center></center>
                    </v-card>
                  </v-dialog>
                </v-layout>
                <v-card-title>
                  <h1>Settings</h1>

                  <v-spacer></v-spacer>
                </v-card-title>
                <v-navigation-drawer v-model="drawer" permanent absolute>
                  <v-toolbar flat class="transparent">
                    <v-list class="pa-0">
                      <v-list-item>
                        <v-list-item-content>
                          <v-list-item-title style="height: 30px; line-height: 40px;">
                            <h1 style="text-align:left!important;">Settings</h1>
                          </v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                  </v-toolbar>

                  <v-list class="pt-0" dense>
                    <v-divider></v-divider>

                    <v-list-item
                      v-for="item in navItems"
                      :key="item.title"
                      v-bind:class="{ activeClass: item.active }"
                      @click="activeItem(item.title)"
                    >
                      <v-list-item-action>
                        <v-icon v-if="item.active" style="color:black;">{{ item.icon }}</v-icon>
                        <v-icon v-else>{{ item.icon }}</v-icon>
                      </v-list-item-action>

                      <v-list-item-content>
                        <v-list-item-title style="height: 30px; line-height: 40px;">
                          <h2 v-if="item.active" style="text-align:left!important;">{{ item.title }}</h2>
                          <h2
                            v-else
                            style="text-align:left!important;color:rgba(0,0,0,0.54);"
                          >{{ item.title }}</h2>
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-navigation-drawer>
                <v-layout row wrap>
                  <v-flex xs2 style="max-width:13.667%!important"></v-flex>
                  <v-flex
                    xs10
                    style="margin-top:-98px!important;height:100%!important;margin-left: -18px; padding-top:28px!important; padding-left: 22px;background-color:rgba(0, 0, 0, 0.04)"
                  >
                    <h2>Detection</h2>
                    <h3>Choose what is most important- speed of inference, or quality of detection? Scout can detect more plates, but it will take longer.</h3>
                    <h3>Choose what you would like the threshold to be for a notification of being followed or familiar face detected</h3>
                    <v-slider
                      v-model="fruits"
                      :tick-labels="ticksLabels"
                      :max="2"
                      step="1"
                      ticks="always"
                      tick-size="3"
                    ></v-slider>
                    <h3>Choose what you would like the threshold to be for a notification of being followed or familiar face detected</h3>

                    <v-layout row wrap>
                      <v-flex
                        xs12
                      >we need to have an inline checkbox, label and text field in this section to allow them to enable the alert type as well as edit the frequency for the specific alert</v-flex>
                      <v-flex xs6>X detections in a single drive</v-flex>
                      <v-flex xs6>X detections in x hours</v-flex>
                      <v-flex xs6>X detections in x days</v-flex>
                      <v-flex xs6>X detections total</v-flex>
                      <v-flex xs12>In-bound, then out-of-bound detection</v-flex>
                    </v-layout>

                    <v-layout row wrap>
                      <v-flex xs6>
                        <h3>Make/Model Detection</h3>
                        <v-autocomplete
                          v-model="settings.homestate"
                          :items="states"
                          flat
                          hide-no-data
                          hide-details
                          label="Home State"
                          solo-inverted
                        ></v-autocomplete>
                      </v-flex>
                      <v-flex xs6>
                        <h3>Out of Bounds Alerts</h3>
                        <v-text-field
                          style="margin-top: 12px!important;"
                          solo
                          label="Home Zip Code"
                          v-model="settings.homezip"
                        ></v-text-field>
                      </v-flex>
                    </v-layout>

                    <h2>Integrations</h2>
                    <h3>Tesla Auth</h3>
                    <v-layout row wrap>
                      <v-flex xs6>
                        <v-text-field
                          style="margin-top: 12px!important;"
                          solo
                          label="Detection Task Name"
                          v-model="settings.tesla.token"
                        ></v-text-field>
                      </v-flex>
                      <v-flex xs2>
                        <v-btn
                          style="line-height: 44px;margin-top:12px;height:46px!important;"
                          round
                          color="primary"
                          dark
                          @click="refreshToken()"
                        >
                          <span style="margin-top:6px!important;">Refresh Token</span>
                        </v-btn>
                      </v-flex>
                    </v-layout>
                    <h3>IFTTT</h3>
                    <v-layout row wrap>
                      <v-flex xs6>
                        <v-text-field
                          style="margin-top: 12px!important;"
                          solo
                          label="Detection Task Name"
                          v-model="settings.ifttt.taskname"
                        ></v-text-field>
                      </v-flex>
                      <v-flex xs6>
                        <v-text-field
                          style="margin-top: 12px!important;"
                          solo
                          label="API Key"
                          v-model="settings.ifttt.apikey"
                        ></v-text-field>
                      </v-flex>
                    </v-layout>
                    <h2>Network</h2>
                    <v-layout row wrap>
                      <v-flex xs6>
                        <h3>Mobile Hotspot</h3>
                        <v-layout row wrap>
                          <v-flex xs6>
                            <v-text-field
                              append-inner-text="testing"
                              style="margin-top: 12px!important;"
                              solo
                              label="SSID"
                              v-model="settings.hotspot.ssid"
                            ></v-text-field>
                          </v-flex>
                          <v-flex xs6>
                            <v-text-field
                              style="margin-top: 12px!important;"
                              solo
                              type="password"
                              label="Password"
                              v-model="settings.hotspot.password"
                            ></v-text-field>
                          </v-flex>
                        </v-layout>
                      </v-flex>
                      <v-flex xs6>
                        <h3>Home Network</h3>
                        <v-layout row wrap>
                          <v-flex xs6>
                            <v-text-field
                              style="margin-top: 12px!important;"
                              solo
                              label="SSID"
                              v-model="settings.homenetwork.ssid"
                            ></v-text-field>
                          </v-flex>
                          <v-flex xs6>
                            <v-text-field
                              style="margin-top: 12px!important;"
                              solo
                              type="password"
                              label="Password"
                              v-model="settings.homenetwork.password"
                            ></v-text-field>
                          </v-flex>
                        </v-layout>
                      </v-flex>
                    </v-layout>

                    <center>
                      <v-btn
                        style="line-height: 44px;margin-top:12px;height:46px!important;"
                        round
                        color="primary"
                        dark
                        @click="refreshToken()"
                      >
                        <span style="margin-top:6px!important;">Save Settings</span>
                      </v-btn>
                    </center>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-card>
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>
                   
                    
                  

<script>
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
  name: "TesMap",

  data: () => ({
    teslaToken: false,
    settings: {
      alerts: {
        singleDrive: { enabled: true }
      },
      homestate: "California",
      hotspot: { ssid: "iPhonewifi", password: "changeme" },
      homenetwork: { ssid: null, password: null },
      ifttt: { taskname: "detection", apikey: "ssdo8vsa9wwwkvchci99w" },
      tesla: { token: "sdslkda9wwifghsi" }
    },
    stateChosen: null,
    states: [
      "Alabama",
      "Alaska",
      "American Samoa",
      "Arizona",
      "Arkansas",
      "California",
      "Colorado",
      "Connecticut",
      "Delaware",
      "District of Columbia",
      "Federated States of Micronesia",
      "Florida",
      "Georgia",
      "Guam",
      "Hawaii",
      "Idaho",
      "Illinois",
      "Indiana",
      "Iowa",
      "Kansas",
      "Kentucky",
      "Louisiana",
      "Maine",
      "Marshall Islands",
      "Maryland",
      "Massachusetts",
      "Michigan",
      "Minnesota",
      "Mississippi",
      "Missouri",
      "Montana",
      "Nebraska",
      "Nevada",
      "New Hampshire",
      "New Jersey",
      "New Mexico",
      "New York",
      "North Carolina",
      "North Dakota",
      "Northern Mariana Islands",
      "Ohio",
      "Oklahoma",
      "Oregon",
      "Palau",
      "Pennsylvania",
      "Puerto Rico",
      "Rhode Island",
      "South Carolina",
      "South Dakota",
      "Tennessee",
      "Texas",
      "Utah",
      "Vermont",
      "Virgin Island",
      "Virginia",
      "Washington",
      "West Virginia",
      "Wisconsin",
      "Wyoming"
    ],
    fruits: 0,
    ticksLabels: [
      "Quickest Notification of Obvious Follow Vehicles",
      "An Even Distribution",
      "More Plate Readings, No Hurry"
    ],

    tempSwitch: false,
    drawer: true,
    navItems: [
      { title: "Detection", icon: "remove_red_eye", active: true },
      { title: "Integrations", icon: "mdi-puzzle-outline", active: false },
      { title: "Network", icon: "mdi-wifi", active: false },
      { title: "Storage", icon: "mdi-nas", active: false },
      { title: "Hardware", icon: "mdi-smoke-detector", active: false },
      { title: "Temperature", icon: "mdi-oil-temperature", active: false },
      { title: "Help", icon: "mdi-help-circle-outline", active: false }
    ],
    nameSet: false,
    doIKnow: null,

    clusterOptions: {},
    headers: [
      {
        text: "Plate",
        align: "left",
        sortable: false,
        value: "plate"
      },
      { text: "Year", value: "year" },
      { text: "Make", value: "make" },
      { text: "Model", value: "model" },
      { text: "#/Detections", value: "numDetections" },
      { text: "First Seen", value: "firstSeen" },
      { text: "Last Seen", value: "lastSeen" },
      { text: "Status", value: "status" }
    ],
    platesDetected: [],
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
    pipers: [],
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
    dateRanges: [],
    showVid: false,

    petHidden: false,
    similarImages: [
      {
        isSame: false,
        imgUrl: "",
        id: 2
      }
    ],
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
      this.faces = await FaceService.getFaces();
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
  methods: {
    refreshToken() {
      this.teslaToken = true;
    },
    activeItem(item) {
      console.log(`new active item:${item}`);

      var vm = this;
      vm.navItems.forEach(oneitem => {
        if (oneitem.title != item) {
          oneitem.active = false;
        } else {
          oneitem.active = true;
        }
      });
      console.log(`allitems:${vm.navItems}`);
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
.activeClass {
  background-color: rgba(0, 0, 0, 0.04) !important;
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

