import math

MaxX = 6
MaxY = 5

def get_default_data():
    arr = [[0.0 for _ in range(MaxY)] for _ in range(MaxX)]
    # Заполнение матрицы вручную
    values = [
        [6, 9, -2, -8, -8, 144],
        [14, 11, 4, 7, 3, -32],
        [8, 10, 2, 4, -1, -59],
        [8, -4, 6, -5, -3, -10],
        [-1, -6, -7, 7, 7, 14]
    ]
    for j in range(MaxY):
        for i in range(MaxX - 1):
            arr[i][j] = values[j][i]
        arr[MaxX - 1][j] = values[j][MaxX - 1]
    return arr

def display_array(arr):
    for j in range(MaxY):
        if j == 0:
            print("/", end="")
        elif j == MaxY - 1:
            print("\\", end="")
        else:
            print("|", end="")
        for i in range(MaxX):
            val = arr[i][j]
            if i != MaxX - 1:
                print(f" {val:6.2f}*x{j+1}", end="")
            else:
                print(f" = {val:6.2f}", end="")
        print()
    print()

def display_result(arr):
    print("Результат:")
    for j in range(MaxY):
        val = arr[MaxX - 1][j]
        print(f"x{j + 1} = {val:5.2f}")

def calc_one_step(arr, raz_elem_index):
    iteration_number = raz_elem_index + 1
    column_number = raz_elem_index + 1
    print(f"Итерация {iteration_number}:")
    print(f"Выберем максимальный по модулю элемент в {column_number} столбце.")

    max_value_row_index = raz_elem_index
    max_value = 0
    max_value_abs = -math.inf

    for j in range(MaxY):
        val = arr[raz_elem_index][j]
        abs_val = abs(val)
        if abs_val > max_value_abs:
            max_value_abs = abs_val
            max_value = val
            max_value_row_index = j

    max_value_row_number = max_value_row_index + 1
    print(f"Он находится в {max_value_row_number} строке (это элемент {max_value:.2f}).")
    print(f"Поменяем местами строки {iteration_number} и {max_value_row_number}.")

    for i in range(MaxX):
        arr[i][raz_elem_index], arr[i][max_value_row_index] = arr[i][max_value_row_index], arr[i][raz_elem_index]

    display_array(arr)

    print(f"Разделим {iteration_number} строку на диагональный элемент a{iteration_number}{iteration_number} ({arr[raz_elem_index][raz_elem_index]:.2f}).")
    print(f"Все элементы {column_number} столбца, кроме a{iteration_number}{iteration_number}, равны 0.")
    print("Для остальных элементов матрицы построим прямоугольники с вершинами в этих элементах и в выделенном элементе.")

    raz_elem = arr[raz_elem_index][raz_elem_index]
    for i in range(MaxX):
        arr[i][raz_elem_index] /= raz_elem

    for j in range(MaxY):
        if j == raz_elem_index:
            continue
        val_in_column = arr[raz_elem_index][j]
        for i in range(MaxX):
            arr[i][j] -= arr[i][raz_elem_index] * val_in_column

    display_array(arr)

def main():
    arr = get_default_data()
    print("Исходная система уравнений:")
    display_array(arr)

    for i in range(5):
        calc_one_step(arr, i)

    display_result(arr)
    input("Нажмите любую клавишу для выхода...")

if __name__ == "__main__":
    main()
