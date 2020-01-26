<template>
    <v-col cols="12" md="12">
        <v-btn
            color="blue"
            @click="$router.push({ name: 'tasks_create' }).catch(() => {})"
            v-if="!isNull(user)"
            class="mb-3"
            >Create</v-btn
        >
        <div v-if="requested">
            <v-simple-table v-if="error === null">
                <template v-slot:default>
                    <thead>
                        <tr>
                            <th class="text-left">Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="task in tasks" :key="task">
                            <td @click="openTask(task)" class="pc">
                                {{ task }}
                            </td>
                        </tr>
                    </tbody>
                </template>
            </v-simple-table>
            <div class="red" v-if="error !== null" style="white-space: pre;">
                {{ error }}
            </div>

            <v-pagination
                v-model="page"
                :length="maxpage"
                total-visible="6"
                v-if="error === null"
            />
        </div>
    </v-col>
</template>

<script>
import { isNull } from '@/utils/types';
import { mapState } from 'vuex';

export default {
    data: function() {
        return {
            requested: false,
            page: 1,
            maxpage: 1,
            error: null,
            tasks: [],
        };
    },

    computed: mapState(['user']),

    methods: {
        fetchTasks: async function() {
            try {
                const r = await this.$http.get(
                    `/tasks/?limit=10&offset=${(this.page - 1) * 10}`
                );
                this.error = null;
                const { task_ids: tasks, count } = r.data;
                this.tasks = tasks;
                this.maxpage = Math.floor((count + 9) / 10);
                this.requested = true;
            } catch (e) {
                this.error = e.response.data.error;
            }
            this.requested = true;
        },
        openTask: function(taskIdx) {
            this.$router
                .push({ name: 'task', params: { idx: taskIdx } })
                .catch(() => {});
        },
        isNull,
    },

    created: async function() {
        const { page = '1' } = this.$route.query;

        this.page = parseInt(page);
        await this.fetchTasks();
    },

    watch: {
        $route: async function() {
            await this.fetchTasks();
        },
        page: function(page) {
            this.$router
                .push({ name: 'tasks', query: { page } })
                .catch(() => {});
        },
    },
};
</script>

<style lang="scss" scoped>
.pc {
    cursor: pointer;
}
</style>
