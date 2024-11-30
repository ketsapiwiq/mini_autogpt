import unittest
from think.prompt import commands as static_commands
from action.commands.registry import CommandRegistry
from action.commands import setup

class TestPromptCommands(unittest.TestCase):
    def setUp(self):
        # Initialize the command registry
        setup.setup_commands()

    def test_all_commands_included(self):
        """Test that all possible commands are included in the prompt."""
        # Get commands from both sources
        static_command_names = {cmd['name'] for cmd in static_commands if cmd['enabled']}
        registry_commands = {cmd['name'] for cmd in CommandRegistry.get_available_commands()}

        # Print all commands for debugging
        print("\nStatic commands in prompt.py:")
        for cmd in static_commands:
            print(f"- {cmd['name']} (enabled: {cmd['enabled']})")

        print("\nRegistered commands in registry:")
        for cmd in CommandRegistry.get_available_commands():
            print(f"- {cmd['name']}")

        # Check for commands in registry but not in static commands
        missing_in_static = registry_commands - static_command_names
        if missing_in_static:
            print("\nCommands in registry but missing from prompt.py:")
            for cmd in missing_in_static:
                print(f"- {cmd}")

        # Check for commands in static but not in registry
        extra_in_static = static_command_names - registry_commands
        if extra_in_static:
            print("\nCommands in prompt.py but missing from registry:")
            for cmd in extra_in_static:
                print(f"- {cmd}")

        # Assert all registry commands are included in static commands
        self.assertEqual(missing_in_static, set(), 
            "Some commands from the registry are missing in prompt.py static commands")
        
        # Assert all static commands exist in registry
        self.assertEqual(extra_in_static, set(),
            "Some static commands in prompt.py don't exist in the registry")

if __name__ == '__main__':
    unittest.main()
