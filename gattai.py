"""
スイカゲーム（背景のみ）
=======================================
・ウィンドウ表示と背景描画だけを行うベース部分
・フルーツや物理演算、スコアなどはまだ実装していない
"""
import os
import sys
import math

import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH, HEIGHT = 600, 800
FLOOR_Y = HEIGHT - 60
WALL_MARGIN = 40
GAME_OVER_LINE_Y = 120  # このラインを超えて積み上がったらゲームオーバー（予定）
GRAVITY = 0.5
RESTITUTION = 0.3  # 反発係数（0〜1）
FPS = 60

BALL_RADIUS = 12
BALL_IMAGE_PATH = "fig/0.png"


class Ball:
    """落ちてくる小さい球（画像で表示）"""

    delta = {  # 押下キーと移動量の辞書
        pg.K_a: (-7, 0),
        pg.K_d: (+7, 0),
    }

    def __init__(self, x: float, y: float, image: pg.Surface):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.falling = False  # Enterキーが押されるまでは静止
        size = BALL_RADIUS * 2
        self.image = pg.transform.smoothscale(image, (size, size))

    
    def update_physics(self):
        if not self.falling:
            return

        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # 壁との衝突
        if self.x - BALL_RADIUS < WALL_MARGIN:
            self.x = WALL_MARGIN + BALL_RADIUS
            self.vx *= -RESTITUTION
        if self.x + BALL_RADIUS > WIDTH - WALL_MARGIN:
            self.x = WIDTH - WALL_MARGIN - BALL_RADIUS
            self.vx *= -RESTITUTION

        # 床との衝突
        if self.y + BALL_RADIUS > FLOOR_Y:
            self.y = FLOOR_Y - BALL_RADIUS
            self.vy *= -RESTITUTION
            if abs(self.vy) < 1.0:
                self.vy = 0.0

    def draw(self, key_lst: list[bool],screen: pg.Surface):
        #初期位置移動
        sum_mv = [0, 0]
        if not self.falling:
            for key in self.delta:
                if key_lst[key]:
                    sum_mv[0] += self.delta[key][0]
                    sum_mv[1] += self.delta[key][1]
                # 壁との衝突（初期位置の移動が壁を越えないように制限）
                if self.x - BALL_RADIUS < WALL_MARGIN:
                    self.x = WALL_MARGIN + BALL_RADIUS
                if self.x + BALL_RADIUS > WIDTH - WALL_MARGIN:
                    self.x = WIDTH - WALL_MARGIN - BALL_RADIUS
        self.x += sum_mv[0]
        self.y += sum_mv[1]
        
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect)


def resolve_ball_collision(a: Ball, b: Ball):
    """2つの球が重なっていたら押し戻し、簡易的に弾き合う"""
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = BALL_RADIUS * 2

    if dist == 0 or dist >= min_dist:
        return

    overlap = min_dist - dist
    nx, ny = dx / dist, dy / dist

    # 重なりを均等に押し戻す
    a.x -= nx * overlap / 2
    a.y -= ny * overlap / 2
    b.x += nx * overlap / 2
    b.y += ny * overlap / 2

    # 簡易的な反発（速度を軽く交換して弾く）
    a.vy -= ny * 1.5
    b.vy += ny * 1.5


class Game:
    """ゲーム全体の進行を管理するクラス（現状は背景描画のみ）"""

    def __init__(self):
        pg.init()
        pg.display.set_caption("スイカゲーム（背景のみ）")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()

        self.ball_image = pg.image.load(BALL_IMAGE_PATH).convert_alpha()

        self.balls: list[Ball] = []
        self.current_ball = Ball(WIDTH // 2, GAME_OVER_LINE_Y, self.ball_image)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self._drop_ball()

    def _drop_ball(self):
        self.current_ball.falling = True
        self.balls.append(self.current_ball)
        # 次のボール生成場所を現在のボールのx座標に設定
        next_x = self.current_ball.x
        self.current_ball = Ball(next_x, GAME_OVER_LINE_Y, self.ball_image)

    def update(self):
        for ball in self.balls:
            ball.update_physics()

        # 全ペアの衝突判定
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                resolve_ball_collision(self.balls[i], self.balls[j])

    def draw(self):
        self.screen.fill((250, 240, 210))

        # ゲームオーバーライン
        pg.draw.line(self.screen, (255, 0, 0), (WALL_MARGIN, GAME_OVER_LINE_Y),
                     (WIDTH - WALL_MARGIN, GAME_OVER_LINE_Y), 2)

        # 壁と床
        pg.draw.line(self.screen, (100, 60, 30), (WALL_MARGIN, 0), (WALL_MARGIN, FLOOR_Y), 4)
        pg.draw.line(self.screen, (100, 60, 30), (WIDTH - WALL_MARGIN, 0), (WIDTH - WALL_MARGIN, FLOOR_Y), 4)
        pg.draw.line(self.screen, (100, 60, 30), (WALL_MARGIN, FLOOR_Y), (WIDTH - WALL_MARGIN, FLOOR_Y), 4)

        for ball in self.balls:
            ball.draw(pg.key.get_pressed(), self.screen)
        self.current_ball.draw(pg.key.get_pressed(),self.screen)

        pg.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()