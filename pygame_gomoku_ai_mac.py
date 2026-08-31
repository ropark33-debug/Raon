import random, sys, time
import pygame

N=15; CELL=42; M=42; BOARD=M*2+CELL*(N-1); PANEL=320
W,H=BOARD+PANEL,BOARD
EMPTY,BLACK,WHITE=0,1,2
DIFF={1:("초급",0.55),2:("쉬움",0.25),3:("보통",0.10),4:("어려움",0.03),5:("매우 어려움",0.0)}

BG=(222,184,120); GRID=(55,45,35); PANEL_BG=(34,37,44); TXT=(245,245,245); MUTED=(175,181,191)
BTN=(68,74,86); BTN_H=(91,99,115); BTN_A=(56,120,85); RED=(220,40,40); BLUE=(20,100,180)

class Button:
    def __init__(self,x,y,w,h,text,action): self.rect=pygame.Rect(x,y,w,h); self.text=text; self.action=action
    def draw(self,screen,font,active=False):
        color=BTN_A if active else (BTN_H if self.rect.collidepoint(pygame.mouse.get_pos()) else BTN)
        pygame.draw.rect(screen,color,self.rect,border_radius=8)
        s=font.render(self.text,True,TXT); screen.blit(s,s.get_rect(center=self.rect.center))

def win(board,r,c,stone):
    for dr,dc in ((1,0),(0,1),(1,1),(1,-1)):
        count=1
        for sign in (1,-1):
            nr,nc=r+dr*sign,c+dc*sign
            while 0<=nr<N and 0<=nc<N and board[nr][nc]==stone:
                count+=1; nr+=dr*sign; nc+=dc*sign
        if count>=5: return True
    return False

class AI:
    def __init__(self,stone): self.stone=stone; self.enemy=WHITE if stone==BLACK else BLACK; self.nodes=0
    def candidates(self,b):
        if all(v==EMPTY for row in b for v in row): return [(N//2,N//2)]
        s=set()
        for r in range(N):
            for c in range(N):
                if b[r][c]!=EMPTY:
                    for dr in range(-2,3):
                        for dc in range(-2,3):
                            nr,nc=r+dr,c+dc
                            if 0<=nr<N and 0<=nc<N and b[nr][nc]==EMPTY: s.add((nr,nc))
        return list(s)
    def line_score(self,b,r,c,stone,dr,dc):
        count=1; open_ends=0
        for sign in (1,-1):
            nr,nc=r+dr*sign,c+dc*sign
            while 0<=nr<N and 0<=nc<N and b[nr][nc]==stone:
                count+=1; nr+=dr*sign; nc+=dc*sign
            if 0<=nr<N and 0<=nc<N and b[nr][nc]==EMPTY: open_ends+=1
        if count>=5:return 1_000_000
        if count==4:return 100_000 if open_ends==2 else 20_000
        if count==3:return 8_000 if open_ends==2 else 1_500
        if count==2:return 500 if open_ends==2 else 80
        return 15 if open_ends==2 else 1
    def score(self,b,r,c,stone):
        return sum(self.line_score(b,r,c,stone,dr,dc) for dr,dc in ((1,0),(0,1),(1,1),(1,-1)))
    def choose(self,b,level):
        self.nodes=0; cand=self.candidates(b)
        for stone in (self.stone,self.enemy):
            for r,c in cand:
                b[r][c]=stone; ok=win(b,r,c,stone); b[r][c]=EMPTY
                if ok:return (r,c)
        center=N//2; scored=[]
        for r,c in cand:
            atk=self.score(b,r,c,self.stone); dfn=self.score(b,r,c,self.enemy)
            scored.append((atk*1.08+dfn+20-abs(r-center)-abs(c-center),(r,c))); self.nodes+=1
        scored.sort(reverse=True)
        if not scored:return None
        rnd=DIFF[level][1]
        if rnd and random.random()<rnd:return random.choice(scored[:min(4,len(scored))])[1]
        return scored[0][1]

class Game:
    def __init__(self):
        pygame.init(); pygame.display.set_caption("Pygame 오목 - 사람 대 AI")
        self.screen=pygame.display.set_mode((W,H)); self.clock=pygame.time.Clock()
        self.font=self.mkfont(20); self.small=self.mkfont(16); self.title=self.mkfont(29,True); self.btnfont=self.mkfont(18,True)
        x=BOARD+18
        self.color_btn=[Button(x,142,134,38,"흑으로 시작","black"),Button(x+144,142,134,38,"백으로 시작","white")]
        self.diff_btn=[Button(x,250+(i-1)*38,278,31,f"{i}. {DIFF[i][0]}",str(i)) for i in range(1,6)]
        self.action_btn=[Button(x,485,278,44,"무르기 [R]","undo"),Button(x,539,278,44,"새 게임 [N]","reset")]
        self.human=BLACK; self.ai_stone=WHITE; self.level=3; self.reset()
    def mkfont(self,size,bold=False):
        for name in ("Apple SD Gothic Neo","Arial Unicode MS","Helvetica","Arial"):
            p=pygame.font.match_font(name,bold=bold)
            if p:return pygame.font.Font(p,size)
        return pygame.font.Font(None,size)
    def reset(self):
        self.board=[[0]*N for _ in range(N)]; self.turn=BLACK; self.history=[]; self.last=None; self.over=False; self.hover=None
        self.ai=AI(self.ai_stone); self.ai_time=0; self.ai_nodes=0
        self.msg="당신은 흑입니다. 먼저 두세요." if self.human==BLACK else "당신은 백입니다. AI가 먼저 둡니다."
        if self.human==WHITE: pygame.time.set_timer(pygame.USEREVENT+1,300,loops=1)
    def set_color(self,stone):
        self.human=stone; self.ai_stone=WHITE if stone==BLACK else BLACK; self.reset()
    def place(self,r,c,stone):
        if self.board[r][c]!=EMPTY:return
        self.board[r][c]=stone; self.history.append((r,c,stone)); self.last=(r,c)
        if win(self.board,r,c,stone):
            self.over=True; self.msg="게임 종료: 당신이 이겼습니다!" if stone==self.human else "게임 종료: AI가 이겼습니다."; return
        if len(self.history)==N*N:self.over=True; self.msg="게임 종료: 무승부입니다."; return
        self.turn=WHITE if stone==BLACK else BLACK; self.msg="당신의 차례입니다." if self.turn==self.human else "AI 차례입니다."
    def ai_move(self):
        if self.over or self.turn!=self.ai_stone:return
        self.msg="AI가 수를 계산하고 있습니다..."; self.draw(); pygame.display.flip()
        t=time.perf_counter(); mv=self.ai.choose(self.board,self.level); self.ai_time=time.perf_counter()-t; self.ai_nodes=self.ai.nodes
        if mv:self.place(*mv,self.ai_stone)
    def undo(self):
        if not self.history:return
        count=2 if len(self.history)>=2 else 1
        for _ in range(count):
            if self.history:
                r,c,_=self.history.pop(); self.board[r][c]=EMPTY
        self.last=self.history[-1][:2] if self.history else None; self.over=False
        if not self.history and self.human==WHITE:
            self.turn=BLACK; self.msg="AI가 먼저 둡니다."; pygame.time.set_timer(pygame.USEREVENT+1,250,loops=1)
        else:self.turn=self.human; self.msg="이전 수를 되돌렸습니다."
    def to_screen(self,r,c):return M+c*CELL,M+r*CELL
    def to_board(self,pos):
        x,y=pos; c=round((x-M)/CELL); r=round((y-M)/CELL)
        return (r,c) if 0<=r<N and 0<=c<N and x<BOARD else None
    def draw_board(self):
        self.screen.fill(BG)
        for i in range(N):
            p=M+i*CELL; pygame.draw.line(self.screen,GRID,(M,p),(BOARD-M,p),2); pygame.draw.line(self.screen,GRID,(p,M),(p,BOARD-M),2)
        for r,c in ((3,3),(3,11),(7,7),(11,3),(11,11)):
            pygame.draw.circle(self.screen,GRID,self.to_screen(r,c),5)
        if self.hover and not self.over and self.turn==self.human:
            r,c=self.hover
            if self.board[r][c]==EMPTY:pygame.draw.circle(self.screen,BLUE,self.to_screen(r,c),CELL//2-5,2)
        for r in range(N):
            for c in range(N):
                s=self.board[r][c]
                if s:
                    pos=self.to_screen(r,c); color=(28,28,28) if s==BLACK else (245,245,245)
                    pygame.draw.circle(self.screen,color,pos,CELL//2-4)
                    if s==WHITE:pygame.draw.circle(self.screen,(80,80,80),pos,CELL//2-4,2)
        if self.last:pygame.draw.circle(self.screen,RED,self.to_screen(*self.last),5)
    def draw_panel(self):
        pygame.draw.rect(self.screen,PANEL_BG,(BOARD,0,PANEL,H)); x=BOARD+18
        self.screen.blit(self.title.render("사람 대 AI 오목",True,TXT),(x,20)); self.screen.blit(self.small.render("15 × 15 오목판",True,MUTED),(x,59))
        self.screen.blit(self.font.render(self.msg,True,TXT),(x,92))
        for b in self.color_btn:b.draw(self.screen,self.small,(b.action=="black" and self.human==BLACK) or (b.action=="white" and self.human==WHITE))
        self.screen.blit(self.font.render("AI 난이도",True,TXT),(x,205))
        for i,b in enumerate(self.diff_btn,1):b.draw(self.screen,self.small,i==self.level)
        for b in self.action_btn:b.draw(self.screen,self.btnfont)
        self.screen.blit(self.small.render(f"현재 차례: {'흑' if self.turn==BLACK else '백'}",True,MUTED),(x,606))
        self.screen.blit(self.small.render(f"진행된 수: {len(self.history)}",True,MUTED),(x,630))
        if self.ai_time:self.screen.blit(self.small.render(f"AI 계산: {self.ai_time:.3f}초 / {self.ai_nodes} 후보",True,MUTED),(x,654))
        self.screen.blit(self.small.render("교차점을 클릭해 돌을 놓습니다.",True,MUTED),(x,684))
    def draw(self):self.draw_board(); self.draw_panel()
    def click_panel(self,pos):
        for b in self.color_btn:
            if b.rect.collidepoint(pos):self.set_color(BLACK if b.action=="black" else WHITE);return
        for i,b in enumerate(self.diff_btn,1):
            if b.rect.collidepoint(pos):self.level=i;self.msg=f"AI 난이도: {i}단계 {DIFF[i][0]}";return
        for b in self.action_btn:
            if b.rect.collidepoint(pos):self.undo() if b.action=="undo" else self.reset();return
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:pygame.quit();sys.exit()
                if e.type==pygame.USEREVENT+1:self.ai_move()
                elif e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_r:self.undo()
                    elif e.key==pygame.K_n:self.reset()
                    elif pygame.K_1<=e.key<=pygame.K_5:self.level=e.key-pygame.K_0
                elif e.type==pygame.MOUSEMOTION:self.hover=self.to_board(e.pos)
                elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                    if e.pos[0]>=BOARD:self.click_panel(e.pos)
                    else:
                        p=self.to_board(e.pos)
                        if p and not self.over and self.turn==self.human and self.board[p[0]][p[1]]==EMPTY:
                            self.place(*p,self.human)
                            if not self.over:pygame.time.set_timer(pygame.USEREVENT+1,250,loops=1)
            self.draw();pygame.display.flip();self.clock.tick(60)

if __name__=="__main__":Game().run()
