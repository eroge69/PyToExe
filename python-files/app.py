import webview
from flask import Flask, request, jsonify, render_template_string
from catboost import CatBoostClassifier
import numpy as np

app = Flask(__name__)

# Ваши данные и модели остаются без изменений
lab1_data = [
    "Исправное состояние электродвигателя",
    "Межвитковое короткое замыкание на обмотке электродвигателя",
    "Межфазное короткое замыкание на обмотке электродвигателя",
    "Обрыв фазы обмотки статора электродвигателя",
    "Несимметрия питания электродвигателя"
]

lab1_labels = [
    "Система исправна. Рекомендаций нет",
    "Установить значение сопротивления обмотки фазы В равное",
    "Размокнуть обмотки фаз А и В",
    "Установить в пункте «Параметры» значения тока в фазе А",
    "Проверить напряжение каждой фазы"
]

lab2_data = [
    "Падение напряжения на линии относительно поданного напряжения от 1% до 2%",
    "Падение напряжения на линии относительно поданного напряжения от 2% до 3%",
    "Падение напряжения на линии относительно поданного напряжения от 3% до 4%",
    "Падение напряжения на линии относительно поданного напряжения от 4% до 5%",
    "Падение напряжения на линии относительно поданного напряжения более 5%"
]

lab2_labels = [
    "Система исправна. Рекомендаций нет",
    "Изменить положение переключателя индуктивной нагрузки в положение 3",
    "Изменить положение переключателя модуля линии электропередач в положение 3",
    "Изменить положение переключателя индуктивной нагрузки в положение 4",
    "Изменить положение переключателя модуля линии электропередач в положение 2"
]

lab3_data = [
    "Система работает в режиме #1",
    "Система работает в режиме #2",
    "Система работает в режиме #3",
    "Система работает в режиме #4",
    "Система работает в режиме #5"
]

lab3_labels = [
    "Установить переключатель емкостной нагрузки в положение 2,переключатель индуктивной нагрузки в положение 3",
    "Установить переключатель емкостной нагрузки в положение 1,переключатель индуктивной нагрузки в положение 2",
    "Установить переключатель емкостной нагрузки в положение 5,переключатель индуктивной нагрузки в положение 1",
    "Система исправна. Рекомендаций нет",
    "Установить переключатель емкостной нагрузки в положение 1,переключатель индуктивной нагрузки в положение 3"
]

lab1_numbers = np.tile(np.array(list(range(1, len(lab1_data) + 1))), 10000)
lab2_numbers = np.tile(np.array(list(range(1, len(lab2_data) + 1))), 10000)
lab3_numbers = np.tile(np.array(list(range(1, len(lab3_data) + 1))), 10000)
lab1_labels_encoded = np.tile(np.array(list(range(0, len(lab1_data)))), 10000)
lab2_labels_encoded = np.tile(np.array(list(range(0, len(lab2_data)))), 10000)
lab3_labels_encoded = np.tile(np.array(list(range(0, len(lab3_data)))), 10000)

model_lab1 = CatBoostClassifier(iterations=100, depth=3, learning_rate=0.1, verbose=100)
model_lab2 = CatBoostClassifier(iterations=100, depth=3, learning_rate=0.1, verbose=100)
model_lab3 = CatBoostClassifier(iterations=100, depth=3, learning_rate=0.1, verbose=100)
model_lab1.fit(lab1_numbers, lab1_labels_encoded)
model_lab2.fit(lab2_numbers, lab2_labels_encoded)
model_lab3.fit(lab3_numbers, lab3_labels_encoded)

def get_recommendation(model, choice, labels):
    prediction = model.predict([choice])
    return labels[prediction[0]]

@app.route("/")
def index():
    # Встраиваем HTML-код непосредственно в Python-файл
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>МУЛЬТИАГЕННТНЫЕ СИСТЕМЫ</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 800px;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .lab {
            margin-bottom: 20px;
        }
        select {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            display: block;
            width: 100%;
            padding: 10px;
            font-size: 16px;
            background-color: black;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: grey;
        }
        .result {
            margin-top: 20px;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
            font-size: 16px;
        }
        .overall-result {
            margin-top: 20px;
            padding: 10px;
            background-color: #d4edda;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
        .overall-result.unsatisfactory {
            background-color: #f8d7da;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Лабы с ИИ</h1>
        <div class="lab">
            <label for="lab1">Лабораторная работа №1 «Диагностика электродвигателя»:</label>
            <select id="lab1">
                <option value="1">Исправное состояние электродвигателя</option>
                <option value="2">Межвитковое короткое замыкание на обмотке электродвигателя</option>
                <option value="3">Межфазное короткое замыкание на обмотке электродвигателя</option>
                <option value="4">Обрыв фазы обмотки статора электродвигателя</option>
                <option value="5">Несимметрия питания электродвигателя</option>
            </select>
        </div>
        <div class="lab">
            <label for="lab2">Лабораторная работа №2 «Минимизация потерь в линии электропередачи»:</label>
            <select id="lab2">
                <option value="1">Падение напряжения на линии относительно поданного напряжения от 1% до 2%</option>
                <option value="2">Падение напряжения на линии относительно поданного напряжения от 2% до 3%</option>
                <option value="3">Падение напряжения на линии относительно поданного напряжения от 3% до 4%</option>
                <option value="4">Падение напряжения на линии относительно поданного напряжения от 4% до 5%</option>
                <option value="5">Падение напряжения на линии относительно поданного напряжения более 5%</option>
            </select>
        </div>
        <div class="lab">
            <label for="lab3">Лабораторная работа №3 «Компенсация реактивной мощности»:</label>
            <select id="lab3">
                <option value="1">Система работает в режиме #1</option>
                <option value="2">Система работает в режиме #2</option>
                <option value="3">Система работает в режиме #3</option>
                <option value="4">Система работает в режиме #4</option>
                <option value="5">Система работает в режиме #5</option>
            </select>
        </div>
        <button onclick="getRecommendations()">Начать диагностику</button>
        <div class="result" id="result1"></div>
        <div class="result" id="result2"></div>
        <div class="result" id="result3"></div>
        <div class="overall-result" id="overallResult"></div>
    </div>

    <script>
        async function getRecommendations() {
            const lab1 = document.getElementById("lab1").value;
            const lab2 = document.getElementById("lab2").value;
            const lab3 = document.getElementById("lab3").value;

            const response = await fetch("/get_recommendations", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    lab1: parseInt(lab1),
                    lab2: parseInt(lab2),
                    lab3: parseInt(lab3)
                })
            });

            const data = await response.json();
            document.getElementById("result1").innerText = `Лабораторная работа 1: ${data.lab1}`;
            document.getElementById("result2").innerText = `Лабораторная работа 2: ${data.lab2}`;
            document.getElementById("result3").innerText = `Лабораторная работа 3: ${data.lab3}`;

            const overallResult = document.getElementById("overallResult");
            overallResult.innerText = `Общая оценка работы системы: ${data.overall_result}`;

            if (data.overall_result === "Неудовлетворительно") {
                overallResult.classList.add("unsatisfactory");
            }
            else if (data.overall_result === "Система неисправна") {
                overallResult.classList.add("unsatisfactory");
            }
            else {
                overallResult.classList.remove("unsatisfactory");
            }
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_content)

@app.route("/get_recommendations", methods=["POST"])
def get_recommendations():
    data = request.json
    choice1 = data["lab1"]
    choice2 = data["lab2"]
    choice3 = data["lab3"]

    result1 = get_recommendation(model_lab1, choice1, lab1_labels)
    result2 = get_recommendation(model_lab2, choice2, lab2_labels)
    result3 = get_recommendation(model_lab3, choice3, lab3_labels)

    name_no_rec = "Система исправна. Рекомендаций нет"

    no_recommendations_count = 0
    if result1 == name_no_rec:
        no_recommendations_count += 1
    if result2 == name_no_rec:
        no_recommendations_count += 1
    if result3 == name_no_rec:
        no_recommendations_count += 1

    if no_recommendations_count == 3:
        overall_result = "Все рекомендации выполнены"
    
    elif no_recommendations_count == 2:
        overall_result = "Удовлетворительно"

    elif no_recommendations_count == 1:
        overall_result = "Неудовлетворительно"

    else:
        overall_result = "Система неисправна"

    return jsonify({
        "lab1": result1,
        "lab2": result2,
        "lab3": result3,
        "overall_result": overall_result
    })

def run_flask():
    app.run(debug=False)

if __name__ == "__main__":
    import threading

    window = webview.create_window(
        "Лабы с ИИ",
        "http://127.0.0.1:5000",
        width=1200,
        height=800,
        resizable=True,
        text_select=True,
    )

    threading.Thread(target=run_flask, daemon=True).start()
    webview.start()