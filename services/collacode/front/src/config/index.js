let url = '';

if (process.env.NODE_ENV === 'development') {
    url = 'http://127.0.0.1:9997';
} else {
    url = 'http://127.0.0.1:9997';
}

const serverUrl = url;

const apiUrl = `${serverUrl}/api`;

export { apiUrl };
