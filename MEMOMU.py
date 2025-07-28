import pygame, random, time, os

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MEMOMU")

COLS = {
    'bg': (0,0,0),
    'pink': (255, 105, 180),
    'lpink': (255, 182, 193),
    'blk': (0,0,0),
    'wht': (255,255,255),
    'g': (0,255,0),
    'r': (255,0,0)
}
F = pygame.font.SysFont("arial", 24)
F_BIG = pygame.font.SysFont("arial", 48)
F_MED = pygame.font.SysFont("arial", 32)
F_SML = pygame.font.SysFont("arial", 18)

def load_img(fn, size=(100,100)):
    try:
        img=pygame.image.load(f"assets/{fn}")
        return pygame.transform.scale(img, size)
    except:
        surf=pygame.Surface(size)
        surf.fill(COLS['pink'])
        return surf

def load_sound(fn):
    path = f"assets/{fn}"
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

memomu_img = load_img("MEMOMU1.png", (550, 275))
images = [load_img(f"image{i}.png") for i in range(1,13)]
monluck_imgs = [load_img(f"image{i}.png", (90,90)) for i in range(1,34)]
monad_img = load_img("monad.png", (90,90))
battle_tile_imgs = [load_img(f"image{i}.png") for i in range(14,34)]
avatar_imgs = [load_img(f"image{i}.png") for i in range(1,14)]
yupi, kuku, buuuu = [load_sound(s) for s in ["yupi.mp3", "kuku.mp3", "buuuu.mp3"]]

def play_snd(snd): ch = pygame.mixer.find_channel(); ch.play(snd) if ch and snd else None

def start_music():
    try:
        pygame.mixer.music.load("assets/MEMOMU.mp3")
        pygame.mixer.music.set_volume(0.56)
        pygame.mixer.music.play(-1)
    except: pass

def pause_music():
    try: pygame.mixer.music.pause()
    except: pass

def unpause_music():
    try: pygame.mixer.music.unpause()
    except: pass

def stop_music():
    try: pygame.mixer.music.stop()
    except: pass

class Button:
    def __init__(self, txt, x, y, wh=(180, 56), font=F, col=COLS['lpink'], dynamic_label=False):
        self.txt = txt
        self.rect = pygame.Rect(0,0,*wh)
        self.rect.center = (x,y)
        self.font = font
        self.col = col
        self.dynamic_label = dynamic_label
    def draw(self, color_override=None, text_color=None, dynamic_text=None):
        col = color_override if color_override else self.col
        pygame.draw.rect(screen, col, self.rect, border_radius=12)
        pygame.draw.rect(screen, COLS['blk'], self.rect, width=3, border_radius=12)
        txt_color = text_color if text_color else COLS['blk']
        label = dynamic_text if dynamic_text else self.txt
        t=self.font.render(label,1,txt_color)
        screen.blit(t,t.get_rect(center=self.rect.center))
    def hit(self, pos): return self.rect.collidepoint(pos)

class Tile:
    def __init__(self, x, y, img, idx, note=None, monad=False, let=None, mode="music"):
        self.x, self.y, self.img, self.idx, self.note, self.monad, self.let, self.mode = x,y,img,idx,note,monad,let,mode
        self.vis, self.feedback, self.fb_time, self.ang, self.rot = False, None, 0, 0, False
    def start_rot(self): self.rot=True; self.rot_t=time.time()
    def update(self):
        if self.rot: e=time.time()-self.rot_t; self.ang=e*360; self.rot = e<1
        else: self.ang=0
    def draw(self):
        sz = 90 if self.mode in ["memory","monluck"] else 100
        if self.feedback and time.time()<self.fb_time:
            pygame.draw.rect(screen, self.feedback, (self.x-sz//2-7,self.y-sz//2-7,sz+14,sz+14), border_radius=9)
        pygame.draw.rect(screen, COLS['lpink'], (self.x-sz//2-5,self.y-sz//2-5,sz+10,sz+10), border_radius=9)
        if self.mode in ["memory","monluck"]: pygame.draw.rect(screen, COLS['blk'], (self.x-sz//2,self.y-sz//2,sz,sz), border_radius=9)
        if self.vis:
            im=pygame.transform.rotate(self.img,self.ang)
            screen.blit(im, im.get_rect(center=(self.x,self.y)))
        elif self.mode=="monluck" and self.let:
            t=F_BIG.render(self.let,1,(180,180,180)); screen.blit(t,t.get_rect(center=(self.x,self.y)))
    def play_note(self):
        if self.note is not None:
            try:
                s=pygame.mixer.Sound(f"assets/note{(self.note%8)+1}.mp3")
                play_snd(s)
            except: pass
    def show_fb(self, good): self.feedback = COLS['g'] if good else COLS['r']; self.fb_time = time.time()+0.3; self.start_rot()
    def hit(self, pos): sz = 90 if self.mode in ["memory","monluck"] else 100; return pygame.Rect(self.x-sz//2,self.y-sz//2,sz,sz).collidepoint(pos)

class VirtualKeyboard:
    def __init__(self): self.keys=[]
    def init(self, tiles):
        self.keys=[]
        tile_notes = [(t.idx,t.note) for t in tiles if t.note is not None]
        others = [i for i in range(12) if i not in [idx for idx,_ in tile_notes]]
        notes = [n for _,n in tile_notes]; left=8-len(tile_notes)
        add_notes = [n for n in range(8) if n not in notes][:left] + [random.randint(0,7) for _ in range(left)]
        add_imgs = random.sample(others,min(len(others),left))
        all_notes = tile_notes + list(zip(add_imgs, add_notes))
        for i,(imgidx,note) in enumerate(all_notes):
            self.keys.append(Tile(160+i*60,620,images[imgidx%len(images)],imgidx,note=note,mode="music"))
        for x in [202,262,382,442,502,562,622]: self.keys.append(Tile(x,609,load_img("MEMOMU1.png",(36,44)),-1,mode="music"))
    def draw(self):
        [k.draw() for k in self.keys if k.note is not None]
    def click(self,pos): any(k.hit(pos) and k.play_note() for k in self.keys if k.note is not None)
class BattleMode:
    battle_names = [
        "molandak", "moyaki", "lyraffe", "chog", "skrumpey", "spiky nad", "potato",
        "mouch", "lazy", "retard", "bobr kurwa", "baba", "DAK"
    ]
    def __init__(self, parent):
        self.parent = parent
        self.reset_for_new_game()

    def reset_for_new_game(self):
        self.state = "rules"
        self.battle_player = None
        self.battle_opponent = None
        self.battle_phase = ""
        self.battle_click_rects = []
        self.battle_round = 0
        self.battle_pscore = 0
        self.battle_oscore = 0
        self.battle_grid = []
        self.battle_grid_ai = []
        self.battle_targets = []
        self.battle_ai_targets = []
        self.battle_timer = 0
        self.battle_flashing = False
        self.battle_clicks = []
        self.battle_click_results = []  # Track correct/wrong clicks for visual feedback
        self.battle_anim = 0
        self.battle_last_result = ""
        self.pspeed_bonus = 0
        self.ospeed_bonus = 0
        self.round_bonus = 0
        self.pscore_rounds = []
        self.oscore_rounds = []
        self.go_btn = Button("GO!", WIDTH//2, 610, (170,60), F_BIG)
        self.back_btn = Button("BACK", WIDTH//2, 400, (170,60), F_BIG)
        self.quit_btn = Button("QUIT", WIDTH//2, 650, (170,45), F_BIG)
        self.rules_gotit_btn = Button("GOT IT", WIDTH//2, 520, (170,60), F_BIG)
        self.create_choose_buttons()

    def create_choose_buttons(self):
        W,H=WIDTH,HEIGHT
        self.choose_buttons = []
        img_w, img_h = 60, 60
        col1_x, col2_x = WIDTH//2-180, WIDTH//2+40
        y_start = 90
        y_gap = 44+img_h//2
        self.battle_click_rects = []
        for i in range(7):
            idx = i
            rect = pygame.Rect(col1_x, y_start + i*y_gap, img_w, img_h)
            self.battle_click_rects.append((rect, idx))
        for i in range(6):
            idx = 7+i
            rect = pygame.Rect(col2_x, y_start + i*y_gap, img_w, img_h)
            self.battle_click_rects.append((rect, idx))

    def draw_rules(self):
        screen.fill(COLS['bg'])
        box=pygame.Rect(WIDTH//2-340,HEIGHT//2-220,680,380)
        pygame.draw.rect(screen,COLS['lpink'],box,border_radius=24)
        pygame.draw.rect(screen,COLS['pink'],box,4,border_radius=24)
        t1 = F_BIG.render("BATTLE MODE RULES:",1,COLS['blk'])
        screen.blit(t1, (WIDTH//2-320, HEIGHT//2-200))
        rules = [
            "- Each round: 4x4 grid for you and opponent.",
            "- Your avatar appears 1-5 times per grid (both always equal).",
            "- Rounds 1-2: Only avatars shown, rest are blank.",
            "- Rounds 3-5: All tiles filled (images + avatars).",
            "- Click all your avatars, but one mistake ends your round!",
            "- Each avatar found: +1pt. If you find all avatars and are faster: +1pt bonus.",
            "- Win round (more avatars, or all + speed): +1pt bonus.",
            "- Total score after 5 rounds wins!",
        ]
        for i, line in enumerate(rules):
            font = F
            t = font.render(line,1,COLS['blk'])
            screen.blit(t, (WIDTH//2-320, HEIGHT//2-130+i*35))
        self.rules_gotit_btn.draw()

    def draw_choose_avatar(self):
        screen.fill(COLS['bg'])
        img_w, img_h = 60, 60
        col1_x, col2_x = WIDTH//2-180, WIDTH//2+40
        y_start = 90
        y_gap = 44+img_h//2
        self.battle_click_rects = []
        for i in range(7):
            idx = i
            img = pygame.transform.scale(avatar_imgs[idx], (img_w,img_h))
            rect = pygame.Rect(col1_x, y_start + i*y_gap, img_w, img_h)
            screen.blit(img, rect)
            pygame.draw.rect(screen, COLS['blk'], rect, 2, border_radius=8)
            label = F.render(BattleMode.battle_names[idx],1,COLS['pink'])
            screen.blit(label, (col1_x+img_w+15, y_start + i*y_gap + img_h//2 - 12))
            self.battle_click_rects.append((rect, idx))
        for i in range(6):
            idx = 7+i
            img = pygame.transform.scale(avatar_imgs[idx], (img_w,img_h))
            rect = pygame.Rect(col2_x, y_start + i*y_gap, img_w, img_h)
            screen.blit(img, rect)
            pygame.draw.rect(screen, COLS['blk'], rect, 2, border_radius=8)
            label = F.render(BattleMode.battle_names[idx],1,COLS['pink'])
            screen.blit(label, (col2_x+img_w+15, y_start + i*y_gap + img_h//2 - 12))
            self.battle_click_rects.append((rect, idx))
        screen.blit(F_BIG.render("Choose your fighter!",1,COLS['lpink']),(WIDTH//2-170,30))

    def draw_grids(self):
        screen.fill(COLS['bg'])
        img_sz = int(100*1.3)
        # Avatars
        pimg = pygame.transform.scale(avatar_imgs[self.battle_player], (img_sz,img_sz))
        oimg = pygame.transform.scale(avatar_imgs[self.battle_opponent], (img_sz,img_sz))
        px, py = 60+40, 60
        ox, oy = WIDTH-160-40, 60
        screen.blit(pimg, (px, py))
        screen.blit(oimg, (ox, oy))
        vs_center = WIDTH//2
        t=F_BIG.render("VS",1,COLS['pink'])
        screen.blit(t, t.get_rect(center=(vs_center, 120)))

        pt = F.render(BattleMode.battle_names[self.battle_player],1,COLS['lpink'])
        ot = F.render(BattleMode.battle_names[self.battle_opponent],1,COLS['lpink'])
        ptx = px + img_sz//2 - 30
        otx = ox + img_sz//2 - 30
        screen.blit(pt, (ptx, py + img_sz + 12))
        screen.blit(ot, (otx, oy + img_sz + 12))

        score_y = 180
        ps = F_BIG.render(str(self.battle_pscore),1,COLS['lpink'])
        os = F_BIG.render(str(self.battle_oscore),1,COLS['lpink'])
        ps_rect = ps.get_rect(center=(vs_center-70, score_y))
        os_rect = os.get_rect(center=(vs_center+70, score_y))
        screen.blit(ps, ps_rect)
        screen.blit(os, os_rect)

        gx,gy=120,260
        cell_sz = 67  # Increased from 56px by ~20%
        grid_img_sz = 58  # Increased from 48px by ~20%
        for i in range(16):
            x=gx+(i%4)*cell_sz*1.2; y=gy+(i//4)*cell_sz*1.2
            rect=pygame.Rect(x,y,cell_sz,cell_sz)
            pygame.draw.rect(screen,COLS['lpink'],rect, border_radius=8)
            pygame.draw.rect(screen,COLS['blk'],rect,2, border_radius=8)
            
            # Show images during flashing phase
            if self.battle_flashing and self.battle_grid[i] is not None:
                img_to_draw = self.battle_grid[i]
                img_scaled = pygame.transform.scale(img_to_draw, (grid_img_sz,grid_img_sz))
                img_rect = img_scaled.get_rect(center=rect.center)
                screen.blit(img_scaled, img_rect)
            # Show images and highlights when clicked
            elif self.battle_phase=="click" and i in self.battle_clicks:
                # Determine if this click was correct or incorrect
                click_idx = self.battle_clicks.index(i)
                if click_idx < len(self.battle_click_results):
                    is_correct = self.battle_click_results[click_idx]
                    # Show red or green highlight
                    highlight_color = COLS['g'] if is_correct else COLS['r']
                    pygame.draw.rect(screen, highlight_color, rect, 4, border_radius=8)
                    # Show the image that was clicked
                    if self.battle_grid[i] is not None:
                        img_to_draw = self.battle_grid[i]
                        img_scaled = pygame.transform.scale(img_to_draw, (grid_img_sz,grid_img_sz))
                        img_rect = img_scaled.get_rect(center=rect.center)
                        screen.blit(img_scaled, img_rect)
                else:
                    # Fallback to green highlight if results not tracked yet
                    pygame.draw.rect(screen,COLS['g'],rect,4, border_radius=8)
        gx2,gy2=WIDTH-380,260
        for i in range(16):
            x=gx2+(i%4)*cell_sz*1.2; y=gy2+(i//4)*cell_sz*1.2
            rect=pygame.Rect(x,y,cell_sz,cell_sz)
            pygame.draw.rect(screen,COLS['lpink'],rect, border_radius=8)
            pygame.draw.rect(screen,COLS['blk'],rect,2, border_radius=8)
            if self.battle_flashing and self.battle_grid_ai[i] is not None:
                img_to_draw = self.battle_grid_ai[i]
                img_scaled = pygame.transform.scale(img_to_draw, (grid_img_sz,grid_img_sz))
                img_rect = img_scaled.get_rect(center=rect.center)
                screen.blit(img_scaled, img_rect)
        self.quit_btn.draw()

        # Show result text in a smaller font, centered better
        if self.battle_phase=="result":
            msg_y = HEIGHT - 120
            color = COLS['g'] if self.result_text.startswith("YOU WIN") else COLS['r'] if self.result_text.startswith("YOU LOSE") else COLS['lpink']
            t_msg = F.render(self.result_text,1,color)  # Changed from F_MED to F for smaller font
            msg_rect = t_msg.get_rect(center=(WIDTH//2,msg_y))
            screen.blit(t_msg, msg_rect)
        if self.battle_phase=="ready" and self.battle_round==0:
            self.go_btn.draw()
        if self.battle_phase=="click":
            left = max(0, 15-(time.time()-self.battle_timer))
            t=F.render(f"Time: {int(left)}s",1,COLS['pink'])
            screen.blit(t,(WIDTH//2-30,520))
        if self.battle_phase=="countdown":
            c=int(3-(time.time()-self.battle_anim))
            t=F_BIG.render(str(c),1,COLS['pink'])
            screen.blit(t, t.get_rect(center=(WIDTH//2,520)))

    def draw_end(self):
        screen.fill(COLS['bg'])
        img_sz = int(100*1.3)
        pimg = pygame.transform.scale(avatar_imgs[self.battle_player], (img_sz,img_sz))
        oimg = pygame.transform.scale(avatar_imgs[self.battle_opponent], (img_sz,img_sz))
        screen.blit(pimg, (60+40,60))
        screen.blit(oimg, (WIDTH-160-40,60))
        t=F_BIG.render("VS",1,COLS['pink'])
        screen.blit(t, t.get_rect(center=(WIDTH//2, 120)))
        t=F_BIG.render(f"{self.battle_pscore} : {self.battle_oscore}",1,COLS['pink'])
        screen.blit(t, t.get_rect(center=(WIDTH//2,200)))
        if self.battle_pscore>self.battle_oscore:
            msg="YOU WIN!"; color=COLS['g']
        elif self.battle_pscore<self.battle_oscore:
            msg="YOU LOSE!"; color=COLS['r']
        else: msg="DRAW!"; color=COLS['lpink']
        t=F_BIG.render(msg,1,color)
        screen.blit(t, t.get_rect(center=(WIDTH//2,300)))
        self.back_btn.draw()

    def draw(self):
        if self.state == "rules":
            self.draw_rules()
        elif self.state == "choose":
            self.draw_choose_avatar()
        elif self.state in ["vs", "fight"]:
            self.draw_grids()
        elif self.state == "end":
            self.draw_end()

    def click(self, pos):
        if self.state == "rules":
            if self.rules_gotit_btn.hit(pos):
                self.state = "choose"
        elif self.state == "choose":
            for rect, idx in self.battle_click_rects:
                if rect.collidepoint(pos):
                    self.battle_player = idx
                    pool = list(range(13))
                    pool.remove(idx)
                    self.battle_opponent = random.choice(pool)
                    self.battle_round = 0
                    self.battle_pscore = 0
                    self.battle_oscore = 0
                    self.pscore_rounds = []
                    self.oscore_rounds = []
                    self.state = "vs"
                    self.battle_phase = "ready"
                    return
        elif self.state == "vs":
            if self.battle_phase == "ready" and self.battle_round == 0:
                if self.go_btn.hit(pos):
                    self.prepare_battle_round()
                    self.battle_flashing = True
                    self.battle_anim = time.time()
                    self.battle_phase = "flash"
            elif self.battle_phase == "click":
                self.handle_grid_click(pos)
            if self.quit_btn.hit(pos):
                self.battle_pscore = 0
                self.battle_oscore = 99
                self.state = "end"
            elif self.battle_phase == "result":
                if self.quit_btn.hit(pos):
                    self.battle_pscore = 0
                    self.battle_oscore = 99
                    self.state = "end"
        elif self.state == "end":
            if self.back_btn.hit(pos):
                self.reset_for_new_game()
                self.parent.state = "mode"

    def prepare_battle_round(self):
        avatars = random.randint(1,5)
        self.avatars_this_round = avatars
        self.battle_grid, self.battle_targets = self.make_grid(self.battle_player, avatars, self.battle_round)
        self.battle_grid_ai, self.battle_ai_targets = self.make_grid(self.battle_player, avatars, self.battle_round)
        self.battle_clicks = []
        self.battle_click_results = []  # Clear click results for new round
        self.ai_clicks = []
        self.player_time = None
        self.ai_time = None
        self.battle_timer = 0
        self.result_text = ""
        self.ai_result = None
        self.battle_phase = "flash"
        self.battle_flashing = True
        self.battle_anim = time.time()

    def make_grid(self, avatar_idx, avatars, roundidx):
        grid = [None]*16
        avatar_pos = random.sample(range(16), avatars)
        for i in avatar_pos:
            grid[i] = avatar_imgs[avatar_idx]
        if roundidx < 2:
            for i in range(16):
                if grid[i] is None:
                    grid[i] = None
            return grid, avatar_pos
        else:
            pool = [i for i in range(len(battle_tile_imgs))]
            imgs_needed = 16 - avatars
            imgs = []
            while len(imgs) < imgs_needed:
                random.shuffle(pool)
                imgs += pool[:min(imgs_needed-len(imgs), len(pool))]
            img_ptr = 0
            for i in range(16):
                if grid[i] is None:
                    if img_ptr >= len(imgs):
                        img_ptr = 0
                    grid[i] = battle_tile_imgs[imgs[img_ptr]]
                    img_ptr+=1
            return grid, avatar_pos

    def handle_grid_click(self, pos):
        gx,gy=120,260
        cell_sz = 67  # Updated to match new size
        for i in range(16):
            x=gx+(i%4)*cell_sz*1.2; y=gy+(i//4)*cell_sz*1.2
            rect=pygame.Rect(x,y,cell_sz,cell_sz)
            if rect.collidepoint(pos) and i not in self.battle_clicks:
                if len(self.battle_clicks) < self.avatars_this_round:
                    self.battle_clicks.append(i)
                    
                    # Track if this click was correct or incorrect
                    is_correct = i in self.battle_targets
                    self.battle_click_results.append(is_correct)
                    
                    if i not in self.battle_targets:
                        # Wrong click - immediately end round
                        self.battle_phase="result"
                        self.player_time = time.time()-self.battle_timer
                        self.result_text = self.make_result_text(mistake=True)
                        self.battle_anim = time.time()
                        # Play loss sound
                        if buuuu:
                            play_snd(buuuu)
                        return
                    if sorted(self.battle_clicks)==sorted(self.battle_targets):
                        # All avatars found - player wins
                        self.player_time = time.time()-self.battle_timer
                        self.battle_phase="result"
                        self.result_text = self.make_result_text(mistake=False)
                        self.battle_anim = time.time()
                        # Play win sound
                        if yupi:
                            play_snd(yupi)
                        return

    def ai_play(self):
        ai_delay_per_tile = random.uniform(0.5, 1.1)
        total_time = ai_delay_per_tile * self.avatars_this_round + random.uniform(0, 1)
        return list(self.battle_ai_targets), total_time

    def update(self):
        if self.state != "vs":
            return
        if self.battle_phase == "flash":
            if time.time()-self.battle_anim>0.9:
                self.battle_flashing=False
                self.battle_timer = time.time()
                self.battle_phase="click"
                self.battle_clicks=[]
                self.battle_click_results=[]  # Reset click results for new click phase
                self.ai_done = False
        elif self.battle_phase == "click":
            if self.player_time is not None:
                if not hasattr(self, "ai_result") or not self.ai_result:
                    self.ai_result = self.ai_play()
                    self.ai_clicks, self.ai_time = self.ai_result
                ai_time_val = self.ai_time if self.ai_time is not None else 999
                if time.time() - self.battle_timer >= ai_time_val:
                    self.process_battle_result()
        elif self.battle_phase=="result":
            if time.time()-self.battle_anim>1.6:
                self.next_round_or_end()
        elif self.battle_phase=="countdown":
            if time.time()-self.battle_anim>3:
                self.battle_phase="ready"
                self.battle_clicks=[]
                self.ai_done = False

    def make_result_text(self, mistake=False):
        player_hits = len([i for i in self.battle_clicks if i in self.battle_targets])
        ai_hits = len(self.battle_ai_targets)
        player_all = sorted(self.battle_clicks)==sorted(self.battle_targets)
        ai_all = True
        ai_time_val = self.ai_time if hasattr(self, "ai_time") and self.ai_time is not None else 999
        player_faster = player_all and (self.player_time is not None and self.player_time < ai_time_val)
        msg = ""
        if mistake:
            msg = f"YOU LOSE ROUND! You got {player_hits} pts, Opponent {ai_hits} pts"
            self.battle_pscore += player_hits
            self.battle_oscore += ai_hits+1
        elif player_all and player_faster:
            msg = f"YOU WIN ROUND! {self.avatars_this_round} pts +1 speed +1 win"
            self.battle_pscore += self.avatars_this_round +2
            self.battle_oscore += ai_hits
        elif player_all:
            msg = f"YOU FINISHED! {self.avatars_this_round} pts"
            self.battle_pscore += self.avatars_this_round
            self.battle_oscore += ai_hits+1
        return msg

    def process_battle_result(self):
        if not hasattr(self, "result_text") or not self.result_text:
            self.result_text = self.make_result_text(mistake=not (sorted(self.battle_clicks)==sorted(self.battle_targets)))
        self.battle_phase = "result"
        self.battle_anim = time.time()
        self.ai_result = None

    def next_round_or_end(self):
        self.battle_round += 1
        if self.battle_round >= 5:
            self.state = "end"
        else:
            self.battle_phase = "countdown"
            self.battle_anim = time.time()
            self.prepare_battle_round()
            self.battle_flashing = True
            self.result_text = ""
            self.player_time = None

    def handle_click(self, pos):
        if self.state == "vs" and self.battle_phase == "click":
            self.handle_grid_click(pos)
            if self.quit_btn.hit(pos):
                self.battle_pscore = 0
                self.battle_oscore = 99
                self.state = "end"
        else:
            self.click(pos)
class Game:
    def __init__(self):
        self.state = "menu"
        self.round = 0
        self.score = 0
        self.wager = 10
        self.seq = []
        self.tiles = []
        self.memory_tiles = []
        self.monluck_tiles = []
        self.mem_seq, self.mem_found, self.monluck_hits, self.monluck_clicks = [],set(),0,0
        self.timer, self.scores, self.guess= 0,[],0
        self.vkb = VirtualKeyboard()
        self.music_img_seq=[]
        self.music_playing = True
        self.music_paused = False
        self.music_started = False
        self.letter_map = {7:"M",8:"O",9:"N",14:"L",15:"U",16:"C",17:"K"}
        self.buttons = self.make_buttons()
        self.battle_mode = BattleMode(self)
        self.ensure_music_state(force_start=True)

    def make_buttons(self):
        W,H=WIDTH,HEIGHT
        mode_y = 210 + 85  # move buttons down by 85px (3cm)
        mode_gap = 55
        mode_btns = [
            Button("MUSIC MEMORY",W//2,mode_y, (220,56), F),
            Button("MEMORY",W//2,mode_y+mode_gap, (180,56), F),
            Button("MONLUCK",W//2,mode_y+2*mode_gap, (180,56), F),
            Button("BATTLE",W//2,mode_y+3*mode_gap, (180,56), F),
            Button("SOUND",W-101,51),  # Sound button stays in top right
            Button("BACK",W//2,mode_y+4*mode_gap+20)
        ]
        return {
            "menu": [Button("NEW GAME",W//2,425,(325,66),F_BIG),Button("SOUND",W-101,51),Button("QUIT",W//2,504,(200,60),F_BIG)],
            "mode": mode_btns,
            "game_gotit":[Button("GOT IT",W//2,500)],
            "memory_start":[Button("GO",W//2,HEIGHT//2,(100,50)),Button("QUIT",W//2,HEIGHT//2+75,(100,44))],
            "mem_guess":[Button("QUIT",W//2,HEIGHT-50,(130,44))],
            "memory_phase":[Button("PLAY",W//2,540)],
            "monluck_start":[Button("START",W//2,500)],
            "monluck_result":[Button("AGAIN",W//2-100,450+23,(100,50)),Button("MENU",W//2+100,450+23,(100,50)),Button("QUIT",WIDTH//2,HEIGHT-50,(130,44))],
            "score_table":[Button("RESTART",W//2-150,HEIGHT//2+226,(100,50)),Button("MENU",W//2,HEIGHT//2+226,(100,50)),Button("QUIT",W//2+150,HEIGHT//2+226,(100,50))],
            "music_game_over":[Button("PLAY AGAIN",W//2-100,HEIGHT//2+50,(180,60),F_BIG),Button("QUIT",W//2+100,HEIGHT//2+50,(120,60),F_BIG)]
        }

    def reset(self):
        self.round=0; self.score=0; self.scores=[]; self.seq=[]; self.guess=0; self.mem_seq=[]; self.mem_found=set(); self.monluck_hits=0; self.monluck_clicks=0

    def setup_music(self): self.state = "music_mem_rules"; self.reset()

    def start_music_round(self):
        pos = [(175+i%4*150,150+i//4*150) for i in range(12)]
        n = min(3+self.round,12)
        notes = list(range(n))
        imgs = random.sample(range(len(images)), n)
        pairs = list(zip(imgs,notes))
        fill = [i for i in range(len(images)) if i not in imgs]
        extra = random.sample(fill,12-n) if len(fill)>=12-n else fill+random.choices(range(len(images)),k=12-n-len(fill))
        data = [("note",img,note) for img,note in pairs]+[("filler",img,None) for img in extra]; random.shuffle(data)
        self.tiles=[Tile(x,y,images[img],img,note=note,mode="music") for (kind,img,note),(x,y) in zip(data,pos)]
        seq = [img for img,_ in pairs]; s=list(seq); random.shuffle(s)
        self.music_img_seq = s
        self.seq = [note for _,note in pairs]
        self.vkb.init(self.tiles)
        self.guess=0

    def setup_memory(self):
        pos = [(130+(i%6)*108,75+(i//6)*108) for i in range(30)]
        self.memory_tiles=[Tile(x,y,monluck_imgs[i%len(monluck_imgs)],i,mode="memory") for i,(x,y) in enumerate(pos)]
        self.state = "memory_start"
        self.reset()

    def start_memory_round(self):
        self.round+=1
        n=self.round
        self.mem_seq = random.sample(range(len(self.memory_tiles)), n)
        for t in self.memory_tiles: t.vis=False; t.feedback=None
        self.mem_found=set(); self.timer=time.time(); self.mem_bad=0; self.mem_left=n+1; self.state = "memory_show"

    def setup_monluck(self):
        pos = [(130+(i%6)*108,75+(i//6)*108) for i in range(30)]
        kind = ["normal"]*25+["monad"]*5
        random.shuffle(kind)
        self.monluck_tiles=[]
        img_indices = list(range(33))
        random.shuffle(img_indices)
        img_ptr = 0
        for i,(knd) in enumerate(kind):
            if img_ptr >= 33:
                img_ptr = 0
                random.shuffle(img_indices)
            img = monad_img if knd=="monad" else monluck_imgs[img_indices[img_ptr]]
            t=Tile(pos[i][0],pos[i][1],img,i,monad=(knd=="monad"),mode="monluck",let=self.letter_map[i] if i in self.letter_map else None)
            self.monluck_tiles.append(t)
            img_ptr += 1
        self.monluck_hits=0; self.monluck_clicks=0; self.state="monluck"

    def should_play_music(self):
        return self.state in ["menu", "mode", "credits"]

    def ensure_music_state(self, force_start=False):
        if self.should_play_music():
            if not self.music_started or force_start:
                start_music()
                self.music_playing = True
                self.music_started = True
                self.music_paused = False
            elif self.music_playing and self.music_paused:
                unpause_music()
                self.music_paused = False
            elif not self.music_playing and not self.music_paused:
                pause_music()
                self.music_paused = True
        else:
            if self.music_started and not self.music_paused:
                pause_music()
                self.music_paused = True
                self.music_playing = False

    def draw(self):
        self.ensure_music_state()
        s=self.state
        screen.fill(COLS['blk'])

        if s=="menu":
            screen.blit(memomu_img, (WIDTH//2-275,50))
            [b.draw() for b in self.buttons["menu"]]
            Button("CREDITS",WIDTH-95,HEIGHT-40,(150,50)).draw()
            txt = "SOUND OFF" if not self.music_playing else "SOUND ON"
            Button(txt, WIDTH-101, 51, (150,44)).draw()

        elif s=="mode":
            # Show memomu image as in the main menu
            screen.blit(memomu_img, (WIDTH//2-275,50))
            # Draw all mode buttons, which are moved down by 85px
            for b in self.buttons["mode"]:
                b.draw()
            txt = "SOUND OFF" if not self.music_playing else "SOUND ON"
            Button(txt, WIDTH-101, 51, (150,44)).draw()

        elif s=="music_mem_rules":
            box=pygame.Rect(WIDTH//2-300,HEIGHT//2-200,600,350)
            pygame.draw.rect(screen,COLS['lpink'],box,border_radius=20)
            rules = [
                "MUSIC MEMORY MODE RULES:",
                "- Each round has three phases:",
                "  1. Memory Phase: Listen/watch the real melody (1–3 times).",
                "  2. Tricky Phase: Ignore the fake melody that plays next!",
                "  3. Guessing Phase: Click tiles in order from memory phase.",
                "- Points: +1 per correct tile, +2 bonus for perfect,",
                "  +1 per second left if perfect. Wrong tile ends round.",
                "- 13 rounds total. Highest score wins!",
                "- You can quit at any time using the QUIT button."
            ]
            for i, line in enumerate(rules):
                t = F_SML.render(line,1,COLS['blk'])
                screen.blit(t, (WIDTH//2-280,HEIGHT//2-150+i*28))
            self.buttons["game_gotit"][0].draw()

        elif s in ["memory_rules","monluck_rules"]:
            box=pygame.Rect(WIDTH//2-300,HEIGHT//2-200,600,350); pygame.draw.rect(screen,COLS['lpink'],box,border_radius=20)
            txts = {
                "memory_rules": ["MEMORY Mode Rules:","- Tiles flash in sequence.","- Memorize order.","- Click tiles in any order.","- Limited clicks: round+1.","- Points: 1/correct, +2 perfect, +1/sec only if perfect.","- Too many wrong: round ends."],
                "monluck_rules": ["MONLUCK Mode Rules:","- Click tiles to reveal symbols.","- Find 'monad' tiles in 5 clicks.","- Points: 1=2x,2=5x,3=40x,4=500x,5=1000x.","- No monads: game over!"]
            }
            for i,t in enumerate(txts[s]): screen.blit(F_SML.render(t,1,COLS['blk']),(WIDTH//2-280,HEIGHT//2-150+i*30))
            self.buttons["game_gotit"][0].draw()

        elif s in ["memory_phase","deceiving_phase","guessing_phase"]:
            screen.blit(F.render(f"Score: {self.score}",1,COLS['pink']),(10,10))
            screen.blit(F.render(f"Round: {self.round+1}/13",1,COLS['pink']),(10,40))
            # No pink table for QUIT in guessing phase, just render button
            if s=="memory_phase":
                self.buttons["memory_phase"][0].draw()
                self.buttons["mem_guess"][0].draw()  # QUIT button always visible, works any time
            elif s=="deceiving_phase":
                t=pygame.font.SysFont("arial",34).render("tricky tricky!",1,COLS['lpink'])
                screen.blit(t,t.get_rect(center=(WIDTH//2,66)))
                self.buttons["mem_guess"][0].draw()
            elif s=="guessing_phase":
                t=pygame.font.SysFont("arial",34).render("GMONAD!",1,COLS['lpink']); screen.blit(t,t.get_rect(center=(WIDTH//2,66)))
                tlim=20+self.round*3; left=max(0,tlim-(time.time()-self.timer))
                pygame.draw.rect(screen,COLS['bg'],(WIDTH-210,100,200,50))
                pygame.draw.rect(screen,COLS['pink'],(WIDTH-210,100,int(200*(left/tlim)),50))
                screen.blit(F.render(f"Time: {int(left)}s",1,COLS['blk']),(WIDTH-210,100))
                self.vkb.draw()
                self.buttons["mem_guess"][0].draw()  # QUIT button always visible
            [t.update() or t.draw() for t in self.tiles]

        elif s=="memory_show":
            [t.draw() for t in self.memory_tiles]

        elif s in ["memory_guessing","memory_start"]:
            [t.draw() for t in self.memory_tiles]
            if s=="memory_start": [b.draw() for b in self.buttons["memory_start"]]
            else: self.buttons["mem_guess"][0].draw()
            if s=="memory_guessing":
                tlim=5+(self.round-1)*2; left=max(0,tlim-(time.time()-self.timer))
                pygame.draw.rect(screen,COLS['bg'],(WIDTH-210,100,200,50))
                pygame.draw.rect(screen,COLS['pink'],(WIDTH-210,100,int(200*left/tlim),50))
                screen.blit(F.render(f"Time: {int(left)}s",1,COLS['blk']),(WIDTH-210,100))
                screen.blit(F.render(f"Score: {self.score}",1,COLS['pink']),(10,10))
                screen.blit(F.render(f"Round: {self.round}/10",1,COLS['pink']),(10,40))
                screen.blit(F.render(f"Clicks Left: {self.mem_left}",1,COLS['pink']),(10,70))

        elif s=="monluck":
            [t.update() or t.draw() for t in self.monluck_tiles]
            t=F_BIG.render(f"{5-self.monluck_clicks}",1,COLS['blk'])
            pygame.draw.rect(screen,COLS['lpink'],t.get_rect(center=(38,88)).inflate(8,8)); screen.blit(t,t.get_rect(center=(38,88)))
            self.buttons["monluck_result"][2].draw()

        elif s=="monluck_result":
            screen.blit(memomu_img, (WIDTH//2-275,50))
            mult={1:2,2:5,3:40,4:500,5:1000}
            m = f"YUPI! Score: {int(self.wager*mult.get(self.monluck_hits,0))}" if self.monluck_hits else "GMOVER!"
            t=F_BIG.render(m,1,COLS['blk'])
            pygame.draw.rect(screen,COLS['pink'],t.get_rect(center=(WIDTH//2,HEIGHT//2+60)).inflate(30,20))
            screen.blit(t,t.get_rect(center=(WIDTH//2,HEIGHT//2+60)))
            [b.draw() for b in self.buttons["monluck_result"]]

        elif s=="credits":
            t=F_BIG.render("CREDITS",1,COLS['lpink']); screen.blit(t,t.get_rect(center=(WIDTH//2,HEIGHT//2-100)))
            t2=F_SML.render("MEMOMU by Nhom1984. Music: Your track here.",1,COLS['pink'])
            screen.blit(t2, t2.get_rect(center=(WIDTH//2,HEIGHT//2-30)))
            self.buttons["game_gotit"][0].draw()
            txt = "SOUND ON" if self.music_playing else "SOUND OFF"
            cred_btn = Button(txt, WIDTH-101, 51, (150,44))
            cred_btn.draw()

        elif s=="score_table" and self.scores:
            sf = pygame.font.SysFont("arial",14); smf=pygame.font.SysFont("arial",20)
            n = len(self.scores); lh=18; w=210; h=50+n*lh+30; x=WIDTH//2-w//2
            img_h = min(170,int(400/(memomu_img.get_width()/memomu_img.get_height())))
            screen.blit(pygame.transform.smoothscale(memomu_img,(int(400),img_h)),(WIDTH//2-200,40))
            pygame.draw.rect(screen,COLS['lpink'],(x,250,w,h),border_radius=18); pygame.draw.rect(screen,COLS['pink'],(x,250,w,h),3,border_radius=18)
            t=smf.render("Score Summary",1,COLS['bg']); screen.blit(t,t.get_rect(center=(WIDTH//2,270)))
            for i,p in enumerate(self.scores): screen.blit(sf.render(f"Round {i+1}: {p} pts",1,COLS['blk']),(x+14,285+i*lh))
            screen.blit(sf.render(f"Total: {sum(self.scores)} pts",1,COLS['bg']),(x+14,250+h-22))
            [b.draw() for b in self.buttons["score_table"]]

        elif s=="music_game_over":
            # Draw the background game state but dimmed
            screen.fill(COLS['blk'])
            screen.blit(F.render(f"Score: {self.score}",1,COLS['pink']),(10,10))
            screen.blit(F.render(f"Round: {self.round+1}/13",1,COLS['pink']),(10,40))
            [t.update() or t.draw() for t in self.tiles]
            self.vkb.draw()
            
            # Draw pink overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)  # Semi-transparent
            overlay.fill(COLS['pink'])
            screen.blit(overlay, (0, 0))
            
            # Draw game over box
            box_width, box_height = 400, 250
            box_x = WIDTH//2 - box_width//2
            box_y = HEIGHT//2 - box_height//2
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            pygame.draw.rect(screen, COLS['pink'], box_rect, border_radius=20)
            pygame.draw.rect(screen, COLS['blk'], box_rect, width=4, border_radius=20)
            
            # Draw game over text
            game_over_text = F_BIG.render("GAME OVER!", 1, COLS['blk'])
            game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
            screen.blit(game_over_text, game_over_rect)
            
            # Draw score
            score_text = F_MED.render(f"Score: {self.score}", 1, COLS['blk'])
            score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
            screen.blit(score_text, score_rect)
            
            # Draw buttons
            [b.draw() for b in self.buttons["music_game_over"]]

        elif self.state == "battle":
            self.battle_mode.draw()

    def click(self,pos):
        s=self.state
        if s=="menu":
            if self.buttons["menu"][0].hit(pos): self.state="mode"; self.ensure_music_state()
            elif self.buttons["menu"][1].hit(pos):
                if not self.music_started: start_music(); self.music_started = True; self.music_playing = True; self.music_paused = False
                elif self.music_paused: unpause_music(); self.music_playing = True; self.music_paused = False
                else: pause_music(); self.music_playing = False; self.music_paused = True
            elif self.buttons["menu"][2].hit(pos): stop_music(); pygame.quit(); exit()
            elif Button("CREDITS",WIDTH-95,HEIGHT-40,(150,50)).hit(pos): self.state="credits"
        elif s=="mode":
            if self.buttons["mode"][0].hit(pos): self.state = "music_mem_rules"
            elif self.buttons["mode"][1].hit(pos): self.state = "memory_rules"
            elif self.buttons["mode"][2].hit(pos): self.state = "monluck_rules"
            elif self.buttons["mode"][3].hit(pos):
                self.state = "battle"
                self.battle_mode.reset_for_new_game()
            elif self.buttons["mode"][4].hit(pos):
                if not self.music_started: start_music(); self.music_started = True; self.music_playing = True; self.music_paused = False
                elif self.music_paused: unpause_music(); self.music_playing = True; self.music_paused = False
                else: pause_music(); self.music_playing = False; self.music_paused = True
            elif self.buttons["mode"][5].hit(pos): self.state="menu"; self.ensure_music_state()
        elif s=="music_mem_rules":
            if self.buttons["game_gotit"][0].hit(pos):
                self.music_playing = False; self.music_paused = True; pause_music()
                self.round=0; self.score=0; self.scores=[]; self.start_music_round(); self.state="memory_phase"
        elif s=="memory_rules":
            if self.buttons["game_gotit"][0].hit(pos):
                self.music_playing = False; self.music_paused = True; pause_music()
                self.setup_memory(); self.state="memory_start"
        elif s=="monluck_rules":
            if self.buttons["game_gotit"][0].hit(pos):
                self.music_playing = False; self.music_paused = True; pause_music()
                self.setup_monluck()
        elif s=="memory_phase":
            if self.buttons["memory_phase"][0].hit(pos):
                times = 1 if self.round+1 <= 3 else 2 if 4 <= self.round+1 <= 8 else 3
                for _ in range(times):
                    for imgidx in self.music_img_seq:
                        for t in self.tiles: t.vis = t.idx==imgidx
                        if any(t.vis for t in self.tiles): next(t for t in self.tiles if t.vis).play_note()
                        self.draw(); pygame.display.flip(); time.sleep(0.5)
                        for t in self.tiles: t.vis=False
                    time.sleep(0.5)
                self.state="deceiving_phase"
                self.deception_times = times
                self.deception_img_seq = list(self.music_img_seq)
                while True:
                    random.shuffle(self.deception_img_seq)
                    if self.deception_img_seq!=self.music_img_seq: break
                self.deception_played = 0
                self.deception_play_anim = time.time()
            # Handle QUIT button at all times in music memory
            elif self.buttons["mem_guess"][0].hit(pos):
                self.state="menu"; self.ensure_music_state()
        elif s=="deceiving_phase":
            # QUIT button always works
            if self.buttons["mem_guess"][0].hit(pos):
                self.state="menu"; self.ensure_music_state()
            else:
                if self.deception_played < self.deception_times:
                    if time.time() - self.deception_play_anim > 0.5:
                        for imgidx in self.deception_img_seq:
                            for t in self.tiles: t.vis = t.idx==imgidx
                            if any(t.vis for t in self.tiles): next(t for t in self.tiles if t.vis).play_note()
                            self.draw(); pygame.display.flip(); time.sleep(0.5)
                            for t in self.tiles: t.vis=False
                        time.sleep(0.5)
                        self.deception_played += 1
                        self.deception_play_anim = time.time()
                else:
                    self.state="guessing_phase"; [t for t in self.tiles if setattr(t,"vis",True)]
                    self.music_playing = False; self.music_paused = True; pause_music()
                    self.timer=time.time(); self.guess=0
        elif s=="guessing_phase":
            if self.buttons["mem_guess"][0].hit(pos):  # QUIT always works!
                self.state="menu"; self.ensure_music_state()
            else:
                self.vkb.click(pos)
                for t in self.tiles:
                    if t.hit(pos):
                        t.play_note(); t.start_rot()
                        if t.idx not in self.music_img_seq: t.show_fb(False); play_snd(kuku)
                        elif t.idx != self.music_img_seq[self.guess]: t.show_fb(False); play_snd(kuku)
                        else:
                            t.show_fb(True); self.guess+=1
                            if self.guess>=len(self.music_img_seq):
                                tlim=20+self.round*3; left=max(0,tlim-(time.time()-self.timer))
                                pts = self.guess+2+int(left)
                                self.scores.append(pts); self.score+=pts; self.round+=1
                                if self.round>=13: self.state="score_table"
                                else: self.start_music_round(); self.state="memory_phase"
                                return
                        if t.feedback==COLS['r']:
                            pts = self.guess
                            self.scores.append(pts); self.score+=pts; self.state="music_game_over"
                        break
        elif s=="memory_start":
            if self.buttons["memory_start"][0].hit(pos): self.start_memory_round()
            elif self.buttons["memory_start"][1].hit(pos): self.state="menu"; self.ensure_music_state()
        elif s=="memory_show": pass
        elif s=="memory_guessing":
            for t in self.memory_tiles:
                if t.hit(pos) and not t.vis:
                    self.mem_left-=1; t.vis=True; t.start_rot()
                    if t.idx in self.mem_seq and t.idx not in self.mem_found:
                        self.mem_found.add(t.idx); play_snd(yupi)
                        correct=True
                    else: self.mem_bad+=1; play_snd(kuku); correct=False
                    t.show_fb(correct)
                    perfect = len(self.mem_found)==len(self.mem_seq) and self.mem_bad==0
                    if len(self.mem_found)==len(self.mem_seq) or self.mem_bad>=2 or self.mem_left==0:
                        tlim=5+(self.round-1)*2; left=max(0,tlim-(time.time()-self.timer))
                        pts = len(self.mem_found)+(2 if perfect else 0)+(int(left) if perfect else 0)
                        self.scores.append(pts); self.score+=pts
                        self.state = "memory_start" if self.round<10 else "score_table"
                        return
            if self.buttons["mem_guess"][0].hit(pos): self.state="menu"; self.ensure_music_state()
        elif s=="monluck":
            for t in self.monluck_tiles:
                if t.hit(pos) and not t.vis:
                    t.vis=True; t.start_rot(); self.monluck_clicks+=1
                    t.let = None
                    if t.monad: self.monluck_hits+=1; play_snd(yupi); t.show_fb(True)
                    else: play_snd(kuku); t.show_fb(False)
                    if self.monluck_clicks>=5: self.state="monluck_result"
                    break
            if self.buttons["monluck_result"][2].hit(pos): self.state="menu"; self.ensure_music_state()
        elif s=="monluck_result":
            if self.buttons["monluck_result"][0].hit(pos): self.setup_monluck()
            elif self.buttons["monluck_result"][1].hit(pos): self.state="menu"; self.ensure_music_state()
            elif self.buttons["monluck_result"][2].hit(pos): self.state="menu"; self.ensure_music_state()
        elif s=="score_table":
            if self.buttons["score_table"][0].hit(pos):
                self.setup_memory() if self.round>=10 else self.setup_music()
            elif self.buttons["score_table"][1].hit(pos): self.state="menu"; self.ensure_music_state()
            elif self.buttons["score_table"][2].hit(pos): stop_music(); pygame.quit(); exit()
        elif s=="credits":
            if self.buttons["game_gotit"][0].hit(pos): self.state="menu"
            elif Button("SOUND ON" if self.music_playing else "SOUND OFF", WIDTH-101, 51, (150,44)).hit(pos):
                if not self.music_started: start_music(); self.music_started = True; self.music_playing = True; self.music_paused = False
                elif self.music_paused: unpause_music(); self.music_playing = True; self.music_paused = False
                else: pause_music(); self.music_playing = False; self.music_paused = True
        elif s=="music_game_over":
            if self.buttons["music_game_over"][0].hit(pos):  # PLAY AGAIN
                self.reset()
                self.setup_music()
            elif self.buttons["music_game_over"][1].hit(pos):  # QUIT
                self.state="menu"; self.ensure_music_state()
        elif s=="battle":
            self.battle_mode.handle_click(pos)

    def update(self):
        if self.state=="memory_show":
            elapsed=time.time()-self.timer
            for t in self.memory_tiles: t.vis=False
            if elapsed<1.0:
                for idx in self.mem_seq: self.memory_tiles[idx].vis=True; self.memory_tiles[idx].start_rot()
            else:
                self.state="memory_guessing"; self.timer=time.time()
        elif self.state=="guessing_phase":
            # Check for timeout in guessing phase
            tlim=20+self.round*3; left=max(0,tlim-(time.time()-self.timer))
            if left <= 0:
                # Time's up - end the game
                pts = self.guess
                self.scores.append(pts); self.score+=pts; self.state="music_game_over"
        elif self.state == "battle":
            self.battle_mode.update()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw(); pygame.display.flip()
            for e in pygame.event.get():
                if e.type==pygame.QUIT: stop_music(); running=False
                elif e.type==pygame.MOUSEBUTTONDOWN: self.click(e.pos)
            self.update(); clock.tick(60)
        pygame.quit()

if __name__=="__main__":
    Game().run()
