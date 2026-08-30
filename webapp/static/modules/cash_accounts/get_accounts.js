// webapp/static/modules/cash_accounts/get_accounts.js

export const Accounts = {
        handleApiError(response, data) {
        // Сначала проверяем статус
        if (response.status === 422) {
            // Ошибка валидации Pydantic
            if (data.detail && Array.isArray(data.detail)) {
                // Форматируем ошибки валидации
                const errors = data.detail.map(err => {
                    // Получаем название поля
                    const field = err.loc?.join('.') || 'поле';
                    // Получаем сообщение об ошибке
                    let msg = err.msg;
                    // Если есть контекст с допустимыми значениями
                    if (err.ctx) {
                        if (err.ctx.allowed) {
                            msg += ` (допустимые: ${err.ctx.allowed.join(', ')})`;
                        }
                        if (err.ctx.actual) {
                            msg += ` (получено: ${err.ctx.actual})`;
                        }
                    }
                    return `${field}: ${msg}`;
                });
                return errors.join('; ');
            }
            return data.detail || 'Ошибка валидации данных';
        }
        
        if (response.status === 400) {
            return data.detail || 'Неверный запрос';
        }
        
        if (response.status === 403) {
            return 'У вас нет прав для выполнения этого действия';
        }
        
        if (response.status === 404) {
            return 'Запрашиваемый ресурс не найден';
        }
        
        if (response.status === 500) {
            return 'Внутренняя ошибка сервера. Попробуйте позже.';
        }
        
        return data.detail || data.message || 'Неизвестная ошибка';
    },

    // Получение деталей конкретного счета
    async getCashAccountById(accountId) {
        const resultDiv = document.getElementById('result');
        const contentHeader = document.getElementById('content-header');
        const cashAccountsListButton = document.getElementById('cashAccountsList');
        resultDiv.style.display = 'block';
        resultDiv.textContent = '⏳ Загрузка...';

        try {
            const response = await fetch(`/api/cash/cash-accounts/${accountId}`, {
                headers: {
                    'X-Telegram-Init-Data': window.initData // Используем window.initData
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка загрузки');
            }

            const data = await response.json();
            const account = data.account;

            contentHeader.textContent = `Счет: ${account.title}`;
            cashAccountsListButton.textContent = 'Назад';
            cashAccountsListButton.onclick = this.getAllCashAccounts.bind(this);

            let resultDivHtml = `
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666;">Название:</span>
                        <span style="font-weight: 500;">${account.title}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666;">Баланс:</span>
                        <span style="font-weight: 500; font-size: 18px;">${account.balance} ${account.currency}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666;">Валюта:</span>
                        <span style="font-weight: 500;">${account.currency}</span>
                    </div>
            `;
            
            if (account.balance_in_rubles) {
                resultDivHtml += `
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #666;">В рублях примерно:</span>
                        <span style="font-weight: 500;">${account.balance_in_rubles}</span>
                    </div>
                `;
            }

            // Редактирование счета
            let changeAccountButtons = `
            <div class="change-account-buttons">
                <span class="change-account-header">Редактировать счет:</span>
                <button onclick="" id="changeAccounteBalanceButton" class="change-account-button">Изменить баланс</button>
                <button id="changeAccountTitleButton" class="change-account-button">Изменить название</button>
                <button id="changeAccountCurrencyButton" class="change-account-button">Изменить валюту</button>
                <hr style="margin-top: 10px;">
                <button id="deleteAccountButton" class="change-account-button-danger">Удаление счета</button>
            </div>
            `
            resultDivHtml += changeAccountButtons

            resultDivHtml += `</div>`;

            // Отображаем детальную информацию
            resultDiv.innerHTML = resultDivHtml;
            const changeAccounteBalanceButton = document.getElementById("changeAccounteBalanceButton");
            const changeAccountTitleButton = document.getElementById("changeAccountTitleButton");
            const changeAccountCurrencyButton = document.getElementById("changeAccountCurrencyButton");
            const deleteAccountButton = document.getElementById("deleteAccountButton");
            changeAccounteBalanceButton.onclick = this.changeBalance.bind(this, account.id, account.title, account.balance);
            changeAccountTitleButton.onclick = this.changeAccountTitle.bind(this, account.id, account.title, account.balance);
            changeAccountCurrencyButton.onclick = this.changeAccountCurrency.bind(this, account.id, account.title, account.currency);
            deleteAccountButton.onclick = this.deleteAccount.bind(this, account.id, account.title);

        } catch (error) {
            console.error('Ошибка:', error);
            resultDiv.textContent = `❌ ${error.message || 'Ошибка загрузки счета'}`;
        }
    },

    // Получение всех cash accounts
    async getAllCashAccounts() {
        const resultDiv = document.getElementById('result');
        const contentHeader = document.getElementById('content-header');
        const cashAccountsListButton = document.getElementById('cashAccountsList');
        resultDiv.style.display = 'block';
        resultDiv.textContent = '⏳ Загрузка...';

        try {
            const cashAccountsResponse = await fetch('/api/cash/cash-accounts', {
                headers: {
                    'X-Telegram-Init-Data': window.initData // Используем window.initData
                }
            });
            const cashAccountsData = await cashAccountsResponse.json();
            const cashAccountsList = cashAccountsData.accounts;
            contentHeader.textContent = 'Все счета';

            cashAccountsListButton.textContent = 'Назад';
            cashAccountsListButton.onclick = window.goToHomePage;

            let cardsHTML = '<div style="display: flex; flex-direction: column; gap: 8px;">';

            if (Array.isArray(cashAccountsList) && cashAccountsList.length > 0) {
                cashAccountsList.forEach((cashAccount) => {
                    cardsHTML += `
                        <div class="cash-account-card">
                            <div class="cash-account-row">
                                <span style="font-weight: 500; overflow: hidden; text-overflow: ellipsis;">${cashAccount.title || '-'}</span>
                                <span style="color: #666; font-size: 14px;">${cashAccount.balance || '0'} ${cashAccount.currency || ''}</span>
                            </div>
                            <button onclick="window.Accounts.getCashAccountById(${cashAccount.id})" class="account-detail-button">Открыть</button>
                        </div>
                    `;
                });
            } else {
                cardsHTML += '📭 Нет доступных счетов';
            }
            cardsHTML += `
                <hr style="margin-top: 15px">
                <button id="addNewAccount" class="add-new-account-button">Добавить счет +</button>
            `
            cardsHTML += '</div>';
            resultDiv.innerHTML = cardsHTML;
            const addNewAccountButton = document.getElementById("addNewAccount");
            addNewAccountButton.onclick = Accounts.confirmCreateNewAccount.bind(this);

        } catch (error) {
            console.error('Ошибка:', error);
            resultDiv.textContent = '❌ Ошибка загрузки';
        }
    },

    async changeBalance (cahAccountId, cahAccountTitle, cashAccountBalance) {
        const resultDiv = document.getElementById('result');
        const contentHeader = document.getElementById('content-header');
        resultDiv.style.display = 'block';
        contentHeader.textContent = `Изменение баланса для счета: ${cahAccountTitle}`;

        let resultTextContent = `
        <div class="change-balance-form">
            <span class="current-balance-title">Текущий баланс счета: ${cashAccountBalance}</span>
            <label for="newBalanceInput">Изменить баланс</label>
            <input class="change-balance-input" id="newBalanceInput" name="newBalance" type="number" placeholder="новый баланс" min="1">
            <div id="error-message" style="color: red; font-size: 14px; margin: 5px 0; display: none;"></div>
            <div class="confirm-cancel-buttons">
                <button id="confirmChangeBalance" class="confirm-button">Сохранить</button>
                <button id="cancelChangeBalance" class="cancel-button">Отмена</button>
            </div>
        </div>    
        `
        resultDiv.innerHTML = resultTextContent;

        const confirmChangeBalanceButton = document.getElementById("confirmChangeBalance");
        const cancelChangeBalanceButton = document.getElementById("cancelChangeBalance");
        confirmChangeBalanceButton.onclick = this.confirmChangeBalance.bind(this, cahAccountId);
        cancelChangeBalanceButton.onclick = this.getCashAccountById.bind(this, cahAccountId);
    },

    async changeAccountTitle (cahAccountId, cahAccountTitle, cashAccountBalance) {
        const resultDiv = document.getElementById('result');
        const contentHeader = document.getElementById('content-header');
        resultDiv.style.display = 'block';
        contentHeader.textContent = `Изменение названия счета: ${cahAccountTitle}`;

        let resultTextContent = `
        <div class="change-balance-form">
            <span class="current-balance-title">Текущее название счета: ${cahAccountTitle}</span>
            <label for="newAccountTitleInput">Изменить название</label>
            <input class="change-account-title-input" id="newAccountTitleInput" name="newTitle" type="text" placeholder="новое название" minlength="3" maxlength="55">
            <div id="error-message" style="color: red; font-size: 14px; margin: 5px 0; display: none;"></div>
            <div class="confirm-cancel-buttons">
                <button id="confirmChangeAccountTitle" class="confirm-button">Сохранить</button>
                <button id="cancelChangeAccountTitle" class="cancel-button">Отмена</button>
            </div>
        </div>    
        `
        resultDiv.innerHTML = resultTextContent;

        const confirmChangeAccountTitle = document.getElementById("confirmChangeAccountTitle");
        const cancelChangeAccountTitle = document.getElementById("cancelChangeAccountTitle");
        confirmChangeAccountTitle.onclick = this.confirmChangeAccountTitle.bind(this, cahAccountId);
        cancelChangeAccountTitle.onclick = this.getCashAccountById.bind(this, cahAccountId);
    },

    async changeAccountCurrency (cahAccountId, cahAccountTitle, cashAccountCurrency) {
        const resultDiv = document.getElementById('result');
        const contentHeader = document.getElementById('content-header');
        resultDiv.style.display = 'block';
        contentHeader.textContent = `Изменение валюты счета: ${cahAccountTitle}`;

        let resultTextContent = `
        <div class="change-balance-form">
            <span class="current-balance-title">Текущая валюта: ${cashAccountCurrency}</span>
            <label for="currencyType">Изменить валюту</label>
            <select id="currencyType" name="select">
                <option value="RUB" selected>Рубль</option>
                <option value="USD">Доллар США</option>
            </select>
            <div id="error-message" style="color: red; font-size: 14px; margin: 5px 0; display: none;"></div>
            <div class="confirm-cancel-buttons">
                <button id="confirmChangeAccountCurrency" class="confirm-button">Сохранить</button>
                <button id="cancelChangeAccountCurrency" class="cancel-button">Отмена</button>
            </div>
        </div>    
        `
        resultDiv.innerHTML = resultTextContent;

        const confirmChangeAccountCurrency = document.getElementById("confirmChangeAccountCurrency");
        const cancelChangeAccountCurrency = document.getElementById("cancelChangeAccountCurrency");
        confirmChangeAccountCurrency.onclick = this.confirmChangeAccountCurrency.bind(this, cahAccountId);
        cancelChangeAccountCurrency.onclick = this.getCashAccountById.bind(this, cahAccountId);
    },

    async deleteAccount (cahAccountId, cahAccountTitle) {
        const resultDiv = document.getElementById('result');
        const contentHeader = document.getElementById('content-header');
        resultDiv.style.display = 'block';
        contentHeader.textContent = `Удаление счета: ${cahAccountTitle}`;

        let resultTextContent = `
        <div class="change-balance-form">
            <h2 style="color:red; margin-bottom: 7px;">ВНИМАНИЕ! Вы хотите удалить счет: "${cahAccountTitle}" ?</h2>
            <div id="error-message" style="color: red; font-size: 14px; margin: 5px 0; display: none;"></div>
            <div class="confirm-cancel-buttons">
                <button id="confirmDeleteAccount" class="confirm-button-danger">Удалить</button>
                <button id="cancelDeleteAccount" class="cancel-button">Отмена</button>
            </div>
        </div>    
        `
        resultDiv.innerHTML = resultTextContent;

        const confirmDeleteAccountButton = document.getElementById("confirmDeleteAccount");
        const cancelDeleteAccountButton = document.getElementById("cancelDeleteAccount");
        confirmDeleteAccountButton.onclick = this.confirmDeleteAccount.bind(this, cahAccountId);
        cancelDeleteAccountButton.onclick = this.getCashAccountById.bind(this, cahAccountId);
    },

    async confirmChangeBalance(cashAccountId) {
        const errorDiv = document.getElementById('error-message');
        const resultDiv = document.getElementById('result');
        const newBalanceInput = document.getElementById("newBalanceInput");
        const newBalanceInputValue = newBalanceInput.value;
        
        // Проверка на пустое значение
        if (!newBalanceInputValue || newBalanceInputValue.trim() === '') {
            if (errorDiv) {
                errorDiv.textContent = '❌ Введите новое значение баланса';
                errorDiv.style.display = 'block';
            }
            return;
        }
        
        const newBalance = parseFloat(newBalanceInputValue);
        
        // Проверка на число
        if (isNaN(newBalance)) {
            if (errorDiv) {
                errorDiv.textContent = '❌ Введите корректное число';
                errorDiv.style.display = 'block';
            }
            return;
        }
        
        // Проверка на положительное число
        if (newBalance < 0) {
            if (errorDiv) {
                errorDiv.textContent = '❌ Баланс не может быть отрицательным';
                errorDiv.style.display = 'block';
            }
            return;
        }
        
        try {
            resultDiv.textContent = '⏳ Сохранение...';
            
            const response = await fetch(`/api/cash/cash-accounts/${cashAccountId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': window.initData
                },
                body: JSON.stringify({ 
                    balance: newBalance 
                })
            });
            
            // Проверяем ответ
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || errorData.message || 'Ошибка обновления баланса';
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            console.log('Баланс обновлен:', data);
            
            // Показываем успешное сообщение
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert('✅ Баланс успешно обновлен!');
            }
            
            // Обновляем отображение счета
            await this.getCashAccountById(cashAccountId);
            
        } catch (error) {
            console.error('Ошибка:', error);
            
            // Показываем ошибку
            if (errorDiv) {
                errorDiv.textContent = `❌ ${error.message}`;
                errorDiv.style.display = 'block';
            } else {
                // Если errorDiv не найден, показываем в resultDiv
                resultDiv.innerHTML = `
                    <div style="color: red; padding: 10px; background: #ffebee; border-radius: 8px;">
                        ❌ Ошибка: ${error.message}
                    </div>
                    <button onclick="window.Accounts.getCashAccountById(${cashAccountId})" 
                            style="margin-top: 10px; padding: 8px 16px; border: none; border-radius: 6px; background: #4CAF50; color: white; cursor: pointer;">
                        Назад
                    </button>
                `;
            }
            
            // Также показываем через Telegram Alert
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert(`❌ ${error.message}`);
            }
        }
    },

    async confirmChangeAccountTitle(cashAccountId) {
        const errorDiv = document.getElementById('error-message');
        const resultDiv = document.getElementById('result');
        const newAccountTitleInput = document.getElementById("newAccountTitleInput");
        const newAccountTitleInputValue = newAccountTitleInput.value;
        
        // Проверка на пустое значение
        if (!newAccountTitleInputValue || newAccountTitleInputValue.trim() === '') {
            if (errorDiv) {
                errorDiv.textContent = '❌ Введите новое название';
                errorDiv.style.display = 'block';
            }
            return;
        }

        // Проверка длины названия 
        if (newAccountTitleInputValue.trim().length < 3 || newAccountTitleInputValue.trim().length > 55) {
            if (errorDiv) {
                errorDiv.textContent = '❌ Название должно быть от 3 до 55 символов.';
                errorDiv.style.display = 'block';
            }
            return;
        }
        
        try {
            resultDiv.textContent = '⏳ Сохранение...';
            
            const response = await fetch(`/api/cash/cash-accounts/${cashAccountId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': window.initData
                },
                body: JSON.stringify({ 
                    title: newAccountTitleInputValue 
                })
            });
            
            const data = await response.json();
            if (!response.ok) {
                const errorMessage = this.handleApiError(response, data);
                throw new Error(errorMessage);
            }

            console.log('Название счета обновлено:', data);
            
            // Показываем успешное сообщение
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert('✅ Название успешно изменено!');
            }
            
            // Обновляем отображение счета
            await this.getCashAccountById(cashAccountId);
            
        } catch (error) {
            console.error('Ошибка:', error);
            
            // Показываем ошибку
            if (errorDiv) {
                errorDiv.textContent = `❌ ${error.message}`;
                errorDiv.style.display = 'block';
            } else {
                // Если errorDiv не найден, показываем в resultDiv
                resultDiv.innerHTML = `
                    <div style="color: red; padding: 10px; background: #ffebee; border-radius: 8px;">
                        ❌ Ошибка: ${error.message}
                    </div>
                    <button onclick="window.Accounts.getCashAccountById(${cashAccountId})" 
                            style="margin-top: 10px; padding: 8px 16px; border: none; border-radius: 6px; background: #4CAF50; color: white; cursor: pointer;">
                        Назад
                    </button>
                `;
            }
            
            // Также показываем через Telegram Alert
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert(`❌ ${error.message}`);
            }
        }
    },

    async confirmChangeAccountCurrency(cashAccountId) {
        const errorDiv = document.getElementById('error-message');
        const resultDiv = document.getElementById('result');
        const newAccountCurrencySelect = document.getElementById("currencyType");
        const newAccountCurrencySelectValue = newAccountCurrencySelect.value;
        
        // Проверка на пустое значение
        if (!newAccountCurrencySelectValue || newAccountCurrencySelectValue.trim() === '') {
            if (errorDiv) {
                errorDiv.textContent = '❌ Выберите тип валюты';
                errorDiv.style.display = 'block';
            }
            return;
        }
        
        try {
            resultDiv.textContent = '⏳ Сохранение...';
            
            const response = await fetch(`/api/cash/cash-accounts/${cashAccountId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': window.initData
                },
                body: JSON.stringify({ 
                    currency: newAccountCurrencySelectValue 
                })
            });
            
            const data = await response.json();
            if (!response.ok) {
                const errorMessage = this.handleApiError(response, data);
                throw new Error(errorMessage);
            }

            console.log('Тип валюты обновлен:', data);
            
            // Показываем успешное сообщение
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert('✅ Тип валюты успешно изменен');
            }
            
            // Обновляем отображение счета
            await this.getCashAccountById(cashAccountId);
            
        } catch (error) {
            console.error('Ошибка:', error);
            
            // Показываем ошибку
            if (errorDiv) {
                errorDiv.textContent = `❌ ${error.message}`;
                errorDiv.style.display = 'block';
            } else {
                // Если errorDiv не найден, показываем в resultDiv
                resultDiv.innerHTML = `
                    <div style="color: red; padding: 10px; background: #ffebee; border-radius: 8px;">
                        ❌ Ошибка: ${error.message}
                    </div>
                    <button onclick="window.Accounts.getCashAccountById(${cashAccountId})" 
                            style="margin-top: 10px; padding: 8px 16px; border: none; border-radius: 6px; background: #4CAF50; color: white; cursor: pointer;">
                        Назад
                    </button>
                `;
            }
            
            // Также показываем через Telegram Alert
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert(`❌ ${error.message}`);
            }
        }
    },

    async confirmDeleteAccount(cashAccountId) {
       const errorDiv = document.getElementById('error-message');
        const resultDiv = document.getElementById('result');
    
        try {
            resultDiv.textContent = '⏳ Удаление...';
            
            const response = await fetch(`/api/cash/cash-accounts/${cashAccountId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': window.initData
                },
            });
            
            const data = await response.json();
            if (!response.ok) {
                const errorMessage = this.handleApiError(response, data);
                throw new Error(errorMessage);
            }

            console.log('Счет удален:', data);
            
            // Показываем успешное сообщение
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert('✅ Счет удален');
            }

            // Возвращаемся к списку счетов
            await this.getAllCashAccounts();
            
            
        } catch (error) {
            console.error('Ошибка:', error);
            
            // Показываем ошибку
            if (errorDiv) {
                errorDiv.textContent = `❌ ${error.message}`;
                errorDiv.style.display = 'block';
            } else {
                // Если errorDiv не найден, показываем в resultDiv
                resultDiv.innerHTML = `
                    <div style="color: red; padding: 10px; background: #ffebee; border-radius: 8px;">
                        ❌ Ошибка: ${error.message}
                    </div>
                    <button onclick="window.Accounts.getCashAccountById(${cashAccountId})" 
                            style="margin-top: 10px; padding: 8px 16px; border: none; border-radius: 6px; background: #4CAF50; color: white; cursor: pointer;">
                        Назад
                    </button>
                `;
            }
            
            // Также показываем через Telegram Alert
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert(`❌ ${error.message}`);
            }
        } 
    },

    async confirmCreateNewAccount() {
        const errorDiv = document.getElementById('error-message');
        const resultDiv = document.getElementById('result');
        
        try {
            resultDiv.textContent = '⏳ Сохранение...';
            
            const response = await fetch(`/api/cash/cash-accounts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': window.initData
                },
            });
            
            const data = await response.json();
            if (!response.ok) {
                const errorMessage = this.handleApiError(response, data);
                throw new Error(errorMessage);
            }

            console.log('Создан новый счет:', data[0]);
            console.log('Создан новый счет id:', data[0].cash_account_id);
            
            // Показываем успешное сообщение
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert('✅ Новый счет создан');
            }
            
            // Обновляем отображение счета
            await Accounts.getCashAccountById(data[0].cash_account_id);
            
        } catch (error) {
            console.error('Ошибка:', error);
            
            // Показываем ошибку
            if (errorDiv) {
                errorDiv.textContent = `❌ ${error.message}`;
                errorDiv.style.display = 'block';
            } else {
                // Если errorDiv не найден, показываем в resultDiv
                resultDiv.innerHTML = `
                    <div style="color: red; padding: 10px; background: #ffebee; border-radius: 8px;">
                        ❌ Ошибка: ${error.message}
                    </div>
                    <button onclick="window.Accounts.getCashAccountById(${cashAccountId})" 
                            style="margin-top: 10px; padding: 8px 16px; border: none; border-radius: 6px; background: #4CAF50; color: white; cursor: pointer;">
                        Назад
                    </button>
                `;
            }
            
            // Также показываем через Telegram Alert
            if (window.Telegram?.WebApp) {
                window.Telegram.WebApp.showAlert(`❌ ${error.message}`);
            }
        }
    }
};