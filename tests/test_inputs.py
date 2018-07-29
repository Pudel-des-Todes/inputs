"""Tests for inputs module."""
# pylint: disable=protected-access,no-self-use
from unittest import TestCase, main

try:
    # Python 3
    from unittest import mock
except ImportError:
    # Python 2
    import mock
    PYTHON = 2
    from pathlib2 import PurePath
else:
    PYTHON = 3
    from pathlib import PurePath

import inputs

RAW = ""


class InputEventTestCase(TestCase):
    """Test the InputEvent class."""
    def test_input_event_init(self):
        """Test that the input event sets the required properties."""
        event = inputs.InputEvent(
            "Some Device",
            {'ev_type': 'Key',
             'state': 0,
             'timestamp': 1530900876.367757,
             'code': 'KEY_ENTER'})
        self.assertEqual(event.device, 'Some Device')
        self.assertEqual(event.ev_type, 'Key')
        self.assertEqual(event.state, 0)
        self.assertEqual(event.timestamp, 1530900876.367757)
        self.assertEqual(event.code, 'KEY_ENTER')


KEYBOARD_PATH = "/dev/input/by-path/my-lovely-keyboard-0-event-kbd"
MOUSE_PATH = "/dev/input/by-path/my-lovely-mouse-0-event-mouse"
GAMEPAD_PATH = "/dev/input/by-path/my-lovely-gamepad-0-event-joystick"
OTHER_PATH = "/dev/input/by-path/the-machine-that-goes-ping-other"


class DeviceManagePostrInitTestCase(TestCase):
    """Test the device manager class' post-init method."""

    @mock.patch.object(inputs.DeviceManager, '_find_devices')
    @mock.patch.object(inputs.DeviceManager, '_find_devices_mac')
    @mock.patch.object(inputs.DeviceManager, '_find_devices_win')
    @mock.patch.object(inputs.DeviceManager, '_update_all_devices')
    def test_post_init_linux(
            self,
            mock_update_all_devices,
            mock_find_devices_win,
            mock_find_devices_mac,
            mock_find_devices):
        """On Linux, find_devices is called and the other methods are not."""
        inputs.WIN = False
        inputs.MAC = False
        # pylint: disable=unused-variable
        device_manger = inputs.DeviceManager()
        mock_update_all_devices.assert_called()
        mock_find_devices.assert_called()
        mock_find_devices_mac.assert_not_called()
        mock_find_devices_win.assert_not_called()

    @mock.patch.object(inputs.DeviceManager, '_find_devices')
    @mock.patch.object(inputs.DeviceManager, '_find_devices_mac')
    @mock.patch.object(inputs.DeviceManager, '_find_devices_win')
    @mock.patch.object(inputs.DeviceManager, '_update_all_devices')
    def test_post_init_mac(self,
                           mock_update_all_devices,
                           mock_find_devices_win,
                           mock_find_devices_mac,
                           mock_find_devices):
        """On Mac, find_devices_mac is called and other methods are not."""
        inputs.WIN = False
        inputs.MAC = True
        inputs.DeviceManager()
        mock_update_all_devices.assert_called()
        mock_find_devices_mac.assert_called()
        mock_find_devices.assert_not_called()
        mock_find_devices_win.assert_not_called()

    @mock.patch.object(inputs.DeviceManager, '_find_devices')
    @mock.patch.object(inputs.DeviceManager, '_find_devices_mac')
    @mock.patch.object(inputs.DeviceManager, '_find_devices_win')
    @mock.patch.object(inputs.DeviceManager, '_update_all_devices')
    def test_post_init_win(self,
                           mock_update_all_devices,
                           mock_find_devices_win,
                           mock_find_devices_mac,
                           mock_find_devices):
        """On Windows, find_devices_win is called and other methods are not."""
        inputs.WIN = True
        inputs.MAC = False
        inputs.DeviceManager()
        mock_update_all_devices.assert_called()
        mock_find_devices_win.assert_called()
        mock_find_devices.assert_not_called()
        mock_find_devices_mac.assert_not_called()

    def tearDown(self):
        inputs.WIN = False
        inputs.MAC = False


MOCK_DEVICE = 'My Special Mock Input Device'
MOCK_DEVICE_PATH = '/dev/input/by-id/usb-mock-special-keyboard-event-kbd'


class DeviceManagerTestCase(TestCase):
    """Test the device manager class."""
    # pylint: disable=arguments-differ

    # There can never be too many tests.
    # pylint: disable=too-many-public-methods

    @mock.patch.object(inputs.DeviceManager, '_post_init')
    def setUp(self, mock_method):
        self.device_manger = inputs.DeviceManager()
        self.mock_method = mock_method

    def test_init(self):
        """Test the device manager's __init__ method."""
        self.mock_method.assert_called_with()
        self.assertEqual(self.device_manger.codes['types'][1], 'Key')
        self.assertEqual(self.device_manger.codes['Key'][1], 'KEY_ESC')
        self.assertEqual(self.device_manger.codes['xpad']['right_trigger'], 5)

    def test_update_all_devices(self):
        """Updates all_devices list."""
        # Begins empty
        self.assertEqual(self.device_manger.all_devices, [])

        # Add devices to the lists
        self.device_manger.keyboards = [1, 2, 3]
        self.device_manger.mice = [4, 6, 7]
        self.device_manger.gamepads = [8, 9, 10]
        self.device_manger.other_devices = [11, 12, 13]

        # Collate the list
        self.device_manger._update_all_devices()

        # Check the result
        self.assertEqual(
            self.device_manger.all_devices,
            [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13])

        # Reset the lists
        self.device_manger.keyboards = []
        self.device_manger.mice = []
        self.device_manger.gamepads = []
        self.device_manger.other_devices = []

        # Ends empty
        self.device_manger._update_all_devices()
        self.assertEqual(self.device_manger.all_devices, [])

    @mock.patch('os.path.realpath')
    @mock.patch('inputs.Keyboard')
    def test_parse_device_path_keyboard(
            self,
            mock_keyboard,
            mock_realpath):
        """Parses the path and adds a keyboard object."""
        mock_realpath.side_effect = lambda path: path
        self.device_manger._parse_device_path(KEYBOARD_PATH)
        mock_keyboard.assert_called_with(
            mock.ANY,
            KEYBOARD_PATH,
            None)
        mock_realpath.assert_called_with(KEYBOARD_PATH)
        self.assertEqual(len(self.device_manger.keyboards), 1)
        self.assertEqual(len(self.device_manger._raw), 1)
        self.assertEqual(self.device_manger._raw[0], KEYBOARD_PATH)

    @mock.patch('os.path.realpath')
    @mock.patch('inputs.Keyboard')
    def test_parse_device_path_repeated(
            self,
            mock_keyboard,
            mock_realpath):
        """Must only add a deviceprotected-access once for each path."""
        self.assertEqual(len(self.device_manger.keyboards), 0)
        mock_realpath.side_effect = lambda path: path
        self.device_manger._parse_device_path(KEYBOARD_PATH)
        mock_keyboard.assert_called_with(
            mock.ANY,
            KEYBOARD_PATH,
            None)
        mock_realpath.assert_called_with(KEYBOARD_PATH)
        self.assertEqual(len(self.device_manger.keyboards), 1)
        self.device_manger._parse_device_path(KEYBOARD_PATH)
        self.assertEqual(len(self.device_manger.keyboards), 1)

    @mock.patch('os.path.realpath')
    @mock.patch('inputs.Mouse')
    def test_parse_device_path_mouse(
            self,
            mock_mouse,
            mock_realpath):
        """Parses the path and adds a mouse object."""
        mock_realpath.side_effect = lambda path: path
        self.device_manger._parse_device_path(MOUSE_PATH)
        mock_mouse.assert_called_with(
            mock.ANY,
            MOUSE_PATH,
            None)
        mock_realpath.assert_called_with(MOUSE_PATH)
        self.assertEqual(len(self.device_manger.mice), 1)
        self.assertEqual(len(self.device_manger._raw), 1)
        self.assertEqual(self.device_manger._raw[0], MOUSE_PATH)

    @mock.patch('os.path.realpath')
    @mock.patch('inputs.GamePad')
    def test_parse_device_path_gamepad(
            self,
            mock_gamepad,
            mock_realpath):
        """Parses the path and adds a gamepad object."""
        mock_realpath.side_effect = lambda path: path
        self.device_manger._parse_device_path(GAMEPAD_PATH)
        mock_gamepad.assert_called_with(
            mock.ANY,
            GAMEPAD_PATH,
            None)
        mock_realpath.assert_called_with(GAMEPAD_PATH)
        self.assertEqual(len(self.device_manger.gamepads), 1)
        self.assertEqual(len(self.device_manger._raw), 1)
        self.assertEqual(self.device_manger._raw[0], GAMEPAD_PATH)

    @mock.patch('os.path.realpath')
    @mock.patch('inputs.OtherDevice')
    def test_parse_device_path_other(
            self,
            mock_other,
            mock_realpath):
        """Parses the path and adds an other object."""
        mock_realpath.side_effect = lambda path: path
        self.device_manger._parse_device_path(OTHER_PATH)
        mock_other.assert_called_with(
            mock.ANY,
            OTHER_PATH,
            None)
        mock_realpath.assert_called_with(OTHER_PATH)
        self.assertEqual(len(self.device_manger.other_devices), 1)
        self.assertEqual(len(self.device_manger._raw), 1)
        self.assertEqual(self.device_manger._raw[0], OTHER_PATH)

    def test_parse_invalid_path(self):
        """Raise warning for invalid path."""
        if PYTHON == 3:
            # Disable pylint on Python 2 moaning about assertWarns
            # pylint: disable=no-member
            with self.assertWarns(RuntimeWarning):
                result = self.device_manger._parse_device_path("Bob")

        else:
            result = self.device_manger._parse_device_path("Jim")

        self.assertIsNone(result)

    def test_get_event_type(self):
        """Tests the get_event_type method."""
        self.assertEqual(self.device_manger.get_event_type(0x00), "Sync")
        self.assertEqual(self.device_manger.get_event_type(0x01), "Key")
        self.assertEqual(self.device_manger.get_event_type(0x02), "Relative")
        self.assertEqual(self.device_manger.get_event_type(0x03), "Absolute")

    def test_get_invalid_event_type(self):
        """get_event_type raises exception for an invalid event type."""
        with self.assertRaises(inputs.UnknownEventType):
            self.device_manger.get_event_type(0x64)

    def test_get_event_string(self):
        """get_event_string returns an event string."""
        self.assertEqual(
            self.device_manger.get_event_string('Key', 0x133),
            "BTN_NORTH")
        self.assertEqual(
            self.device_manger.get_event_string('Relative', 0x08),
            "REL_WHEEL")
        self.assertEqual(
            self.device_manger.get_event_string('Absolute', 0x07),
            "ABS_RUDDER")
        self.assertEqual(
            self.device_manger.get_event_string('Switch', 0x05),
            "SW_DOCK")
        self.assertEqual(
            self.device_manger.get_event_string('Misc', 0x04),
            "MSC_SCAN")
        self.assertEqual(
            self.device_manger.get_event_string('LED', 0x01),
            "LED_CAPSL")
        self.assertEqual(
            self.device_manger.get_event_string('Repeat', 0x01),
            "REP_MAX")
        self.assertEqual(
            self.device_manger.get_event_string('Sound', 0x01),
            "SND_BELL")

    def test_get_event_string_on_win(self):
        """get_event_string returns an event string on Windows."""
        inputs.WIN = True
        self.assertEqual(
            self.device_manger.get_event_string('Key', 0x133),
            "BTN_NORTH")
        inputs.WIN = False

    def test_invalid_event_string(self):
        """get_event_string raises an exception for an unknown event code."""
        with self.assertRaises(inputs.UnknownEventCode):
            self.device_manger.get_event_string('Key', 0x999)

    @mock.patch.object(inputs.DeviceManager, '_find_special')
    @mock.patch.object(inputs.DeviceManager, '_find_by')
    def test_find_devices(self, mock_find_by, mock_find_special):
        """It should find by path, id and specials."""
        self.device_manger._find_devices()
        mock_find_by.assert_called_with('path')
        mock_find_by.assert_any_call('id')
        mock_find_special.assert_called_once()

    def test_iter(self):
        """Iter method iterates."""
        self.device_manger.all_devices = [0, 1, 2, 3, 4]
        for index, device in enumerate(self.device_manger):
            self.assertEqual(device, index)

    def test_getitem_index_error(self):
        """Raise index error for invalid index."""
        with self.assertRaises(IndexError):
            # pylint: disable=pointless-statement
            self.device_manger[0]

    def test_getitem(self):
        """It gets the correct item."""
        self.device_manger.all_devices = [0, 1, 2, 3, 4]
        for device in (0, 1, 2, 3, 4):
            self.assertEqual(self.device_manger[device], device)

    @mock.patch.object(inputs.DeviceManager, '_parse_device_path')
    @mock.patch('inputs.open', mock.mock_open(read_data=MOCK_DEVICE))
    @mock.patch('glob.glob')
    def test_find_special(self, mock_glob, mock_parse_device_path):
        """Find a special device."""
        mock_glob.return_value = [
            '/sys/class/input/event1',
            '/sys/class/input/event2',
            '/sys/class/input/event3',
        ]
        self.device_manger.codes['specials'][MOCK_DEVICE] = MOCK_DEVICE_PATH
        self.device_manger._find_special()
        # There should have been 3 calls to _parse_device_path
        self.assertEqual(mock_parse_device_path.call_count, 3)

        # Inpect each call
        for index, call in enumerate(mock_parse_device_path.call_args_list):
            # The first argument of each call should be MOCK_DEVICE_PATH
            self.assertEqual(call[0][0], MOCK_DEVICE_PATH)

            # The second argument of each call should be the target device path
            # E.g. /dev/input/event1 etc
            target_path = '/dev/input/event%d' % (index + 1)

            # The following line coverts backslashes when running tests on Win
            device_path = PurePath(call[0][1]).as_posix()

            self.assertEqual(device_path, target_path)

    @mock.patch.object(inputs.DeviceManager, '_parse_device_path')
    @mock.patch.object(inputs.DeviceManager, '_get_char_names')
    @mock.patch('inputs.open', mock.mock_open(read_data=MOCK_DEVICE))
    @mock.patch('glob.glob')
    def test_find_special_repeated(self,
                                   mock_glob,
                                   mock_get_char_names,
                                   mock_parse_device_path):
        """Find a special device but then it is already known."""
        mock_glob.return_value = [
            '/sys/class/input/event1',
            '/sys/class/input/event2']
        mock_get_char_names.return_value = ['event1', 'event2']
        self.device_manger.codes['specials'][MOCK_DEVICE] = MOCK_DEVICE_PATH
        self.device_manger._find_special()
        mock_parse_device_path.assert_not_called()

    @mock.patch('glob.glob')
    @mock.patch.object(inputs.DeviceManager, '_parse_device_path')
    def test_find_by(self,
                     mock_parse_device_path,
                     mock_glob):
        """It finds the correct paths."""
        mock_devices = [
            '/dev/input/by-path/platform-a-shiny-keyboard-event-kbd',
            '/dev/input/by-path/pci-a-shiny-mouse-event-mouse']
        mock_glob.return_value = mock_devices
        self.device_manger._find_by('path')
        mock_parse_device_path.assert_any_call(mock_devices[0])
        mock_parse_device_path.assert_any_call(mock_devices[1])


class DeviceManagerPlatformTestCase(TestCase):
    """Test the device manager class, methods that are platform specific."""
    # pylint: disable=arguments-differ

    # There can never be too many tests.
    # pylint: disable=too-many-public-methods

    @mock.patch.object(inputs.DeviceManager, '_post_init')
    def setUp(self, mock_method):
        self.device_manager = inputs.DeviceManager()
        self.mock_method = mock_method

    @mock.patch('inputs.Mouse')
    @mock.patch('inputs.MightyMouse')
    @mock.patch('inputs.Keyboard')
    def test_find_devices_mac(self, mock_kb, mock_mighty, mock_mouse):
        """Test the mac version of _find_devices_mac."""
        self.device_manager._find_devices_mac()
        number_of_keyboards = len(self.device_manager.keyboards)
        number_of_mice = len(self.device_manager.mice)

        # We should have 1 keyboard and 2 mice.
        self.assertEqual(number_of_keyboards, 1)
        self.assertEqual(number_of_mice, 2)

        # Each of the classes should be instantiated.
        mock_kb.assert_called_once_with(self.device_manager)
        mock_mighty.assert_called_once_with(self.device_manager)
        mock_mouse.assert_called_once_with(self.device_manager)


class HelpersTestCase(TestCase):
    """Test the device manager class."""
    # pylint: disable=arguments-differ

    # There can never be too many tests.
    # pylint: disable=too-many-public-methods

    @mock.patch('inputs.devices')
    def setUp(self, mock_devices):
        self.devices = mock_devices

    @mock.patch('inputs.devices')
    def test_get_key(self, devices):
        """Get key reads from the first keyboard."""
        keyboard = mock.MagicMock()
        reader = mock.MagicMock()
        keyboard.read = reader
        devices.keyboards = [keyboard]

        inputs.get_key()

        reader.assert_called_once()

    @mock.patch('inputs.devices')
    def test_get_key_index_error(self, devices):
        """Raises unpluggged error if no keyboard attached."""
        devices.keyboards = []
        with self.assertRaises(inputs.UnpluggedError):
            # pylint: disable=pointless-statement
            inputs.get_key()

    @mock.patch('inputs.devices')
    def test_get_mouse(self, devices):
        """Get event reads from the first mouse."""
        mouse = mock.MagicMock()
        reader = mock.MagicMock()
        mouse.read = reader
        devices.mice = [mouse]

        inputs.get_mouse()

        reader.assert_called_once()

    @mock.patch('inputs.devices')
    def test_get_mouse_index_error(self, devices):
        """Raises unpluggged error if no mouse attached."""
        devices.mice = []
        with self.assertRaises(inputs.UnpluggedError):
            # pylint: disable=pointless-statement
            inputs.get_mouse()

    @mock.patch('inputs.devices')
    def test_get_gamepad(self, devices):
        """Get key reads from the first gamepad."""
        gamepad = mock.MagicMock()
        reader = mock.MagicMock()
        gamepad.read = reader
        devices.gamepads = [gamepad]

        inputs.get_gamepad()

        reader.assert_called_once()

    @mock.patch('inputs.devices')
    def test_get_gamepad_index_error(self, devices):
        """Raises unpluggged error if no gamepad attached."""
        devices.gamepads = []
        with self.assertRaises(inputs.UnpluggedError):
            # pylint: disable=pointless-statement
            inputs.get_gamepad()


if __name__ == '__main__':
    main()
