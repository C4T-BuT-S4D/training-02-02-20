let url = '';

if (process.env.NODE_ENV === 'development') {
    url = '127.0.0.1:9997';
} else {
    url = window.location.host;
}

const serverUrl = url;

const apiUrl = `http://${serverUrl}/api`;
const wsUrl = `ws://${serverUrl}/api`;

export { apiUrl, wsUrl };
