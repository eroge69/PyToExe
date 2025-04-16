from app_factory import create_app

# Создаем приложение с помощью фабрики
app = create_app()

# Если файл запускается напрямую, запускаем сервер
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)