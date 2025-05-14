 // ждем загрузку DOM (гарантирует, что JavaScript будет
    //выполняться только после полной загрузки HTML-структуры
    //страницы.)
    document.addEventListener('DOMContentLoaded', function() {
        const authButton = document.getElementById('authButton'); // кнопка войти
        const authModal = document.getElementById('authModal'); // модальное окно
        const loginForm = document.getElementById('loginForm'); // форма входа
        const registerForm = document.getElementById('registerForm'); // форма реги
        const closeBtn = document.querySelector('.close'); // кнопка закрытия модалки
        const authResponse = document.getElementById('authResponse'); // блок уведомлений
        const passwordInput = document.getElementById('regPassword'); // поле ввода пароля
        const addPlaceBtn = document.getElementById('addPlaceBtn');
        const addPlaceForm = document.getElementById('addPlaceForm');
        const addPlaceModal = document.getElementById('addPlaceModal');
        const addPlaceResult = document.getElementById('addPlaceResult');



        // Вешаем обработчик

        // получаем элементы интерфейса
        // Проверяем токен сразу при загрузке страницы
        const token = localStorage.getItem("access_token");
        if (token) {
            authButton.textContent = 'Профиль'; // Меняем кнопку
            console.log("Токен найден, кнопка обновлена");
        } else {
            console.log("Токена нет, оставляем 'Вход'");
        }



        // функция для показа уведомлений
        function showNotification(message, isSuccess, targetElement = authResponse) {
            authResponse.innerHTML = `
                <div class="notification ${isSuccess ? 'success' : 'error'}">
                    ${message}
                </div>
            `;
            // автоматическое закрытие через 5 сек
            setTimeout(() => authResponse.innerHTML = '', 5000);
        }


        function showAddPlaceForm() {
            addPlaceModal.style.display='block';
            document.body.style.overflow = 'hidden';

        }

        function hideAddPlaceForm(){
            addPlaceModal.style.display='none';
            document.body.style.overflow = 'auto';
        }

        // валидация пароля перед отправкой
        passwordInput?.addEventListener('input', function() {
            if (this.value.length > 0 && this.value.length < 8) {
                this.setCustomValidity('Пароль должен содержать минимум 8 символов');
            } else {
                this.setCustomValidity(''); // при валидном пароле сброс ошибки
            }
        });
        // автоматическое добавление токена к HTMX-запросам
        document.body.addEventListener('htmx:configRequest', function(event) {
        // получаем jwt токен из локального хранилища браузера
        const token = localStorage.getItem("access_token");
        // если токен существует то добавляем заголовок Authorization к запросу
        if (token) {
            event.detail.headers['Authorization'] = `Bearer ${token}`;
        }
    });

        // обработчики открытия/закрытия модального окна
        authButton.addEventListener('click', function(e) {
            e.preventDefault(); // отмена стандартного поведения ссылки
            authModal.style.display = 'block'; // показываем модальное окно
            loginForm.style.display = 'block'; // показ формы входа
            registerForm.style.display = 'none'; // скрываем форму реги
            authResponse.innerHTML = ''; // очищаем уведомления
        });
// переключение на регистрацию
        document.getElementById('showRegister')?.addEventListener('click', function(e) {
            e.preventDefault();
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
            authResponse.innerHTML = '';
        });
// переключение на вход
        document.getElementById('showLogin')?.addEventListener('click', function(e) {
            e.preventDefault();
            registerForm.style.display = 'none';
            loginForm.style.display = 'block';
            authResponse.innerHTML = '';
        });
// закрытие модалки
        closeBtn.addEventListener('click', () => authModal.style.display = 'none');
        // закрытие при клике вне модалки
        window.addEventListener('click', (e) => e.target === authModal && (authModal.style.display = 'none'));

        // обработчик HTMX-запросов

   document.body.addEventListener('htmx:afterRequest', function(e) {
    // Успешные запросы
    if (e.detail.successful) {
        // Обработка успешного входа
        if (e.detail.requestConfig.path === "/jwt/login/") {
            // 1. Парсим ответ
            const response = JSON.parse(e.detail.xhr.responseText);

            // 2. Сохраняем токен
            localStorage.setItem("access_token", response.access_token);

            // 3. Обновляем интерфейс
            authModal.style.display = 'none';
            authButton.textContent = 'Профиль';
            showNotification('Вход выполнен успешно!', true);

            // 4. Перенаправляем (если нужно)
            // window.location.href = "/";
        }

        // Обработка успешной регистрации
        if (e.detail.requestConfig.path === "/users/") {
            showNotification('Регистрация успешна! Теперь войдите в систему', true);
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        }
        if (e.detail.requestConfig.path === "/places/") {
            e.stopImmediatePropagation();
            const resultDiv = document.getElementById('addPlaceResult');
            resultDiv.innerHTML = ''; // Очищаем блок
            if (e.detail.successful) {
                showNotification('Место успешно добавлено!', true, resultDiv);
                setTimeout(() => {
                    addPlaceModal.style.display = 'none';
                    addPlaceForm.reset();
                    addPlaceResult.innerHTML = '';
                }, 4000);
            } else {
                const error = JSON.parse(e.detail.xhr.responseText);
                showNotification(error.detail || "Ошибка добавления", false, resultDiv);
            }



        }
    } else {
                        // обработка ошибок валидации
                try {
                // парсим ответ сервера
                    const error = JSON.parse(e.detail.xhr.responseText);
                    let errorMessage = 'Ошибка при обработке запроса';

                    // специфичные ошибки валидации
                    if (error.detail) {
                        if (Array.isArray(error.detail)) {
                            // обработка ошибок Pydantic
                            errorMessage = error.detail.map(err =>
                                `${err.loc ? err.loc.join('.') + ': ' : ''}${err.msg}`
                            ).join('<br>');
                            // для строковых ошибок
                        } else if (typeof error.detail === 'string') {
                            errorMessage = error.detail;
                        } else if (error.detail.msg) {
                            errorMessage = error.detail.msg;
                        }
                    }

                    // специальная обработка ошибки пароля
                    if (errorMessage.includes('password') || errorMessage.includes('пароль')) {
                        passwordInput?.focus();
                    }

                    showNotification(errorMessage, false);
                } catch {
             // обработка ошибок парсинга
                    showNotification('Ошибка соединения с сервером', false);
                }
    }
    });
    addPlaceBtn?.addEventListener('click', function(e) {
        e.preventDefault();
        const token = localStorage.getItem("access_token");

        if (token) {
            showAddPlaceForm();
        } else {
            authModal.style.display = 'block';
            showNotification('Для добавления места войдите в систему', false);
        }
    });
    window.hideAddPlaceForm = hideAddPlaceForm;
    window.showAddPlaceForm = showAddPlaceForm;
    // Закрытие по клику вне модалки
    window.addEventListener('click', (e) => {
        if (e.target === authModal) {
            authModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
        if (e.target === addPlaceModal) {
            hideAddPlaceForm();
        }

    });
});