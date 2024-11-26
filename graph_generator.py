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
