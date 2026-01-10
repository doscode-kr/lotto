#!/usr/bin/env python3
import json
import time
import re
from os import environ
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright
from login import login

# .env loading is handled by login module import


def run(playwright: Playwright) -> None:
    """
    연금복권 720+를 구매합니다.
    '모든 조'를 선택하여 임의의 번호로 5매(5,000원)를 구매합니다.
    
    Args:
        playwright: Playwright 객체
    """
    # Create browser, context, and page
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Perform login using injected page
    login(page)

    try:
        # Navigate directly to Pension 720 Game Page
        page.goto("https://el.dhlottery.co.kr/game/pension720/game.jsp")
        print('✅ Navigated to Lotto 720 page')
        
        # Wait for the game UI to load
        page.locator(".lotto720_btn_auto_number").wait_for(state="visible", timeout=15000)

        # [자동번호] 클릭
        page.locator(".lotto720_btn_auto_number").click()

        # [선택완료] 클릭
        page.locator("a:has-text('선택 완료')").first.click()
        
        time.sleep(1)

        # Verify Amount
        payment_amount_el = page.locator(".lotto720_price.lpcurpay")
        time.sleep(1)
        
        payment_amount_text = payment_amount_el.inner_text().strip()
        payment_val = int(re.sub(r'[^0-9]', '', payment_amount_text) or '0')

        if payment_val != 5000:
            print(f"❌ Error: Payment mismatch (Expected 5000, Displayed {payment_val})")
            return

        # [구매하기] 클릭
        page.locator("a:has-text('구매하기')").first.click()
        
        # Handle Confirmation Popup
        confirm_popup = page.locator("#lotto720_popup_confirm")
        confirm_popup.wait_for(state="visible", timeout=5000)
        
        # Click Final Purchase Button
        confirm_popup.locator("a.btn_blue").click()
        
        time.sleep(2)
        print("✅ Lotto 720: All sets purchased successfully!")
        

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        context.close()
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

