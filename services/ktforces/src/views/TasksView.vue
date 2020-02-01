<template>
    <v-col cols="12" md="12">
        <v-card>
            <v-card-title id="tv-task"
                >Task #{{ $route.params.idx }}</v-card-title
            >
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
                            {{ name }} by
                            <i @click="openUser(author)" class="author">{{
                                author
                            }}</i>
                        </h1>
                        <h1 v-if="flagShow !== null">Flag: {{ flagShow }}</h1>
                        <div
                            class="data mb-3 mt-3 pb-3 pt-3 pl-2 pr-2"
                            id="tv-data"
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
                                id="tv-flag"
                                required
                                outlined
                                class="mt-3"
                            />
                            <div
                                class="red"
                                v-if="flagerror !== null"
                                style="white-space: pre;"
                                id="tv-flag-r"
                            >
                                {{ flagerror }}
                            </div>
                            <div
                                class="green"
                                v-if="flagok !== ''"
                                style="white-space: pre;"
                                id="tv-flag-r"
                            >
                                {{ flagok }}
                            </div>
                            <v-btn
                                class="mt-3"
                                color="blue"
                                @click="submit"
                                id="tv-submit"
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
            flagShow: null,
        };
    },

    methods: {
        openUser: function(username) {
            this.$router
                .push({ name: 'profile', params: { username } })
                .catch(() => {});
        },
        decrypt: async function(data, key, encryption) {
            try {
                data = new Uint8Array(
                    atob(data)
                        .split('')
                        .map(c => c.charCodeAt(0))
                );
                key = new Uint8Array(
                    atob(key)
                        .split('')
                        .map(c => c.charCodeAt(0))
                );
                encryption = new Uint8Array(
                    atob(encryption)
                        .split('')
                        .map(c => c.charCodeAt(0))
                );

                const goCrypto = new window.Go();

                await WebAssembly.instantiate(
                    encryption,
                    goCrypto.importObject
                ).then(function(obj) {
                    let wasm = obj.instance;
                    window.wasmdecrypt = wasm;
                    goCrypto.run(wasm);
                });

                if (key.length != 16) {
                    this.flagerror = 'Invalid key';
                    return [];
                }

                window.wasmdecrypt.exports.allocateKey(16);
                window.wasmdecrypt.exports.allocateData(data.length);
                let keyAddr = window.wasmdecrypt.exports.keyAddr();
                let dataAddr = window.wasmdecrypt.exports.dataAddr();
                let buf = new Uint8Array(
                    window.wasmdecrypt.exports.memory.buffer
                );

                for (let i = keyAddr; i < keyAddr + 16; ++i) {
                    buf[i] = key[i - keyAddr];
                }
                for (let i = dataAddr; i < dataAddr + data.length; ++i) {
                    buf[i] = data[i - dataAddr];
                }

                window.wasmdecrypt.exports.decrypt();

                let resultAddr = window.wasmdecrypt.exports.resultAddr();

                return buf.slice(resultAddr, resultAddr + data.length);
            } catch {
                this.flagerror = 'Error during decryption';
                return [];
            }
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
            const {
                name,
                data,
                key = null,
                flag = null,
                encryption,
                public: pub,
                author,
            } = r.data;
            this.name = name;
            if (key !== null) {
                this.data = JSON.parse(
                    (await this.decrypt(data, key, encryption)).reduce(function(
                        dt,
                        byte
                    ) {
                        return dt + String.fromCharCode(byte);
                    },
                    '')
                ).description;
            } else {
                this.data = 'Protected';
            }
            this.flagShow = flag;
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

.author {
    cursor: pointer;
}
</style>
