#!/usr/bin/env python3
import pyautogui, time

pyautogui.PAUSE = 0.2

width, height = pyautogui.size()
print(f"Screen: {width}x{height}")

# Test positions from right edge
for offset in [100, 150, 200, 250, 300, 350]:
    x = width - offset
    y = 18
    print(f"\nClicking ({x}, {y})...")
    pyautogui.moveTo(x, y, duration=0.2)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(0.8)
    ss = pyautogui.screenshot()
    fname = f'C:\\test\\github\\trae_auto\\click_{offset}px.png'
    ss.save(fname)
    print(f"Saved: {fname}")
