import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import subprocess

from main import load_config, generate_complex_plantuml_script, save_plantuml_script, generate_graph

class TestDependencyVisualizer(unittest.TestCase):

    # Тест для функции load_config
    @patch("main.os.path.exists")
    def test_load_config_valid(self, mock_exists):
        # Мокаем os.path.exists, чтобы он всегда возвращал True (файл существует)
        mock_exists.return_value = True
        config = load_config("config.toml")
        self.assertIsInstance(config, dict)
        self.assertIn("visualizer_path", config)
        self.assertIn("package_name", config)
        self.assertIn("output_path", config)

    @patch("main.os.path.exists")
    def test_load_config_file_not_found(self, mock_exists):
        # Мокаем os.path.exists, чтобы он возвращал False (файл не существует)
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            load_config("nonexistent_config.toml")

    # Тест для генерации скрипта PlantUML
    def test_generate_complex_plantuml_script(self):
        script = generate_complex_plantuml_script("SamplePackage", num_levels=3, max_dependencies_per_level=2)
        self.assertIn('"SamplePackage_Dependency0" --> "SamplePackage_Dependency0_Sub1"', script)
        self.assertIn('"SamplePackage_Dependency0" --> "SamplePackage_Dependency0_Sub2"', script)

    # Тест для сохранения скрипта PlantUML в файл
    @patch("builtins.open", new_callable=mock_open)
    def test_save_plantuml_script(self, mock_open):
        script = "@startuml\npackage SamplePackage { ... }\n@enduml"
        script_path = "generate_img.puml"

        # Вызов метода save_plantuml_script
        save_plantuml_script(script, script_path)

        # Проверяем, что open был вызван с нужным путем и режимом
        mock_open.assert_called_once_with(script_path, "w")

        # Проверяем, что метод write был вызван с правильными параметрами
        mock_open().write.assert_called_once_with(script)

    # Тест для генерации графа с использованием subprocess
    @patch("subprocess.run")
    def test_generate_graph(self, mock_subprocess):
        mock_subprocess.return_value = MagicMock(returncode=0)
        plantuml_path = "C://Users//Anastasia//Downloads//plantuml-1.2024.8.jar"
        script_path = "generate_img.puml"
        output_image_path = "graph_dependencies.png"

        generate_graph(plantuml_path, script_path, output_image_path)
        mock_subprocess.assert_called_once_with([
            "java", "-jar", plantuml_path,
            "-tpng", script_path,
            "-o", os.path.dirname(output_image_path)
        ], capture_output=True, text=True, check=True)

    # Тест для генерации графа с ошибкой
    @patch("subprocess.run")
    def test_generate_graph_with_error(self, mock_subprocess):
        # Симулируем ошибку при генерации графа
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "java -jar")

        with self.assertRaises(RuntimeError):
            generate_graph("C://Users//Anastasia//Downloads//plantuml-1.2024.8.jar", "generate_img.puml",
                           "graph_dependencies.png")

if __name__ == "__main__":
    unittest.main()
