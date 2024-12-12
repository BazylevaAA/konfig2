import unittest
from unittest.mock import patch, mock_open
import os
import requests
import zipfile

from main import download_file, get_dependencies, generate_puml_graph


class TestDownloadFile(unittest.TestCase):

    @patch('requests.get')
    @patch('os.path.exists')
    def test_download_file_when_exists(self, mock_exists, mock_get):
        # Имитация того, что файл уже существует
        mock_exists.return_value = True
        url = "http://example.com/file.zip"
        save_path = "path/to/file.zip"

        result = download_file(url, save_path)

        # Проверяем, что файл не был скачан, так как он уже существует
        mock_get.assert_not_called()
        self.assertEqual(result, save_path)

    @patch('requests.get')
    @patch('os.path.exists')
    def test_download_file_when_not_exists(self, mock_exists, mock_get):
        # Имитация того, что файл не существует
        mock_exists.return_value = False
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"data"]
        url = "http://example.com/file.zip"
        save_path = "path/to/file.zip"

        # Имитация скачивания
        result = download_file(url, save_path)

        # Проверяем, что запрос был выполнен
        mock_get.assert_called_once_with(url, stream=True)
        self.assertEqual(result, save_path)

    @patch('requests.get')
    @patch('os.path.exists')
    def test_download_file_http_error(self, mock_exists, mock_get):
        # Имитация того, что файл не существует
        mock_exists.return_value = False
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        url = "http://example.com/file.zip"
        save_path = "path/to/file.zip"

        # Симулируем ошибку при скачивании
        result = download_file(url, save_path)

        # Проверяем, что был вызван HTTP запрос и ошибка была обработана
        mock_get.assert_called_once_with(url, stream=True)
        self.assertIsNone(result)


class TestGetDependencies(unittest.TestCase):

    @patch('zipfile.ZipFile')
    @patch('os.path.exists')
    @patch('requests.get')
    def test_get_dependencies(self, mock_get, mock_exists, mock_zip):
        # Имитация того, что файл существует
        mock_exists.return_value = True
        mock_response = mock_get.return_value
        mock_response.status_code = 200

        # Мокируем работу с Zip файлом и парсинг XML
        mock_zip_obj = mock_zip.return_value.__enter__.return_value
        mock_zip_obj.namelist.return_value = ['package.nuspec']

        # Содержимое .nuspec файла
        mock_nuspec_file = mock_open(
            read_data='<package><metadata><dependencies><dependency id="Newtonsoft.Json" version="12.0.0" /></dependencies></metadata></package>')
        mock_zip_obj.open.return_value = mock_nuspec_file()

        package_name = "Newtonsoft.Json.Bson"
        package_version = "1.0.3"
        result = get_dependencies(package_name, package_version)

        # Добавляем вывод результата для отладки
        print(f"Dependencies result: {result}")

        # Проверяем, что зависимости были корректно извлечены
        self.assertIn("Newtonsoft.Json.12.0.0", result.get(f"{package_name}.{package_version}", {}).get('dependencies', set()))

    @patch('zipfile.ZipFile')
    @patch('os.path.exists')
    @patch('requests.get')
    def test_get_dependencies_no_nuspec(self, mock_get, mock_exists, mock_zip):
        # Имитация того, что файл существует, но не содержит .nuspec
        mock_exists.return_value = True
        mock_response = mock_get.return_value
        mock_response.status_code = 200

        # Мокируем работу с Zip файлом, но не предоставляем .nuspec файл
        mock_zip_obj = mock_zip.return_value.__enter__.return_value
        mock_zip_obj.namelist.return_value = []

        package_name = "Newtonsoft.Json.Bson"
        package_version = "1.0.3"
        result = get_dependencies(package_name, package_version)

        # Проверяем, что пустые зависимости возвращены
        self.assertEqual(result.get(f"{package_name}.{package_version}", {}).get('dependencies', set()), set())


class TestGeneratePumlGraph(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    def test_generate_puml_graph(self, mock_file):
        # Мокируем данные зависимостей
        all_dependencies = {
            "Newtonsoft.Json.Bson.1.0.3": {
                'dependencies': {'Newtonsoft.Json.13.0.1'},
                'authors': {'James Newton-King'}
            },
            "Newtonsoft.Json.13.0.1": {
                'dependencies': set(),
                'authors': {'James Newton-King'}
            }
        }

        puml_path = "graph_dependencies.puml"

        # Вызываем функцию
        generate_puml_graph(all_dependencies, puml_path)

        # Проверяем, что файл был открыт для записи
        mock_file.assert_called_with(puml_path, 'w')

        # Получаем текст, который был записан в файл
        handle = mock_file()
        written_content = handle.write.call_args_list[0][0][0]

        # Добавляем вывод содержимого для отладки
        print(f"Written content: {written_content}")

        # Проверяем, что в содержимом есть нужные зависимости и авторы
        self.assertIn("package \"Newtonsoft.Json.Bson\"", written_content)
        self.assertIn("Newtonsoft.Json.Bson --> Newtonsoft.Json", written_content)
        self.assertIn("Newtonsoft.Json.Bson : James Newton-King", written_content)


if __name__ == '__main__':
    unittest.main()
