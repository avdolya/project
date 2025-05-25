document.addEventListener('htmx:configRequest', function(e) {
    const token = localStorage.getItem('access_token');

    function isTokenExpired(token) {
        if (!token) return true;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (typeof payload.exp !== 'number') {
                console.error("Токен не содержит срок действия (exp)");
                localStorage.removeItem('access_token');
                return true;
            }
            const isExpired = payload.exp < Math.floor(Date.now() / 1000);
            if (isExpired) {
                console.log("Токен просрочен. Удаляем...");
                localStorage.removeItem('access_token');
            }
            return isExpired;
        } catch (e) {
            console.error("Ошибка декодирования токена:", e);
            localStorage.removeItem('access_token');
            return true;
        }
    }


    if (!token || isTokenExpired(token)) {
            localStorage.removeItem('access_token');
            e.detail.shouldSwap = false;
            window.location.href = '/';
            window.showNotification('Сессия истекла! Войдите снова', false);
            return;
    } else {
        e.detail.headers['Authorization'] = 'Bearer ' + token;

        e.detail.headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }

});
