<template>
    <v-col cols="12" md="12">
        <v-card>
            <v-card-title>Create collab</v-card-title>
            <v-form>
                <v-container>
                    <v-text-field
                        v-model="format"
                        label="Format"
                        required
                        outlined
                    />
                    <span
                        class="red"
                        v-if="error !== null"
                        style="white-space: pre;"
                        >{{ error }}
                    </span>
                </v-container>
            </v-form>
            <v-btn class="ml-3 mb-3" color="blue" @click="submit">Create</v-btn>
        </v-card>
    </v-col>
</template>

<script>
export default {
    data: function() {
        return {
            error: null,
            format: 'text/x-c++src',
        };
    },

    methods: {
        submit: async function() {
            try {
                const r = await this.$http.post('/new_collab/', {
                    format: this.format,
                });
                this.error = null;
                const { token: idx } = r.data;
                this.$router.push({ name: 'collab', params: { idx } });
            } catch (e) {
                this.error = e.response.data.error;
            }
        },
    },
};
</script>
