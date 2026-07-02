from application import *
from platform import system,node
from utils.g import clients, rootdir
from ipaddress import ip_address

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

# --- 允許下載 NAS 對應腳本的 IP（連續範圍以 (起, 迄) 表示，含頭尾）---
ALLOWED_IP_RANGES = [
    (ip_address('140.123.106.210'), ip_address('140.123.106.248')),  # 140.123.106.210 ~ .248
    (ip_address('140.123.106.37'),  ip_address('140.123.106.37')),   # 140.123.106.37
    (ip_address('127.0.0.1'),       ip_address('127.0.0.1')),        # 本機測試
]

def _is_allowed_ip(ip_str:str) -> bool:
    """檢查來源 IP 是否在允許的 IP 範圍內。"""
    try:
        ip = ip_address(ip_str)
    except ValueError:
        return False
    return any(start <= ip <= end for start, end in ALLOWED_IP_RANGES)

def _send_nas_script(filename:str):
    """提供 NAS 網路磁碟機腳本，僅限白名單 IP 下載（腳本含明文帳密）。"""
    ip = get_remote_addr()
    if not _is_allowed_ip(ip):
        logger.warning(f"[{ip}] 嘗試從非白名單 IP 下載 {filename}，已拒絕")
        abort(403)
    return send_file(
        rootdir / 'script' / filename,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream',
    )

@tools_bp.route('/lab_NAS.cmd', methods=['GET'])
def download_lab_nas_cmd():
    """Windows 版網路磁碟機對應腳本。"""
    return _send_nas_script('lab_NAS.cmd')

@tools_bp.route('/lab_NAS.sh', methods=['GET'])
def download_lab_nas_sh():
    """Linux / macOS 版網路磁碟機掛載腳本。"""
    return _send_nas_script('lab_NAS.sh')

# --- 新增：抓取即時油價的輔助函式 ---
def get_live_gas_price():
    """
    從經濟部能源局的 API 抓取即時油價 (更健壯的版本)。
    我們抓取「95無鉛汽油」的價格。
    """
    url = "https://www.moea.gov.tw/oil102/oil1021010/A00/MOEA_OilPrice.json"
    
    # 【優化 1】新增 User-Agent，假裝是 Chrome 瀏覽器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    default_price = 31.0  # 預設油價
    
    try:
        # 【優化 2】將 timeout 時間從 5 秒延長到 10 秒
        response = requests.get(url, headers=headers, timeout=10)
        
        # 檢查伺服器是否回傳成功 (HTTP 200)
        response.raise_for_status() 
        
        data = response.json()
        
        for item in data.get('result', {}).get('oil_price_list', []):
            if item.get('product') == '95無鉛汽油':
                return float(item.get('price'))
        
        # 如果 JSON 中沒有 95 無鉛
        print("抓取油價成功，但在 JSON 中未找到 '95無鉛汽油'。")
        return default_price
    
    except Exception as e:
        # 捕捉其他可能的錯誤 (e.g., JSON 解碼失敗)
        print(f"!!! 抓取油價時發生未預期的錯誤: {e}")
        return default_price

# --- 新增：計算油錢的函式 (來自你之前的需求) ---
def calculate_fuel_cost(distance_km, fuel_efficiency_kpl, price_per_liter):
    """
    根據路程距離、車輛油耗和每公升油價計算總油錢。
    """
    if fuel_efficiency_kpl <= 0:
        return 0.0 # 避免除以零的錯誤
    
    fuel_needed_liters = distance_km / fuel_efficiency_kpl
    total_cost = fuel_needed_liters * price_per_liter
    return total_cost

# --- 這是你本來就有的計算邏輯 ---
def calculate_shared_trip_cost(total_fuel_cost, toll_fee, parking_fee, total_people, include_driver=False):
    """
    計算並分攤一趟旅程的總費用（油錢、過路費、停車費）。
    """
    # 1. 計算總花費
    total_cost = total_fuel_cost + toll_fee + parking_fee

    # 2. 決定分攤人數
    if include_driver:
        sharers = total_people
    else:
        sharers = total_people - 1

    # 3. 避免人數少於1造成錯誤
    if sharers <= 0:
        if total_people == 1 and not include_driver:
            return total_cost, 0.0, 0, "只有一位司機，乘客 0 人，無需分攤。"
        return total_cost, 0.0, 0, "分攤人數錯誤（小於等於 0）。"

    # 4. 計算每人應付金額
    cost_per_person = total_cost / sharers
    
    message = f"車上總共 {total_people} 人，由 {sharers} 位乘客分攤。"
    if include_driver:
        message = f"車上總共 {total_people} 人，所有人（含司機）均分。"
        
    return total_cost, cost_per_person, sharers, message
# --- 邏輯結束 ---


# --- 修改後的路由 ---
@tools_bp.route('/gas-money', methods=['GET', 'POST'])
def cost_splitter():
    results = None
    live_gas_price = 31.0 # 預設值

    if request.method == 'GET':
        # 載入頁面時，抓取即時油價
        live_gas_price = get_live_gas_price()

    if request.method == 'POST':
        try:
            # 1. 從表單接收新欄位的資料
            distance_km = float(request.form.get('distance_km', 0))
            fuel_efficiency_kpl = float(request.form.get('fuel_efficiency_kpl', 15.0)) # 預設 15km/L
            price_per_liter = float(request.form.get('price_per_liter', 0)) # 油價
            
            # 2. 接收其他費用
            toll_fee = float(request.form.get('toll_fee', 0))
            parking_fee = float(request.form.get('parking_fee', 0))
            
            # 3. 接收人數資訊
            total_people = int(request.form.get('total_people', 1))
            driver_pays = 'driver_pays' in request.form
            
            # 4. 【核心修改】用新欄位計算總油錢
            calculated_fuel_cost = calculate_fuel_cost(distance_km, fuel_efficiency_kpl, price_per_liter)
            
            # 5. 呼叫舊的函式來計算分攤
            total_cost, cost_per_person, sharers, message = calculate_shared_trip_cost(
                calculated_fuel_cost, # 傳入剛算出來的油錢
                toll_fee, 
                parking_fee, 
                total_people, 
                driver_pays
            )
            
            # 6. 將結果打包
            results = {
                'total_cost': total_cost,
                'cost_per_person': cost_per_person,
                'sharers': sharers,
                'message': message,
                'calculated_fuel_cost': calculated_fuel_cost # 額外把油錢也傳過去，方便顯示
            }
            # 把油價也傳回去，這樣 POST 刷新後油價欄位才不會跑掉
            live_gas_price = price_per_liter 
            
        except ValueError:
            flash('請輸入有效的數字！', 'error')
            live_gas_price = get_live_gas_price() # 發生錯誤時，還是要抓一次油價
        except Exception as e:
            flash(f'發生錯誤：{e}', 'error')
            live_gas_price = get_live_gas_price()
            
    # 無論 GET 或 POST，都渲染同一個模板
    # 注意：我們傳入了 live_gas_price 變數
    return render_template(
        'tools/gas_money.html', 
        title="油錢分攤小工具", 
        results=results,
        live_gas_price=live_gas_price
    )