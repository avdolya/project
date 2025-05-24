document.addEventListener('DOMContentLoaded', function() {
    // ====================== DOM Элементы ======================
    const elements = {
        authButton: document.getElementById('authButton'),
        authModal: document.getElementById('authModal'),
        loginForm: document.getElementById('loginForm'),
        registerForm: document.getElementById('registerForm'),
        closeBtn: document.querySelector('.close'),
        authResponse: document.getElementById('authResponse'),
        passwordInput: document.getElementById('regPassword'),
        addPlaceBtn: document.getElementById('addPlaceBtn'),
        addPlaceForm: document.getElementById('addPlaceForm'),
        addPlaceModal: document.getElementById('addPlaceModal'),
        addPlaceResult: document.getElementById('addPlaceResult'),
        showRegister: document.getElementById('showRegister'),
        showLogin: document.getElementById('showLogin')
    };

    // ====================== Инициализация ======================
    initAuthState();
    setupEventListeners();

    // ====================== Основные функции ======================
    function initAuthState() {
        const token = localStorage.getItem("access_token");
        if (token && !isTokenExpired(token)) {
        } else {
            setUnauthenticatedState();
        }
    }

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



    function setUnauthenticatedState() {
        elements.authButton.onclick = (e) => {
            e.preventDefault();
            showModal(elements.authModal);
            elements.loginForm.style.display = 'block';
            elements.registerForm.style.display = 'none';
        };
    }

    // ====================== Вспомогательные функции ======================
    function showNotification(message, isSuccess, targetElement = elements.authResponse) {
        targetElement.innerHTML = `
            <div class="notification ${isSuccess ? 'success' : 'error'}">
                ${message}
            </div>
        `;
        setTimeout(() => targetElement.innerHTML = '', 5000);
    }

    function showModal(modalElement) {
        modalElement.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    function hideModal(modalElement) {
        modalElement.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    // ====================== Обработчики событий ======================
    function setupEventListeners() {
        // Авторизация
        elements.authButton.addEventListener('click', handleAuthButtonClick);
        elements.closeBtn.addEventListener('click', () => hideModal(elements.authModal));
        elements.showRegister?.addEventListener('click', handleShowRegister);
        elements.showLogin?.addEventListener('click', handleShowLogin);

        // Добавление места
        elements.addPlaceBtn?.addEventListener('click', handleAddPlaceClick);

        // Валидация пароля
        elements.passwordInput?.addEventListener('input', validatePassword);

        // Закрытие модалок по клику вне
        window.addEventListener('click', handleOutsideClick);

        // HTMX обработчики
        document.addEventListener('htmx:configRequest', function(e) {
        const token = localStorage.getItem('access_token');
        if (token) {
            e.detail.headers['Authorization'] = 'Bearer ' + token;

            e.detail.headers['Content-Type'] = 'application/x-www-form-urlencoded';
        } else {
            console.error('No token found in localStorage!');
        }
        });

        document.body.addEventListener('htmx:afterRequest', handleHtmxResponse);
    }

    function handleAuthButtonClick(e) {
        e.preventDefault();
        showModal(elements.authModal);
        elements.loginForm.style.display = 'block';
        elements.registerForm.style.display = 'none';
        elements.authResponse.innerHTML = '';
    }

    function handleShowRegister(e) {
        e.preventDefault();
        elements.loginForm.style.display = 'none';
        elements.registerForm.style.display = 'block';
        elements.authResponse.innerHTML = '';
    }

    function handleShowLogin(e) {
        e.preventDefault();
        elements.registerForm.style.display = 'none';
        elements.loginForm.style.display = 'block';
        elements.authResponse.innerHTML = '';
    }

    function handleAddPlaceClick(e) {
        e.preventDefault();
        const token = localStorage.getItem("access_token");
        token ? showModal(elements.addPlaceModal) : (
            showModal(elements.authModal),
            showNotification('Для добавления места войдите в систему', false)
        );
    }

    function validatePassword() {
        if (this.value.length > 0 && this.value.length < 8) {
            this.setCustomValidity('Пароль должен содержать минимум 8 символов');
        } else {
            this.setCustomValidity('');
        }
    }

    function handleOutsideClick(e) {
        if (e.target === elements.authModal) hideModal(elements.authModal);
        if (e.target === elements.addPlaceModal) hideModal(elements.addPlaceModal);
    }



    function handleHtmxResponse(e) {
        if (e.detail.successful) {
            handleSuccessfulResponse(e);
        } else {
            handleErrorResponse(e);
        }
    }

    function handleSuccessfulResponse(e) {
        const path = e.detail.requestConfig.path;

        if (path === "/jwt/login/") {
            const response = JSON.parse(e.detail.xhr.responseText);
            localStorage.setItem("access_token", response.access_token);
            hideModal(elements.authModal);
            setAuthenticatedState();
            showNotification('Вход выполнен успешно!', true);
        }
        else if (path === "/users/") {
            showNotification('Регистрация успешна! Теперь войдите в систему', true);
            elements.loginForm.style.display = 'block';
            elements.registerForm.style.display = 'none';
        }
        else if (path === "/places/") {
            e.stopImmediatePropagation();
            elements.addPlaceResult.innerHTML = '';
            showNotification('Место успешно добавлено!', true, elements.addPlaceResult);
            setTimeout(() => {
                hideModal(elements.addPlaceModal);
                elements.addPlaceForm.reset();
                elements.addPlaceResult.innerHTML = '';
            }, 4000);
        }
    }

    function handleErrorResponse(e) {
        try {
            const error = JSON.parse(e.detail.xhr.responseText);
            let errorMessage = 'Ошибка при обработке запроса';

            if (error.detail) {
                if (Array.isArray(error.detail)) {
                    errorMessage = error.detail.map(err =>
                        `${err.loc ? err.loc.join('.') + ': ' : ''}${err.msg}`
                    ).join('<br>');
                } else if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (error.detail.msg) {
                    errorMessage = error.detail.msg;
                }
            }

            if (errorMessage.includes('password') || errorMessage.includes('пароль')) {
                elements.passwordInput?.focus();
            }

            showNotification(errorMessage, false);
        } catch {
            showNotification('Ошибка соединения с сервером', false);
        }
    }

    // Экспорт функций для глобального доступа
    window.hideAddPlaceForm = () => hideModal(elements.addPlaceModal);
    window.showAddPlaceForm = () => showModal(elements.addPlaceModal);
});