<template>
    <v-col cols="12" md="12">
        <v-btn
            color="blue"
            @click="$router.push({ name: 'collabs_create' }).catch(() => {})"
            v-if="!isNull(user)"
            class="mb-3"
            id="collabs-create"
            >Create</v-btn
        >
        <div v-if="requested">
            <v-simple-table v-if="error === null" id="t-list">
                <template v-slot:default>
                    <thead>
                        <tr>
                            <th class="text-left">Token</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="collab in collabs" :key="collab">
                            <td @click="openCollab(collab)" class="pc">
                                {{ collab }}
                            </td>
                        </tr>
                    </tbody>
                </template>
            </v-simple-table>
            <div class="red" v-if="error !== null" style="white-space: pre;">
                {{ error }}
            </div>
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
            error: null,
            collabs: [],
        };
    },

    computed: mapState(['user']),

    methods: {
        fetchCollabs: async function() {
            try {
                const r = await this.$http.get('/my_collabs/');
                this.error = null;
                this.collabs = r.data;
            } catch (e) {
                this.error = e.response.data.error;
            }
            this.requested = true;
        },
        openCollab: function(collab) {
            this.$router
                .push({ name: 'collab', params: { idx: collab } })
                .catch(() => {});
        },
        isNull,
    },

    created: async function() {
        await this.fetchCollabs();
    },
};
</script>

<style lang="scss" scoped>
.pc {
    cursor: pointer;
}
</style>
