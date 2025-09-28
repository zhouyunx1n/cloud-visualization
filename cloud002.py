import pygame
import pandas as pd
import math

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

WIDTH, HEIGHT = 700, 700
CENTER = (WIDTH // 2, HEIGHT // 2)
RING_RADIUS = 230

values = [d['value'] for d in data]
min_value = min(values)
max_value = max(values)

def get_color(value):
    # 云量越大，颜色越亮
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    # 深蓝到白色
    r = int(0 + ratio * (255 - 0))
    g = int(51 + ratio * (255 - 51))
    b = int(102 + ratio * (255 - 102))
    return (r, g, b)

def get_radius(value):
    # 云量越大，圆点越大
    if max_value == min_value:
        return 8
    return 8 + (value - min_value) / (max_value - min_value) * 22

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('香港日平均云量星环动画')
font = pygame.font.SysFont('SimHei', 32)
info_font = pygame.font.SysFont('SimHei', 24)
clock = pygame.time.Clock()

num_days = len(data)
angle_step = 2 * math.pi / num_days
running = True
current = 0

# 渐变背景
def draw_gradient_bg(surface, center, inner_color, outer_color, radius):
    for i in range(radius, 0, -1):
        ratio = i / radius
        r = int(inner_color[0] * ratio + outer_color[0] * (1 - ratio))
        g = int(inner_color[1] * ratio + outer_color[1] * (1 - ratio))
        b = int(inner_color[2] * ratio + outer_color[2] * (1 - ratio))
        pygame.draw.circle(surface, (r, g, b), center, i)

while running:
    # 绘制径向渐变背景
    draw_gradient_bg(screen, CENTER, (60, 120, 255), (10, 20, 60), WIDTH//2)

    # 绘制所有圆点
    for i, d in enumerate(data):
        angle = i * angle_step
        x = CENTER[0] + RING_RADIUS * math.cos(angle - math.pi/2)
        y = CENTER[1] + RING_RADIUS * math.sin(angle - math.pi/2)
        color = get_color(d['value'])
        radius = get_radius(d['value'])
        if i == current:
            # 高亮当前日期：外发光描边
            for glow in range(1, 7):
                alpha = max(0, 80 - glow*12)
                glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, alpha), (int(x), int(y)), int(radius)+glow)
                screen.blit(glow_surf, (0,0))
            pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))
            pygame.draw.circle(screen, (255,255,255), (int(x), int(y)), int(radius), 2)
        else:
            pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))

    # 中间半透明信息框
    info_box_width = 320
    info_box_height = 80
    info_box = pygame.Surface((info_box_width, info_box_height), pygame.SRCALPHA)
    info_box.fill((30, 30, 40, 180))
    screen.blit(info_box, (CENTER[0]-info_box_width//2, CENTER[1]-info_box_height//2))

    # 显示日期和云量
    d = data[current]
    info_text = f"{d['month']}月{d['day']}日"
    value_text = f"云量：{d['value']}%"
    info_surface = font.render(info_text, True, (255,255,255))
    value_surface = info_font.render(value_text, True, (200,220,255))
    screen.blit(info_surface, (CENTER[0]-info_surface.get_width()//2, CENTER[1]-30))
    screen.blit(value_surface, (CENTER[0]-value_surface.get_width()//2, CENTER[1]+10))

    pygame.display.flip()
    clock.tick(12)  # 动画速度

    current = (current + 1) % num_days

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

