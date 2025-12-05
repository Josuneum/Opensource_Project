# Stage1 : NetworkX 최적 경로 찾기 게임
import pygame
import networkx
import itertools
import random
import math

from core.config import SCREEN_WIDTH, SCREEN_HEIGHT
from core.button import Button

class Stage1:
    def __init__(self, engine, difficulty):
        self.engine = engine
        self.difficulty = difficulty
        self.buttons = []
        self.nodes = []
        self.connections = []
        self.player_path = []
        self.last_button = None
        self.finished = False
        self.success = False
        node_count = {1: 6, 2: 8, 3: 10}[self.difficulty]
        
        # Back 버튼 생성
        back_btn = Button(15, 15, 60, 40, "Back", 18,
                          callback=self.back_to_start)
        self.buttons.append(back_btn)
        
        # 노드 생성
        self.nodes = self.generate_nodes(node_count)
        self.start, self.end = self.find_start_end(self.nodes)
        
        # 그래프 생성
        self.G = self.build_graph_with_distance(self.nodes)
        self.best_path, self.best_distance = self.tsp_path_with_endpoints(self.G, self.start, self.end)
        
        # 노드를 버튼으로 변환
        self.node_to_buttons()

    def tsp_path_with_endpoints(self, G, start, end):
        nodes = list(G.nodes())
        nodes.remove(start)
        nodes.remove(end)

        best_length = float("inf")
        best_path = None

        for perm in itertools.permutations(nodes):
            path = [start] + list(perm) + [end]
            cost = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))

            if cost < best_length:
                best_length = cost
                best_path = path

        return best_path, best_length

    def generate_nodes(self, count, min_dist=60):
        nodes = []
        MARGIN = 80

        while len(nodes) < count:
            x = random.randint(MARGIN, SCREEN_WIDTH - MARGIN)
            y = random.randint(MARGIN, SCREEN_HEIGHT - MARGIN)
            pos = (x, y)

            if all(math.dist(pos, p) >= min_dist for _, p in nodes):
                nodes.append((len(nodes), pos))

        return nodes

    def build_graph_with_distance(self, nodes):
        G = networkx.Graph()
        for node_id, pos in nodes:
            G.add_node(node_id, pos=pos)
        for i, (id1, pos1) in enumerate(nodes):
            for id2, pos2 in nodes[i+1:]:
                dist = math.dist(pos1, pos2)
                G.add_edge(id1, id2, weight=dist)
        return G

    def find_start_end(self, nodes):
        start = min(nodes, key=lambda x: x[1][0])[0]
        end = max(nodes, key=lambda x: x[1][0])[0]
        return start, end

    def node_clicked(self, btn):
        if self.finished:
            return

        # 첫 클릭은 반드시 start
        if self.last_button is None:
            if btn.node_id != self.start:
                return
            self.last_button = btn
            return

        if btn.node_id == self.last_button.node_id:
            return

        if btn.node_id in self.player_path:
            return

        if btn.node_id == self.end:
            self.connections.append((self.last_button.rect.center, btn.rect.center))
            self.finished = True
            self.check_result()
            return

        self.player_path.append(btn.node_id)
        self.connections.append((self.last_button.rect.center, btn.rect.center))
        self.last_button = btn

    def check_result(self):
        # player_path에는 start, end가 없고 중간 노드만 있으므로:
        player_nodes = [self.start] + self.player_path + [self.end]

        print("DEBUG player:", player_nodes)
        print("DEBUG best  :", self.best_path)

        if player_nodes == self.best_path:
            self.success = True
        else:
            self.success = False
            self.answer_path = self.best_path

        self.finished = True



    def node_to_buttons(self):
        for node_id, pos in self.nodes:
            label = "S" if node_id == self.start else "E" if node_id == self.end else str(node_id)
            btn = Button(pos[0], pos[1], 40, 40, label, 20, None)
            setattr(btn, "node_id", node_id)
            btn.callback = lambda b=btn: self.node_clicked(b)
            self.buttons.append(btn)


    def back_to_start(self):
        from .stage1_difficulty import Stage1DifficultyScreen
        self.engine.change_scene(Stage1DifficultyScreen(self.engine))

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((40, 40, 40))

        # 노드 연결선
        for p1, p2 in self.connections:
            pygame.draw.line(screen, (255, 255, 0), p1, p2, 4)

        # 마우스와 마지막 클릭 노드 연결선
        if self.last_button is not None and not self.finished:
            pygame.draw.line(screen, (0, 200, 255),
                             self.last_button.rect.center,
                             pygame.mouse.get_pos(), 2)

        # 버튼 표시
        for btn in self.buttons:
            btn.draw(screen)

        # 결과 메시지
        if self.finished:
            font = pygame.font.SysFont(None, 50)
            msg = "SUCCESS!" if self.success else "TRY AGAIN!"
            color = (0, 255, 0) if self.success else (255, 0, 0)
            text = font.render(msg, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - 100, 50))

        # draw() 내부 아래에 추가

    # 실패 시 정답 경로를 초록색으로 표시
        if self.finished and not self.success:
            for i in range(len(self.answer_path) - 1):
                n1 = self.answer_path[i]
                n2 = self.answer_path[i+1]

                pos1 = self.G.nodes[n1]["pos"]
                pos2 = self.G.nodes[n2]["pos"]

                pygame.draw.line(screen, (0, 255, 0), pos1, pos2, 4)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.buttons:
                btn.handle_event(event)