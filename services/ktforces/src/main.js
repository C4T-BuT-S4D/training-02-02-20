import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import VueForceNextTick from 'vue-force-next-tick';
import axios from 'axios';
import { apiUrl } from '@/config';

Vue.use(VueForceNextTick);

const goCrypto = new window.Go();

fetch('/wasm/captcha.wasm')
    .then(resp => resp.arrayBuffer())
    .then(bytes =>
        WebAssembly.instantiate(bytes, goCrypto.importObject).then(function(
            obj
        ) {
            let wasm = obj.instance;
            window.wasmcaptcha = wasm;
            goCrypto.run(wasm);
        })
    )
    .then(function() {
        fetch('/wasm/crypto.wasm')
            .then(resp => resp.arrayBuffer())
            .then(bytes => {
                window.encryptwasm = new Uint8Array(bytes);
                WebAssembly.instantiate(bytes, goCrypto.importObject).then(
                    function(obj) {
                        let wasm = obj.instance;
                        window.wasmcrypto = wasm;
                        goCrypto.run(wasm);
                    }
                );
            })
            .then(function() {
                Vue.config.productionTip = false;

                axios.defaults.baseURL = apiUrl;
                axios.defaults.withCredentials = true;

                Vue.prototype.$http = axios;
                store.$http = axios;

                new Vue({
                    router,
                    store,
                    vuetify,
                    render: h => h(App),
                }).$mount('#app');
            });
    });
