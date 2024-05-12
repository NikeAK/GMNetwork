# GM Network
[![Telegram channel](https://img.shields.io/endpoint?url=https://runkit.io/damiankrawczyk/telegram-badge/branches/master?url=https://t.me/oxcode1)](https://t.me/oxcode1)

✈️[Telegram Channel](https://t.me/oxcode1)

![img1](data/demo/demo.png)

## 💡Функционал  
| Функционал                                                     | Поддерживается  |
|----------------------------------------------------------------|:---------------:|
| Многопоточность                                                |        ✅       |
| Локальная база данных                                          |        ✅       |
| Поддержка прокси любого формата                                |        ✅       |
| Регистрация аккаунта по реферальному коду                      |        ✅       |
| Daily CHECK-IN                                                 |        ✅       |
| Выполнение квестов на GM Network                               |        ✅       |
| Выполнение квестов QuestN, клейм NFT                           |        🛠️       |
| Сбор информации об аккаунте                                    |        ✅       |
| Экспорт информации об аккаунтах в txt, excel по ключам         |        ✅       |
| Генерация кошельков EVM                                        |        ✅       |

## [⚙️Настройки](https://github.com/NikeAK/GMNetwork/blob/main/data/config.py)
| Настройка                  | Описание                                                        |
|----------------------------|-----------------------------------------------------------------|
| **REFERRAL_CODE**          | Реферальный код                                                 |
| **DO_QUESTN**              | Квесты QuestN (требуются твиттер) - True/False                  |
| **BNB_RPC**                | Провайдер BNB RPC                                               |
| **USE_PROXY**              | Использовать прокси? - True/False                               |
| **LOGGER_PROXY**           | Вывод информацию о статусе прокси - True/False                  |
| **REQUESTSERROR_ATTEMPTS** | Максимальное число попыток неудачных запросов                   |
| **RATELIMIT_SLEEP**        | Время сна, после превышения лимита запросов - [min, max]        |
| **PROXY_CHEKER_TIMEOUT**   | Тайм-аут проверки прокси                                        |
| **EXPORT_SEPARATOR**       | Символ разделения данных для экспорта в TXT                     |
| **EXPORT_DATA**            | Используемые данные для экспорта, записываются через запятую    |

$\color{#58A6FF}\textsf{\Large\&#x24D8;\kern{0.2cm}\normalsize Note}$
**Перед началом работы, заполните $\color{yellow}{\textsf{private-keys.txt}}$ и $\color{yellow}{\textsf{proxy.txt}}$**

## ⚡️Быстрый запуск
1. Запустите $\color{orange}{\textsf{Setup.bat}}$. Этот скрипт автоматически создаст виртуальное окружение, активирует его, установит все необходимые зависимости из файла requirements.txt и удалит не нужные файлы.
2. После успешного выполнения $\color{orange}{\textsf{Setup.bat}}$, вы можете запустить $\color{orange}{\textsf{Main.bat}}$. Этот скрипт активирует виртуальное окружение и запустит софт.

## 🛠️Ручная установка
```shell
~ >>> python -m venv Venv              #Создание виртуального окружения
~ >>> Venv/Scripts/activate            #Активация виртуального окружения
~ >>> pip install -r requirements.txt  #Установка зависимостей
~ >>> python main.py                   #Запуск
```

## 💰DONATION EVM ADDRESS: 
**0x1C6E533DCb9C65BD176D36EA1671F7463Ce8C843**
