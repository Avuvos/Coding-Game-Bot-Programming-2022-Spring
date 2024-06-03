import math
import sys
from collections import namedtuple
from typing import List

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

Entity = namedtuple('Entity',
                    ['idx', 'type', 'x', 'y', 'shield_life', 'is_controlled', 'health', 'vx', 'vy', 'near_base',
                     'threat_for'])
ROAM_SPOT = "BOT"
ATTACKING_TURN = [0]

TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_ENEMY_HERO = 2

MAP_WIDTH = 17630
MAP_HEIGHT = 9000
BASE_RADIUS = 300

MIDDLE_X = MAP_WIDTH // 2
MIDDLE_Y = MAP_HEIGHT // 2
DELTA_MID = 2700

WIND_RANGE = 1280
SHIELD_RANGE = 2200
CONTROL_RANGE = 2200

MONSTER_SPEED = 400
HERO_SPEED = 800
HERO_DMG = 2

DANGER_ZONE = MONSTER_SPEED + BASE_RADIUS

MANA_COST = 10

MAX_TURNS = 220
LATE_GAME = 125
MID_GAME = 65
EARLY_GAME = 40

BASE_DEF_POS_X = 5500
BASE_DEF_POS_Y = 3340
SUPER_AGGRO_X = 16500
SUPER_AGGRO_Y = 7632
ENEMY_SIDE_X1 = 12000
ENEMY_SIDE_Y1 = 8200
ENEMY_SIDE_X2 = 17000
ENEMY_SIDE_Y2 = 3600

base_x, base_y = [int(i) for i in input().split()]
enemy_base_x, enemy_base_y = MAP_WIDTH - base_x, MAP_HEIGHT - base_y
my_mana = [0]

if base_x == 0:
    DEFAULT_DEF_POS = [(4700, 1600), (3000, 3600)]
    AGGRO_DEF_POS = [(6000, 730), (3000, 5900)]
    DEFAULT_ATTACK_POS = [(15500, 6300)]
    MIDDLE_AGGRO_X = MIDDLE_X + DELTA_MID
    MIDDLE_AGGRO_Y = MIDDLE_Y

else:
    DEFAULT_DEF_POS = [(MAP_WIDTH - 3000, MAP_HEIGHT - 3600), (MAP_WIDTH - 4700, MAP_HEIGHT - 1600)]
    AGGRO_DEF_POS = [(MAP_WIDTH - 6000, MAP_HEIGHT - 730), (MAP_WIDTH - 3000, MAP_HEIGHT - 5900)]
    DEFAULT_ATTACK_POS = [(MAP_WIDTH - 15500, MAP_HEIGHT - 6300)]
    MIDDLE_AGGRO_X = MIDDLE_X - DELTA_MID
    MIDDLE_AGGRO_Y = MIDDLE_Y
    BASE_DEF_POS_X = MAP_WIDTH - BASE_DEF_POS_X
    BASE_DEF_POS_Y = MAP_HEIGHT - BASE_DEF_POS_Y
    SUPER_AGGRO_X = MAP_WIDTH - SUPER_AGGRO_X
    SUPER_AGGRO_Y = MAP_HEIGHT - SUPER_AGGRO_Y
    ENEMY_SIDE_X1 = MAP_WIDTH - ENEMY_SIDE_X1
    ENEMY_SIDE_Y1 = MAP_HEIGHT - ENEMY_SIDE_Y1
    ENEMY_SIDE_X2 = MAP_WIDTH - ENEMY_SIDE_X2
    ENEMY_SIDE_Y2 = MAP_HEIGHT - ENEMY_SIDE_Y2
heroes_per_player = int(input())  # Always 3


# UTILS START-----------------------------------------------------------------------------------
def printd(msg: str):
    print(msg, file=sys.stderr, flush=True)


def dist(x1: int, y1: int, x2: int, y2: int) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def close_to_mid(hero: Entity) -> bool:
    return dist(hero.x, hero.y, MIDDLE_X, MIDDLE_Y) <= 6000


def close_to_mid_aggro(hero: Entity) -> bool:
    return dist(hero.x, hero.y, MIDDLE_AGGRO_X, MIDDLE_AGGRO_Y) <= 6000


def close_to_base(hero: Entity) -> bool:
    return dist(hero.x, hero.y, BASE_DEF_POS_X, BASE_DEF_POS_Y) <= 3000


def close_to_enemy_base(e: Entity) -> bool:
    return dist(e.x, e.y, enemy_base_x, enemy_base_y) <= 5500


def get_hero_idx(hero: Entity) -> int:
    if base_x == 0:
        return hero.idx
    return hero.idx - 3


def have_enough_mana() -> bool:
    return my_mana[0] >= MANA_COST


def use_mana():
    my_mana[0] -= MANA_COST


def move(x: int, y: int, msg: str = "") -> str:
    return f"MOVE {x} {y} {msg}"


def wind(x: int, y: int, msg: str = "") -> str:
    return f"SPELL WIND {x} {y} {msg}"


def shield(e: Entity, msg: str = "") -> str:
    return f"SPELL SHIELD {e.idx} {msg}"


def control(e: Entity, x: int, y: int, msg: str = "") -> str:
    return f"SPELL CONTROL {e.idx} {x} {y} {msg}"


# UTILS END -----------------------------------------------------------------------------------


# SPELLS FUNCTIONS START -----------------------------------------------------------------------------------

def in_wind_range(hero: Entity, m: Entity) -> bool:
    return dist(hero.x, hero.y, m.x, m.y) <= WIND_RANGE


# might be slightly wrong
def in_wind_range_next_turn(hero: Entity, m: Entity) -> bool:
    return dist(hero.x, hero.y, m.x, m.y) <= WIND_RANGE + HERO_SPEED + MONSTER_SPEED


def in_wind_range_any(hero: Entity) -> bool:
    return any(in_wind_range(hero, m) for m in monsters)


def in_wind_range_any_not_shielded(hero: Entity) -> bool:
    return any(in_wind_range(hero, m) and not is_shielded(m) for m in monsters)


def in_shield_range(hero: Entity, m: Entity) -> bool:
    return dist(hero.x, hero.y, m.x, m.y) <= SHIELD_RANGE


def in_control_range(hero: Entity, m: Entity) -> bool:
    return dist(hero.x, hero.y, m.x, m.y) <= CONTROL_RANGE


# shield monsters coming to enemy base
def in_shield_range_any(hero: Entity) -> bool:
    return any(in_shield_range(hero, m) and m.near_base == 1 and threat_for == 2 for m in monsters)


def is_shielded(e: Entity) -> bool:
    return e.shield_life != 0


def find_controllable_hero(hero: Entity) -> Entity:
    for eh in enemy_heroes:
        if in_control_range(hero, eh) and not is_shielded(eh) and not eh.is_controlled:
            return eh
    return None


def find_controllable_target(hero: Entity) -> Entity:
    for m in monsters:
        if in_control_range(hero, m) and threat_for == 0 and not m.threat_for == 2 \
                and not m.is_controlled and not is_shielded(m):
            return m
    return None


# SPELLS FUNCTIONS END -----------------------------------------------------------------------------------

# MONSTER FUNCTIONS START -----------------------------------------------------------------------------------
def turns_to_reach_some_base(monster: Entity, baseX: int, baseY: int) -> int:
    dist_from_base = dist(baseX, baseY, monster.x, monster.y) - BASE_RADIUS
    return int(dist_from_base // MONSTER_SPEED)


def turns_to_reach_base(monster: Entity) -> int:
    return turns_to_reach_some_base(monster, base_x, base_y)


def turns_to_reach_enemy_base(monster: Entity) -> int:
    return turns_to_reach_some_base(monster, enemy_base_x, enemy_base_y)


def can_kill_monster(hero: Entity, monster: Entity) -> bool:
    # check if i can even kill this monster in time assuming im HITTING it.
    time = turns_to_reach_base(monster)
    kill_time = math.ceil(monster.health // HERO_DMG)
    return kill_time <= time


def get_monster_rank(monster: Entity) -> int:
    monster_rank = 0
    if monster.near_base == 1 and monster.threat_for == 1:
        monster_rank += 500
    elif monster.threat_for == 1:
        monster_rank += 250
    total_dist_from_base = dist(monster.x, monster.y, base_x, base_y)
    dist_from_base_normalized = 1 / (total_dist_from_base + 1)
    monster_rank += dist_from_base_normalized * 250
    return monster_rank


def closest_entity_to_hero(hero: Entity, entities: List[Entity]) -> Entity:
    res = None
    min_dist = float('inf')
    for e in entities:
        curr_dist = dist(hero.x, hero.y, e.x, e.y)
        if curr_dist < min_dist:
            min_dist = curr_dist
            res = e
    return res


def closest_monster_to_hero(hero: Entity) -> Entity:
    return closest_entity_to_hero(hero, monsters)


def closest_enemy_hero_to_hero(hero: Entity) -> Entity:
    return closest_entity_to_hero(hero, enemy_heroes)


def closest_monster_to_enemy_base_not_shielded() -> Entity:
    res = None
    min_dist = float('inf')
    for m in monsters:
        curr_dist = dist(enemy_base_x, enemy_base_y, m.x, m.y)
        if curr_dist < min_dist and not is_shielded(m):
            min_dist = curr_dist
            res = m
    return res


def monster_in_range_of_hero(hero: Entity) -> bool:
    return any(m for m in monsters if dist(hero.x, hero.y, m.x, m.y) <= CONTROL_RANGE)


# MONSTER FUNCTIONS END -----------------------------------------------------------------------------------


# ATTACK FUNCTIONS START -----------------------------------------------------------------------------------

def hero_in_attack_pos(hero: Entity) -> bool:
    return dist(hero.x, hero.y, DEFAULT_ATTACK_POS[0][0], DEFAULT_ATTACK_POS[0][1]) <= 5000


def use_mana_offensive(hero: Entity) -> bool:  # will use "base safety func"
    threat_level = eval_base_safety()
    cost = max(MANA_COST, threat_level)
    # printd(f"cost = {cost}")
    return my_mana[0] >= cost


def use_shield_offensive(hero: Entity) -> bool:
    return use_mana_offensive(hero) and can_shield_monster(hero)


def should_shield_self(hero: Entity) -> bool:
    return hero.shield_life == 0 and use_mana_offensive(hero) and hero_in_attack_pos(hero)


def can_shield_monster(hero: Entity) -> bool:
    return in_shield_range_any(hero)


def should_explore_monster(hero: Entity, m: Entity) -> bool:
    return hero_in_attack_pos(hero) and m is not None and dist(hero.x, hero.y, m.x, m.y) <= 5000 \
           and not is_shielded(m)


def farm_or_defend(hero: Entity, monster: Entity) -> str:
    if not close_to_base(hero) or monster is None:
        return move(BASE_DEF_POS_X, BASE_DEF_POS_Y, "DEFEND")
    return move(monster.x, monster.y, "FARM")


# at least k monsters near enemy base
def enemy_under_pressure(k) -> bool:
    monsters_dist = sorted([(dist(e.x, e.y, enemy_base_x, enemy_base_y)) for e in monsters])
    printd(" ".join([str(x) for x in monsters_dist]))
    return sum([1 for m in monsters if close_to_enemy_base(m)]) >= k


def spells_logic(hero: Entity, target_x: int, target_y: int) -> str:
    ctrl_target = find_controllable_target(hero)
    monster = closest_monster_to_hero(hero)
    closest_not_shielded = closest_monster_to_enemy_base_not_shielded()
    if not use_mana_offensive(hero):
        return move(target_x, target_y, "ROAM")
    if closest_not_shielded is not None and in_shield_range(hero, closest_not_shielded) \
            and dist(closest_not_shielded.x, closest_not_shielded.y, enemy_base_x, enemy_base_y) <= 5000:
        use_mana()
        return shield(closest_not_shielded, "TAKE THAT")
    if in_wind_range_any(hero) and not is_shielded(monster) and hero_in_attack_pos(hero) and turn > EARLY_GAME:
        use_mana()
        return wind(enemy_base_x, enemy_base_y, "PUSH EM")
    if ctrl_target is not None and turn > EARLY_GAME:
        use_mana()
        return control(ctrl_target, enemy_base_x, enemy_base_y, "NOPE")
    if use_shield_offensive(hero) and not is_shielded(monster) and turn > EARLY_GAME:
        use_mana()
        return shield(monster, "TAKE THAT")
    return move(target_x, target_y, "ROAM")


def roam_around_enemy_base(hero: Entity) -> str:
    global ROAM_SPOT
    target_x, target_y = ENEMY_SIDE_X1, ENEMY_SIDE_Y1
    if ROAM_SPOT == "BOT":
        if dist(hero.x, hero.y, ENEMY_SIDE_X1, ENEMY_SIDE_Y1) <= 100:
            ROAM_SPOT = "TOP"
            target_x, target_y = ENEMY_SIDE_X2, ENEMY_SIDE_Y2
    elif ROAM_SPOT == "TOP":
        target_x, target_y = ENEMY_SIDE_X2, ENEMY_SIDE_Y2
        if dist(hero.x, hero.y, ENEMY_SIDE_X2, ENEMY_SIDE_Y2) <= 100:
            ROAM_SPOT = "BOT"
            target_x, target_y = ENEMY_SIDE_X1, ENEMY_SIDE_Y1
    if monster_in_range_of_hero(hero) and use_mana_offensive(hero):
        return spells_logic(hero, target_x, target_y)
    return move(target_x, target_y, "ROAM")


def aggro_function(hero: Entity) -> str:
    dist_from_aggro_pos = dist(hero.x, hero.y, SUPER_AGGRO_X, SUPER_AGGRO_Y)
    if enemy_under_pressure(2):
        ATTACKING_TURN[0] = 3  # change to 4?
        printd(f"dist from attack pos = {dist_from_aggro_pos}")
        if dist_from_aggro_pos <= 2200 and in_wind_range_any(hero) and have_enough_mana():
            use_mana()
            return wind(enemy_base_x, enemy_base_y, "PUSH EM")
        return move(SUPER_AGGRO_X, SUPER_AGGRO_Y, "GO AGGRO")
    else:
        return roam_around_enemy_base(hero)


def super_aggro_function(hero: Entity) -> str:
    ATTACKING_TURN[0] -= 1
    dist_from_aggro_pos = dist(hero.x, hero.y, SUPER_AGGRO_X, SUPER_AGGRO_Y)
    controllable_hero = find_controllable_hero(hero)
    printd(f"Attacking Turn = {ATTACKING_TURN[0]}")
    printd(f"dist from attack pos = {dist_from_aggro_pos}")
    m = closest_monster_to_enemy_base_not_shielded()
    if m is not None and dist(enemy_base_x, enemy_base_y, m.x, m.y) <= 2500 \
            and in_shield_range(hero, m) and have_enough_mana():
        use_mana()
        return shield(m, "TAKE THAT")
    if dist_from_aggro_pos <= 2200 and in_wind_range_any(hero) and have_enough_mana():
        printd("attack!!")  # this ^^ is key
        use_mana()
        return wind(enemy_base_x, enemy_base_y, "PUSH EM")
    if controllable_hero is not None:
        use_mana()
        return control(controllable_hero, base_x, base_y, "NOPE")
    return move(SUPER_AGGRO_X, SUPER_AGGRO_Y, "GO AGGRO")


# ATTACK FUNCTIONS END -----------------------------------------------------------------------------------


# DEFENSE FUNCTIONS START -----------------------------------------------------------------------------------

def base_hp_threat() -> int:
    if my_hp == 1:
        return 20
    if my_hp == 2:
        return 10
    return 0


def monsters_near_base() -> int:
    count = 0
    def1, def2 = defenders[0], defenders[1]
    for m in monsters:
        if not can_kill_monster(def1, m) and not can_kill_monster(def2, m):
            count += 1
    return count


def game_turn_state() -> int:
    if turn < MID_GAME:
        return 0
    elif MID_GAME <= turn < LATE_GAME:
        return 10
    return 20


def eval_base_safety() -> int:
    threat_level = 0
    threat_level += monsters_near_base() * 10
    threat_level += base_hp_threat()
    threat_level += game_turn_state()
    if check_threats():
        threat_level += 10
    return threat_level


def check_threats() -> bool:
    found_threat = False
    for m in monsters:
        turns_to_hit = turns_to_reach_base(m)
        for eh in enemy_heroes:
            if turns_to_hit <= 5 and in_wind_range_next_turn(eh, m) and enemy_mana >= MANA_COST:
                found_threat = True
    return found_threat


def get_defenders_targets():
    defense_targets = [None, None]
    if monster_ranked:
        m = monster_ranked[0][1]
        if dist(defenders[0].x, defenders[0].y, m.x, m.y) < dist(defenders[1].x, defenders[1].y, m.x, m.y):
            defense_targets[0] = m
        else:
            defense_targets[1] = m
    if len(monster_ranked) > 1:
        defense_targets[defense_targets.index(None)] = monster_ranked[1][1]
    return defense_targets


def enemy_triple_stack() -> bool:
    if len(enemy_heroes) <= 2: return False
    eps = 1200
    count = 0
    for i in range(len(enemy_heroes)):
        h1 = enemy_heroes[i]
        if dist(h1.x, h1.y, base_x, base_y) >= 7000: return False
        for j in range(i + 1, len(enemy_heroes)):
            h2 = enemy_heroes[j]
            if dist(h1.x, h1.y, h2.x, h2.y) < eps:
                count += 1
    return count >= 2


def handle_triple_stack(hero: Entity, eh: Entity) -> str:
    if in_control_range(hero, eh) and eh.is_controlled == 0 and have_enough_mana():
        use_mana()
        return control(eh, enemy_base_x, enemy_base_y, "NOPE")
    elif in_wind_range(hero, eh) and have_enough_mana():
        use_mana()
        return wind(enemy_base_x, enemy_base_y, "PUSH EM")
    return move(eh.x, eh.y, "OMW")


def enemy_not_attacking() -> bool:
    if len(enemy_heroes) < 3: return False
    for eh in enemy_heroes:
        if dist(eh.x, eh.y, base_x, base_y) <= 10000:
            return False
    return True


# DEFENSE FUNCTIONS END -----------------------------------------------------------------------------------


def get_attacker_action_late(hero: Entity) -> str:
    target_x, target_y = DEFAULT_ATTACK_POS[0][0], DEFAULT_ATTACK_POS[0][1]
    monster = closest_monster_to_hero(hero)
    threat_level = eval_base_safety()
    printd(f"threat = {threat_level}")
    if ATTACKING_TURN[0] > 0:
        return super_aggro_function(hero)
    if enemy_under_pressure(2) and my_mana[0] >= 30:
        printd(f"enemy is under pressure!")
        return aggro_function(hero)
    if threat_level >= 20 and my_mana[0] <= 60:  # go help base or farm i guess
        return farm_or_defend(hero, monster)
    if my_mana[0] >= 80 or (my_mana[0] >= 40 and enemy_under_pressure(4)):
        return aggro_function(hero)
    if not use_mana_offensive(hero) or not hero_in_attack_pos(hero):
        return move(target_x, target_y, "ROAM")
    if turn >= EARLY_GAME:
        return roam_around_enemy_base(hero)
    return move(target_x, target_y, "ROAM")


def get_attacker_action_early(hero: Entity) -> str:
    target_x, target_y = MIDDLE_AGGRO_X, MIDDLE_AGGRO_Y
    monster = closest_monster_to_hero(hero)
    if turn > 14 and monster is not None:
        target_x, target_y = monster.x, monster.y
    if monster is not None and dist(base_x, base_y, monster.x, monster.y) <= DANGER_ZONE + BASE_RADIUS \
            and in_wind_range(hero, monster) and have_enough_mana():
        use_mana()
        return wind(enemy_base_x, enemy_base_y, "PUSH DEF")
    return move(target_x, target_y, "FARM")


def get_attacker_action(hero: Entity) -> str:
    if turn < 85 and my_mana[0] <= 200:  # should be EARLY_GAME, but im testing it
        return get_attacker_action_early(hero)
    return get_attacker_action_late(hero)


def get_defender_action_late(hero: Entity) -> str:
    idx = get_hero_idx(hero) - 1
    target_x, target_y = DEFAULT_DEF_POS[idx][0], DEFAULT_DEF_POS[idx][1]
    eh = closest_enemy_hero_to_hero(hero)
    if enemy_triple_stack() and eh is not None:
        return handle_triple_stack(hero, eh)
    if def_targets[idx] is not None:
        m = def_targets[idx]
        printd(f"hero {hero.idx} {can_kill_monster(hero, m)} {m.idx} {turns_to_reach_base(m)} {m.health // 2}")
        target_x, target_y = m.x, m.y
        if is_shielded(m):
            return move(target_x, target_y, "DEFEND")
        if have_enough_mana() and in_wind_range_any(hero):
            if not can_kill_monster(hero, m) or check_threats():
                use_mana()
                return wind(enemy_base_x, enemy_base_y, "PUSH EM")
    return move(target_x, target_y, "DEFEND")


def get_defender_action_early(hero: Entity) -> str:
    idx = get_hero_idx(hero) - 1
    target_x, target_y = AGGRO_DEF_POS[idx][0], AGGRO_DEF_POS[idx][1]
    monster = def_targets[idx]
    if monster is not None:
        target_x, target_y = monster.x, monster.y
    return move(target_x, target_y, "FARM")


# TODO - try to identify threats like enemy hero pushing monsters to my base
def get_defender_action(hero: Entity) -> str:
    if turn < EARLY_GAME:
        return get_defender_action_early(hero)
    return get_defender_action_late(hero)


# game loop
turn = 0
while True:
    turn += 1
    # health: Your base health
    # mana: Ignore in the first league; Spend ten mana to cast a spell
    my_hp, my_mana[0] = [int(j) for j in input().split()]
    enemy_hp, enemy_mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see

    monsters = []
    my_heroes = []
    enemy_heroes = []

    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=monster, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Ignore for this league; Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this monster
        # vx: Trajectory of this monster
        # near_base: 0=monster with no target yet, 1=monster targeting a base
        # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in
                                                                                               input().split()]

        entity = Entity(_id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        if _type == TYPE_MONSTER:
            monsters.append(entity)
        elif _type == TYPE_MY_HERO:
            my_heroes.append(entity)
        elif _type == TYPE_ENEMY_HERO:
            enemy_heroes.append(entity)

    # only add monster if its close enough to our base
    monster_ranked = [(get_monster_rank(m), m) for m in monsters if dist(base_x, base_y, m.x, m.y) <= 9500]
    monster_ranked.sort(reverse=True)

    attacker = my_heroes[0]
    defenders = [my_heroes[1], my_heroes[2]]
    def1_idx, def2_idx = 0, 1
    def_targets = get_defenders_targets()

    # curr strategy
    # hero 0 is attacker
    # heroes 1 and 2 are defenders

    print(get_attacker_action(attacker))
    print(get_defender_action(defenders[def1_idx]))
    print(get_defender_action(defenders[def2_idx]))
