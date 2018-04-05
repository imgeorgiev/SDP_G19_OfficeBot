#  a file to demonstrate that we could use nodes to represent the desks and junctions
#  which would ease expansion of the layout, and allow for the destination to be re-calculated mid-journey

north = 0  # degrees
east = 90
south = 180
west = 270

# map is a set of nodes and their adjacent nodes with directions
layout = { '1': {('J1', east)},  # desks
           '2': {('J1', west)},
           '3': {('J2', west)},
           '4': {('J4', north)},
           '5': {('J4', east)},
           '6': {('J5', east)},
           '7': {('J6', west)},
           '8': {('J7', east)},

           # junctions
           'J1': {('1', west),   ('2', east),   ('J2', north)},
           'J2': {('3', east),   ('J1', south), ('J3', north)},
           'J3': {('J2', south), ('J4', west),  ('J5', north)},
           'J4': {('4', south),  ('5', west),   ('J3', east)},
           'J5': {('6', west),   ('J3', south), ('J6', north)},
           'J6': {('7', east),   ('J5', south), ('J7', north)},
           'J7': {('8', west),   ('J6', south)}
       }

def main():
    print(convertCompassToLeftRight(layout, '1', '4'))

def bfs_paths(graph, start, goal):
    queue = [(start, [])]
    while queue:
        (vertex, path) = queue.pop(0)
        if type(vertex) is str:
            vertex = [vertex]

        for next in graph[vertex[0]] - set(path):
            if next[0] == goal:
                yield path + [next[1]]
            else:
                queue.append((next, path + [next[1]]))


def shortest_path(graph, start, goal):
    try:
        return next(bfs_paths(graph, start, goal))
    except StopIteration:
        return []
    except KeyError:
        print("Invalid value for desk")
        return []


def convertCompassToLeftRight(graph, start, goal):
    path = shortest_path(graph, start, goal)
    route = []
    if len(path) < 2:
        return []

    for i in range(len(path) - 1):
        # next orientation - current orientation will return degrees to turn
        degreesToTurn = path[i + 1] - path[i]
        
        if degreesToTurn == 0:
            route.append("straight")

        elif degreesToTurn == 90 or degreesToTurn == -270:
            route.append("right")

        elif degreesToTurn == 270 or degreesToTurn == -90:
            route.append("left")

        else:
            route.append("back")

    return route


if __name__ == '__main__':
    main()
