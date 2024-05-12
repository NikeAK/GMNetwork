#-------------------------------------- Settings ------------------------------------------------

REFERRAL_CODE = 'KI5W'                  # Реферальный код

DO_QUESTN = False                       # Квесты QuestN (требуются твиттер) - True/False
BNB_RPC = 'https://rpc.ankr.com/bsc'    # Провайдер bnb

USE_PROXY = True                        # Использовать прокси? - True/False
LOGGER_PROXY = False                    # Вывод информацию о статусе прокси - True/False

REQUESTSERROR_ATTEMPTS = 7              # Максимальное число попыток неудачных запросов
RATELIMIT_SLEEP = [35, 60]              # Время сна, после превышения лимита запросов - [min, max]

PROXY_CHEKER_TIMEOUT = 5                # Тайм-аут для проверки прокси

#-------------------------------------- Export -----------------------------------------------------
'''
Доступные данные для экспорта:

id                  - Номер аккаунта в БД

address             - Адресс кошелька EVM
privatekey          - Приватный ключ EVM
twitter_token       - Твиттер auth_token
proxy               - Прокси привязанный к аккаунты

balance_bnb         - Баланс в сети bnb
claim_mission       - QuestN GM Mission ❌✅
claim_network       - QuestN GM Network ❌✅

checkin             - Последний CHECK-IN ❌✅
balance             - Баланс аккаунта

id_gm               - Номер аккаунта в GM Network
email               - Email привязанный к аккаунту (...)
invite_code         - Реферальный код у аккаунта

agent_id            - Номер агента
agent_nft_id        - NFT ID агента
agent_token_id      - Токен ID агента
agent_name          - Имя агента
agent_description   - Описание агента
agent_image         - Изображение агента
agent_rarity        - Редкость агента
agent_energy        - Доход агента

boost               - Множитель
level               - Уровень

EXPORT_DATA - Используемые данные для экспорта, записываются через запятую [test1, test2, ...]
EXPORT_SEPARATOR - Символ разделения данных для экспорта в TXT

'''

EXPORT_SEPARATOR = ':'
EXPORT_DATA = 'agent_id, checkin'

