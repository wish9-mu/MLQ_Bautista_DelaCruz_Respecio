def read_line(prompt):
    try:
        return input(prompt)
    except EOFError:
        return ""


def read_int_or_default(prompt, default=None, min_val=None, max_val=None):
    s = read_line(prompt).strip()
    if s == "":
        return default
    try:
        v = int(s)
        if min_val is not None and v < min_val:
            print(f"Value must be ≥ {min_val}. Using default: {default}")
            return default
        if max_val is not None and v > max_val:
            print(f"Value must be ≤ {max_val}. Using default: {default}")
            return default
        return v
    except ValueError:
        print(f"Invalid integer. Using default: {default}")
        return default


def read_yes_no_default(prompt, default=True):
    s = read_line(f"{prompt} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
    if s in ("y", "yes"):
        return True
    if s in ("n", "no"):
        return False
    return default


