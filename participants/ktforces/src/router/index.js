import Vue from "vue";
import VueRouter from "vue-router";
import Scoreboard from "@/views/Scoreboard";
import Tasks from "@/views/Tasks";
import store from "@/store";
import { isNull } from "@/utils/types";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "index",
    component: Scoreboard
  },
  {
    path: "/tasks/",
    name: "tasks",
    component: Tasks
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

router.beforeEach(async (to, from, next) => {
  const user = await store.dispatch("GET_USER");
  if (to.matched.some(record => record.meta.auth)) {
    if (isNull(user)) {
      next({
        name: "login",
        query: { redirect: to.name }
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
