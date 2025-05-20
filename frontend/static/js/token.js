// static/js/token.js
document.addEventListener('htmx:configRequest', function(e) {
    const token = localStorage.getItem('access_token');
    console.log('HTMX sending token:', token); // Логирование для отладки

    if (token) {
        e.detail.headers['Authorization'] = 'Bearer ' + token;
        // Явно указываем тип контента
        e.detail.headers['Content-Type'] = 'application/x-www-form-urlencoded';
    } else {
        console.error('No token found in localStorage!');
    }
});