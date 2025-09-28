import pygame
import pandas as pd
import math

# ====== 可修改参数 ======
CSV_FILE = 'cloud.csv'
WIDTH, HEIGHT = 540, 540
CENTER = (WIDTH // 2, HEIGHT // 2)
RING_RADIUS = 170

# 配色板
BABY_POWDER = (243, 246, 243)
JORDY_BLUE = (158, 190, 237)
CHEFCHAOUEN_BLUE = (78, 144, 245)
APPLE_GREEN = (148, 192, 0)
DARK_MOSS_GREEN = (75, 107, 3)

BG_COLOR = JORDY_BLUE
TITLE_COLOR = CHEFCHAOUEN_BLUE
LABEL_COLOR = DARK_MOSS_GREEN
VALUE_COLOR = APPLE_GREEN
LOW_COLOR = DARK_MOSS_GREEN
HIGH_COLOR = BABY_POWDER
GLOW_COLOR = CHEFCHAOUEN_BLUE

TITLE_FONT_NAME = 'bahnschrift'
INFO_FONT_NAME = 'bahnschrift'
LEGEND_FONT_NAME = 'bahnschrift'
TITLE_FONT_SIZE = 22
INFO_FONT_SIZE = 22
VALUE_FONT_SIZE = 18
LEGEND_FONT_SIZE = 14

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
    # 云量低：DARK_MOSS_GREEN -> APPLE_GREEN -> CHEFCHAOUEN_BLUE -> JORDY_BLUE -> BABY_POWDER
    ratio = (value - min_value) / (max_value - min_value) if max_value > min_value else 0
    if ratio < 0.25:
        t = ratio / 0.25
        c1, c2 = DARK_MOSS_GREEN, APPLE_GREEN
    elif ratio < 0.5:
        t = (ratio - 0.25) / 0.25
        c1, c2 = APPLE_GREEN, CHEFCHAOUEN_BLUE
    elif ratio < 0.75:
        t = (ratio - 0.5) / 0.25
        c1, c2 = CHEFCHAOUEN_BLUE, JORDY_BLUE
    else:
        t = (ratio - 0.75) / 0.25
        c1, c2 = JORDY_BLUE, BABY_POWDER
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return (r, g, b)

def get_radius(value):
    # 云量越大，圆点越大
    if max_value == min_value:
        return 7
    return 7 + (value - min_value) / (max_value - min_value) * 16

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('The average daily cloud content in Hong Kong')

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
    screen.blit(title, (WIDTH//2-title.get_width()//2, 18))

    # 绘制所有圆点
    for i, d in enumerate(data):
        angle = i * angle_step
        x = CENTER[0] + RING_RADIUS * math.cos(angle - math.pi/2)
        y = CENTER[1] + RING_RADIUS * math.sin(angle - math.pi/2)
        color = get_color(d['value'])
        radius = get_radius(d['value'])
        if i == current:
            # 高亮当前日期：外发光描边
            for glow in range(1, 5):
                alpha = max(0, 80 - glow*15)
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
    screen.blit(info_surface, (CENTER[0]-info_surface.get_width()//2, CENTER[1]-22))
    screen.blit(value_surface, (CENTER[0]-value_surface.get_width()//2, CENTER[1]+10))

    # 下方图例（缩小版）
    legend_y = HEIGHT - 55
    # 低云量
    low_color = get_color(min_value)
    low_radius = get_radius(min_value)
    pygame.draw.circle(screen, low_color, (CENTER[0]-40, legend_y), int(low_radius))
    low_text = legend_font.render("Low", True, low_color)
    screen.blit(low_text, (CENTER[0]-40-low_text.get_width()//2, legend_y+low_radius+2))
    # 高云量
    high_color = get_color(max_value)
    high_radius = get_radius(max_value)
    pygame.draw.circle(screen, high_color, (CENTER[0]+40, legend_y), int(high_radius))
    high_text = legend_font.render("High", True, high_color)
    screen.blit(high_text, (CENTER[0]+40-high_text.get_width()//2, legend_y+high_radius+2))
    # 图例说明
    legend_label = legend_font.render("Cloud content (color & size)", True, (60, 80, 120))
    screen.blit(legend_label, (CENTER[0]-legend_label.get_width()//2, legend_y+max(low_radius, high_radius)+12))

    pygame.display.flip()
    clock.tick(12)  # 动画速度

    current = (current + 1) % num_days

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
