import pygame
import pandas as pd
import math
import random

# 读取数据
df = pd.read_csv('cloud.csv', encoding='utf-8')
data = []
for i, row in df.iterrows():
    if pd.isna(row['Month']) or pd.isna(row['Day']) or pd.isna(row['Value']):
        continue
    data.append({
        'month': int(row['Month']),
        'day': int(row['Day']),
        'value': float(row['Value'])
    })

WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH//2, HEIGHT//2)
RADIUS_MIN = 80
RADIUS_MAX = 180
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

values = [d['value'] for d in data]
min_value = min(values)
max_value = max(values)
num_days = len(data)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Average cloud cover in Hong Kong (percentage)')
# 字体设置
title_font = pygame.font.SysFont('Arial Black', 24)
font = pygame.font.SysFont('Arial', 18)
small_font = pygame.font.SysFont('Arial', 12)
clock = pygame.time.Clock()

def get_color(value, highlight=False):
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    r = int(120 + ratio * 80)
    g = int(180 + ratio * 50)
    b = int(255 - ratio * 60)
    if highlight:
        r = min(255, r+60)
        g = min(255, g+60)
        b = min(255, b+60)
    return (r, g, b)

def get_radius(value):
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    return RADIUS_MIN + ratio * (RADIUS_MAX - RADIUS_MIN)

def draw_flower(grow_idx, grow_progress):
    for i, d in enumerate(data):
        angle = 2 * math.pi * i / num_days - math.pi/2
        radius = get_radius(d['value'])
        color = get_color(d['value'], highlight=(i==grow_idx))
        # 动画：当前生长的花瓣长度逐步增加
        if i < grow_idx:
            r = radius
        elif i == grow_idx:
            r = RADIUS_MIN + (radius - RADIUS_MIN) * grow_progress
        else:
            r = RADIUS_MIN
        # 花瓣主干
        x1 = CENTER[0] + math.cos(angle) * RADIUS_MIN
        y1 = CENTER[1] + math.sin(angle) * RADIUS_MIN
        x2 = CENTER[0] + math.cos(angle) * r
        y2 = CENTER[1] + math.sin(angle) * r
        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)
        # 花瓣末端毛刺
        if r > RADIUS_MIN + 6:
            for j in range(5):
                fuzz_angle = angle + (random.random()-0.5)*0.12
                fuzz_len = r + 6 + random.randint(0, 10)
                fx = CENTER[0] + math.cos(fuzz_angle) * fuzz_len
                fy = CENTER[1] + math.sin(fuzz_angle) * fuzz_len
                pygame.draw.line(screen, color, (x2, y2), (fx, fy), 1)
            # 花瓣末端圆点
            pygame.draw.circle(screen, color, (int(x2), int(y2)), 3 if i!=grow_idx else 5)

def draw_month_labels():
    for m in range(12):
        angle = 2 * math.pi * (sum([1 for d in data if d['month'] < m+1]) + 15) / num_days - math.pi/2
        label_radius = RADIUS_MAX + 20
        x = CENTER[0] + math.cos(angle) * label_radius
        y = CENTER[1] + math.sin(angle) * label_radius
        label = small_font.render(MONTH_NAMES[m], True, (180, 200, 255))
        screen.blit(label, (x-label.get_width()//2, y-label.get_height()//2))

def draw_legend():
    legend_x = 30
    legend_y = HEIGHT - 60
    for i in range(80):
        ratio = i / 80
        value = min_value + ratio * (max_value - min_value)
        color = get_color(value)
        pygame.draw.rect(screen, color, (legend_x+i, legend_y, 1, 10))
    min_text = small_font.render(f"{min_value:.0f}%", True, (180, 200, 255))
    max_text = small_font.render(f"{max_value:.0f}%", True, (180, 200, 255))
    screen.blit(min_text, (legend_x-10, legend_y+12))
    screen.blit(max_text, (legend_x+80-10, legend_y+12))
    explain = small_font.render("Cloud cover (petal length & color)", True, (180, 200, 255))
    screen.blit(explain, (legend_x, legend_y+26))

running = True
grow_idx = 0
grow_progress = 0.0
GROW_SPEED = 0.18  # 动画速度加快

while running:
    screen.fill((10, 18, 32))
    # 标题
    title = title_font.render("Average cloud cover in Hong Kong (percentage)", True, (220, 230, 255))
    screen.blit(title, (WIDTH//2-title.get_width()//2, 18))
    # 花朵动画
    draw_flower(grow_idx, grow_progress)
    # 月份
    draw_month_labels()
    # 年份
    year_text = font.render("2025", True, (180, 200, 255))
    screen.blit(year_text, (CENTER[0]-year_text.get_width()//2, CENTER[1]-year_text.get_height()//2))
    # 图例
    draw_legend()
    pygame.display.flip()
    clock.tick(30)

    # 动画控制
    grow_progress += GROW_SPEED
    if grow_progress >= 1.0:
        grow_progress = 0.0
        grow_idx += 1
        if grow_idx >= num_days:
            grow_idx = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
