const BASE_URL = '';   

async function apiCall(method, url, body) {
    const options = {
        method: method,
        credentials: 'include',
        headers: {}
    };

    if (body !== undefined) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    }

    const response = await fetch(BASE_URL + url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        
        throw new Error(data.message || 'Something went wrong');
    }

    return data;
}


const api = {
    get:  (url)       => apiCall('GET', url),
    post: (url, body) => apiCall('POST', url, body)
};
