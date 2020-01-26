import Vue from 'vue';
import VueRouter from 'vue-router';
import Scoreboard from '@/views/Scoreboard';
import Tasks from '@/views/Tasks';
import TasksCreate from '@/views/TasksCreate';
import TasksView from '@/views/TasksView';
import Profile from '@/views/Profile';
import store from '@/store';
import { isNull } from '@/utils/types';

Vue.use(VueRouter);

const routes = [
    {
        path: '/',
        name: 'index',
        component: Scoreboard,
    },
    {
        path: '/users/:username/',
        name: 'profile',
        component: Profile,
        meta: {
            auth: true,
        },
    },
    {
        path: '/tasks/create/',
        name: 'tasks_create',
        component: TasksCreate,
        meta: {
            auth: true,
        },
    },
    {
        path: '/tasks/:idx',
        name: 'task',
        component: TasksView,
        meta: {
            auth: true,
        },
    },
    {
        path: '/tasks/',
        name: 'tasks',
        component: Tasks,
        meta: {
            auth: true,
        },
    },
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
});

function dec2hex(dec) {
    return ('0' + dec.toString(16)).substr(-2);
}

function str2hex(str) {
    let res = '';
    for (let i = 0; i < str.length; i += 1) {
        res += dec2hex(str.charCodeAt(i));
    }
    return res;
}

router.beforeEach(async (to, from, next) => {
    const user = await store.dispatch('GET_USER');
    if (to.matched.some(record => record.meta.auth)) {
        if (isNull(user)) {
            next({
                name: 'index',
                query: {
                    redirect: str2hex(
                        JSON.stringify({
                            name: to.name,
                            query: to.query,
                            params: to.params,
                        })
                    ),
                },
            });
        } else {
            next();
        }
    } else {
        next();
    }
});

export default router;
