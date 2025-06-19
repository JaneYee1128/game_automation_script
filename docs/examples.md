# 使用示例

本文档提供了一系列使用游戏自动化脚本工具的实际示例，帮助您理解如何将其应用于不同类型的游戏和场景。

## 目录

1. [基础示例](#基础示例)
2. [RPG游戏自动化](#rpg游戏自动化)
3. [卡牌游戏自动化](#卡牌游戏自动化)
4. [MOBA游戏辅助](#moba游戏辅助)
5. [FPS游戏辅助](#fps游戏辅助)
6. [模拟经营游戏自动化](#模拟经营游戏自动化)
7. [多账号管理](#多账号管理)
8. [自定义复杂脚本](#自定义复杂脚本)

## 基础示例

### 简单点击操作

```python
from src.screen_capture import ScreenCapture
from src.image_recognition import ImageRecognition
import pyautogui
import time

# 初始化组件
screen_capture = ScreenCapture()
image_recognition = ImageRecognition()

# 加载按钮模板
button_template = "start_button.png"

# 主循环
while True:
    # 捕获屏幕
    screen = screen_capture.capture_screen()
    
    # 查找按钮
    results = image_recognition.find_template(screen, button_template, threshold=0.8)
    
    # 如果找到按钮，点击它
    if results:
        x, y, w, h, confidence = results[0]
        center_x = x + w // 2
        center_y = y + h // 2
        pyautogui.click(center_x, center_y)
        print(f"点击按钮，位置: ({center_x}, {center_y})，置信度: {confidence:.2f}")
        break
    
    # 等待一段时间再次尝试
    time.sleep(1)
```

### 录制和回放操作序列

```python
from src.event_recorder import EventRecorder
from src.event_player import EventPlayer
import time

# 初始化组件
recorder = EventRecorder()
player = EventPlayer()

# 录制操作
print("开始录制，请执行您想要自动化的操作...")
recorder.start_recording()
input("按Enter键停止录制...")
recorder.stop_recording()

# 保存录制
recording_name = "my_game_sequence"
recorder.save_recording(recording_name)
print(f"录制已保存为: {recording_name}")

# 等待几秒钟
print("3秒后开始回放...")
time.sleep(3)

# 回放录制
player.load_recording(recording_name)
player.start_playback()
print("回放开始")

# 等待回放完成
while player.is_playing():
    time.sleep(0.5)

print("回放完成")
```

## RPG游戏自动化

### 自动打怪升级

```python
from src.screen_capture import ScreenCapture
from src.image_recognition import ImageRecognition
import pyautogui
import time
import random

class AutoRPGFarmer:
    def __init__(self):
        self.screen_capture = ScreenCapture()
        self.image_recognition = ImageRecognition()
        
        # 加载所需模板
        self.monster_template = "monster.png"
        self.attack_button_template = "attack_button.png"
        self.health_low_template = "health_low.png"
        self.potion_button_template = "potion_button.png"
        
    def find_and_click(self, template, threshold=0.8):
        """查找模板并点击"""
        screen = self.screen_capture.capture_screen()
        results = self.image_recognition.find_template(screen, template, threshold)
        
        if results:
            x, y, w, h, confidence = results[0]
            center_x = x + w // 2
            center_y = y + h // 2
            
            # 添加小的随机偏移，使点击更自然
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            
            pyautogui.click(center_x + offset_x, center_y + offset_y)
            return True
        
        return False
    
    def check_health(self):
        """检查血量是否过低"""
        screen = self.screen_capture.capture_screen()
        results = self.image_recognition.find_template(screen, self.health_low_template, threshold=0.7)
        return len(results) > 0
    
    def use_potion(self):
        """使用药水"""
        return self.find_and_click(self.potion_button_template)
    
    def find_monster(self):
        """寻找怪物"""
        return self.find_and_click(self.monster_template, threshold=0.7)
    
    def attack(self):
        """攻击"""
        return self.find_and_click(self.attack_button_template)
    
    def run(self, duration_minutes=30):
        """运行自动打怪脚本"""
        end_time = time.time() + duration_minutes * 60
        
        while time.time() < end_time:
            # 检查血量
            if self.check_health():
                print("血量过低，使用药水")
                if self.use_potion():
                    time.sleep(1)
                else:
                    print("无法使用药水，可能已用完")
                    break
            
            # 寻找怪物
            if self.find_monster():
                print("发现怪物，准备攻击")
                time.sleep(0.5)
                
                # 攻击怪物
                if self.attack():
                    print("攻击中...")
                    # 等待战斗动画完成
                    time.sleep(3)
                else:
                    print("无法点击攻击按钮")
            else:
                # 没找到怪物，移动角色
                print("未发现怪物，移动角色")
                # 随机方向移动
                direction = random.choice(["w", "a", "s", "d"])
                pyautogui.keyDown(direction)
                time.sleep(1)
                pyautogui.keyUp(direction)
            
            # 短暂等待
            time.sleep(0.5)

# 使用示例
if __name__ == "__main__":
    farmer = AutoRPGFarmer()
    print("开始自动打怪，将运行30分钟...")
    farmer.run(duration_minutes=30)
```

## 卡牌游戏自动化

### 自动对战

```python
from src.screen_capture import ScreenCapture
from src.image_recognition import ImageRecognition
import pyautogui
import time
import random

class CardGameBot:
    def __init__(self):
        self.screen_capture = ScreenCapture()
        self.image_recognition = ImageRecognition()
        
        # 加载卡牌和按钮模板
        self.card_templates = {
            "attack_card": "attack_card.png",
            "defense_card": "defense_card.png",
            "spell_card": "spell_card.png"
        }
        
        self.button_templates = {
            "end_turn": "end_turn_button.png",
            "confirm": "confirm_button.png"
        }
        
        self.enemy_templates = {
            "enemy_character": "enemy_character.png",
            "enemy_minion": "enemy_minion.png"
        }
        
    def find_cards(self, card_type):
        """查找特定类型的卡牌"""
        screen = self.screen_capture.capture_screen()
        return self.image_recognition.find_template(screen, self.card_templates[card_type], threshold=0.75)
    
    def find_targets(self, target_type):
        """查找可攻击的目标"""
        screen = self.screen_capture.capture_screen()
        return self.image_recognition.find_template(screen, self.enemy_templates[target_type], threshold=0.75)
    
    def click_button(self, button_type):
        """点击界面按钮"""
        screen = self.screen_capture.capture_screen()
        results = self.image_recognition.find_template(screen, self.button_templates[button_type], threshold=0.8)
        
        if results:
            x, y, w, h, _ = results[0]
            pyautogui.click(x + w//2, y + h//2)
            return True
        return False
    
    def play_card(self, card_result, target_result=None):
        """打出卡牌，可选择目标"""
        if not card_result:
            return False
        
        x, y, w, h, _ = card_result
        card_pos = (x + w//2, y + h//2)
        
        # 点击卡牌
        pyautogui.click(card_pos)
        time.sleep(0.5)
        
        # 如果需要选择目标
        if target_result:
            tx, ty, tw, th, _ = target_result
            target_pos = (tx + tw//2, ty + th//2)
            pyautogui.click(target_pos)
        
        # 有时需要确认
        time.sleep(0.5)
        self.click_button("confirm")
        
        return True
    
    def play_turn(self):
        """执行一个回合的操作"""
        # 先打出攻击牌
        attack_cards = self.find_cards("attack_card")
        if attack_cards:
            # 寻找敌方随从作为目标
            enemy_minions = self.find_targets("enemy_minion")
            if enemy_minions:
                self.play_card(attack_cards[0], enemy_minions[0])
            else:
                # 没有随从，攻击敌方英雄
                enemy_heroes = self.find_targets("enemy_character")
                if enemy_heroes:
                    self.play_card(attack_cards[0], enemy_heroes[0])
        
        # 打出防御牌
        defense_cards = self.find_cards("defense_card")
        if defense_cards:
            self.play_card(defense_cards[0])
        
        # 打出法术牌
        spell_cards = self.find_cards("spell_card")
        if spell_cards:
            enemy_targets = self.find_targets("enemy_character")
            if enemy_targets:
                self.play_card(spell_cards[0], enemy_targets[0])
        
        # 结束回合
        time.sleep(1)
        return self.click_button("end_turn")
    
    def run_game(self, num_turns=10):
        """运行自动对战"""
        for turn in range(num_turns):
            print(f"执行第 {turn+1} 回合...")
            if self.play_turn():
                print("回合结束，等待对手...")
                # 等待对手回合
                time.sleep(random.uniform(5, 10))
            else:
                print("无法结束回合，游戏可能已结束")
                break

# 使用示例
if __name__ == "__main__":
    bot = CardGameBot()
    print("开始自动对战，将进行10个回合...")
    bot.run_game(num_turns=10)
```

## MOBA游戏辅助

### 小地图监控与警报

```python
from src.screen_capture import ScreenCapture
from src.image_recognition import ImageRecognition
import numpy as np
import time
import winsound  # 用于播放警报声

class MiniMapMonitor:
    def __init__(self, minimap_region):
        """
        初始化小地图监控器
        
        参数:
        minimap_region: 小地图在屏幕上的区域 (x, y, width, height)
        """
        self.screen_capture = ScreenCapture()
        self.image_recognition = ImageRecognition()
        self.minimap_region = minimap_region
        
        # 存储上一帧的小地图图像
        self.previous_minimap = None
        
        # 敌人图标模板
        self.enemy_icon_template = "enemy_icon.png"
        
        # 警报冷却时间（秒）
        self.alert_cooldown = 5
        self.last_alert_time = 0
    
    def capture_minimap(self):
        """捕获小地图区域"""
        return self.screen_capture.capture_screen(self.minimap_region)
    
    def detect_enemies(self, minimap_image):
        """检测小地图上的敌人图标"""
        results = self.image_recognition.find_template(
            minimap_image, 
            self.enemy_icon_template,
            threshold=0.7
        )
        return results
    
    def detect_changes(self, current_minimap):
        """检测小地图变化"""
        if self.previous_minimap is None:
            self.previous_minimap = current_minimap
            return False, 0
        
        # 计算两帧之间的差异
        diff = cv2.absdiff(current_minimap, self.previous_minimap)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh_diff = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # 计算变化的像素百分比
        change_percent = np.count_nonzero(thresh_diff) / thresh_diff.size
        
        # 更新上一帧
        self.previous_minimap = current_minimap
        
        # 如果变化超过阈值，返回True
        return change_percent > 0.05, change_percent
    
    def play_alert(self):
        """播放警报声"""
        current_time = time.time()
        if current_time - self.last_alert_time > self.alert_cooldown:
            winsound.Beep(1000, 500)  # 1000Hz, 500ms
            self.last_alert_time = current_time
    
    def run(self, duration_minutes=30):
        """运行小地图监控"""
        end_time = time.time() + duration_minutes * 60
        
        print(f"开始监控小地图，将运行{duration_minutes}分钟...")
        
        while time.time() < end_time:
            # 捕获小地图
            minimap = self.capture_minimap()
            
            # 检测敌人
            enemies = self.detect_enemies(minimap)
            
            # 检测变化
            has_