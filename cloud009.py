import pygame
import pandas as pd
import math
import os

# ====== 可修改参数 ======
CSV_FILE = 'cloud.csv'
WIDTH, HEIGHT = 900, 1000
CENTER = (WIDTH // 2, HEIGHT // 2)
RING_RADIUS = 300

BG_COLOR = (0, 0, 0)
TITLE_COLOR = (120, 220, 255)
LABEL_COLOR = (255, 255, 255)
VALUE_COLOR = (80, 255, 220)
LOW_COLOR = (30, 60, 180)
HIGH_COLOR = (120, 255, 255)
GLOW_COLOR = (255, 255, 255)
TITLE_FONT_NAME = 'bahnschrift'  # 未来感字体，可换成 'Orbitron', 'Arial Black', 'Segoe UI'
INFO_FONT_NAME = 'bahnschrift'
LEGEND_FONT_NAME = 'bahnschrift'
TITLE_FONT_SIZE = 38
INFO_FONT_SIZE = 36
VALUE_FONT_SIZE = 32
LEGEND_FONT_SIZE = 22

# ====== 读取数据 ======
df = pd.read_csv(CSV_FILE, encoding='utf-8')
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

values = [d['value'] for d in data]
min_value = min(values)
max_value = max(values)
num_days = len(data)
angle_step = 2 * math.pi / num_days

def get_color(value):
    # 云量越大，颜色越亮，低为深蓝，高为亮青蓝白
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    # 深蓝 -> 青蓝 -> 白
    if ratio < 0.5:
        t = ratio * 2
        r = int(LOW_COLOR[0] + (HIGH_COLOR[0] - LOW_COLOR[0]) * t)
        g = int(LOW_COLOR[1] + (HIGH_COLOR[1] - LOW_COLOR[1]) * t)
        b = int(LOW_COLOR[2] + (HIGH_COLOR[2] - LOW_COLOR[2]) * t)
    else:
        t = (ratio - 0.5) * 2
        r = int(HIGH_COLOR[0] + (255 - HIGH_COLOR[0]) * t)
        g = int(HIGH_COLOR[1] + (255 - HIGH_COLOR[1]) * t)
        b = int(HIGH_COLOR[2] + (255 - HIGH_COLOR[2]) * t)
    return (r, g, b)

def get_radius(value):
    # 云量越大，圆点越大
    if max_value == min_value:
        return 10
    return 10 + (value - min_value) / (max_value - min_value) * 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('The average daily cloud content in Hong Kong')

# 字体
def get_font(name, size, bold=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except:
        return pygame.font.SysFont('arial', size, bold=bold)

title_font = get_font(TITLE_FONT_NAME, TITLE_FONT_SIZE, True)
info_font = get_font(INFO_FONT_NAME, INFO_FONT_SIZE, True)
value_font = get_font(INFO_FONT_NAME, VALUE_FONT_SIZE, True)
legend_font = get_font(LEGEND_FONT_NAME, LEGEND_FONT_SIZE, True)
clock = pygame.time.Clock()

running = True
current = 0

while running:
    screen.fill(BG_COLOR)

    # 标题
    title = title_font.render("The average daily cloud content in Hong Kong", True, TITLE_COLOR)
    screen.blit(title, (WIDTH//2-title.get_width()//2, 40))

    # 绘制所有圆点
    for i, d in enumerate(data):
        angle = i * angle_step
        x = CENTER[0] + RING_RADIUS * math.cos(angle - math.pi/2)
        y = CENTER[1] + RING_RADIUS * math.sin(angle - math.pi/2)
        color = get_color(d['value'])
        radius = get_radius(d['value'])
        if i == current:
            # 高亮当前日期：外发光描边
            for glow in range(1, 8):
                alpha = max(0, 120 - glow*15)
                glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*GLOW_COLOR, alpha), (int(x), int(y)), int(radius)+glow*2)
                screen.blit(glow_surf, (0,0))
            pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))
            pygame.draw.circle(screen, (255,255,255), (int(x), int(y)), int(radius), 2)
        else:
            pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))

    # 中间英文日期和云量，无背景
    d = data[current]
    info_text = f"{d['month']:02d}-{d['day']:02d}"
    value_text = f"Cloud content: {d['value']:.0f}%"
    info_surface = info_font.render(info_text, True, LABEL_COLOR)
    value_surface = value_font.render(value_text, True, VALUE_COLOR)
    screen.blit(info_surface, (CENTER[0]-info_surface.get_width()//2, CENTER[1]-40))
    screen.blit(value_surface, (CENTER[0]-value_surface.get_width()//2, CENTER[1]+10))

    # 下方图例
    legend_y = HEIGHT - 90
    # 低云量
    low_color = get_color(min_value)
    low_radius = get_radius(min_value)
    pygame.draw.circle(screen, low_color, (CENTER[0]-100, legend_y), int(low_radius))
    low_text = legend_font.render("Low", True, low_color)
    screen.blit(low_text, (CENTER[0]-100-low_text.get_width()//2, legend_y+low_radius+8))
    # 高云量
    high_color = get_color(max_value)
    high_radius = get_radius(max_value)
    pygame.draw.circle(screen, high_color, (CENTER[0]+100, legend_y), int(high_radius))
    high_text = legend_font.render("High", True, high_color)
    screen.blit(high_text, (CENTER[0]+100-high_text.get_width()//2, legend_y+high_radius+8))
    # 图例说明
    legend_label = legend_font.render("Cloud content (color & size)", True, (180, 220, 255))
    screen.blit(legend_label, (CENTER[0]-legend_label.get_width()//2, legend_y+max(low_radius, high_radius)+32))

    pygame.display.flip()
    clock.tick(12)  # 动画速度

    current = (current + 1) % num_days

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
