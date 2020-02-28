from model import *

def range_8(cell, map):
    r = cell.row
    c = cell.col
    res = []
    res.append(Cell(r, c + 1))
    res.append(Cell(r + 1, c + 1))
    res.append(Cell(r - 1, c + 1))
    res.append(Cell(r, c - 1))
    res.append(Cell(r + 1, c - 1))
    res.append(Cell(r - 1, c - 1))
    res.append(Cell(r, c))
    res.append(Cell(r + 1, c))
    res.append(Cell(r - 1, c))

    final_res = []
    for cella in res:
        if cella.row > -1 and cella.row < map.row_num and cella.col > -1 and cella.col < map.col_num:
            final_res.append(cella)
    return final_res

def init_base_graph(world):
    map = world.get_map()
    graph = []
    for r in range(map.row_num):
        tmp = []
        for c in range(map.col_num):
            tmp.append(0)
        graph.append(tmp)

    return graph

#TODO: Wheight it
def best_cell_for_range_8_spell(world, units, heal):
    map = world.get_map()

    graph = init_base_graph(world)
    for unit in units:
        for cell in range_8(cell=unit.cell, map=map):
            x = (heal and unit.hp + 2 > unit.base_unit.max_hp)
            if unit.hp > 1 and (not x):
                graph[cell.row][cell.col] += 1

    best_cell = Cell(1, 1)
    best_score = 0
    for r in range(map.row_num):
        for c in range(map.col_num):
            if graph[r][c] > best_score:
                best_score = graph[r][c]
                best_cell = Cell(r, c)


    return best_cell
