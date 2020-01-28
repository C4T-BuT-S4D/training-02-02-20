let url = '';

if (process.env.NODE_ENV === 'development') {
    url = 'http://127.0.0.1:9998';
} else {
    url = 'http://10.10.10.11:9998';
}

const serverUrl = url;

const apiUrl = `${serverUrl}/api`;

export { apiUrl };
