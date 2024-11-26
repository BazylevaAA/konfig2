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