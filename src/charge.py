#!/usr/bin/env python3
import os
import re
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, Page
from login import login

# .env loading is handled by login module import

CHARGE_PIN = os.environ.get('CHARGE_PIN')

def parse_keypad(page: Page) -> dict:
    """
    랜덤 키패드 이미지를 OCR로 분석하여 각 숫자의 위치를 파악합니다.
    
    키패드 구조:
    - 숫자 0-9: 10개
    - 전체삭제: 1개
    - 백스페이스: 1개
    - 총 12개 버튼
    
    Args:
        page: Playwright Page 객체
        
    Returns:
        dict: {숫자(str): element} 형태의 버튼 매핑 (0-9만 포함)
        
    Raises:
        Exception: 키패드 버튼을 찾지 못했을 경우
    """
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import io

    # 키패드 이미지 대기
    page.wait_for_selector(".kpd-layer", state="visible")
    
    # 키패드 버튼들 가져오기
    buttons = page.locator("img.kpd-data")
    count = buttons.count()
    
    if count == 0:
        raise Exception("No keypad buttons found")

    # 버튼 위치 정보 수집
    button_positions = []
    for i in range(count):
        btn = buttons.nth(i)
        box = btn.bounding_box()
        if box:
            button_positions.append({
                'element': btn,
                'x': box['x'],
                'y': box['y'],
                'w': box['width'],
                'h': box['height']
            })

    # 전체 키패드 영역 스크린샷 (캡처 후 메모리에서 처리)
    keypad_layer = page.locator(".kpd-layer")
    keypad_box = keypad_layer.bounding_box()
    screenshot_bytes = page.screenshot(clip=keypad_box)
    keypad_img = Image.open(io.BytesIO(screenshot_bytes))

    number_map = {}
    
    # 좌표 기준 정렬 (y 우선, x 다음)
    button_positions.sort(key=lambda b: (b['y'], b['x']))

    for idx, btn_info in enumerate(button_positions):
        # 상대 좌표 계산
        lx = btn_info['x'] - keypad_box['x']
        ly = btn_info['y'] - keypad_box['y']
        
        crop_box = (lx, ly, lx + btn_info['w'], ly + btn_info['h'])
        button_img = keypad_img.crop(crop_box)
        
        text = None
        
        # 전처리 및 OCR 시도 (여러 전략)
        gray = button_img.convert('L')
        
        # 1. 기본 대비 향상
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)
        binary = enhanced.point(lambda p: p > 128 and 255)
        
        configs = [
            r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789', # 단일 문자
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',  # 단일 라인
            r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'   # 단일 단어
        ]
        
        for config in configs:
            result = pytesseract.image_to_string(binary, config=config).strip()
            if result.isdigit() and len(result) == 1:
                text = result
                break
        
        if not text:
            # 샤프닝 시도
            sharp = enhanced.filter(ImageFilter.SHARPEN)
            binary_sharp = sharp.point(lambda p: p > 128 and 255)
            for config in configs:
                result = pytesseract.image_to_string(binary_sharp, config=config).strip()
                if result.isdigit() and len(result) == 1:
                    text = result
                    break

        if text and text not in number_map:
            number_map[text] = btn_info['element']

    return number_map

def charge_deposit(page: Page, amount: int) -> bool:
    """
    [간편충전] 기능을 사용하여 예치금을 충전합니다.
    
    Args:
        page: 로그인된 Playwright Page 객체
        amount: 충전할 금액 (5000, 10000, 20000 중 하나)
        
    Returns:
        bool: 충전 요청 성공 여부
    """
    if not CHARGE_PIN:
        print("❌ Error: CHARGE_PIN not found in environment variables.")
        return False

    print(f"Navigating to charge page for {amount:,} won...")
    page.goto("https://www.dhlottery.co.kr/mypage/mndpChrg")
    
    # 간편충전 선택
    page.click("text=간편충전")
    
    # 금액 선택
    amount_map = {5000: "5,000", 10000: "10,000", 20000: "20,000"}
    if amount not in amount_map:
        print(f"❌ Error: Invalid amount {amount}. Choose 5000, 10000, 20000.")
        return False
        
    page.select_option("select#amoundApply", label=f"{amount_map[amount]}원")
    
    # 충전하기 버튼 클릭 (간편충전 하단 버튼)
    page.click("button[onclick*='fn_openEcRegistAccountCheck']")
    
    # PIN 키패드 대기
    number_map = parse_keypad(page)
    
    if len(number_map) < 9:
        print(f"❌ Error: Keypad recognition failed (only {len(number_map)} digits).")
        return False
        
    for digit in CHARGE_PIN:
        if digit in number_map:
            number_map[digit].click()
            time.sleep(0.3)
        else:
            return False
            
    page.wait_for_load_state("networkidle")
    return True

def run(playwright: Playwright, amount: int):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        login(page)
        success = charge_deposit(page, amount)
        if success:
            print("✅ Charge completed successfully!")
        else:
            print("❌ Charge failed.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        context.close()
        browser.close()

if __name__ == "__main__":
    amount = 10000
    if len(sys.argv) > 1:
        try:
            amount = int(sys.argv[1].replace(',', ''))
        except ValueError:
            pass
            
    with sync_playwright() as playwright:
        run(playwright, amount)
