from datetime import datetime
import json
import math
import numpy as np
import pandas as pd
from scipy.stats import norm

# ==================== 1. Black-Scholes Delta 計算模型 ====================


def calculate_delta(S, K, T, r, sigma, option_type="call"):
    """S: 現價, K: 履約價, T: 年化剩餘天數, r: 無風險利率, sigma: 隱含波動度(IV)"""
    if T <= 0 or sigma <= 0:
        return 0.0

    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))

    if option_type.lower() == "call":
        return float(norm.cdf(d1))
    else:
        return float(norm.cdf(d1) - 1.0)


# ==================== 2. 模擬 / 抓取當日行情數據 ====================


def main():
    # 說明：實務上可以透過期交所 Open Data API 或 yfinance 抓取即時標的價與 IV
    spot_price = 23000  # 假設台指期現價
    vix = 16.5  # 假設當日 VIX
    r = 0.015  # 年化無風險利率 1.5%
    days_to_expiration = 4  # 週選擇權距離結算日天數
    T = days_to_expiration / 365.0
    sigma = vix / 100.0  # 轉換為小數

    # 生成當週選擇權核心履約價檔位 (履約價間隔 100 點)
    strikes = range(spot_price - 1000, spot_price + 1050, 100)

    options_list = []
    for K in strikes:
        c_delta = calculate_delta(
            spot_price, K, T, r, sigma, option_type="call"
        )
        p_delta = calculate_delta(spot_price, K, T, r, sigma, option_type="put")

        # 簡單推算權利金估計值
        c_price = round(max(0.1, (spot_price - K) * 0.5 + 50), 1)
        p_price = round(max(0.1, (K - spot_price) * 0.5 + 50), 1)

        options_list.append({
            "strike": K,
            "call_delta": c_delta,
            "call_price": c_price,
            "put_delta": p_delta,
            "put_price": p_price,
        })

    output_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "spot_price": spot_price,
        "vix": vix,
        "options": options_list,
    }

    # 寫入 data.json 給前端網頁讀取
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("data.json 更新成功！")


if __name__ == "__main__":
    main()
