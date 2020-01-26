<template>
    <v-col cols="12" md="12">
        <v-card>
            <v-card-title>Create task</v-card-title>
            <v-form>
                <v-container>
                    <v-text-field
                        v-model="name"
                        label="Name"
                        required
                        outlined
                    />
                    <v-textarea
                        v-model="description"
                        label="Description"
                        required
                        outlined
                    />
                    <v-text-field
                        v-model="flag"
                        label="Flag"
                        required
                        outlined
                    />
                    <v-checkbox v-model="pub" label="public" />
                    <span
                        class="red"
                        v-if="error !== null"
                        style="white-space: pre;"
                        >{{ error }}
                    </span>
                </v-container>
            </v-form>
            <v-btn class="ml-3 mb-3" color="blue" @click="submit">Create</v-btn>
            <div v-if="captcha">
                <span class="mb-3 ml-3">Captcha: </span>
                <v-progress-circular
                    indeterminate
                    color="purple"
                    class="mb-3 ml-3"
                />
            </div>
        </v-card>
    </v-col>
</template>

<script>
export default {
    data: function() {
        return {
            error: null,
            name: null,
            description: null,
            flag: null,
            pub: false,
            captcha: false,
        };
    },

    methods: {
        dec2hex: function(dec) {
            return ('0' + dec.toString(16)).substr(-2);
        },

        generateId: function(len) {
            let arr = new Uint8Array(len);
            window.crypto.getRandomValues(arr);
            return arr;
        },

        encrypt: function(data, key) {
            if (key.length != 16) {
                return '';
            }

            window.wasmcrypto.exports.allocateKey(16);
            window.wasmcrypto.exports.allocateData(data.length);
            let keyAddr = window.wasmcrypto.exports.keyAddr();
            let dataAddr = window.wasmcrypto.exports.dataAddr();
            let buf = new Uint8Array(window.wasmcrypto.exports.memory.buffer);

            for (let i = keyAddr; i < keyAddr + 16; ++i) {
                buf[i] = key[i - keyAddr];
            }
            for (let i = dataAddr; i < dataAddr + data.length; ++i) {
                buf[i] = data.charCodeAt(i - dataAddr);
            }

            window.wasmcrypto.exports.encrypt();

            let resultAddr = window.wasmcrypto.exports.resultAddr();

            return buf.slice(resultAddr, resultAddr + data.length);
        },

        submit: async function() {
            let key, nonce;
            try {
                const r = await this.$http.get('/captcha/');
                key = r.data.key;
                nonce = r.data.nonce;
                this.error = null;
            } catch (e) {
                this.error = e.response.data.error;
                return;
            }
            this.captcha = true;
            await this.$forceNextTick();
            window.wasmcaptcha.exports.allocateNonce(nonce.length);
            let buf = new Uint8Array(window.wasmcaptcha.exports.memory.buffer);
            let nonceAddr = window.wasmcaptcha.exports.nonceAddr();
            for (let i = nonceAddr; i < nonceAddr + nonce.length; ++i) {
                buf[i] = nonce.charCodeAt(i - nonceAddr);
            }
            let captcha = window.wasmcaptcha.exports.captcha();
            this.captcha = false;
            const form = {
                task: {},
                pow: {
                    key: key,
                    nonce: nonce,
                    answer: captcha.toString(),
                },
            };
            const enckey = this.generateId(16);
            const data = JSON.stringify({ description: this.description });
            form.task = {
                name: this.name,
                data: btoa(
                    this.encrypt(data, enckey).reduce(function(data, byte) {
                        return data + String.fromCharCode(byte);
                    }, '')
                ),
                key: btoa(
                    enckey.reduce(function(data, byte) {
                        return data + String.fromCharCode(byte);
                    }, '')
                ),
                flag: this.flag,
                encryption: btoa(
                    window.encryptwasm.reduce(function(data, byte) {
                        return data + String.fromCharCode(byte);
                    }, '')
                ),
                public: this.pub,
            };
            try {
                const r = await this.$http.post('/tasks/', form);
                this.error = null;
                const { id: idx } = r.data;
                this.$router.push({ name: 'task', params: { idx } });
            } catch (e) {
                this.error = e.response.data.error;
            }
        },
    },
};
</script>
