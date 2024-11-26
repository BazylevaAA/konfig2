import os
import subprocess
import toml


def load_config(config_path):
    """Загружает конфигурационный файл TOML."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Файл конфигурации {config_path} не найден.")

    try:
        with open(config_path, "r") as file:
            config = toml.load(file)
        return config
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки конфигурации: {e}")


def generate_complex_plantuml_script(package_name, num_levels=3, max_dependencies_per_level=2):
    """Генерация сложной структуры зависимостей с транзитивными связями."""
    plantuml_script = "@startuml\n"
    plantuml_script += f"package {package_name} {{\n"

    # Начальная точка - корневой пакет
    dependencies = [f"{package_name}_Dependency0"]
    plantuml_script += f'"{package_name}" --> "{dependencies[0]}"\n'

    # Генерация зависимостей по уровням
    for level in range(1, num_levels + 1):
        new_dependencies = []
        for dependency in dependencies:
            for i in range(1, max_dependencies_per_level + 1):
                sub_dependency = f"{dependency}_Sub{i}"
                plantuml_script += f'"{dependency}" --> "{sub_dependency}"\n'
                new_dependencies.append(sub_dependency)
        dependencies = new_dependencies

    plantuml_script += "}\n@enduml"
    return plantuml_script


def save_plantuml_script(script, script_path):
    """Сохраняет скрипт PlantUML в файл."""
    try:
        with open(script_path, "w") as file:
            file.write(script)
    except Exception as e:
        raise RuntimeError(f"Ошибка сохранения PlantUML-скрипта: {e}")


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
    config = load_config(config_path)

    plantuml_path = config.get("visualizer_path")
    package_name = config.get("package_name")
    output_image_path = config.get("output_path")

    if not all([plantuml_path, package_name, output_image_path]):
        raise RuntimeError("Некорректный формат конфигурационного файла.")

    script_path = "generate_img.puml"

    print("Генерация графа зависимостей...")
    plantuml_script = generate_complex_plantuml_script(
        package_name, num_levels=3, max_dependencies_per_level=2
    )
    save_plantuml_script(plantuml_script, script_path)

    print(f"Путь к PlantUML: {plantuml_path}")
    print(f"Путь к скрипту: {script_path}")
    print(f"Путь к изображению: {output_image_path}")

    generate_graph(plantuml_path, script_path, output_image_path)
    print("Граф зависимостей успешно сгенерирован!")


if __name__ == "__main__":
    main()
