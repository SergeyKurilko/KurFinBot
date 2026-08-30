// webapp/static/app.js

import { Accounts } from "./modules/cash_accounts/get_accounts.js";

// Получаем объект Telegram WebApp
const tg = window.Telegram.WebApp;

// Настройка интерфейса
// tg.MainButton.setText('🔄 Обновить');
// tg.MainButton.onClick(() => {
//     goToHomePage();
// });
// tg.MainButton.show();

// Растягиваем на весь экран
tg.expand();

// Сигналим о готовности
tg.ready();

console.log('✅ WebApp загружен!');

// Получаем initData
window.initData = tg.initData;
const initData = window.initData;

// Проверяем, что данные есть
if (!initData) {
    document.getElementById('user-status').textContent = '❌ Ошибка: не в Telegram';
    document.getElementById('user-status').style.color = 'red';
    tg.showAlert('Откройте приложение через Telegram');
} else {
    document.getElementById('user-status').textContent = '🔄 Авторизация...';
    // Авторизуемся
    authenticate();
}

// Функция авторизации
async function authenticate() {
    try {
        const response = await fetch('/api/auth/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-Init-Data': initData
            }
        });

        if (!response.ok) {
            throw new Error('Auth failed');
        }

        const data = await response.json();
        console.log('✅ Авторизован:', data.user);

        // Обновляем UI
        document.getElementById('user-status').textContent =
            `👤 ${data.user.username || 'без юзернейма'}`;

        // Сохраняем пользователя
        window.currentUser = data.user;

        const MainMenuButtons = document.getElementById("main-menu-buttons");
        if (data.user.is_boss) {
            MainMenuButtons.innerHTML = `
                <button id="cashAccountsList" class="main-button">Все счета</button>
            `
            const cashAccountsListButton = document.getElementById("cashAccountsList")
            cashAccountsListButton.onclick = Accounts.getAllCashAccounts
        } else {
            MainMenuButtons.innerHTML = `
                Нет доступа к счетам
            `
        }


    } catch (error) {
        console.error('❌ Ошибка авторизации:', error);
        document.getElementById('user-status').textContent = '❌ Ошибка авторизации';
        document.getElementById('user-status').style.color = 'red';
        tg.showAlert('Ошибка авторизации');
    }
}

// Функция для тестового запроса к API
async function testApi() {
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = '⏳ Загрузка...';

    try {
        // Сначала проверяем ping (без авторизации)
        const pingResponse = await fetch('/api/test/ping');
        const pingData = await pingResponse.json();
        console.log('Ping:', pingData);

        // Теперь получаем данные пользователя
        const userResponse = await fetch('/api/test/me', {
            headers: {
                'X-Telegram-Init-Data': initData
            }
        });

        const userData = await userResponse.json();
        console.log('User data:', userData);

        resultDiv.innerHTML = `
            <div style="background: #f0f0f0; padding: 10px; border-radius: 8px; text-align: left;">
                <strong>✅ API работает!</strong><br>
                <strong>Пользователь:</strong> ${userData.user?.username || 'Не найден'}<br>
                <strong>ID:</strong> ${userData.user?.id || 'Нет'}<br>
                <strong>Босс:</strong> ${userData.user?.is_boss ? 'Да' : 'Нет'}
            </div>
        `;

        tg.showAlert('Тест API успешен!');

    } catch (error) {
        console.error('❌ Ошибка API:', error);
        resultDiv.innerHTML = `
            <div style="background: #ffebee; padding: 10px; border-radius: 8px; color: #c62828;">
                ❌ Ошибка: ${error.message}
            </div>
        `;
        tg.showAlert('Ошибка при тестировании API');
    }
}

// To home
function goToHomePage() {
    const resultDiv = document.getElementById('result');
    const contentHeader = document.getElementById('content-header');
    
    contentHeader.textContent = 'Добро пожаловать в Mini App!';
    resultDiv.innerHTML = '';
    resultDiv.style.display = 'none';

    const MainMenuButtons = document.getElementById("main-menu-buttons");
    if (window.currentUser.is_boss) {
        MainMenuButtons.innerHTML = `
            <button id="cashAccountsList" class="main-button">Все счета</button>
        `
        const cashAccountsListButton = document.getElementById("cashAccountsList")
        cashAccountsListButton.onclick = Accounts.getAllCashAccounts
    } else {
        MainMenuButtons.innerHTML = `
            Нет доступа к счетам
        `
    }
}

window.goToHomePage = goToHomePage;
window.Accounts = Accounts;
window.authenticate = authenticate;

// Делаем testApi глобальной для onclick
window.testApi = testApi;