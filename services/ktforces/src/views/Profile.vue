<template>
    <v-col cols="12" md="12">
        <v-card>
            <v-card-title>User {{ $route.params.username }}</v-card-title>
            <div v-if="requested">
                <div
                    class="red"
                    v-if="error !== null"
                    style="white-space: pre;"
                >
                    {{ error }}
                </div>
                <div v-if="error === null" id="user-view">
                    <v-container>
                        <div>Name: {{ name }}</div>
                        <div>Username: {{ username }}</div>
                        <div>Score: {{ score }}</div>
                    </v-container>
                </div>
            </div>
        </v-card>
    </v-col>
</template>

<script>
export default {
    data: function() {
        return {
            requested: false,
            error: null,
            username: null,
            name: null,
            score: null,
        };
    },

    created: async function() {
        try {
            const r = await this.$http.get(
                `/users/profile/${this.$route.params.username}/`
            );
            this.error = null;
            const { username, name, score } = r.data;
            this.username = username;
            this.name = name;
            this.score = score;
        } catch (e) {
            this.error = e.response.data.error;
        }
        this.requested = true;
    },
};
</script>
