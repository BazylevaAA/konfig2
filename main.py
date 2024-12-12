import requests
import os
import argparse
import xml.etree.ElementTree as ET
import zipfile
import toml


def download_file(url, save_path):
    if os.path.exists(save_path):
        print(f"Файл {save_path} уже существует. Пропуск скачивания.")
        return

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Файл успешно скачан и сохранен в: {save_path}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Ошибка при запросе: {err}")
    except Exception as err:
        print(f"Произошла ошибка: {err}")

def get_dependencies(package_name, package_version, depth=0, max_depth=1, all_dependencies=None, package_details=None):
    if all_dependencies is None:
        all_dependencies = {}
    if package_details is None:
        package_details = {}
    if depth > max_depth:
        return all_dependencies, package_details

    url = f"https://www.nuget.org/api/v2/package/{package_name}/{package_version}"
    save_directory = r"C:/Users/Anastasia/PycharmProjects/konfig2"
    save_file_path = os.path.join(save_directory, f"{package_name}.{package_version}.nupkg")
    download_file(url, save_file_path)

    nupkg_path = save_file_path
    if not os.path.exists(nupkg_path):
        print(f"{nupkg_path} не найден.")
        return all_dependencies, package_details

    try:
        with zipfile.ZipFile(nupkg_path, 'r') as zip_ref:
            nuspec_file = [f for f in zip_ref.namelist() if f.endswith('.nuspec')]
            if nuspec_file:
                with zip_ref.open(nuspec_file[0]) as file:
                    tree = ET.parse(file)
                    root = tree.getroot()
                    namespaces = {'ns': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}

                    # Получение версии и автора
                    metadata = root.find("ns:metadata", namespaces)
                    if metadata is not None:
                        version = metadata.find("ns:version", namespaces).text if metadata.find("ns:version", namespaces) is not None else "Unknown"
                        authors = metadata.find("ns:authors", namespaces).text if metadata.find("ns:authors", namespaces) is not None else "Unknown"
                    else:
                        version = "Unknown"
                        authors = "Unknown"

                    # Сохранение информации о пакете
                    package_details[f"{package_name}.{package_version}"] = {
                        "name": package_name,
                        "version": version,
                        "author": authors
                    }

                    # Парсинг зависимостей
                    dependencies_set = set()
                    for dependency in root.findall(".//ns:dependency", namespaces):
                        dep_id = dependency.get('id')
                        dep_version = dependency.get('version')
                        if dep_id and dep_version:
                            dep_package = f"{dep_id}.{dep_version}"
                            dependencies_set.add(dep_package)
                            if dep_package not in all_dependencies:
                                all_dependencies[dep_package] = set()
                                get_dependencies(dep_id, dep_version, depth + 1, max_depth, all_dependencies, package_details)
                    all_dependencies[f"{package_name}.{package_version}"] = dependencies_set
    except Exception as e:
        print(f"Ошибка при обработке {package_name}.{package_version}: {e}")

    return all_dependencies, package_details

def build_plantuml_graph(dependencies, package_details):
    graph = "@startuml\n"
    graph += "skinparam linetype ortho\n"

    for package_name_version, deps in dependencies.items():
        details = package_details.get(package_name_version, {})
        package_name = details.get("name", "Unknown")
        package_author = details.get("author", "Unknown")
        package_version = details.get("version", "Unknown")

        # Создание узла пакета
        graph += f"package \"{package_name} ({package_version})\" as {package_name_version} {{}}\n"

        # Добавление заметки с автором
        graph += f"note right of {package_name_version}\n"
        graph += f"Author: {package_author}\n"
        graph += f"Version: {package_version}\n"
        graph += "end note\n"

        # Добавление зависимостей
        for dep in deps:
            graph += f"{package_name_version} --> {dep}\n"

    graph += "@enduml"
    return graph

def save_graph(graph_content, output_path):
    with open(output_path, "w") as f:
        f.write(graph_content)
    print(f"Граф зависимостей сохранен в {output_path}")


def generate_image(plantuml_path, input_path, output_path):
    os.system(f"java -jar {plantuml_path} -tpng {input_path} -o .")
    print(f"Изображение графа сохранено в {output_path}")


def read_config(tool):
    with open(tool, "r", encoding="utf-8") as f:
        config = toml.load(f)
    return config

def print_dependencies(dependencies):
    print("Список зависимостей:")
    for package, deps in dependencies.items():
        print(f"{package}:")
        for dep in deps:
            print(f"  - {dep}")


def main():
    parser = argparse.ArgumentParser(description="Визуализация зависимостей .NET пакетов с использованием PlantUML.")
    parser.add_argument("tool", help="Путь к конфигурационному файлу TOML")
    args = parser.parse_args()
    config = read_config(args.tool)
    plantuml_path = config["visualization"]["plantuml_path"]
    output_graph_path = config["output"]["graph_path"]
    package_name = "Newtonsoft.Json.Bson"
    package_version = "1.0.3"
    print(f"Package name: {package_name}, Package version: {package_version}")

    all_dependencies, package_details = get_dependencies(package_name, package_version)
    print_dependencies(all_dependencies)

    plantuml_graph = build_plantuml_graph(all_dependencies, package_details)
    save_graph(plantuml_graph, output_graph_path)
    generate_image(plantuml_path, output_graph_path, output_graph_path.replace(".puml", ".png"))


if __name__ == "__main__":
    main()
