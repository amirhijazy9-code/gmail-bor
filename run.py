import asyncio
import os
import random
import string
import time
import yaml
import requests
from playwright.async_api import async_playwright


class GmailCreator:
    SIGNUP_URL = "https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp"

    # ==========================================
    # 1. إعدادات البروكسي (تكساس)
    # ==========================================
    USE_PROXY = True
    PROXY_SERVER = "http://45.76.233.138:15096" 
    PROXY_USER = "aaaawp"                       
    PROXY_PASS = "aaaawp"                       

    # ==========================================
    # 2. إعدادات الأرقام من 5sim
    # ==========================================
    SMS_API_KEY = "YOUR_5SIM_API_KEY" # <-- حط مفتاح 5sim هنا
    SMS_COUNTRY = "usa" 
    SMS_OPERATOR = "any" 
    SMS_PRODUCT = "google" 

    # ==========================================
    # 3. إعدادات بوت التليجرام
    # ==========================================
    TG_TOKEN = "8806725251:AAHrfFPO_jscNhSp6hQwLDFl1nWHW43WCfY" # <-- حط التوكن هنا
    TG_CHAT_ID = "7426994511"          # <-- حط الـ ID بتاعك هنا

    def __init__(self, config_path="config.yaml"):
        with open(config_path, encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        self.out_dir = self.cfg.get("output_dir", "./accounts")
        os.makedirs(self.out_dir, exist_ok=True)

    def send_telegram(self, msg):
        if self.TG_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN":
            url = f"https://api.telegram.org/bot{self.TG_TOKEN}/sendMessage"
            payload = {"chat_id": self.TG_CHAT_ID, "text": msg}
            try:
                requests.post(url, json=payload, timeout=10)
            except:
                pass

    async def _pause(self, page):
        await asyncio.sleep(random.uniform(1.0, 2.0))

    async def _human_click(self, page, selector):
        try:
            el = page.locator(selector).first
            await el.wait_for(state="visible", timeout=15000)
            box = await el.bounding_box()
            if box:
                x = box["x"] + box["width"] / 2 + random.uniform(-5, 5)
                y = box["y"] + box["height"] / 2 + random.uniform(-5, 5)
                await page.mouse.move(x, y, steps=random.randint(5, 10))
                await asyncio.sleep(random.uniform(0.2, 0.5))
                await page.mouse.click(x, y)
            else:
                await el.click()
        except Exception as e:
            print(f"[!] مشكلة في الضغط: {e}")

    async def _type_slow(self, page, selector, text, timeout=15000):
        try:
            el = page.locator(selector).first
            await el.wait_for(state="visible", timeout=timeout)
            await el.click()
            await asyncio.sleep(0.3)
            for ch in text:
                await el.type(ch, delay=random.randint(10, 30)) 
        except Exception as e:
            print(f"[!] مشكلة في كتابة {text}: {e}")

    def _rand_name(self):
        return "master " + random.choice(["hassan", "saleh", "adel", "mahmoud"])

    def _rand_user(self):
        return f"master{random.randint(10000, 99999)}"

    def _rand_pass(self):
        return "Amir1234**"

    def buy_number(self):
        headers = {"Authorization": f"Bearer {self.SMS_API_KEY}"}
        url = f"https://5sim.net/v1/user/buy/activation/{self.SMS_COUNTRY}/{self.SMS_OPERATOR}/{self.SMS_PRODUCT}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f"[+] تم شراء رقم: {data['phone']}")
            return data['id'], data['phone']
        else:
            print(f"[!] فشل شراء رقم: {r.text}")
            return None, None

    def check_code(self, order_id):
        headers = {"Authorization": f"Bearer {self.SMS_API_KEY}"}
        url = f"https://5sim.net/v1/user/check/{order_id}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if data['status'] == 'RECEIVED':
                print(f"[+] تم استلام الكود: {data['sms'][0]['code']}")
                return data['sms'][0]['code']
        return None

    def finish_order(self, order_id):
        headers = {"Authorization": f"Bearer {self.SMS_API_KEY}"}
        requests.get(f"https://5sim.net/v1/user/finish/{order_id}", headers=headers)

    def cancel_order(self, order_id):
        headers = {"Authorization": f"Bearer {self.SMS_API_KEY}"}
        requests.get(f"https://5sim.net/v1/user/cancel/{order_id}", headers=headers)

    async def _create_one(self, browser):
        proxy_settings = None
        if self.USE_PROXY:
            proxy_settings = {
                "server": self.PROXY_SERVER,
                "username": self.PROXY_USER,
                "password": self.PROXY_PASS
            }

        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            locale="en-US",
            proxy=proxy_settings
        )
        page = await context.new_page()
        page.set_default_timeout(60000)

        try:
            print("[*] بيفتح صفحة التسجيل...")
            await page.goto(self.SIGNUP_URL, wait_until="commit", timeout=60000)
            await page.wait_for_timeout(3000)

            if await page.locator('text="For my personal use"').count() > 0:
                await self._human_click(page, 'text="For my personal use"')
                await page.wait_for_timeout(2000)

            if await page.locator('button:has-text("Accept all")').count() > 0:
                await self._human_click(page, 'button:has-text("Accept all")')
                await page.wait_for_timeout(2000)

            print("[*] بيكتب الاسم...")
            full = self._rand_name()
            await self._type_slow(page, 'input[name="firstName"]', full.split(" ")[0])
            await self._type_slow(page, 'input[name="lastName"]', full.split(" ")[1])
            await self._pause(page)
            await self._human_click(page, 'button:has-text("Next")')
            await page.wait_for_timeout(3000)

            print("[*] بيكتب تاريخ الميلاد والجنس...")
            
            month_el = page.locator('select[name="month"]').first
            if await month_el.count() > 0:
                await month_el.focus()
                await page.keyboard.press("ArrowDown")
                await page.wait_for_timeout(500)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1000)

            if await page.locator('input[name="day"]').count() > 0:
                await self._type_slow(page, 'input[name="day"]', "15")
                
            if await page.locator('input[name="year"]').count() > 0:
                await self._type_slow(page, 'input[name="year"]', "1988")
                
            gender_el = page.locator('select[name="gender"]').first
            if await gender_el.count() > 0:
                await gender_el.focus()
                await page.keyboard.press("ArrowDown")
                await page.wait_for_timeout(500)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1000)

            await self._pause(page)
            await self._human_click(page, 'button:has-text("Next")')
            await page.wait_for_timeout(3000)

            print("[*] بيكتب اليوزر...")
            user = self._rand_user()
            await self._type_slow(page, 'input[name="Username"]', user)
            await self._pause(page)
            await self._human_click(page, 'button:has-text("Next")')
            await page.wait_for_timeout(3000)

            print("[*] بيكتب الباسورد...")
            pwd = self._rand_pass()
            
            await self._type_slow(page, 'input[name="Passwd"]', pwd)
            await page.wait_for_timeout(1500) 
            await self._type_slow(page, 'input[name="ConfirmPasswd"]', pwd)
            await self._pause(page)
            
            await self._human_click(page, 'button:has-text("Next")')
            await page.wait_for_timeout(4000)

            print("\n[!] جاري التحقق...")
            
            try_another = page.locator('text="Try another way"')
            if await try_another.count() > 0:
                print("[*] محاولة تخطي الـ QR...")
                await try_another.click()
                await page.wait_for_timeout(2000)
                
                sms_option = page.locator('text="Text message"')
                if await sms_option.count() > 0:
                    await sms_option.click()
                    await page.wait_for_timeout(2000)

            order_id, phone = self.buy_number()
            if not order_id:
                print("[!] مفيش رصيد أو أرقام متاحة، بنلغي.")
                return False

            print(f"[*] بيكتب الرقم: {phone}")
            phone_clean = phone.replace("+1", "").strip()
            await self._type_slow(page, 'input[type="tel"]', phone_clean)
            
            await self._human_click(page, 'button:has-text("Next")')
            await page.wait_for_timeout(3000)

            print("[*] بنستنى الكود من 5sim...")
            code = None
            for _ in range(24):
                await asyncio.sleep(5)
                code = self.check_code(order_id)
                if code:
                    break
            
            if not code:
                print("[!] الكود مجاش، بنلغي الرقم.")
                self.cancel_order(order_id)
                return False

            print(f"[*] بيكتب الكود: {code}")
            await self._type_slow(page, 'input[name="code"]', code)
            await self._human_click(page, 'button:has-text("Next")')
            await page.wait_for_timeout(4000)

            self.finish_order(order_id)

            for label in ("Next", "I agree", "Continue", "Accept"):
                if await page.locator(f'button:has-text("{label}")').count() > 0:
                    try:
                        await self._human_click(page, f'button:has-text("{label}")')
                        await self._pause(page)
                    except Exception:
                        pass

            await page.wait_for_timeout(5000)

            path = os.path.join(self.out_dir, f"{user}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"username: {user}@gmail.com\n")
                f.write(f"password: {pwd}\n")
                f.write(f"created:  {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            msg = f"✅ تم إنشاء حساب جديد:\n\n📧 الإيميل: {user}@gmail.com\n🔑 الباسورد: {pwd}"
            self.send_telegram(msg)
            
            print(f"[+] created {user}@gmail.com -> {path}")
            return True

        except Exception as e:
            print(f"[!] failed: {e}")
            return False
        finally:
            await context.close()

    async def run(self):
        count = self.cfg.get("count", 1)
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                channel="chrome", 
                headless=False, 
                proxy={"server": "http://per-context"}, 
                args=["--disable-blink-features=AutomationControlled"]
            )
            for i in range(count):
                print(f"\n[*] حساب {i+1}/{count}")
                await self._create_one(browser)
            await browser.close()
            print(f"\n[=] خلص!")


if __name__ == "__main__":
    asyncio.run(GmailCreator().run())
