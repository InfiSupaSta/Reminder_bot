class Helper:

    """
    Class with info about current FSM state. All existing states are located in this directory
    in *_state.py modules.

    # Aiogram will provide info about states like 'SomeClass:some_state' if class was
    # created like below

    class SomeClass(StatesGroup):
        some_state = State()
        ...
    """

    state = {
        'OffsetState:offset': 'setting your time offset'
    }

    action = {
        'OffsetState:offset': 'please input an your timezone offset. It must starts with + or - sign, '
                              'be in range from -12 to + 14, '
                              'can looks like +7, -9:30, +5.45.\n'
                              'Separators between numbers can be comma(,), dot(.), or colon(:).'
    }
