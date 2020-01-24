<template>
  <v-app>
    <login-form v-model="loginForm" />
    <register-form v-model="registerForm" />
    <me-form v-model="meForm" v-if="!isNull(user)" />

    <v-app-bar app clipped-left>
      <v-app-bar-nav-icon @click="show = !show" />
      <v-toolbar-title>KTForces</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="green" @click="loginForm = true" v-if="isNull(user)"
        >Login</v-btn
      >
      <v-btn color="green" v-else @click="meForm = true">{{
        user.username
      }}</v-btn>
      <v-btn
        color="red"
        class="ml-3"
        @click="registerForm = true"
        v-if="isNull(user)"
        >Register</v-btn
      >
      <v-btn class="ml-3" color="red" v-else @click="logout">Logout</v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="show" app clipped>
      <v-list dense>
        <v-list-item
          link
          @click="$router.push({ name: 'index' }).catch(() => {})"
        >
          <v-list-item-action>
            <v-icon>mdi-align-vertical-bottom</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Scoreboard</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item
          link
          @click="$router.push({ name: 'tasks' }).catch(() => {})"
        >
          <v-list-item-action>
            <v-icon>mdi-cube-outline</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Tasks</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-content>
      <v-container fluid>
        <v-row>
          <router-view />
        </v-row>
      </v-container>
    </v-content>

    <v-footer app>
      <span>&copy; lalala lul where is my backend?</span>
    </v-footer>
  </v-app>
</template>

<script>
import LoginForm from "@/components/LoginForm";
import RegisterForm from "@/components/RegisterForm";
import MeForm from "@/components/MeForm";

import { mapState } from "vuex";
import { isNull } from "@/utils/types";

export default {
  data: () => ({
    show: null,
    loginForm: false,
    registerForm: false,
    meForm: false
  }),

  components: {
    LoginForm,
    RegisterForm,
    MeForm
  },

  created: async function() {
    this.$vuetify.theme.dark = true;
  },

  computed: mapState(["user"]),

  methods: {
    isNull,
    logout: async function() {
      await this.$http.get("/logout/");
      await this.$store.dispatch("UPDATE_USER");

      if (this.$route.meta.auth) {
        this.$router
          .push({
            name: "index",
            query: { redirect: this.$route.name }
          })
          .catch(() => {});
      }
    }
  }
};
</script>
