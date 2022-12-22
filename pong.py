import time, random, pygame, queue
from threading import Thread
from dataclasses import dataclass

player1_keys = {
    "UP": pygame.K_w,
    "DOWN": pygame.K_s,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d
}

player2_keys = {
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT
}

@dataclass
class Player:
    name: str
    wins: int
    hits: int
    movement_keys: dict[str, int]
    colour: tuple[int,int,int]

class CounterThread(Thread):
    def setup(self):
        self.count = 0
        self.interval = 1
        self.enabled = False
        self.callbacks= []
        self.on_count_callback = None
        self.on_count_ = 0
        self.name = "Counter thread"
    def run(self):
        if self.enabled:
            print("Timer already working")
            return
        self.enabled = True
        while self.enabled:
            time.sleep(self.interval)
            if not self.enabled:
                break
            self.count = self.count + 1
            if len(self.callbacks) > 0:
                for callback in self.callbacks:
                    callback(self.count)

    def on_increment(self, callback):
        self.callbacks.append(callback)
    def off_increment(self, callback):
        self.callbacks.remove(callback)
    def reset(self):
        self.count = 0
    def stop(self):
        self.enabled = False
        print("Stopped counter thread")
    def count(self):
        return self.count

class PlayerHandler(Thread):
    def setup(self, player, spawn_x):
        spawn_y = round((window_y-1)/2)
        self.working = False
        self.player: Player = player
        self.direction: int = 0
        self.length: int = 5
        self.loop_delay = 0.1
        self.blocks = [(spawn_x, spawn_y)]
        self.x = spawn_x
        step = block_length
        for _ in range(self.length):
            self.blocks.append((spawn_x, spawn_y+step))
            step = step + block_length
        print(self.blocks)
        
    def get_x(self):
        return self.x
    def run(self):
        #draw starting blockjs
        for block in self.blocks:
            x = block[0]
            y = block[1]
            pygame.draw.rect(display, self.player.colour, [x,y,block_length,block_length])
        pygame.display.update()
        while self.working:
            if self.direction != 0:
                self.move()
            time.sleep(self.loop_delay)

    def enable(self):
        self.working = True
    def disable(self):
        self.working = False
    def move(self):
        next_y = self.blocks[0][1]+self.direction
        if next_y < 0:
            return
        next_y = self.blocks[self.length][1]+self.direction
        if next_y > window_y-1:
            return
        old_blocks = self.blocks
        self.blocks = []
        for block in old_blocks:
            x = self.x
            y = block[1]
            pygame.draw.rect(display, bkg_colour, [x,y,block_length,block_length])
        
        for block in old_blocks:
            x = self.x
            y = block[1]+self.direction
            pygame.draw.rect(display, self.player.colour, [x,y,block_length,block_length])
            self.blocks.append((x,y))
        pygame.display.update()
    
    def HandleEvent(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            key = event.key
            print(key)
            if key == self.player.movement_keys["UP"]:
                self.direction = -10
            elif key == self.player.movement_keys["DOWN"]:
                self.direction = 10
        elif event.type == pygame.KEYUP:
            key = event.key
            print(key)
            if key == self.player.movement_keys["UP"] or  key == self.player.movement_keys["DOWN"]:
                self.direction = 0
    
class BallHandler(Thread):
    def setup(self, size: int, colour: tuple[int,int,int]):
        self.size = size
        self.colour = colour      
        self.loop_delay = 0.2
        self.x = round(window_x/2, -1)
        self.y = round(window_y/2, -1)
        self.working = False
        self.up = bool(random.randint(0,1))
        self.right = bool(random.randint(0,1))
        counter_thread.on_increment(self.onUpdate)
        
    def onUpdate(self, count):
        if count/5 == round(count/5):
            if self.loop_delay > 0.08:
                self.loop_delay = self.loop_delay - 0.02
    def run(self):

        while self.working:
            new_x: int = 0
            new_y: int = 0
            if self.right:
                new_x = self.x + self.size
            else:
                new_x = self.x - self.size 
            if self.up:
                new_y = self.y - self.size
                if new_y < 0:
                    print("New y is out of bounds (below)")
                    new_y = self.y + self.size
                    self.up = False
            else:
                new_y = self.y + self.size
                if new_y > window_y-1: 
                    print("New y is out of bounds (above)")
                    new_y = self.y - self.size
                    self.up = True

            new_x = int(new_x)
            new_y = int(new_y)
            if new_x < 0:
                    print("New x is out of bounds (below)")
                    if plr2_handler.get_x() == 0:
                        EndMatch(plr1)
                    elif plr1_handler.get_x() == 0:
                        EndMatch(plr2)
                    break
            elif new_x > window_x-1:
                    print("New x is out of bounds (above)")
                    if plr2_handler.get_x() == window_x-10:
                        EndMatch(plr1)
                    elif plr1_handler.get_x() == window_x-10:
                        EndMatch(plr2)
                    break
            else:
                block_colour = display.get_at((new_x, new_y)) 
                if block_colour == plr1.colour:
                    plr1.hits = plr1.hits + 1
                    self.right = not self.right
                    continue
                elif block_colour == plr2.colour:
                    plr2.hits = plr2.hits + 1
                    self.right = not self.right
                    continue
                
                
            pygame.draw.rect(display, bkg_colour, [self.x, self.y,self.size,self.size])

            self.x = new_x
            self.y = new_y
            pygame.draw.rect(display, self.colour, [self.x, self.y,self.size,self.size])
            pygame.display.update()
            time.sleep(self.loop_delay)
    def enable(self):
        self.working = True
    def disable(self):
        self.working = False


def EndMatch(victor: Player):
    print(f"{victor} wins!")
    display.fill(bkg_colour)
    
    font = pygame.font.SysFont(None, 40)
    text = font.render(f"{victor.name} wins!", True, (255,0,0))
    display.blit(text, (0,30))

    font = pygame.font.SysFont(None, 20)
    text = font.render("R to restart", True, (0,255,0))
    display.blit(text, (0,70))

    pygame.display.update()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                init()
                break
        elif event.type == pygame.QUIT:
            exit()
            break
    EndMatch(victor)

def EventHandler(event: pygame.event.Event):
        if event.type == pygame.QUIT:
            exit()
        else:
            plr1_handler.HandleEvent(event)
            plr2_handler.HandleEvent(event)

def exit():
    plr1_handler.disable()
    plr2_handler.disable()
    ball_handler.disable()
    pygame.quit()

def init():
    display.fill(bkg_colour)
    pygame.display.update()
    plr1_handler.enable()
    plr2_handler.enable()
    ball_handler.enable()

    counter_thread.start()
    plr1_handler.start()
    plr2_handler.start()
    ball_handler.start()

    while True:
        for event in pygame.event.get():
            EventHandler(event)
       # GoLeft()

block_length = 10
window_x =  400
window_y =  200
bkg_colour = (0,0,0)
main_queue = queue.Queue()

plr1 = Player(input("Player 1: "), 0,0, player1_keys, (255,0,0)) #input("Player 1's Name: ")
plr2 = Player(input("Player 2: "), 0,0, player2_keys, (0,0,255)) #input("Player 2's Name: ")
counter_thread = CounterThread()
counter_thread.setup()
plr1_handler = PlayerHandler(name="Player 1")
plr1_handler.setup(plr1, 0)
plr2_handler = PlayerHandler(name="Player 2")
plr2_handler.setup(plr2, window_x-10)
ball_handler = BallHandler(name="Ball")
ball_handler.setup(10, (255,255,255))


pygame.init()
pygame.display.set_caption('Pong ping game (OblivCode)')
display=pygame.display.set_mode((window_x, window_y))
clock = pygame.time.Clock()

init()
