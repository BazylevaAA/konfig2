import requests


def get_package_dependencies(package_name):
    """Запрашивает зависимости для указанного пакета из NuGet API."""
    url = f"https://api.nuget.org/v3/registration5-gz-semver2/{package_name.lower()}/index.json"

    try:
        # Отправляем запрос к NuGet API
        response = requests.get(url)
        response.raise_for_status()

        # Парсим JSON ответ
        data = response.json()

        # Печатаем полученные данные для отладки
        print(f"Ответ от NuGet API: {data}")

        versions = data['items'][0]['items']  # Получаем доступ к версиям пакета

        # Извлекаем зависимости из данных о версии
        dependencies = {}
        for version_data in versions:
            version = version_data['catalogEntry']['version']

            # Проверка, есть ли зависимости у данной версии
            version_dependencies = version_data['catalogEntry'].get('dependencyGroups', [])

            # Если зависимости найдены, извлекаем их
            dependencies_list = []
            for group in version_dependencies:
                for dep in group.get('dependencies', []):
                    dep_name = dep['id']
                    dep_version = dep['range']
                    dependencies_list.append(f"{dep_name} {dep_version}")

            print(f"Зависимости для версии {version}: {dependencies_list}")
            dependencies[version] = dependencies_list

        return dependencies

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к NuGet API: {e}")
        return None


def generate_complex_plantuml_script(package_name, dependencies):
    plantuml_script = f"@startuml\npackage {package_name} {{\n"

    for dep in dependencies:
        parts = dep.split(" ")

        # If there's only one part (version number), skip it or handle differently
        if len(parts) == 1:
            print(f"Warning: Skipping dependency with no name: {dep}")
            continue
        elif len(parts) == 2:
            dep_name, dep_version = parts
            plantuml_script += f"    {dep_name} : {dep_version}\n"
        else:
            print(f"Warning: Skipping invalid dependency format: {dep}")
            continue

    plantuml_script += "}\n@enduml"
    return plantuml_script


def save_plantuml_script(script, script_path):
    """Сохраняет скрипт PlantUML в файл."""
    try:
        with open(script_path, "w") as file:
            file.write(script)
    except Exception as e:
        raise RuntimeError(f"Ошибка сохранения PlantUML-скрипта: {e}")


