<template>
    <v-col cols="12" md="12">
        <v-card>
            <v-card-title>Task #{{ $route.params.idx }}</v-card-title>
            <div v-if="requested">
                <div
                    class="red"
                    v-if="error !== null"
                    style="white-space: pre;"
                >
                    {{ error }}
                </div>
                <div v-if="error === null">
                    <v-container>
                        <h1>
                            {{ name }} by <i>{{ author }}</i>
                        </h1>
                        <div
                            class="data mb-3 mt-3 pb-3 pt-3 pl-2 pr-2"
                            v-html="data"
                        />
                        <div v-if="pub">
                            Task is <span style="color: green">public</span>
                        </div>
                        <div v-if="!pub">
                            Task is <span style="color: red">private</span>
                        </div>
                        <v-form>
                            <v-text-field
                                v-model="flag"
                                label="Flag"
                                required
                                outlined
                                class="mt-3"
                            />
                            <div
                                class="red"
                                v-if="flagerror !== null"
                                style="white-space: pre;"
                            >
                                {{ flagerror }}
                            </div>
                            <div
                                class="green"
                                v-if="flagok !== ''"
                                style="white-space: pre;"
                            >
                                {{ flagok }}
                            </div>
                            <v-btn class="mt-3" color="blue" @click="submit"
                                >Submit</v-btn
                            >
                        </v-form>
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
            error: null,
            requested: false,
            name: null,
            data: null,
            pub: null,
            flag: null,
            author: null,
            flagerror: null,
            flagok: '',
        };
    },

    methods: {
        decrypt: function(data) {
            return atob(data);
        },

        submit: async function() {
            try {
                const r = await this.$http.post(
                    `/tasks/${this.$route.params.idx}/`,
                    {
                        flag: this.flag,
                    }
                );
                this.flagerror = null;
                this.flagok = `OK. Score: ${r.data.score}`;
                await this.$store.dispatch('UPDATE_USER');
            } catch (e) {
                this.flagerror = e.response.data.error;
                this.flagok = '';
            }
        },
    },

    created: async function() {
        try {
            const r = await this.$http.get(`/tasks/${this.$route.params.idx}/`);
            this.error = null;
            const { name, data, key, encryption, public: pub, author } = r.data;
            this.name = name;
            this.data = this.decrypt(data, key, encryption);
            this.pub = pub;
            this.author = author;
        } catch (e) {
            this.error = e.response.data.error;
        }
        this.requested = true;
    },
};
</script>

<style lang="scss" scoped>
.data {
    background-color: rgba($color: #222222, $alpha: 0.5);
    border-radius: 20px;
    white-space: pre-wrap;
}
</style>
