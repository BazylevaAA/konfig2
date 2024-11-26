import unittest
from unittest.mock import patch, MagicMock
import os
import subprocess
from main import load_config, generate_complex_plantuml_script, save_plantuml_script, generate_graph


class TestDependencyVisualizer(unittest.TestCase):

    @patch("main.os.path.exists")
    def test_load_config_valid(self, mock_exists):
        # Мокаем os.path.exists, чтобы он всегда возвращал True (т.е. файл существует)
        mock_exists.return_value = True
        config = load_config("config.toml")
        self.assertIsInstance(config, dict)
        self.assertIn("visualizer_path", config)
        self.assertIn("package_name", config)
        self.assertIn("output_path", config)

        @patch("main.os.path.exists")
        def test_load_config_file_not_found(self, mock_exists):
            mock_exists.return_value = False
            with self.assertRaises(FileNotFoundError):
                load_config("nonexistent_config.toml")

    def test_generate_complex_plantuml_script(self):
        script = generate_complex_plantuml_script("SamplePackage", num_levels=2, max_dependencies_per_level=2)
        self.assertIn('package SamplePackage {', script)
        self.assertIn('"SamplePackage" --> "SamplePackage_Dependency0"', script)
        self.assertIn('"SamplePackage_Dependency0" --> "SamplePackage_Dependency0_Sub1"', script)
        self.assertIn('"SamplePackage_Dependency0_Sub1" --> "SamplePackage_Dependency0_Sub2"', script)

    @patch("main.open", new_callable=MagicMock)
    def test_save_plantuml_script(self, mock_open):
        script = "@startuml\npackage SamplePackage { ... }\n@enduml"
        save_plantuml_script(script, "generate_img.puml")
        mock_open.assert_called_once_with("generate_img.puml", "w")
        handle = mock_open()
        handle.write.assert_called_once_with(script)

