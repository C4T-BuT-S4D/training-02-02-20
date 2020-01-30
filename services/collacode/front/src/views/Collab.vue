<template>
    <v-col cols="12" md="12">
        <v-card>
            <v-card-title>Collab #{{ $route.params.idx }}</v-card-title>
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
                        <codemirror
                            v-model="data"
                            :options="cmOption"
                        ></codemirror>
                    </v-container>
                </div>
            </div>
        </v-card>
    </v-col>
</template>

<script>
import { wsUrl } from '@/config';
import DiffMatchPatch from 'diff-match-patch';

export default {
    data: function() {
        return {
            error: null,
            requested: false,
            data: null,
            cmOption: {
                tabSize: 4,
                indentUnit: 4,
                styleActiveLine: true,
                lineNumbers: true,
                theme: 'yonce',
            },
            recvS: null,
            sendS: null,
            senderId: null,
        };
    },

    created: async function() {
        try {
            const r = await this.$http.get(
                `/get_collab/${this.$route.params.idx}/`
            );
            this.error = null;
            const { data, format } = r.data;
            this.data = data;
            this.prevData = data;
            this.cmOption.mode = format;
        } catch (e) {
            this.error = e.response.data.error;
        }
        this.requested = true;

        const self = this;

        self.sendS = new WebSocket(`${wsUrl}/code/`);

        self.sendS.onopen = function() {
            self.sendS.onmessage = function(event) {
                const { sender_id } = JSON.parse(event.data);
                self.senderId = sender_id;

                self.recvS = new WebSocket(`${wsUrl}/subscribe/`);

                self.recvS.onopen = function() {
                    self.recvS.onmessage = function(event) {
                        const { data, sender_id } = JSON.parse(event.data);
                        if (sender_id !== self.senderId) {
                            const dmp = new DiffMatchPatch();
                            const patch = dmp.patch_fromText(data);
                            self.data = dmp.patch_apply(patch, self.data)[0];
                            self.prevData = self.data;
                        }
                    };
                    self.recvS.send(
                        JSON.stringify({ token: self.$route.params.idx })
                    );
                };

                const tick = function() {
                    const dmp = new DiffMatchPatch();
                    const patch = dmp.patch_make(
                        self.prevData === null ? '' : self.prevData,
                        self.data === null ? '' : self.data
                    );
                    const patchText = dmp.patch_toText(patch);
                    if (patchText.length > 0) {
                        self.sendS.send(
                            JSON.stringify({
                                token: self.$route.params.idx,
                                diff: patchText,
                            })
                        );
                    }
                    self.prevData = self.data;
                    setTimeout(tick, 100);
                };

                tick();
            };
        };
    },
};
</script>
