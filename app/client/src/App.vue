<template>
  <v-app style="
  font-family: Gotham, sans-serif;
">
    <v-content class="darkBG">
      <router-view></router-view>
    </v-content>
    <v-bottom-navigation
      style
      v-model="bottomNav"
      :background-color="color"
      :value="true"
      :active.sync="activeSync"
      fixed
      dark
      shift
    >
      <v-btn
        v-for="item in items"
        dark
        :key="item.title"
        :to="`${(item.link==='/timeline')?'#':item.link}`"
        @click="checkWarning(item.link)"
      >
        <span style="padding-top: 20px!important;" class="bold">{{item.title}}</span>
        <v-icon style="padding-top: 14px!important;">{{item.icon}}</v-icon>
      </v-btn>
    </v-bottom-navigation>
    <div class="text-center">
      <v-bottom-sheet v-model="dialog" inset>
        <v-sheet class="text-center" height="200px">
          <v-btn class="mt-6" text color="error" @click="dialog = !dialog">close</v-btn>
          <div class="my-3">
            <h3>Searchable timeline coming soon. For now, choose a plate detection over on the Recent page, then click "Play Video" to revisit the scene.</h3>
          </div>
        </v-sheet>
      </v-bottom-sheet>
    </div>
  </v-app>
</template>

<script>
import HelloWorld from "./components/HelloWorld";

export default {
  name: "App",

  components: {
    HelloWorld
  },
  data() {
    return {
      activeSync: 0,
      dialog: false,
      items: [
        { title: "RECENT", icon: "history", link: "/" },
        { title: "PLATES", icon: "aspect_ratio", link: "/plates" },
        { title: "FACES", icon: "face", link: "/faces" },
        { title: "TIMELINE", icon: "mdi-filmstrip", link: "/timeline" },
        { title: "SETTINGS", icon: "settings", link: "/settings" }
      ],
      bottomNav: 0,
      userLoggedIn: true
    };
  },
  created() {},
  methods: {
    checkWarning(link) {
      var vm = this;

      if (link === "/timeline") {
        this.dialog = true;
        var vm = this;
        vm.$router.push({
          name: "Recent"
        });
      }
    }
  },
  computed: {
    color() {
      switch (this.bottomNav) {
        case 0:
          return "black";
        case 1:
          return "black";
        case 2:
          return "black";
        case 3:
          return "black";
        case 4:
          return "black";
        case 5:
          return "black";
      }
    }
  }
};
</script>

<style>
/* .darkBG {
  background-color: black !important;
} */
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

