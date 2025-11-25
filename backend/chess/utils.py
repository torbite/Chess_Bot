import math

def get_next_multiple_number(num, mult):
    return math.ceil(num / mult) * mult

def get_previous_multiple_number(n: int, x: int):
    return (n // x) * x

def get_roof_square_number(p):
    file = p % 8
    return file + 56
    
def get_bottom_square_number(p):
    return p % 8

def top_left_diagonal_square_number(bit_pos: int) -> int:
    row = bit_pos // 8
    col = bit_pos % 8
    steps = min(col, 7 - row)
    return bit_pos + steps * 7


def top_right_diagonal_square_number(bit_pos: int) -> int:
    row = bit_pos // 8
    col = bit_pos % 8
    steps = min(7 - col, 7 - row)
    return bit_pos + steps * 9


def bottom_right_diagonal_square_number(bit_pos: int) -> int:
    row = bit_pos // 8
    col = bit_pos % 8
    steps = min(7 - col, row)
    return bit_pos - steps * 7


def bottom_left_diagonal_square_number(bit_pos: int) -> int:
    row = bit_pos // 8
    col = bit_pos % 8
    steps = min(col, row)
    return bit_pos - steps * 9

def get_hv_rules(bit_pos, limit_range = False):
    row = bit_pos // 8
    col = bit_pos % 8

    horizontal_rules = []
    vertical_rules = []
    diag_rules = []

    def append_if_not_empty(container, values):
        if values:
            container.append(values)

    if not limit_range:
        # Horizontal (left / right)
        append_if_not_empty(
            horizontal_rules,
            list(range(bit_pos - 1, row * 8 - 1, -1)) if col > 0 else []
        )
        append_if_not_empty(
            horizontal_rules,
            list(range(bit_pos + 1, row * 8 + 8)) if col < 7 else []
        )

        # Vertical (up / down)
        append_if_not_empty(
            vertical_rules,
            list(range(bit_pos + 8, 64, 8)) if row < 7 else []
        )
        append_if_not_empty(
            vertical_rules,
            list(range(bit_pos - 8, -1, -8)) if row > 0 else []
        )

        # Diagonals
        # Up-left
        up_left = []
        r, c = row + 1, col - 1
        while r <= 7 and c >= 0:
            up_left.append(r * 8 + c)
            r += 1
            c -= 1
        append_if_not_empty(diag_rules, up_left)

        # Up-right
        up_right = []
        r, c = row + 1, col + 1
        while r <= 7 and c <= 7:
            up_right.append(r * 8 + c)
            r += 1
            c += 1
        append_if_not_empty(diag_rules, up_right)

        # Down-right
        down_right = []
        r, c = row - 1, col + 1
        while r >= 0 and c <= 7:
            down_right.append(r * 8 + c)
            r -= 1
            c += 1
        append_if_not_empty(diag_rules, down_right)

        # Down-left
        down_left = []
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0:
            down_left.append(r * 8 + c)
            r -= 1
            c -= 1
        append_if_not_empty(diag_rules, down_left)
    else:
        # Adjacent squares only
        if col > 0:
            append_if_not_empty(horizontal_rules, [bit_pos - 1])
        if col < 7:
            append_if_not_empty(horizontal_rules, [bit_pos + 1])

        if row < 7:
            append_if_not_empty(vertical_rules, [bit_pos + 8])
        if row > 0:
            append_if_not_empty(vertical_rules, [bit_pos - 8])

        if row < 7 and col > 0:
            append_if_not_empty(diag_rules, [bit_pos + 7])
        if row < 7 and col < 7:
            append_if_not_empty(diag_rules, [bit_pos + 9])
        if row > 0 and col < 7:
            append_if_not_empty(diag_rules, [bit_pos - 7])
        if row > 0 and col > 0:
            append_if_not_empty(diag_rules, [bit_pos - 9])

    return horizontal_rules, vertical_rules, diag_rules
