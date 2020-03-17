import random

from model import *
import utils


# def neighbor_cells(cell):
#     res = []
#     if (cell.col > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))
#     if (cell.row > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))
#     if (cell.col > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))
#     if (cell.col > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))



class AI:
    t1 = True
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.path_for_my_units = None

    def blablabla(self, seed, world):
        f_king = utils.range_8(cell=world.get_friend().king.center, map=world.get_map())
        for path in seed:
            for cell in f_king:
                for cell2 in path.cells:
                    if cell==cell2:
                        seed.remove(path)

        seed.sort(key=lambda x: len(x.cells))
        if len(seed) < 1:
            return None

        return seed[0]

    def find_path(self, world):
        map = world.get_map()
        e1_king = utils.range_8(cell=world.get_first_enemy().king.center, map=map)
        e2_king = utils.range_8(cell=world.get_second_enemy().king.center, map=map)

        seed1 = []
        seed2 = []

        all_paths = world.get_me().paths_from_player
        for path in all_paths:
            for cell in e1_king:
                if path.cells[-1] == cell:
                    seed1.append(path)
            for cell in e2_king:
                if path.cells[-1] == cell:
                    seed2.append(path)

        seed1.sort(key=lambda x: len(x.cells))
        seed2.sort(key=lambda x: len(x.cells))

        if len(seed2[0].cells) < len(seed1[0].cells):
            seed1, seed2 = seed2, seed1
        if world.get_current_turn() % 20 == 0:
            p = self.blablabla(seed=seed2, world=world)
            if p is None:
                return  seed1[0]
            else:
                return p
        else:
            return seed1[0]



    # this function is called in the beginning for deck picking and pre process
    def pick(self, world):
        print("pick started!")

        # pre process
        map = world.get_map()
        self.rows = map.row_num
        self.cols = map.col_num

        print("map log :", map.cells[0][0])

        # choosing all flying units
        all_base_units = world.get_all_base_units()
        my_hand = [base_unit for base_unit in all_base_units if base_unit.is_flying]

        # picking the chosen hand - rest of the hand will automatically be filled with random base_units
        world.choose_hand_by_id(type_ids=[0, 1, 2, 5, 6])
        # other pre process
        self.path_for_my_units = world.get_friend().paths_from_player[0]
    # it is called every turn for doing process during the game
    def turn(self, world):
        print("turn started:", world.get_current_turn())
        myself = world.get_me()
        max_ap = world.get_game_constants().max_ap

        if self.t1:
            for unit in myself.hand:
                world.put_unit(base_unit=unit, path=self.find_path(world))

        enemy_units = world.get_first_enemy().units + world.get_second_enemy().units
        friend_units = world.get_friend().units
        my_units = world.get_me().units

        hand = []
        for base_unit in myself.hand:
            hand.append(utils.uws(base_unit=base_unit))
        for unit in hand:
            unit.scr()
        hand.sort(key=lambda x: x.score, reverse=True)

        for unit in hand:
            world.put_unit(base_unit=unit.base_unit, path=self.find_path(world))


        # this code     tries to cast the received spell
        received_spell = world.get_received_spell()
        if received_spell is not None:
            print(received_spell)
            if received_spell.type == SpellType.HP and world.get_current_turn() > 15:
                if received_spell.target == SpellTarget.ENEMY:
                    world.cast_area_spell(center=utils.best_cell_for_range_8_spell(world, enemy_units, heal=False),
                                          spell=received_spell)
                else:
                    world.cast_area_spell(center=utils.best_cell_for_range_8_spell(world, friend_units, heal=True),
                                          spell=received_spell)

            elif received_spell.type == SpellType.TELE:
                last_unit = myself.units[-1]
                mid_cell = self.path_for_my_units.cells[len(self.path_for_my_units.cells) // 2 - 2]
                world.cast_unit_spell(last_unit, path=self.path_for_my_units, cell=mid_cell, spell=received_spell)
            elif received_spell.type == SpellType.DUPLICATE:
                best_score = 0
                best_unit = friend_units[0]
                for unit in friend_units:
                    unit_score = unit.hp + unit.attack + unit.range + 100 * int(unit.target != None) + 1000 * int(unit.target_if_king != None)
                    if (unit_score > best_score):
                        best_score = unit_score
                        best_unit = unit
                    world.cast_area_spell(best_unit.cell, spell=received_spell)

            elif received_spell.type == SpellType.HASTE:
                world.cast_area_spell(center=utils.best_cell_for_range_8_spell(world, enemy_units, heal=False),
                                      spell=received_spell)

            #Damage Upgrade Code:
            best_score = 0
            best_unit = my_units[0]
            for unit in my_units:
                unit_score = 10 * unit.hp  + 100 * int(unit.target_if_king != None)
                if (unit_score > best_score):
                    best_score = unit_score
                    best_unit = unit

            world.upgrade_unit_damage(unit=best_unit)
            world.upgrade_unit_range(unit=best_unit)

    # it is called after the game ended and it does not affect the game.
    # using this function you can access the result of the game.
    # scores is a map from int to int which the key is player_id and value is player_score
    def end(self, world, scores):
        print("end started!")
        print("My score:", scores[world.get_me().player_id])
