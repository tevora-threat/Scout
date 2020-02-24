import Vue from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify';
import {
  LMap,
  LTileLayer,
  LMarker,
  LPopup,
  LIcon,
  LIconDefault,
  LDistanceGrid,
  LTooltip,
  LPolyline,
  findRealParent,
  propsBinder
} from "vue2-leaflet";
import Vue2LeafletMarkerCluster from "vue2-leaflet-markercluster";
import Vue2LeafletRotatedMarker from "vue2-leaflet-rotatedmarker";
import 'leaflet.marker.slideto'
import "leaflet/dist/leaflet.css";

Vue.use(require('vue-moment'));
Vue.component('v-locatecontrol', Vue2LeafletLocatecontrol);

import LMovingMarker from 'vue2-leaflet-movingmarker'
Vue.component("v-rotated-marker", Vue2LeafletRotatedMarker);

import {
  Icon,
  latLngBounds
} from "leaflet";

import "leaflet/dist/leaflet.css";
import "./stylus/main.styl";

Vue.config.productionTip = false;

Vue.component("l-map", LMap);
Vue.component("l-tile-layer", LTileLayer);
Vue.component("l-polyline", LPolyline);
Vue.component('l-moving-marker', LMovingMarker)
Vue.component("l-marker", LMarker);
Vue.component("l-icon", LIcon);
Vue.component("l-popup", LPopup);
Vue.component("l-tooltip", LTooltip);
Vue.component("v-marker-cluster", Vue2LeafletMarkerCluster);

delete Icon.Default.prototype._getIconUrl;

Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});


Vue.config.productionTip = false

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')