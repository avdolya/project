document.addEventListener('htmx:configRequest', function(e) {
    const token = localStorage.getItem('access_token');

    if (token) {
        e.detail.headers['Authorization'] = 'Bearer ' + token;

        e.detail.headers['Content-Type'] = 'application/x-www-form-urlencoded';
    } else {
        console.error('No token found in localStorage!');
    }
});