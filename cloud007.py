import pygame
import pandas as pd
import random
import math

# ====== 可修改参数 ======
CSV_FILE = 'cloud.csv'
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 600
BG_COLOR = (245, 245, 255)
TITLE_COLOR = (40, 40, 80)
LABEL_COLOR = (60, 60, 60)
CLOUD_COLOR = (180, 200, 255)
PARTICLE_COLOR = (120, 160, 220)
PARTICLE_COLOR_HIGH = (80, 120, 200)
PARTICLE_COLOR_LOW = (200, 220, 255)
FONT_NAME = 'arial'
TITLE_FONT_SIZE = 38
LABEL_FONT_SIZE = 20
TICK_FONT_SIZE = 16
LEGEND_FONT_SIZE = 18
CLOUD_WIDTH = 60
CLOUD_HEIGHT = 38
PARTICLE_RADIUS = 5
PARTICLE_JITTER = 8  # 手绘感抖动
CLOUD_SPACING = 40   # 云朵之间距离
TOP_MARGIN = 110
BOTTOM_MARGIN = 120
LEFT_MARGIN = 80
RIGHT_MARGIN = 80

# ====== 数据读取与处理 ======
df = pd.read_csv(CSV_FILE, encoding='utf-8')
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
print(df.columns)  # 调试用，确认列名

def get_col(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    raise Exception(f"列名不匹配，请检查csv文件！候选：{candidates}")

cols = list(df.columns)
year_col = get_col(cols, ['year', '年/year'])
month_col = get_col(cols, ['month', '月/month'])
day_col = get_col(cols, ['day', '日/day'])
value_col = get_col(cols, ['value', '數值/value'])


dates = [f"{int(row[year_col])}-{int(row[month_col]):02d}-{int(row[day_col]):02d}" for _, row in df.iterrows()]
values = [float(row[value_col]) for _, row in df.iterrows()]
n_points = len(values)
min_val, max_val = min(values), max(values)

# ====== pygame初始化 ======
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('The average daily cloud content in Hong Kong')

title_font = pygame.font.SysFont(FONT_NAME, TITLE_FONT_SIZE, bold=True)
label_font = pygame.font.SysFont(FONT_NAME, LABEL_FONT_SIZE)
tick_font = pygame.font.SysFont(FONT_NAME, TICK_FONT_SIZE)
legend_font = pygame.font.SysFont(FONT_NAME, LEGEND_FONT_SIZE)

clock = pygame.time.Clock()

def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def draw_cloud_particles(center_x, center_y, value, n_particles, color_low, color_high):
    # 椭圆分布，带手绘抖动
    for i in range(n_particles):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.5, 1.0)
        a = CLOUD_WIDTH * r * random.uniform(0.85, 1.15) / 2
        b = CLOUD_HEIGHT * r * random.uniform(0.85, 1.15) / 2
        x = center_x + a * math.cos(angle) + random.uniform(-PARTICLE_JITTER, PARTICLE_JITTER)
        y = center_y + b * math.sin(angle) + random.uniform(-PARTICLE_JITTER, PARTICLE_JITTER)
        # 渐变色
        t = (value - min_val) / (max_val - min_val + 1e-6)
        color = lerp_color(color_low, color_high, t)
        pygame.draw.circle(screen, color, (int(x), int(y)), PARTICLE_RADIUS)

def draw():
    screen.fill(BG_COLOR)

    # 标题
    title_surf = title_font.render('The average daily cloud content in Hong Kong', True, TITLE_COLOR)
    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, TOP_MARGIN // 2))
    screen.blit(title_surf, title_rect)

    # 云朵粒子
    start_x = LEFT_MARGIN
    y_cloud = TOP_MARGIN + 80
    for i in range(n_points):
        x_cloud = start_x + i * (CLOUD_WIDTH + CLOUD_SPACING)
        if x_cloud > WINDOW_WIDTH - RIGHT_MARGIN:
            # 换行显示
            y_cloud += CLOUD_HEIGHT + 60
            start_x = LEFT_MARGIN
            x_cloud = start_x
        value = values[i]
        # 粒子数量与云含量成正比
        n_particles = int(10 + (value - min_val) / (max_val - min_val + 1e-6) * 60)
        draw_cloud_particles(x_cloud, y_cloud, value, n_particles, PARTICLE_COLOR_LOW, PARTICLE_COLOR_HIGH)
        # 日期标注
        date_text = tick_font.render(dates[i], True, LABEL_COLOR)
        screen.blit(date_text, (x_cloud - date_text.get_width() // 2, y_cloud + CLOUD_HEIGHT // 2 + 10))
        start_x = x_cloud + CLOUD_WIDTH + CLOUD_SPACING

    # 图例
    legend_x = LEFT_MARGIN
    legend_y = WINDOW_HEIGHT - BOTTOM_MARGIN + 40
    # 低含量云朵
    draw_cloud_particles(legend_x + 60, legend_y, min_val, 15, PARTICLE_COLOR_LOW, PARTICLE_COLOR_HIGH)
    min_text = legend_font.render('Lower', True, PARTICLE_COLOR_LOW)
    screen.blit(min_text, (legend_x + 30, legend_y + CLOUD_HEIGHT // 2 + 18))
    # 高含量云朵
    draw_cloud_particles(legend_x + 180, legend_y, max_val, 70, PARTICLE_COLOR_LOW, PARTICLE_COLOR_HIGH)
    max_text = legend_font.render('Higher', True, PARTICLE_COLOR_HIGH)
    screen.blit(max_text, (legend_x + 160, legend_y + CLOUD_HEIGHT // 2 + 18))
    # 图例说明
    legend_label = legend_font.render('Cloud Content (%)', True, LABEL_COLOR)
    screen.blit(legend_label, (legend_x + 80, legend_y - 28))

    # Y轴标签
    label_surf = label_font.render('Each cloud: one day', True, LABEL_COLOR)
    screen.blit(label_surf, (LEFT_MARGIN, TOP_MARGIN - 40))

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw()
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

if __name__ == '__main__':
    main()
