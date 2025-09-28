import pygame
import pandas as pd
import math
import random

# ====== 可修改参数 ======
CSV_FILE = 'cloud.csv'
WIDTH, HEIGHT = 900, 600
TOP_MARGIN = 70
BOTTOM_MARGIN = 90
LEFT_MARGIN = 60
RIGHT_MARGIN = 60
BAR_WIDTH = 22
BAR_GAP = 14
CLOUD_RADIUS_BASE = 18
CLOUD_RADIUS_VAR = 32
PARTICLE_MIN = 12
PARTICLE_MAX = 38
PARTICLE_SIZE = 6
PARTICLE_FLOAT = 10
BG_COLOR = (12, 18, 32)  # 深夜蓝
BAR_COLOR_LOW = (60, 120, 255)  # 霓虹蓝
BAR_COLOR_HIGH = (180, 80, 255)  # 霓虹紫
BAR_GLOW_COLOR = (120, 220, 255)
CLOUD_COLOR_LOW = (120, 255, 255)  # 青蓝
CLOUD_COLOR_HIGH = (255, 120, 255)  # 粉紫
CLOUD_GLOW_COLOR = (255, 255, 255)
TITLE_COLOR = (180, 220, 255)
LABEL_COLOR = (120, 220, 255)
VALUE_COLOR = (255, 255, 255)
LEGEND_COLOR = (120, 220, 255)
TITLE_FONT_NAME = 'bahnschrift'  # 推荐Orbitron/Bahnschrift/Segoe UI
LABEL_FONT_NAME = 'bahnschrift'
VALUE_FONT_NAME = 'bahnschrift'
LEGEND_FONT_NAME = 'bahnschrift'
TITLE_FONT_SIZE = 38
LABEL_FONT_SIZE = 16
VALUE_FONT_SIZE = 20
LEGEND_FONT_SIZE = 14
FPS = 30

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

def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('The average daily cloud content in Hong Kong')

def get_font(name, size, bold=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except:
        return pygame.font.SysFont('arial', size, bold=bold)

title_font = get_font(TITLE_FONT_NAME, TITLE_FONT_SIZE, True)
label_font = get_font(LABEL_FONT_NAME, LABEL_FONT_SIZE, False)
value_font = get_font(VALUE_FONT_NAME, VALUE_FONT_SIZE, True)
legend_font = get_font(LEGEND_FONT_NAME, LEGEND_FONT_SIZE, True)
clock = pygame.time.Clock()

# ====== 云朵粒子生成 ======
def generate_cloud_particles(cx, cy, cloud_ratio, n_particles, t_anim):
    particles = []
    for i in range(n_particles):
        angle = random.uniform(0, 2*math.pi)
        r = random.uniform(0.5, 1.0)
        cloud_radius = CLOUD_RADIUS_BASE + cloud_ratio * CLOUD_RADIUS_VAR
        x = cx + cloud_radius * r * math.cos(angle)
        y = cy + cloud_radius * r * math.sin(angle)
        # 未来感漂浮动画
        x += math.sin(t_anim + i*0.7) * PARTICLE_FLOAT * random.uniform(0.7, 1.2)
        y += math.cos(t_anim + i*0.9) * PARTICLE_FLOAT * random.uniform(0.7, 1.2)
        particles.append((x, y))
    return particles

def draw_glow_rect(surface, color, rect, glow_color, glow_radius=16):
    # 画发光柱体
    x, y, w, h = rect
    glow_surf = pygame.Surface((w+glow_radius*2, h+glow_radius*2), pygame.SRCALPHA)
    for i in range(glow_radius, 0, -2):
        alpha = int(60 * (i/glow_radius))
        pygame.draw.rect(glow_surf, (*glow_color, alpha), (i, i, w, h), border_radius=8)
    surface.blit(glow_surf, (x-glow_radius, y-glow_radius))
    pygame.draw.rect(surface, color, rect, border_radius=8)

def draw_glow_circle(surface, color, pos, radius, glow_color, glow_radius=18):
    # 画发光云粒子
    x, y = pos
    glow_surf = pygame.Surface((radius*2+glow_radius*2, radius*2+glow_radius*2), pygame.SRCALPHA)
    for i in range(glow_radius, 0, -2):
        alpha = int(80 * (i/glow_radius))
        pygame.draw.circle(glow_surf, (*glow_color, alpha), (radius+glow_radius, radius+glow_radius), radius+i)
    surface.blit(glow_surf, (x-radius-glow_radius, y-radius-glow_radius))
    pygame.draw.circle(surface, color, (x, y), radius)

running = True
t_anim = 0

while running:
    screen.fill(BG_COLOR)
    t_anim += 0.04

    # 标题
    title = title_font.render("The average daily cloud content in Hong Kong", True, TITLE_COLOR)
    screen.blit(title, (WIDTH//2-title.get_width()//2, 22))

    # 柱状图+云朵
    plot_height = HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
    bar_area_width = num_days * BAR_WIDTH + (num_days-1) * BAR_GAP
    start_x = (WIDTH - bar_area_width) // 2
    for i, d in enumerate(data):
        ratio = (d['value'] - min_value) / (max_value - min_value + 1e-6)
        bar_x = start_x + i * (BAR_WIDTH + BAR_GAP)
        bar_h = int(ratio * plot_height * 0.85 + 30)
        bar_y = HEIGHT - BOTTOM_MARGIN - bar_h
        bar_color = lerp_color(BAR_COLOR_LOW, BAR_COLOR_HIGH, ratio)
        bar_glow = lerp_color(BAR_GLOW_COLOR, BAR_COLOR_HIGH, ratio)
        draw_glow_rect(screen, bar_color, (bar_x, bar_y, BAR_WIDTH, bar_h), bar_glow, glow_radius=12)
        # 柱顶云朵
        cloud_cx = bar_x + BAR_WIDTH // 2
        cloud_cy = bar_y
        n_particles = int(PARTICLE_MIN + ratio * (PARTICLE_MAX - PARTICLE_MIN))
        cloud_color = lerp_color(CLOUD_COLOR_LOW, CLOUD_COLOR_HIGH, ratio)
        cloud_glow = lerp_color(CLOUD_GLOW_COLOR, CLOUD_COLOR_HIGH, ratio)
        particles = generate_cloud_particles(cloud_cx, cloud_cy, ratio, n_particles, t_anim)
        for px, py in particles:
            draw_glow_circle(screen, cloud_color, (int(px), int(py)), PARTICLE_SIZE, cloud_glow, glow_radius=8)
        # 日期标注
        date_text = label_font.render(f"{d['month']:02d}-{d['day']:02d}", True, LABEL_COLOR)
        screen.blit(date_text, (bar_x + BAR_WIDTH//2 - date_text.get_width()//2, HEIGHT - BOTTOM_MARGIN + 8))
        # 云量标注
        value_text = value_font.render(f"{int(d['value'])}%", True, VALUE_COLOR)
        screen.blit(value_text, (bar_x + BAR_WIDTH//2 - value_text.get_width()//2, bar_y - 28))

    # 图例
    legend_y = HEIGHT - 54
    # 低云量柱+云
    low_ratio = 0
    low_bar_color = lerp_color(BAR_COLOR_LOW, BAR_COLOR_HIGH, low_ratio)
    low_bar_glow = lerp_color(BAR_GLOW_COLOR, BAR_COLOR_HIGH, low_ratio)
    draw_glow_rect(screen, low_bar_color, (LEFT_MARGIN, legend_y, BAR_WIDTH, 22), low_bar_glow, glow_radius=8)
    low_cloud_color = lerp_color(CLOUD_COLOR_LOW, CLOUD_COLOR_HIGH, low_ratio)
    low_cloud_glow = lerp_color(CLOUD_GLOW_COLOR, CLOUD_COLOR_HIGH, low_ratio)
    low_particles = generate_cloud_particles(LEFT_MARGIN + BAR_WIDTH//2, legend_y, low_ratio, PARTICLE_MIN, t_anim)
    for px, py in low_particles:
        draw_glow_circle(screen, low_cloud_color, (int(px), int(py)), PARTICLE_SIZE, low_cloud_glow, glow_radius=5)
    low_text = legend_font.render("Low", True, low_bar_color)
    screen.blit(low_text, (LEFT_MARGIN + BAR_WIDTH//2 - low_text.get_width()//2, legend_y+26))

    # 高云量柱+云
    high_ratio = 1
    high_bar_color = lerp_color(BAR_COLOR_LOW, BAR_COLOR_HIGH, high_ratio)
    high_bar_glow = lerp_color(BAR_GLOW_COLOR, BAR_COLOR_HIGH, high_ratio)
    draw_glow_rect(screen, high_bar_color, (WIDTH-RIGHT_MARGIN-BAR_WIDTH, legend_y, BAR_WIDTH, 22), high_bar_glow, glow_radius=8)
    high_cloud_color = lerp_color(CLOUD_COLOR_LOW, CLOUD_COLOR_HIGH, high_ratio)
    high_cloud_glow = lerp_color(CLOUD_GLOW_COLOR, CLOUD_COLOR_HIGH, high_ratio)
    high_particles = generate_cloud_particles(WIDTH-RIGHT_MARGIN-BAR_WIDTH//2, legend_y, high_ratio, PARTICLE_MAX, t_anim)
    for px, py in high_particles:
        draw_glow_circle(screen, high_cloud_color, (int(px), int(py)), PARTICLE_SIZE, high_cloud_glow, glow_radius=5)
    high_text = legend_font.render("High", True, high_bar_color)
    screen.blit(high_text, (WIDTH-RIGHT_MARGIN-BAR_WIDTH//2 - high_text.get_width()//2, legend_y+26))

    # 图例说明
    legend_label = legend_font.render("Cloud content (bar height & cloud size)", True, LEGEND_COLOR)
    screen.blit(legend_label, (WIDTH//2-legend_label.get_width()//2, legend_y+38))

    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

