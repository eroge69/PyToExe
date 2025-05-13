import sys
import os
from collections import deque


def read_graph_from_file(file_path):
    """
    Чтение двудольного графа из файла в формате Графоида
    Возвращает:
    - размеры долей (U_size, V_size)
    - матрицу смежности
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Чтение размеров долей
    U_size, V_size = map(int, lines[0].split())

    # Чтение матрицы смежности
    adj_matrix = []
    for line in lines[1:1 + U_size]:
        row = list(map(int, line.split()))
        adj_matrix.append(row)

    return U_size, V_size, adj_matrix


def write_graph_to_file(file_path, U_size, V_size, adj_matrix, matching, colors=None):
    """
    Запись результата в файл в формате, понятном Графоиду
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        # Записываем размеры долей
        f.write(f"{U_size} {V_size}\n")

        # Записываем матрицу смежности
        for row in adj_matrix:
            f.write(' '.join(map(str, row)) + '\n')

        # Записываем цвета вершин (если переданы)
        if colors:
            f.write("<Vertex_Colors>\n")
            for v, color in colors.items():
                f.write(f"{v} {color}\n")

        # Записываем информацию о паросочетании для вывода в текстовое окно
        f.write("<Text>\n")
        f.write("Наибольшее паросочетание:\n")
        for u in range(U_size):
            if matching[u] != -1:
                f.write(f"{u + 1} - {matching[u] + 1}\n")
        f.write(f"Размер паросочетания: {sum(1 for x in matching if x != -1)}\n")


def bfs(U_size, V_size, adj_matrix, pair_U, pair_V, dist):
    """
    Поиск в ширину для нахождения увеличивающей цепи
    """
    queue = deque()

    for u in range(U_size):
        if pair_U[u] == -1:
            dist[u] = 0
            queue.append(u)
        else:
            dist[u] = float('inf')

    dist_null = float('inf')

    while queue:
        u = queue.popleft()

        if dist[u] < dist_null:
            for v in range(V_size):
                if adj_matrix[u][v] and pair_V[v] == -1:
                    dist_null = dist[u] + 1
                elif adj_matrix[u][v] and dist[pair_V[v]] == float('inf'):
                    dist[pair_V[v]] = dist[u] + 1
                    queue.append(pair_V[v])

    return dist_null != float('inf')


def dfs(u, U_size, V_size, adj_matrix, pair_U, pair_V, dist):
    """
    Поиск в глубину для нахождения увеличивающей цепи
    """
    for v in range(V_size):
        if adj_matrix[u][v] and pair_V[v] == -1:
            pair_U[u] = v
            pair_V[v] = u
            return True
        elif adj_matrix[u][v] and dist[pair_V[v]] == dist[u] + 1:
            if dfs(pair_V[v], U_size, V_size, adj_matrix, pair_U, pair_V, dist):
                pair_U[u] = v
                pair_V[v] = u
                return True
    dist[u] = float('inf')
    return False


def find_max_matching(U_size, V_size, adj_matrix):
    """
    Алгоритм Хопкрофта-Карпа для нахождения наибольшего паросочетания
    """
    pair_U = [-1] * U_size  # Паросочетание для долей U
    pair_V = [-1] * V_size  # Паросочетание для долей V
    dist = [0] * U_size
    result = 0

    while bfs(U_size, V_size, adj_matrix, pair_U, pair_V, dist):
        for u in range(U_size):
            if pair_U[u] == -1:
                if dfs(u, U_size, V_size, adj_matrix, pair_U, pair_V, dist):
                    result += 1

    return pair_U, pair_V


def color_matched_vertices(U_size, V_size, pair_U, pair_V):
    """
    Раскрашивает вершины, входящие в паросочетание
    """
    colors = {}

    # Цвета: красный для вершин из паросочетания
    for u in range(U_size):
        if pair_U[u] != -1:
            colors[u] = "красный"

    for v in range(V_size):
        if pair_V[v] != -1:
            colors[v + U_size] = "красный"

    return colors


def main():
    if len(sys.argv) != 2:
        print("Usage: python max_matching.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "output_graph.txt"

    # Чтение входного графа
    U_size, V_size, adj_matrix = read_graph_from_file(input_file)

    # Нахождение наибольшего паросочетания
    pair_U, pair_V = find_max_matching(U_size, V_size, adj_matrix)

    # Раскраска вершин, входящих в паросочетание
    colors = color_matched_vertices(U_size, V_size, pair_U, pair_V)

    # Запись результата
    write_graph_to_file(output_file, U_size, V_size, adj_matrix, pair_U, colors)

    # Вывод информации в консоль Графоида
    print("<Text>")
    print("Наибольшее паросочетание найдено успешно!")
    print(f"Размер паросочетания: {sum(1 for x in pair_U if x != -1)}")
    print("Результат сохранен в файл output_graph.txt")


if __name__ == "__main__":
    main()