import unittest
from graph_generator import generate_complex_plantuml_script

class TestGenerateComplexPlantUMLScript(unittest.TestCase):
    def test_valid_dependencies(self):
        package_name = "TestPackage"
        dependencies = ["Dependency1 [1.0.0,2.0.0)", "Dependency2 [3.0.0]"]
        expected_script = (
            "@startuml\n"
            "package TestPackage {\n"
            "    Dependency1 : [1.0.0,2.0.0)\n"
            "    Dependency2 : [3.0.0]\n"
            "}\n"
            "@enduml"
        )
        result = generate_complex_plantuml_script(package_name, dependencies)
        self.assertEqual(result.strip(), expected_script.strip())

    def test_invalid_dependencies(self):
        package_name = "TestPackage"
        dependencies = ["InvalidDependencyFormat", "Dependency3"]
        expected_script = (
            "@startuml\n"
            "package TestPackage {\n"
            "}\n"
            "@enduml"
        )
        result = generate_complex_plantuml_script(package_name, dependencies)
        self.assertEqual(result.strip(), expected_script.strip())

if __name__ == "__main__":
    unittest.main()
