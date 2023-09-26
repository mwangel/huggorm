import pygame
import random
import time
from enum import Enum

##########################################3
# Idéer
#
# * Monster
# * Fler ägg samtidigt men de försvinner snabbare.
# * Man rör sig snabbare och snabbare.
# * Ett ägg som gör en kortare.
# * Ett ägg som ger 5 poäng.
# * Ett ägg som gör att man kan äta monster.
# * Bomb som spränger runt omkring sig.
# * Monstret blir längre efter varje bana.
# * Monster som inte kan gå genom väggar.
##########################################3


class Riktning(Enum):
    HÖGER = "höger"
    VÄNSTER = "vänster"
    UPP = "upp"
    NER = "ner"


class Monster:
    x: int
    y: int
    hastighet: int
    riktning: str = Riktning.HÖGER
    color: pygame.Color


speed = 8
pygame.init()
fps = pygame.time.Clock()

gameIcon = pygame.image.load('snake-icon-48.png')
pygame.display.set_icon(gameIcon)

spelplan_bredd = 50
spelplan_hojd = 40
pluttstorlek = 20

pixel_width = pluttstorlek * spelplan_bredd
pixel_height = pluttstorlek * spelplan_hojd
S = pluttstorlek
x_squares = pixel_width // S
y_squares = pixel_height // S
screen = pygame.display.set_mode((pixel_width, pixel_height))
pygame.display.set_caption("HUGGORM - ett spel av Harry och Egard!")

# Sound effects
sound_yum = pygame.mixer.Sound("yum1.wav")
sound_fanfar = pygame.mixer.Sound("tadadadaa.wav")
sound_bom = pygame.mixer.Sound("bom.wav")

# Colors and fonts
color_orm = pygame.Color(0, 255, 0)
color_hinder = pygame.Color(127, 127, 127)
color_background = pygame.Color(50, 1, 50)
color_egg = pygame.Color(0, 0, 255)
color_health_egg = pygame.Color(255, 30, 30)
color_gameover_text = pygame.Color(255, 50, 50)
color_score_text = pygame.Color(200, 200, 50)
color_score_background = pygame.Color(40, 40, 40)
score_font = pygame.font.SysFont('courier', 23)

orm = [[x_squares // 2 * S, y_squares // 2 * S]]
riktning = None
score = 0

eggplats = [2 * S, 2 * S]
egg_life_time_in_moves = 50
egg_timer = egg_life_time_in_moves
egg_typ = 'ägg'

namn = ''
max_sekunder = 120
minsta_poang = 2

hinder = []

startplats = [x_squares // 2 * S, y_squares // 2 * S]


def get_value(txt: str):
    """abc=123 -> 123"""
    return txt.split("=")[1].strip()


def make_color(txt: str):
    [a, b, c] = txt.split(",")
    return pygame.Color(int(a), int(b), int(c))


def ladda_bana(nummer, spela_musik):
    global hinder
    global startplats
    global namn
    global max_sekunder
    global minsta_poang
    global S
    global color_background
    global color_hinder

    hinder.clear()
    filnamn = 'bana{:02d}.txt'.format(nummer)
    print(filnamn)
    with open(filnamn) as f:
        namn = get_value(f.readline())
        max_sekunder = get_value(f.readline())
        minsta_poang = get_value(f.readline())
        musik = get_value(f.readline())
        color_background = make_color(get_value(f.readline()))
        color_hinder = make_color(get_value(f.readline()))

        pygame.mixer.music.load(musik)
        if spela_musik:
            pygame.mixer.music.stop()
            pygame.mixer.music.play(-1)

        radnummer = 0
        while rad := f.readline():
            for tecken_position in range(0, len(rad)):
                if rad[tecken_position] == '#':
                    hinder.append([tecken_position * S, radnummer * S])
                if rad[tecken_position] == 'S':
                    startplats = [tecken_position * S, radnummer * S]

            radnummer = radnummer + 1
        print("Startplats:", startplats)

    # Gör så att man ser ut som en prick när man startar en ny bana.
    for ormdel in orm:
        ormdel[0] = startplats[0]
        ormdel[1] = startplats[1]


def slagit_i_huvudet(x, y):
    global hinder
    for hinderdel in hinder:
        if hinderdel[0] == x and hinderdel[1] == y:
            return True
    return False


def rita_egget(plats):
    if egg_typ == 'ägg':
        pygame.draw.circle(screen, color_egg, (plats[0] + S//2, plats[1] + S//2), S//2)
    else:  # 'extraliv'
        ex = plats[0]
        ey = plats[1]
        s3 = S//3

        pygame.draw.polygon(
            screen,
            color_health_egg,
            [(ex+s3, ey), (ex+2*s3, ey), (ex+2*s3, ey+s3),
             (ex+3*s3, ey+s3), (ex+3*s3, ey+2*s3), (ex+2*s3, ey+2*s3),
             (ex+2*s3, ey+3*s3), (ex+s3, ey+3*s3), (ex+s3, ey+2*s3),
             (ex, ey+2*s3), (ex, ey+s3), (ex+s3, ey+s3),
             ],
            4
        )


def rita_alla_hinder():
    for hinderdel in hinder:
        pygame.draw.rect(
            screen,
            color_hinder,
            pygame.Rect(hinderdel[0], hinderdel[1], S, S),
            border_top_left_radius=hinder_radie,
            border_top_right_radius=hinder_radie,
            border_bottom_left_radius=hinder_radie,
            border_bottom_right_radius=hinder_radie,
        )


def flytta_monster( monster: Monster ):
    riktningar = [Riktning.HÖGER, Riktning.VÄNSTER, Riktning.UPP, Riktning.NER]
    if monster.riktning == Riktning.HÖGER:
        monster.x += 1
    elif monster.riktning == Riktning.NER:
        monster.y += 1
    elif monster.riktning == Riktning.UPP:
        monster.y -= 1
    elif monster.riktning == Riktning.VÄNSTER:
        monster.x -= 1

    if monster.x > 50:
        monster.x = 0
    elif monster.x < 1:
        monster.x = 50
    elif monster.y < 1:
        monster.y = 40
    elif monster.y > 40:
        monster.y = 0

    if random.randint(0, 10) == 0:
        monster.riktning = riktningar[ random.randint(0, 3) ]

def rita_monster( monster: Monster ):
    pygame.draw.circle( screen, monster.color, (monster.x * S + S//2, monster.y * S + S//2), S*(0.5) )


def show_score():
    score_surface = score_font.render('Nivå ' + str(bannummer) + '. Poäng: ' + str(score) + '. Liv: ' + str(liv), True, color_score_text, color_score_background)
    score_rect = score_surface.get_rect()
    score_rect.topleft = (0, 0)
    screen.blit(score_surface, score_rect)


def game_over(text):
    pygame.mixer.music.stop()
    my_font = pygame.font.SysFont('times new roman', 50)
    gameover_surface = my_font.render((text if text else 'Game Over! ') + str(score) + " poäng", True, color_gameover_text)
    gameover_rect = gameover_surface.get_rect()
    gameover_rect.midtop = (pixel_width // 2, pixel_height // 2)
    screen.blit(gameover_surface, gameover_rect)
    pygame.display.flip()
    time.sleep(2)
    quit()


def lose_a_life(text):
    global liv
    global startplats
    global orm
    global riktning

    sound_bom.play()
    liv -= 1
    if liv <= 0:
        game_over(text)
    time.sleep(1)

    for ormdel in orm:
        ormdel[0] = startplats[0]
        ormdel[1] = startplats[1]

    riktning = ''


###################################################
# Start
###################################################
bannummer = 1
ladda_bana(nummer=bannummer, spela_musik=True)
pygame.mixer.music.set_volume(0.75)
pygame.mixer.music.play(-1, 0, 300)
musik = True
paused = False
hinder_radie = 5
ny_bana = True

liv = 1


monster = Monster()
monster.x = 20
monster.y = 20
monster.hastighet = 1
monster.riktning = Riktning.HÖGER
monster.color = pygame.Color("red")


while True:
    # Lyssna på knapptryckningar
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                # Tryck på Q för att avsluta.
                game_over('Hej då! ')
            elif event.key == pygame.K_DOWN:
                riktning = Riktning.NER
            elif event.key == pygame.K_RIGHT:
                riktning = Riktning.HÖGER
            elif event.key == pygame.K_UP:
                riktning = Riktning.UPP
            elif event.key == pygame.K_LEFT:
                riktning = Riktning.VÄNSTER
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_1:
                if speed > 1: speed -= 1
            elif event.key == pygame.K_2:
                speed += 1
            elif event.key == pygame.K_PLUS:
                bannummer += 1
                ladda_bana(bannummer, spela_musik=musik)
            elif event.key == pygame.K_MINUS:
                bannummer -= 1
                ladda_bana(bannummer, spela_musik=musik)
            elif event.key == pygame.K_m:
                musik = not musik
                if musik:
                    pygame.mixer.music.play(-1, 0, 300)
                else:
                    pygame.mixer.music.stop()

    if paused:
        fps.tick(10)
        continue

    # Rensa allt från bilden
    screen.fill(color_background)

    # Hitta en ny plats för ormens huvud
    huvudX = orm[0][0]
    huvudY = orm[0][1]
    if riktning == Riktning.HÖGER:
        huvudX += S
    elif riktning == Riktning.NER:
        huvudY += S
    elif riktning == Riktning.UPP:
        huvudY -= S
    elif riktning == Riktning.VÄNSTER:
        huvudX -= S

    if riktning:
        # Har man gått på sig själv?
        ny_huvudplats = [huvudX, huvudY]
        if ny_huvudplats in orm:
            lose_a_life("Du gick på dig själv.. ")
            continue

        # Gå runt till andra sidan om man kommit till kanten.
        if huvudX < 0:
            huvudX = ny_huvudplats[0] = pixel_width
        elif huvudX > pixel_width:
            huvudX = ny_huvudplats[0] = 0
        elif huvudY < 0:
            huvudY = ny_huvudplats[1] = pixel_height
        elif huvudY > pixel_height:
            huvudY = ny_huvudplats[1] = 0

        # Sätt in nya huvudplatsen först på ormen.
        orm.insert(0, ny_huvudplats)

        # Kolla om man kört in i kanten.
        if slagit_i_huvudet(huvudX, huvudY):
            lose_a_life("Kanten var för hård :( ")

        # Äten av ett monster?
        if [monster.x * S, monster.y * S] in orm:
            lose_a_life("Uppäten av ett monster!")

        # Kolla om man har ätit en matbit.
        if egg_timer > 0 and huvudX == eggplats[0] and huvudY == eggplats[1]:
            # Ge poäng och flytta ägget.
            sound_yum.play()
            score = score + 1
            if egg_typ == 'extraliv':
                liv += 1
            egg_timer = -1  # negativ egg_timer gör att ägg inte ritas ut

            if score % 5 == 0:
                bannummer = bannummer + 1
                riktning = None
                time.sleep(1)
                try:
                    ladda_bana(bannummer, musik)
                    ny_bana = True
                except FileNotFoundError:
                    game_over("Du vann! ")  # Nästa bana finns inte, då har man ju vunnit.
        else:
            # Tag bort svans-spetsen så att ormen inte blir oändligt lång.
            orm.pop()

    # Rita väggarna
    rita_alla_hinder()

    flytta_monster( monster )

    # Rita monster
    rita_monster( monster )

    # Rita huggormen
    for ormdel in orm:
        pygame.draw.rect(screen, color_orm, pygame.Rect(ormdel[0], ormdel[1], S, S))
        #pygame.draw.circle(screen, color_orm, (ormdel[0] + S//2, ormdel[1] + S//2), S*(0.6))
    pygame.draw.circle(screen, color_orm, (orm[0][0] + S//2, orm[0][1] + S//2), S*(0.7))

    # Rita ägg.
    if egg_timer > 0:
        rita_egget(eggplats)
        egg_timer = egg_timer - 1
    elif random.randint(1, 10) == 10:
        # Slumpa fram en ny äggplats och kolla att ägget inte är inne i en vägg.
        while True:
            egg_x = random.randint(1, x_squares-2)
            egg_y = random.randint(1, y_squares-2)
            eggplats = [egg_x * S, egg_y * S]
            if eggplats not in hinder: break
        # Ställ in äggklockan
        egg_timer = egg_life_time_in_moves
        egg_typ = 'extraliv' if random.randint(1, 10) == 1 else 'ägg'
        print("Ny äggplats:", eggplats)


    # Rita poängen.
    show_score()

    # Rita ut alltihop och vänta tills det är dags för nästa frame.
    pygame.display.update()
    if ny_bana:
        ny_bana = False
        sound_fanfar.play()
        time.sleep(2)
        pygame.event.clear()
    fps.tick(speed)
