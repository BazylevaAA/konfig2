import os
import subprocess
import toml
from graph_generator import get_package_dependencies, generate_complex_plantuml_script, save_plantuml_script


def load_config(config_path):
    """Загружает конфигурационный файл TOML."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Файл конфигурации {config_path} не найден.")

    try:
        with open(config_path, "r") as file:
            config = toml.load(file)

        # Проверка наличия необходимых параметров в конфигурации
        required_keys = ["visualizer_path", "package_name", "output_path"]
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise RuntimeError(f"Отсутствуют обязательные параметры в конфигурации: {', '.join(missing_keys)}")

        return config
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки конфигурации: {e}")


def generate_graph(plantuml_path, script_path, output_image_path):
    """Генерирует граф на основе PlantUML-скрипта."""
    try:
        command = [
            "java", "-jar", plantuml_path,
            "-tpng", script_path,
            "-o", os.path.dirname(output_image_path)
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        if result.returncode != 0:
            raise RuntimeError("Ошибка генерации PNG-файла.")
    except Exception as e:
        raise RuntimeError(f"Ошибка при генерации графа: {e}")


def main():
    """Главная функция."""
    config_path = "config.toml"
    try:
        config = load_config(config_path)
    except RuntimeError as e:
        print(e)
        return

    plantuml_path = config.get("visualizer_path")
    package_name = config.get("package_name")
    output_image_path = config.get("output_path")

    if not all([plantuml_path, package_name, output_image_path]):
        print("Некорректный формат конфигурационного файла.")
        return

    # Проверка существования plantuml_path
    if not os.path.exists(plantuml_path):
        print(f"Ошибка: файл {plantuml_path} не найден.")
        return

    print("Получение зависимостей пакета...")
    dependencies = get_package_dependencies(package_name)
    if dependencies is None:
        print("Не удалось получить зависимости.")
        return

    print("Генерация графа зависимостей...")
    plantuml_script = generate_complex_plantuml_script(package_name, dependencies)

    script_path = "generate_img.puml"  # Можно сделать путь динамическим
    try:
        save_plantuml_script(plantuml_script, script_path)
    except RuntimeError as e:
        print(f"Ошибка сохранения скрипта PlantUML: {e}")
        return

    print("Визуализация графа...")
    try:
        generate_graph(plantuml_path, script_path, output_image_path)
    except RuntimeError as e:
        print(f"Ошибка при генерации графа: {e}")
        return

    print("Граф зависимостей успешно сгенерирован!")


if __name__ == "__main__":
    main()
