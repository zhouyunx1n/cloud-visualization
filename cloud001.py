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

WIDTH, HEIGHT = 700, 500
CENTER = (WIDTH // 2, HEIGHT // 2 + 30)

values = [d['value'] for d in data]
min_value = min(values)
max_value = max(values)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('云量云朵动画')
font = pygame.font.SysFont('SimHei', 32)
info_font = pygame.font.SysFont('SimHei', 24)
clock = pygame.time.Clock()

num_days = len(data)
running = True
current = 0

# 云朵形状判定函数（椭圆+圆组合）
def in_cloud_shape(x, y):
    # 主椭圆
    cx, cy = CENTER
    if ((x-cx)/120)**2 + ((y-cy)/50)**2 < 1:
        return True
    # 左圆
    if ((x-(cx-60))**2 + (y-(cy-20))**2) < 40**2:
        return True
    # 右圆
    if ((x-(cx+70))**2 + (y-(cy-10))**2) < 50**2:
        return True
    # 上圆
    if ((x-(cx+10))**2 + (y-(cy-40))**2) < 35**2:
        return True
    return False

# 预生成云朵区域的点池（加速）
cloud_points = []
for _ in range(8000):
    x = random.randint(CENTER[0]-160, CENTER[0]+160)
    y = random.randint(CENTER[1]-70, CENTER[1]+70)
    if in_cloud_shape(x, y):
        cloud_points.append((x, y))

while running:
    # 背景
    screen.fill((135, 180, 255))

    # 当前云量
    d = data[current]
    cloud_ratio = (d['value'] - min_value) / (max_value - min_value) if max_value > min_value else 0
    # 浮点数量（最少300，最多1200）
    num_dots = int(300 + cloud_ratio * 900)

    # 画云朵浮点
    for i in range(num_dots):
        x, y = cloud_points[i % len(cloud_points)]
        # 颜色和透明度随云量变化
        alpha = int(120 + 100 * cloud_ratio + random.randint(-20, 20))
        dot_color = (255, 255, 255, max(80, min(220, alpha)))
        dot_radius = random.randint(4, 8)
        # 用Surface画带透明度的小圆点
        dot_surf = pygame.Surface((dot_radius*2, dot_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, dot_color, (dot_radius, dot_radius), dot_radius)
        screen.blit(dot_surf, (x-dot_radius, y-dot_radius))

    # 半透明信息框
    info_box_width = 320
    info_box_height = 80
    info_box = pygame.Surface((info_box_width, info_box_height), pygame.SRCALPHA)
    info_box.fill((30, 30, 40, 180))
    screen.blit(info_box, (CENTER[0]-info_box_width//2, 60))

    # 显示日期和云量
    info_text = f"{d['month']}月{d['day']}日"
    value_text = f"云量：{d['value']}%"
    info_surface = font.render(info_text, True, (255,255,255))
    value_surface = info_font.render(value_text, True, (200,220,255))
    screen.blit(info_surface, (CENTER[0]-info_surface.get_width()//2, 70))
    screen.blit(value_surface, (CENTER[0]-value_surface.get_width()//2, 110))

    pygame.display.flip()
    clock.tick(10)  # 动画速度

    current = (current + 1) % num_days

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
