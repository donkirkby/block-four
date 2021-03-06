from mittmcts import Draw

from block_four_game import BlockFourGame, BlockFourMove


def test_initial_state():
    game = BlockFourGame()

    state = game.initial_state(player=1)

    assert game.get_cell(state, 0, 0) is None
    assert state.player == 1
    assert game.get_size() == 9


def test_initial_state_small():
    game = BlockFourGame(field_size=2, field_count=2)

    state = game.initial_state(player=1)

    assert game.get_cell(state, 0, 0) is None
    assert game.get_size() == 4


def test_get_cell():
    game = BlockFourGame(field_size=1, field_count=3)
    state = game.initial_state(cells="""\
+..
...
.-.

""")

    assert 1 == game.get_cell(state, row=0, column=0)
    assert -1 == game.get_cell(state, row=2, column=1)
    assert None is game.get_cell(state, row=2, column=2)


def test_format():
    game = BlockFourGame(field_size=2, field_count=2)
    expected_text = """\
+..+
.--.
....
-++-"""
    state = game.initial_state(cells=expected_text)

    text = game.format(state)

    assert expected_text == text


def test_move():
    game = BlockFourGame()
    state1 = game.initial_state(player=1)
    move = BlockFourMove(row=1, column=3)
    state2 = game.apply_move(state1, move)

    assert game.get_cell(state2, 1, 3) == 1
    assert game.get_cell(state2, 2, 3) is None
    assert state2.player == -1


def test_filled_field():
    game = BlockFourGame(field_size=2, field_count=2)
    state1 = game.initial_state(player=1, cells="""\
++..
....
....
..--
""")
    expected_state = """\
++..
++..
....
..--"""

    state2 = game.apply_move(state1, BlockFourMove(1, 0))

    assert expected_state == game.format(state2)


def test_current_player1():
    state = BlockFourGame().initial_state(player=1)

    player = BlockFourGame.current_player(state)

    assert player == 1


def test_current_player2():
    game = BlockFourGame()
    state1 = game.initial_state(player=1)
    state2 = game.apply_move(state1, BlockFourMove(1, 3))

    player = game.current_player(state2)

    assert player == -1


def test_get_first_moves():
    game = BlockFourGame(field_size=1, field_count=2)
    state = game.initial_state(player=1)
    expected_moves = [BlockFourMove(0, 0),
                      BlockFourMove(0, 1),
                      BlockFourMove(1, 0),
                      BlockFourMove(1, 1)]

    is_random, moves = game.get_moves(state)

    assert expected_moves == moves
    assert is_random is False


def test_get_later_moves():
    game = BlockFourGame(field_size=1, field_count=2)
    state = game.initial_state(cells="""\
+.
.-
""")
    expected_moves = [BlockFourMove(0, 1),
                      BlockFourMove(1, 0)]

    _, moves = game.get_moves(state)

    assert expected_moves == moves


def test():
    game = BlockFourGame(field_size=2, field_count=2)
    state = game.initial_state(cells="""\
+...
....
.-..
....
""")
    expected_moves = [BlockFourMove(0, 1),
                      BlockFourMove(0, 2),
                      BlockFourMove(2, 0),
                      BlockFourMove(2, 2)]

    _, moves = game.get_moves(state)

    assert expected_moves == moves


def test_no_winner():
    game = BlockFourGame(field_size=1, field_count=2)
    state = game.initial_state(cells="""\
++
+.
""")
    winner = game.get_winner(state)

    assert winner is None


def test_winner():
    game = BlockFourGame(field_size=1, field_count=2)
    state = game.initial_state(cells="""\
++
+-
""")
    winner = game.get_winner(state)

    assert winner == 1


def test_winner_draw():
    game = BlockFourGame(field_size=1, field_count=2)
    state = game.initial_state(cells="""\
++
--
""")
    winner = game.get_winner(state)

    assert winner is Draw
