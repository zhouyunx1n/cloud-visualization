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
data.sort(key=lambda x: (x['month'], x['day']))

WIDTH, HEIGHT = 900, 900
LEFT_MARGIN = 120
TOP_MARGIN = 110
CELL_W = 55
CELL_H = 24
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

values = [d['value'] for d in data]
min_value = min(values)
max_value = max(values)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Average cloud cover in Hong Kong (percentage)')
title_font = pygame.font.SysFont('Arial Black', 28)
font = pygame.font.SysFont('Arial', 18)
small_font = pygame.font.SysFont('Arial', 12)
clock = pygame.time.Clock()

def get_color(value, alpha=255):
    # 蓝色渐变
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    r = int(120 + ratio * 80)
    g = int(180 + ratio * 50)
    b = int(255 - ratio * 60)
    return (r, g, b, alpha)

def get_radius(value):
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    return 5 + ratio * 10  # 更小的气泡

# 动画参数
bubble_states = []
for d in data:
    bubble_states.append({
        'alpha': 0,      # 透明度
        'appeared': False, # 是否已完全浮现
        'phase': random.uniform(0, math.pi*2) # 呼吸动画初相位
    })

current_idx = 0
bubble_appear_speed = 18  # 每帧增加的透明度
breath_speed = 0.08       # 呼吸动画速度
highlight_breath_speed = 0.18  # 当前日期气泡呼吸更快
running = True

while running:
    # 浅色背景
    screen.fill((240, 248, 255))  # AliceBlue

    # 标题
    title = title_font.render("Average cloud cover in Hong Kong (percentage)", True, (30, 80, 120))
    screen.blit(title, (WIDTH//2-title.get_width()//2, 28))

    # 月份
    for m in range(12):
        label = font.render(MONTH_NAMES[m], True, (40, 60, 80))
        x = LEFT_MARGIN + m*CELL_W + CELL_W//2 - label.get_width()//2
        screen.blit(label, (x, TOP_MARGIN-32))

    # 日期
    for d in range(1, 32):
        label = font.render(str(d), True, (40, 60, 80))
        y = TOP_MARGIN + (d-1)*CELL_H + CELL_H//4 - label.get_height()//2
        screen.blit(label, (LEFT_MARGIN-32, y))

    # 气泡动画
    for idx, d in enumerate(data):
        m_idx = d['month']-1
        d_idx = d['day']-1
        x = LEFT_MARGIN + m_idx*CELL_W + CELL_W//2
        y = TOP_MARGIN + d_idx*CELL_H + CELL_H//2
        state = bubble_states[idx]
        # 逐步浮现
        if idx <= current_idx and not state['appeared']:
            state['alpha'] += bubble_appear_speed
            if state['alpha'] >= 255:
                state['alpha'] = 255
                state['appeared'] = True
        # 呼吸动画
        if state['appeared']:
            if idx == current_idx:
                state['phase'] += highlight_breath_speed
            else:
                state['phase'] += breath_speed
            breath = 1.0 + 0.18 * math.sin(state['phase'])
        else:
            breath = 1.0
        # 当前日期高亮
        if idx == current_idx:
            radius = int(get_radius(d['value']) * breath * 1.18)
            color = get_color(d['value'], alpha=int(state['alpha']))
        else:
            radius = int(get_radius(d['value']) * breath)
            color = get_color(d['value'], alpha=int(state['alpha']))
        # 画带透明度的气泡
        bubble_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, color, (radius, radius), radius)
        screen.blit(bubble_surf, (x-radius, y-radius))

    # 图例
    legend_x = WIDTH-220
    legend_y = HEIGHT-80
    for i in range(80):
        ratio = i/80
        value = min_value + ratio*(max_value-min_value)
        color = get_color(value)
        pygame.draw.circle(screen, color, (legend_x+20+i, legend_y), 8)
    min_text = small_font.render(f"{min_value:.0f}%", True, (40, 60, 80))
    max_text = small_font.render(f"{max_value:.0f}%", True, (40, 60, 80))
    screen.blit(min_text, (legend_x+10, legend_y+18))
    screen.blit(max_text, (legend_x+80, legend_y+18))
    explain = small_font.render("Cloud cover (bubble size & color)", True, (40, 60, 80))
    screen.blit(explain, (legend_x, legend_y+34))

    # 当前日期说明
    d = data[current_idx]
    info_text = f"{MONTH_NAMES[d['month']-1]} {d['day']}, Cloud cover: {d['value']}%"
    info_surface = font.render(info_text, True, (30, 80, 120))
    screen.blit(info_surface, (WIDTH//2-info_surface.get_width()//2, HEIGHT-40))

    pygame.display.flip()
    clock.tick(30)

    # 动画控制
    current_idx += 1
    if current_idx >= len(data):
        current_idx = 0
        # 重置所有气泡
        for state in bubble_states:
            state['alpha'] = 0
            state['appeared'] = False
            state['phase'] = random.uniform(0, math.pi*2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
