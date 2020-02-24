<template>
  <v-container>
    <v-layout v-if="!notTesting">
      <v-flex xs12>
        <l-map
          :zoom="zoom"
          ref="myMap"
          :center="center"
          :options="mapOptions"
          pitch="50"
          style="height: 100%!important;"
          @update:center="centerUpdate"
          @update:zoom="zoomUpdate"
          class="mapBoi"
        >
          <l-tile-layer v-if="satMap" :url="urlSAT" :attribution="attribution" />
          <l-tile-layer v-else :url="url" :attribution="attribution" />

          <template v-for="event in filteredList">
            <l-marker
              v-if="event.faceID"
              class="face"
              :lat-lng="[event.location.coordinates[1],event.location.coordinates[0]]"
            >
              <l-icon
                :icon-size="[56,71]"
                :icon-anchor="[28,70]"
                :icon-url="require(`../assets/face_icon.png`)"
              ></l-icon>
            </l-marker>
            <l-marker
              v-if="event.plateID"
              class="face"
              :lat-lng="[event.location.coordinates[1],event.location.coordinates[0]]"
            >
              <l-icon
                :icon-size="[56,71]"
                :icon-anchor="[28,70]"
                :icon-url="require(`../assets/car_icon.png`)"
              ></l-icon>
              <l-popup>
                <img width="600" :src="grabThumbVehicle(event.vehicleImgPath)" />
              </l-popup>
            </l-marker>
            <l-marker
              v-if="event.type==='face' && !faceHidden && (showAll||event.showSingle)"
              class="face"
              :lat-lng="[event.coords[1],event.coords[0]]"
            >
              <l-icon
                :icon-size="[56,71]"
                :icon-anchor="[28,70]"
                :icon-url="require(`../assets/face_icon.png`)"
              ></l-icon>
            </l-marker>
            <l-marker
              v-if="event.type==='plate' && !plateHidden && (showAll||event.showSingle)"
              class="face"
              :lat-lng="[event.coords[1],event.coords[0]]"
            >
              <l-icon
                :icon-size="[56,71]"
                :icon-anchor="[28,70]"
                :icon-url="require(`../assets/car_icon.png`)"
              ></l-icon>
              <l-popup>
                <img width="600" :src="`CHANGEME/${event.imgName}.png`" />
              </l-popup>
            </l-marker>
          </template>

          <template v-for="event in rangeEvents">
            <l-marker
              v-if="event.type==='plate' && !plateHidden && (showAll||event.showSingle)"
              class="face"
              :lat-lng="[event.coords[1],event.coords[0]]"
            >
              <l-icon
                :icon-size="[56,71]"
                :icon-anchor="[28,70]"
                :icon-url="require(`../assets/car_icon.png`)"
              ></l-icon>
              <l-popup>
                <img width="600" :src="require(`../assets/tescrop.png`)" />
              </l-popup>
            </l-marker>
          </template>

          <template v-for="event in randomFaces">
            <l-marker
              :key="event.id"
              v-if="!plateHidden && (showAll)"
              class="face"
              :lat-lng="event.latlng"
            >
              <l-icon
                :icon-size="[56,71]"
                :icon-anchor="[28,70]"
                :icon-url="require(`../assets/face_icon.png`)"
              ></l-icon>
              <l-popup>
                <img width="600" :src="require(`../assets/tescrop.png`)" />
              </l-popup>
            </l-marker>
          </template>

          <template v-if="showDrives">
            <l-polyline
              v-for="(drive, index) in allDrives"
              @click="printDriveID(drive[0].driveID)"
              :color="randomColor(index)"
              :key="drive[0]._id"
              :lat-lngs="parseDrives(drive)"
              weight="8"
            ></l-polyline>
          </template>
        </l-map>
      </v-flex>
    </v-layout>
  </v-container>
</template>




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
          <v-btn
            v-if="!satMap"
            color="grey darken-1"
            fab
            dark
            absolute
            @click="satMap = !satMap"
            top
            outlined
            right
            style="top:30%;"
          >
            <v-icon>mdi-google-earth</v-icon>
          </v-btn>
          <v-btn
            v-if="satMap"
            color="green darken-1"
            fab
            dark
            absolute
            @click="satMap = !satMap"
            top
            right
            style="top:30%;"
          >
            <v-icon>mdi-google-earth</v-icon>
          </v-btn>
          <v-btn
            v-if="faceHidden"
            color="green darken-1"
            fab
            dark
            absolute
            @click="faceHidden = !faceHidden"
            top
            outlined
            right
            style="top:50%;"
          >
            <v-icon>face</v-icon>
          </v-btn>
          <v-btn
            v-if="!faceHidden"
            color="purple darken-1"
            fab
            dark
            absolute
            @click="faceHidden = !faceHidden"
            top
            right
            style="top:50%;"
          >
            <v-icon>face</v-icon>
          </v-btn>
          
          <v-btn
            v-if="plateHidden"
            color="grey darken-1"
            fab
            @click="plateHidden = !plateHidden"
            dark
            absolute
            top
            outlined
            right
            style="top:60%;"
          >
            <img
              height="30px"
              src="data:image/png;base64,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"
              alt
            />
          </v-btn>
          <v-btn
            v-if="!plateHidden"
            color="red darken-2"
            fab
            @click="plateHidden = !plateHidden"
            dark
            absolute
            top
            right
            style="top:60%;"
          >
            <img
              height="30px"
              src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAATgAAAE5CAYAAAAEIzzPAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA4ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ1IDc5LjE2MzQ5OSwgMjAxOC8wOC8xMy0xNjo0MDoyMiAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo5OTQ5ZGRjZC02ZGE3LTRmZWYtYTNmMC0yMzZmMzdjNTg1MTciIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6M0U0RUNBRDU0QTUxMTFFOUE0RDhEQkU2RDJFMTkyMUUiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6M0U0RUNBRDQ0QTUxMTFFOUE0RDhEQkU2RDJFMTkyMUUiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTkgKE1hY2ludG9zaCkiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo0ODJkMjk0ZC03OTI0LTQ2ZTQtYTg4YS1mNzBkOGFlZTQ5MGQiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDpkMWIzZTg0Zi1lZTFhLWU5NGItOTg0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"
              alt
            />

          </v-btn>
       <span style="top:98%;right:4%;position:absolute;z-index:101;color:white;">&copy; 2019 Tevora</span>

          <img
          v-if="satMap"
          absolute
            top
            right
            class="shadowed"
            style="top:82%;right:4%;position:absolute;z-index:100;" height="100px" :src="require(`../assets/scoutpng.png`)" alt />
            <img
            v-else
          absolute
            top
            right
            style="top:82%;right:4%;position:absolute;z-index:100;" height="100px" :src="require(`../assets/scoutblack.png`)" alt />
          <v-flex xs3>
            <v-text-field
            style="margin-top: 12px!important;padding-top:0!important;"
              v-if="showAll"
              solo
              label="Search"
              v-model="search"
              prepend-inner-icon="search"
              append-icon="keyboard_arrow_right"
              class="roundCard searchLine"
            ></v-text-field>
            <!-- we need to change height if search bar not showing -->
            <v-card v-bind:class="{singleClassFace:(!showAll&&singleEvent.faceID&&singleEvent.notNamed),singleClassNamedFace:(!showAll&&singleEvent.faceID&&singleEvent.personName&&(singleEvent.similarFaces.length>0)),singleClassNamedFaceNoSimilar:(!showAll&&singleEvent.faceID&&singleEvent.personName&&!singleEvent.notNamed&&(singleEvent.similarFaces.length===0)),singleClassPlate:(!showAll&&singleEvent.plateID),searchClass:showAll}" style="overflow-x:hidden!important; overflow-y:auto!important;border-radius:6px!important;" color="rgb(255, 255, 255, 0.9)">
              <v-container
                fluid
                grid-list-lg
                style="padding-left:0px!important;padding-right:0px!important;padding-bottom:0!important;"
              >
                <center>
                  <h2 v-if="showAll" style="padding-top: 16px!important;margin-bottom: -24px!important;">Recently Detected</h2>
                  <h3 v-if="!showAll">{{singleEvent.street}}, {{singleEvent.city}}</h3>
                  <h2 v-if="!showAll">{{singleEvent.ts|moment("dddd, MMMM Do | h:mmA")}}</h2>
                  <h1 v-if="!showAll&&singleEvent.personName">{{singleEvent.personName}}</h1>
<v-layout align-center row wrap v-else-if="!showAll && singleEvent.faceID">
  
  <v-flex xs6>
                  <h1 v-if="singleEvent.gender">{{singleEvent.gender}}</h1>
                  

                  Male, Late-20s
                                    


                                    <h2 >{{singleEvent.makeModel}}</h2>


  </v-flex>
  <v-flex xs6 style="text-align:left!important;">
    <h3 v-if="!showAll">{{singleEvent.dateTime}}</h3>
                  <h3 v-if="!showAll">{{singleEvent.streetCity}}</h3>
  </v-flex>
</v-layout>

                </center>
<template v-if="showAll">
  <br />
</template>
                <v-layout v-if="singleEvent.plateID" row wrap>
                  <v-flex xs12>
<center>
  <v-layout row wrap v-if="!showAll && singleEvent.plateID">
    <v-flex xs12>
                            
        </v-flex>

  </v-layout>
  <h1 v-if="!showAll && singleEvent.plateID" style="padding-top:64px!important;"class="display-4">{{singleEvent.speed}}</h1>
  <v-layout v-if="!showAll && singleEvent.plateID" row wrap>
    <v-flex xs3>
<h2 v-if="singleEvent.status==='D'" style="margin-top:-32px!important;color:gray">P R N <span style="color:black;">D</span></h2>
<h2 v-else style="margin-top:-32px!important;color:gray"><span style="color:black;">P</span> R N D</h2>

    </v-flex>
    <v-flex xs6>
<h2 style="margin-top:-32px!important;">MPH</h2>
    </v-flex>
    <v-flex xs3>
    </v-flex>

  </v-layout>
  </center>
                  </v-flex>
                  <v-flex xs6 style="padding-right:0px!important;">

                    <v-progress-linear
                      background-color="green"
                      rounded
                      height="4"
                      class="negPower"
                                            style="background:rgba(0, 0, 0, 0.17);"
                      v-if="!showAll"
                      :buffer-value="singleEvent.negPower"
                    ></v-progress-linear>
                  </v-flex>
                  <v-flex xs6 style="padding-left:0px!important;">
                    <v-progress-linear
                      :buffer-value="singleEvent.posPower"
                      background-color="black"
                      style="background:rgba(0, 0, 0, 0.17);"
                      rounded
                      height="4"
                      v-if="!showAll"
                    ></v-progress-linear>
                  </v-flex>












                  <v-flex xs12 v-if="!showAll && singleEvent.plateID"><center><h2 >{{singleEvent.vyear}} {{singleEvent.vmake}} {{singleEvent.vmodel}}</h2>
                                                         <h1 v-if="singleEvent.plateID">{{singleEvent.plateContent}}</h1></center>
                                    

                  </v-flex>
                </v-layout>
                <center>
                  <div v-if="singleEvent.plateID" class="img-overlay-wrap">
                    <img
                      v-if="!showAll"
                      :src="grabThumbVehicle(singleEvent.vehicleImgPath)"
                      width="100%" height="500px" style="object-fit: cover;object-position: 50% 0%;"
                      alt
                    />

                  </div>
                  <div v-else class="img-overlay-wrap">
                    <img v-if="!showAll" :src="grabPerson(singleEvent.currentImg)" width="100%" height="500px" style="object-fit: cover;object-position: 50% 0%;" alt />
 
                  </div>




                  
                  <div v-if="!showAll" class="text-center">
                    <v-btn v-if="singleEvent.plateID" style="line-height: 44px;margin-top:-124px" rounded color="primary" dark @click="tryVideo(singleEvent)">Play Video</v-btn>
                    <v-btn v-if="singleEvent.faceID"  style="line-height: 44px;margin-top:-144px" rounded color="primary" dark @click="tryVideo(singleEvent)">Play Video</v-btn>


                  </div>
                  <v-container
                    v-if="!showAll && singleEvent.faceID"
                    v-bind="{ [`grid-list-xs`]: true }"
                    fluid
                    style="padding-top:0!important;"
                    @mouseleave="resetImg()"
                  >
                                    <h2 v-if="singleEvent.notNamed">Do you know this person's name?</h2>
<v-layout row wrap>
  <v-spacer v-if="singleEvent.notNamed && doIKnow!='yes'"></v-spacer>
                <v-flex  xs5 v-if="singleEvent.notNamed&&!doIKnow">
                  <v-radio-group v-model="doIKnow" row>
                    <v-radio label="No" value="no"></v-radio>
                    <v-radio label="Yes" value="yes"></v-radio>
                  </v-radio-group>
                </v-flex>
                  <v-spacer v-if="singleEvent.notNamed"></v-spacer>

                <v-flex xs6 v-if="singleEvent.notNamed && doIKnow">


                  <v-combobox
      v-model="firstName"
      :items="faces"
      item-text="personName"
      item-value="personName"
      :search-input.sync="faceSearch"
      hide-selected
      label="Name this person"
      small-chips
    >



<template v-slot:selection="data">{{ data.item.personName?data.item.personName : data.item }}</template>
          <template v-slot:item="data" style="line-height: 27px!important;">{{ data.item.personName }}</template>

        



      <template v-slot:no-data>
  <v-list-item>
    <v-list-item-content>
      <v-list-item-title>
        No named faces matching "
        <strong>{{ faceSearch }}</strong>". Press
        <kbd>enter</kbd>
        to add {{ faceSearch }}!
      </v-list-item-title>
    </v-list-item-content>
  </v-list-item>
</template>
    </v-combobox>

                </v-flex>
                <v-flex xs5 v-if="-singleEvent.notNamed&& doIKnow">
                                      <v-btn style="line-height: 44px;margin-top:16px!important;" rounded color="primary" dark @click="nameFace(singleEvent)">Save</v-btn>

                </v-flex>
              </v-layout>
                  <h2 v-if="singleEvent.notNamed && (singleEvent.similarFaces.length>0)">Are these the person you see above?</h2>
                  <h2 v-if="!singleEvent.notNamed && (singleEvent.similarFaces.length>0)">Are the faces below also {{singleEvent.personName}}?</h2>
                    <v-layout wrap style="padding-left:16px;padding-right:16px;">



<v-item-group
        v-model="singleEvent.similarFacesSelected"
        multiple
      >
      <v-container class="pa-1">
        <v-row>
          <v-col
            v-for="n in singleEvent.similarFaces"
                        :key="n._id"
            :cols="`${(singleEvent.similarFaces.length>1)?4:12}`"


                        style="padding:2px!important;"
          >
            <v-item v-slot:default="{ active, toggle }">
                                      <v-card >

              <v-img
                :src="grabThumb(n.detectionImgPath)"
                            height="150px"
                class="text-right pa-2"
                @click="toggle"
                @change="toggleChanged(n)"
              >
                <v-btn
                  icon
                  dark
                >
                  <v-icon color='primary'>
                    {{ active ? 'mdi-checkbox-marked-circle' : 'mdi-checkbox-marked-circle-outline' }}
                  </v-icon>
                </v-btn>
              </v-img>
                                      </v-card >

            </v-item>
          </v-col>
        </v-row>
        </v-container>
      </v-item-group>







                    </v-layout>
                  </v-container>
                   <div v-if="!showAll && singleEvent.faceID" class="text-center">
                    <v-btn v-if="singleEvent.similarFaces.length>0" style="line-height: 44px;" rounded color="primary" dark @click="saveChanges(singleEvent)">Save / Close</v-btn>
                  </div>
                </center>
                <v-layout row wrap>
                  <v-flex
                    v-if="showAll"
                    v-for="event in filteredList"
                    :key="event.id"
                    xs12
                    style="padding-left:0px!important;padding-right:0px!important;"
                  >
                    <v-hover>
                      
                      <v-card
                        slot-scope="{ hover }"
                        :color="`${hover ? 'rgb(93.3, 93.3, 93.3, 0.1)' : 'transparent'}`"
                        flat
                        @click="moveCenter(event)"
                        style="cursor:pointer;"
                      >
                        <v-layout row justify-space-around>
                          <v-flex v-if="event.type!='face'" xs3 style="padding-left: 20px!important;margin-top:12px!important;">
                            <v-img
                              v-if="event.faceID"
                              style="border-radius: 20px;"
                              :src="grabThumb(event.detectionImgPath)"
                              width="125px"
                              contain
                            ></v-img>
                            <v-img
                              v-else
                              style="border-radius: 20px;"
                              :src="grabThumbVehicle(event.vehicleImgPath)"
                              width="125px"
                              contain
                            ></v-img>
                          </v-flex>
                          <v-flex v-else xs3 style="padding-left: 20px!important;">
                            <v-img
                              v-if="event.type==='face'"
                              style="border-radius: 20px;"
                              :src="event.faceUrl"
                              width="125px"
                              contain
                            ></v-img>
                            <v-img
                              v-else
                              style="border-radius: 20px;"
                              :src="`CHANGEME/${event.imgName}.png`"
                              width="125px"
                              contain
                            ></v-img>
                          </v-flex>
                          <v-flex xs8>
                            <v-card-title primary-title style="padding-top:12px!important;">
                              <div v-if="event.plate==='plate'">
                                <h2 class="headline">{{event.title}}</h2>
                                                                <div class="sub">{{event.streetCity}}</div>

                                <div class="sub">{{event.makeModel}}</div>
                                <div class="sub">{{event.dateTime}}</div>
                              </div>
                              <div v-else-if="event.type==='face'">
                                <h2 v-if="event.title === 'Truman'&& singleEvent.notNamed" class="headline">Male, Late-20s</h2>
                                <h2 v-else class="headline">{{event.title}}</h2>

                                <div class="sub">{{event.streetCity}}</div>
                                <div class="sub">{{event.dateTime}}</div>
                              </div>
                              <div v-else>
                                <h2 v-if="event.faceID" class="headline">{{event.personName}}</h2>

                                <h2 v-if="event.plateID" class="headline">{{event.plateContent}}</h2>


                                <div class="sub">{{event.street}}, {{event.city}}</div>
                                                                <div v-if="event.plateID" class="sub">{{event.vyear}} {{event.vmake}} {{event.vmodel}}</div>

                                
                                <div class="sub">{{event.ts|moment("dddd, MMMM Do | h:mmA")}}</div>
                              </div>
                            </v-card-title>
                          </v-flex>

                        </v-layout>
                      </v-card>
                    </v-hover>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-card>
          </v-flex>
          <v-flex v-if="!showAll && showVideo" xs9 style="padding-left:24px!important;padding-right:24px!important;">
            <v-card
            style="height: calc(100vh - 380px); overflow-y:auto!important;border-radius:6px!important;">
              <v-container
                fluid
                grid-list-lg
                style="padding-left:0px!important;padding-bottom:0!important;padding-right:0px!important;padding-top:0px!important;padding-bottom:0px!important;"
              >
                <video
                  @playing="vidPlaying"
                  style="width:100%;"

                  controls
                  id="singleVideo"
                  :src="vidName"
                  autoplay
                  muted
                  loop
                  type="video/mp4"
                ></video>
              </v-container>
            </v-card>
          </v-flex>
        </v-layout>
        
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import {
  LMap,
  LTileLayer,
  LMarker,
  LPopup,
  LDistanceGrid,
  LTooltip,
  LIcon
} from "vue2-leaflet";
import PlateService from "../service/PlateService.js";
import FaceService from "../service/FaceService.js";
import PollService from "../service/PollService.js";
import GeoService from "../service/GeoService.js";
import DriveService from "../service/DriveService.js";
import Vue2LeafletRotatedMarker from "vue2-leaflet-rotatedmarker";
import Vue2LeafletMarkerCluster from "vue2-leaflet-markercluster";
import LMovingMarker from "vue2-leaflet-movingmarker";

import { icon, latLngBounds, gridLayer } from "leaflet";

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
    firstName: null,
    faceSearch: null,
    facesSelected: [],
    faces: [],

    showDrives: false,
    D1,
    D2,
    D3,
    showRangeDrives: false,
    rangeDrives: [],
    followDialog: false,
    currentJSON: {},
    satMap: false,
    allDrives: [],
    nameSet: false,
    doIKnow: null,

    randomPlates2: [],
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
    detected: [
      {
        streetCity: "",
        vmake: "",
        vmodel: "",
        vyear: "",
        plateContent: "",
        personName: ""
      }
    ],
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
    similarFaces: [],
    notTesting: false,
    faceHidden: false,
    saveChangesBtn: false,
    plateHidden: false,
    showSearch: true,
    currentInfo: {},
    showInfo: false,
    polls: [],
    faces: [],
    zoom: 18,
    center: L.latLng(33.68100147731155, -117.84374809416478),
    url:
      "https://api.mapbox.com/styles/v1/tev43478638w46/cjtsk7iaj1oll1fnz5gxgd1dh/tiles/256/{z}/{x}/{y}?access_token=CHANGEME(MapBoxAccessToken)",
    urlSAT:
      "https://api.mapbox.com/styles/v1/tev43478638w46/cjyu4edci0tcg1cl71f1y8z2c/tiles/256/{z}/{x}/{y}?access_token=CHANGEME(MapBoxAccessToken)",
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
  watch: {
    firstName(val, prev) {
      console.log(`new face added:${val}`);
    },
    doIKnow: function(doIKnowNew, doIKnowNewOld) {
      var vm = this;
      if (doIKnowNew === "no") {
        console.log(
          `they dont know the persons name, we need to do a nameUpdate and use stranger name`
        );
        vm.nameFace(vm.singleEvent);
      }
    },

    "singleEvent.similarFacesSelected": function(
      newSimilarFaces,
      oldSimilarFaces
    ) {
      var vm = this;
      vm.saveChangesBtn = true;
    }
  },
  async created() {
    var ip = require("ip");

    console.log(`IP ADDRESS:${ip.address()}`);
    var vm = this;
    console.log(`showDrives status:${vm.showDrives}`);

    if (vm.$route.params.search) {
      console.log("the params:", vm.$route.params);

      vm.search = vm.$route.params.search;
    } else {
      console.log("no params");
    }

    this.faces = await FaceService.getFaces();
    this.allDrives = await DriveService.getDrives();
    console.log(`allDrives:${this.allDrives}`);

    var faceDetections = await FaceService.getDetections();
    var plateDetections = await PlateService.getAllDetections();

    var allDetections = await faceDetections.concat(plateDetections);

    this.detected = await allDetections.sort((a, b) => {
      if (a.ts === b.ts) {
        // If two elements have same number, then the one who has larger rating.average wins
        return b._id - a._id;
      } else {
        // If two elements have different number, then the one who has larger number wins
        return b.ts - a.ts;
      }
    });

    //get similarImages for each faceDetection
    faceDetections.forEach(fD => {
      var similarFaces = [];
      var similarFacesSelected = [];
      var allDetectionsForThisFace = faceDetections.filter(function(
        faceDetection
      ) {
        return faceDetection.faceID == fD.faceID;
      });
      console.log(`all detections for this face:${allDetectionsForThisFace}`);

      allDetectionsForThisFace.forEach(specDetection => {
        if (specDetection._id != fD._id)
          similarFaces.push({
            _id: specDetection._id,
            detectionImgPath: specDetection.detectionImgPath,
            personImgPath: specDetection.personImgPath
          });
      });

      console.log(`similarFaces for listing:${similarFaces}`);

      console.log("setting isSame true");

      fD.similarFaces = similarFaces;
      similarFaces.forEach(similarFace => {
        similarFacesSelected.push(similarFaces.indexOf(similarFace));
      });
      fD.similarFacesSelected = similarFacesSelected;
      console.log(fD.similarFaces);
    });

    console.log(this.detected);

    if (vm.$route.params.showDrives) {
      var searchedDriveIds = this.filteredList.map(function(item) {
        return item["driveID"];
      });
      console.log(`driveIDs from filteredList:${searchedDriveIds}`);

      this.allDrives = await PollService.getMultipleDrivePolls(
        searchedDriveIds
      );
      console.log(await this.allDrives);

      vm.showDrives = vm.$route.params.showDrives;
    } else {
      console.log("no params");
    }
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
    async oneDrive(detection) {
      var vm = this;
      vm.allDrives.forEach(drive => {
        if (typeof drive === "array") {
          if (drive[0].driveID === detection.driveID) {
            console.log(`we have our one drive:$${drive}`);

            return [drive];
          }
        } else {
          if (drive._driveID === detection.driveID) {
            console.log(`we have our one drive:$${drive}`);

            return [drive];
          }
        }
      });
    },
    saveChanges(detection) {
      var vm = this;
      detection.similarFaces.forEach(similarFace => {
        if (
          !detection.similarFacesSelected.includes(
            detection.similarFaces.indexOf(similarFace)
          )
        ) {
          //delete detection from face, make a new stranger
          console.log(
            `splitting ${similarFace} into its own face, with detectionID:${similarFace._id}`
          );
          console.log(
            `adding faceID to be made oldFaceID:${similarFace.faceID}`
          );

          FaceService.makeStranger(similarFace._id, detection.faceID);
        }
      });

      this.showAll = true;
      this.showVideo = false;
      this.showPolyLine = false;
      // vm.$forceUpdate();
      // vm.$router.go(0);
      vm.reCreate();
    },
    toggleChanged(n) {
      console.log(n);
    },
    checkSame(n) {
      console.log(
        `check current state is ${n.isSame}, now switching to ${!n.isSame}`
      );
      n.isSame = !n.isSame;
      console.log(`check new state is ${n.isSame}`);
    },
    checkState(n) {
      return n.isSame;
    },

    getUpdatedGeo(detectionID) {
      let obj = this.detected.find(o => o["_id"] === detectionID);
      console.log("returning now:", obj.streetCity);

      return obj.streetCity;
    },

    grabGeocode(geocodeID) {
      // Lazily load input items
      var updatedStreetCity = "";
      console.log(`https://10.6.6.13/api/geocodes/${geocodeID}`);

      fetch(`https://10.6.6.13/api/geocodes/${geocodeID}`)
        .then(res => res.json())
        .then(res => {
          // var resp = res.data[0]
          console.log(res);

          updatedStreetCity = `${res[0].road}, ${res[0].city}`;
        })
        .catch(err => {
          console.log(err);
        })
        .finally(() => {
          console.log(updatedStreetCity);
          return updatedStreetCity;
        });
    },
    grabThumb(path) {
      //   console.log(path);

      var fileName = path.split("/").pop();
      //   console.log(fileName);

      var imgUrl = `https://10.6.6.13/thumb/face/${fileName}`;
      console.log(imgUrl);
      return imgUrl;

      //return FaceService.grabThumb(fileName);
    },
    grabPerson(path) {
      //   console.log(path);

      var fileName = path.split("/").pop();
      //   console.log(fileName);

      var imgUrl = `https://10.6.6.13/image/face/${fileName}`;
      console.log(imgUrl);
      return imgUrl;
    },

    grabThumbVehicle(path) {
      //   console.log(path);

      var fileName = path.split("/").pop();
      //   console.log(fileName);

      var imgUrl = `https://10.6.6.13/thumb/plate/${fileName}`;
      // console.log(imgUrl);
      return imgUrl;

      //   return FaceService.grabThumb(path);
    },

    grabVideo(path) {
      //   console.log(path);

      var fileName = path.split("/").pop();
      //   console.log(fileName);

      var vidUrl = `https://10.6.6.13/video/${fileName}`;
      console.log(`vidURL$:${vidUrl}`);
      return vidUrl;

      //   return FaceService.grabThumb(path);
    },
    async nameFace(faceDetection) {
      var vm = this;

      //we need to know if they picked an existing or new face

      var faceID = faceDetection.faceID;
      if (typeof vm.firstName === "string") {
        //we just need to update the name like we originally were

        await FaceService.nameFace(vm.firstName, faceID);
        vm.showAll = true;
        vm.showVideo = false;
        vm.showPolyLine = false;
        vm.firstName = null;

        vm.reCreate();
      } else if (vm.firstName === null) {
        await FaceService.nameFace(faceDetection.personName, faceID);
        vm.showAll = true;
        vm.showVideo = false;
        vm.showPolyLine = false;
        vm.firstName = null;

        vm.reCreate();
      } else {
        var selectedFace = vm.firstName;
        var oldFaceID = faceID;
        var newFaceID = selectedFace._id;
        var newName = selectedFace.personName;

        await FaceService.updateDetection(
          faceDetection._id,
          oldFaceID,
          newFaceID,
          newName
        );
        this.showAll = true;
        this.showVideo = false;
        this.showPolyLine = false;
        this.firstName = null;

        vm.reCreate();
        //will have to check if tehre are any detections with faceID oldFaceID before deleting the face so we dont fuck something up
      }
    },
    getColor(driveID) {
      var vm = this;
      vm.detected.forEach(detection => {
        if (detection.driveID) {
          console.log("has a driveID");

          if (detection.driveID === driveID) {
            console.log(`we have a match, setting to ${detection.polyColor}`);

            return detection.polyColor;
          } else {
            return;
          }
        } else {
          return;
        }
      });
    },
    printDriveID(driveID) {
      console.log(driveID);
    },
    getJSON() {
      var vm = this;
    },
    randomColor(i) {
      var myArray = ["#00abb6", "#ff9933", "#3399ff", "#ff3333"];

      var rand = myArray[i];
      return rand;
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
    },
    logCoords(coords) {
      console.log(`[${coords[0]},${coords[1]}],`);
    },
    resetImg() {},
    previewImg(currentImg) {},
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
      console.log(`trying video for event:`);

      if (event.faceID) {
        // var vm = this;
        console.log(event);

        if (event.videoFileName) {
          console.log(event.videoFileName);

          vm.vidName = `${vm.grabVideo(event.videoFileName)}#t=${
            event.secondsIntoVideo - 3 < 0 ? 0 : event.secondsIntoVideo - 3
          }`;
          console.log(vm.vidName);
        }
        this.showVideo = true;
        var newcoord = event.location.coordinates[1] + 0.015;
        this.$refs.myMap.mapObject.flyTo(
          L.latLng(newcoord, event.location.coordinates[0]),
          15
        );
      } else {
        var vm = this;
        vm.$router.push({
          name: "Timeline",
          params: { detection: event }
        });
      }
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
    locationFound(l) {
      console.log(`the location found was: ${l}`);
    },
    async moveCenter(center) {
      // mapObject.flyTo(L.latLng(center[0], center[1]));
      center.currentImg = center.personImgPath;

      this.singleEvent = center;
      this.allDrives = await PollService.getMultipleDrivePolls([
        center.driveID
      ]);
      if (center.driveID) {
        this.showDrives = true;
      }

      //centers the marker
      this.$refs.myMap.mapObject.flyTo(
        L.latLng(
          center.location.coordinates[1],
          center.location.coordinates[0]
        ),
        15
      );

      const bounds = latLngBounds(this.drives2);

      this.showAll = false;
      this.detected.forEach(event => {
        event.showSingle = false;
      });
      center.showSingle = true;
      if (this.singleEvent.plateID) {
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
    },
    async reCreate() {
      var ip = require("ip");

      console.log(`IP ADDRESS:${server.address().address}`);
      console.log(req.connection.remoteAddress);

      var vm = this;
      vm.doIKnow = null;
      vm.firstName = null;
      console.log(`showDrives status:${vm.showDrives}`);

      if (vm.$route.params.search) {
        console.log("the params:", vm.$route.params);

        vm.search = vm.$route.params.search;
      } else {
        console.log("no params");
      }

      this.faces = await FaceService.getFaces();
      this.allDrives = await DriveService.getDrives();
      console.log(`allDrives:${this.allDrives}`);

      var faceDetections = await FaceService.getDetections();
      var plateDetections = await PlateService.getAllDetectionsDD();
      var plateDetections = await PlateService.getDetections();

      var allDetections = await faceDetections.concat(plateDetections);

      this.detected = await allDetections.sort((a, b) => {
        if (a.ts === b.ts) {
          // If two elements have same number, then the one who has larger rating.average wins
          return b._id - a._id;
        } else {
          // If two elements have different number, then the one who has larger number wins
          return b.ts - a.ts;
        }
      });

      //get similarImages for each faceDetection
      faceDetections.forEach(fD => {
        var similarFaces = [];
        var similarFacesSelected = [];
        var allDetectionsForThisFace = faceDetections.filter(function(
          faceDetection
        ) {
          return faceDetection.faceID == fD.faceID;
        });
        console.log(`all detections for this face:${allDetectionsForThisFace}`);

        allDetectionsForThisFace.forEach(specDetection => {
          if (specDetection._id != fD._id)
            similarFaces.push({
              _id: specDetection._id,
              detectionImgPath: specDetection.detectionImgPath,
              personImgPath: specDetection.personImgPath
            });
        });

        console.log(`similarFaces for listing:${similarFaces}`);

        console.log("setting isSame true");

        fD.similarFaces = similarFaces;
        similarFaces.forEach(similarFace => {
          similarFacesSelected.push(similarFaces.indexOf(similarFace));
        });
        fD.similarFacesSelected = similarFacesSelected;
        console.log(fD.similarFaces);
      });

      console.log(this.detected);

      if (vm.$route.params.showDrives) {
        var searchedDriveIds = this.filteredList.map(function(item) {
          return item["driveID"];
        });
        console.log(`driveIDs from filteredList:${searchedDriveIds}`);

        var plateDetections = await PlateService.getAllDetections();

        var plateIDs = [vm.$route.params.plateID];

        const theseDetections = await plateDetections.filter(
          detection => detection.plateID === plateIDs[0]
        );
        theseDetections.forEach(detection => {});

        console.log(
          `just the detections of plateID ${plateIDs[0]}:${theseDetections}`
        );
        var driveIDs = [];
        theseDetections.forEach(detection => {
          if (!driveIDs.includes(detection.driveID)) {
            driveIDs.push(detection.driveID);
          }
        });
        console.log(`the drives we need to load:${driveIDs}`);

        this.allDrives = await PollService.getMultipleDrivePolls(driveIDs);
        console.log(await this.allDrives);

        vm.showDrives = vm.$route.params.showDrives;
      } else {
        console.log("no params");
      }
    }
  },
  computed: {
    filteredList() {
      return this.detected.filter(event => {
        var checkAgainst = {
          streetCity: "",
          vmake: "",
          vmodel: "",
          vyear: "",
          plateContent: "",
          personName: ""
        };

        var searchObject = { ...checkAgainst, ...event };

        return (
          searchObject.streetCity
            .toLowerCase()
            .includes(this.search.toLowerCase()) ||
          searchObject.vmake
            .toLowerCase()
            .includes(this.search.toLowerCase()) ||
          searchObject.vmodel
            .toLowerCase()
            .includes(this.search.toLowerCase()) ||
          searchObject.vyear
            .toLowerCase()
            .includes(this.search.toLowerCase()) ||
          searchObject.vyear
            .toLowerCase()
            .includes(this.search.toLowerCase()) ||
          searchObject.personName
            .toLowerCase()
            .includes(this.search.toLowerCase()) ||
          searchObject.plateContent
            .toLowerCase()
            .includes(this.search.toLowerCase())
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
      // this.$refs.getLocation.mapObject.onlocationfound()
      this.$refs.myMap.mapObject.getBounds();
      this.$refs.clusterRef.mapObject.refreshClusters();
      this.clusterOptions = { disableClusteringAtZoom: 16 };
    });
  }
};
</script>

<style>
@import "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css";
@import "~leaflet/dist/leaflet.css";

@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";

.singleClassFace {
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
span.v-btn__content {
  line-height: 44px !important;
  /* margin-top: 8px!important; */
}
.sub {
  line-height: 1.5rem !important;
}
/* label .v-label.theme--light {
  padding-bottom:24px!important;
} */

.v-input .v-label {
  height: 20px;
  line-height: 23px !important;
}

@media only screen and (min-width: 1904px) {
  .container {
    max-width: 1985px;
  }
}

.shadowed {
  -webkit-filter: drop-shadow(2px 2px 10px rgba(0, 0, 0, 0.6)) !important;
  filter: url(#drop-shadow);
  -ms-filter: "progid:DXImageTransform.Microsoft.Dropshadow(OffX=12, OffY=12, Color='#444')";
  filter: "progid:DXImageTransform.Microsoft.Dropshadow(OffX=12, OffY=12, Color='#444')";
}

/* .img-overlay-wrap {
  position: relative;
  display: inline-block; 
  transition: transform 150ms ease-in-out;
  width: 100% !important;
}

.img-overlay-wrap img {
  display: block;
  max-width: 100%;
  height: auto;
}

.img-overlay-wrap svg {
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
}

.img-overlay-wrap:hover svg {
  opacity: 1;
} */

.negPower {
  transform: rotate(180deg);
}
</style>


<style>
/* 
FROM APP.VUE
*/
span.red.darken-2 {
  padding-top: 8px !important;
}
body,
p,
h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: "GothamBook";
}

.normal {
  font-weight: 400;
}

.bold,
strong {
  font-weight: 700;
}

.light {
  font-weight: 300;
}
</style>


<style>
/* 
FROM JUSTMAP.VUE
*/
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";

/* .singleClassNamedFace {
  height: calc(100vh - 365px);
} */

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

<style>
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";

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

.mapBoi {
  min-height: 100% !important;
  /* min-width: 1024px !important; */

  /* Set up proportionate scaling */
  width: 100% !important;
  height: auto !important;

  /* Set up positioning */
  /* position: fixed !important; */
  top: 0 !important;
  left: 0 !important;
}
</style>

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

.searchClass {
  height: calc(100vh - 224px);
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

/* .img-overlay-wrap {
  position: relative;
  display: inline-block; 
  transition: transform 150ms ease-in-out;
  width: 100% !important;
}

.img-overlay-wrap img {
  display: block;
  max-width: 100%;
  height: auto;
}

.img-overlay-wrap svg {
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
}

.img-overlay-wrap:hover svg {
  opacity: 1;
} */

.negPower {
  transform: rotate(180deg);
}
</style>

<style>
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";

/* .singleClassNamedFace {
  height: calc(100vh - 365px);
} */

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

<style>
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";

/* .leaflet-marker-icon{
    transform: rotate(var(--marker-rotation)deg);
} */

/* .singleClassNamedFace {
  height: calc(100vh - 365px);
} */

.singleClassNamedFaceNoSimilar {
  height: calc(100vh - 680px);
  overflow-y: hidden;
}

.singleClassNamedFace {
  height: calc(100vh - 366px);
  overflow-y: hidden;
}

.singleClassPlate {
  height: calc(100vh - 376px);
  overflow-y: hidden;
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
<style>
@import "~leaflet/dist/leaflet.css";
html,
body {
  height: 100%;
  margin: 0;
}
</style>

<style>
/* FROM MAP.VUE */
@import "~leaflet.markercluster/dist/MarkerCluster.css";
@import "~leaflet.markercluster/dist/MarkerCluster.Default.css";

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

.mapBoi {
  min-height: 100% !important;
  min-width: 1024px !important;

  /* Set up proportionate scaling */
  width: 100% !important;
  height: auto !important;

  /* Set up positioning */
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
}

/* .mapBoi {
  min-height: 100% !important;
  min-width: 1024px !important;

  width: 100% !important;
  height: auto !important;

  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
} */
</style>

<style scoped>
#input-14 {
  padding-top: 0 !important;
}
</style>

