<template>
    <v-col cols="12" md="12">
        <div v-if="requested">
            <v-simple-table v-if="error === null">
                <template v-slot:default>
                    <thead>
                        <tr>
                            <th class="text-left">Username</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in users" :key="user">
                            <td class="pc">
                                {{ user }}
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
            users: [],
        };
    },

    computed: mapState(['user']),

    methods: {
        fetchUsers: async function() {
            try {
                const r = await this.$http.get(
                    `/users/?limit=10&offset=${(this.page - 1) * 10}`
                );
                this.error = null;
                const { users, count } = r.data;
                this.users = users;
                this.maxpage = Math.floor((count + 9) / 10);
                this.requested = true;
            } catch (e) {
                this.error = e.response.data.error;
            }
            this.requested = true;
        },
        isNull,
    },

    created: async function() {
        const { page = '1' } = this.$route.query;

        this.page = parseInt(page);
        await this.fetchUsers();
    },

    watch: {
        $route: async function() {
            await this.fetchUsers();
        },
        page: function(page) {
            this.$router
                .push({ name: 'index', query: { page } })
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
