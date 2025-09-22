# Simple Input Functions for MLFQ Scheduler
# These functions help us get input from the user in a friendly way

def get_user_input(prompt):
    """
    Get input from the user with a prompt.
    If there's an error (like pressing Ctrl+C), return an empty string.
    """
    # Uses try-except to handle errors gracefully (W3Schools: Python Try Except)
    # If the user presses Ctrl+C or there's an input error, we catch it
    try:
        # Uses input() to get text from the user (W3Schools: Python Input)
        # This pauses the program until the user types something and presses Enter
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        # Returns empty string if there's an error (GeeksforGeeks: Python Exception Handling)
        # This prevents the program from crashing when user presses Ctrl+C
        return ""

def get_number(prompt, default_value=None, min_value=None, max_value=None):
    """
    Get a number from the user.
    
    Parameters:
    - prompt: What to ask the user
    - default_value: What to use if they press Enter without typing anything
    - min_value: Smallest number allowed
    - max_value: Largest number allowed
    
    Returns: The number the user entered, or the default if they didn't enter anything
    """
    # Uses get_user_input() to get text from the user (GeeksforGeeks: Python Functions)
    # Uses .strip() to remove spaces from the beginning and end (W3Schools: Python String Methods)
    user_input = get_user_input(prompt).strip()
    
    # If they didn't type anything, use the default
    # Uses if statement to check if the input is empty (W3Schools: Python If Statement)
    # Uses == to compare the input with an empty string (GeeksforGeeks: Python Operators)
    if user_input == "":
        return default_value
    
    # Try to convert their input to a number
    # Uses try-except to handle conversion errors (W3Schools: Python Try Except)
    try:
        # Uses int() to convert the text to a number (W3Schools: Python Built-in Functions)
        # This will fail if the user typed something like "abc" instead of "123"
        number = int(user_input)
        
        # Check if the number is too small
        # Uses if statement with and to check multiple conditions (W3Schools: Python If Statement)
        # Uses < to compare the number with the minimum allowed value (GeeksforGeeks: Python Operators)
        if min_value is not None and number < min_value:
            # Uses print() to show an error message to the user (W3Schools: Python Output)
            # Uses f-string to insert values into the message (W3Schools: Python String Formatting)
            print(f"Number must be at least {min_value}. Using default: {default_value}")
            return default_value
            
        # Check if the number is too big
        # Uses if statement with and to check multiple conditions (W3Schools: Python If Statement)
        # Uses > to compare the number with the maximum allowed value (GeeksforGeeks: Python Operators)
        if max_value is not None and number > max_value:
            # Uses print() to show an error message to the user (W3Schools: Python Output)
            # Uses f-string to insert values into the message (W3Schools: Python String Formatting)
            print(f"Number must be no more than {max_value}. Using default: {default_value}")
            return default_value
            
        return number
        
    except ValueError:
        # Uses print() to show an error message to the user (W3Schools: Python Output)
        # Uses f-string to insert the default value into the message (W3Schools: Python String Formatting)
        print(f"That's not a valid number. Using default: {default_value}")
        return default_value

def get_yes_or_no(prompt, default_answer=True):
    """
    Ask the user a yes/no question.
    
    Parameters:
    - prompt: What to ask the user
    - default_answer: What to use if they just press Enter
    
    Returns: True for yes, False for no
    """
    # Uses if-else to choose the right prompt format (W3Schools: Python If Statement)
    # Uses f-string to create a prompt that shows the default answer (W3Schools: Python String Formatting)
    if default_answer:
        full_prompt = f"{prompt} [Y/n]: "
    else:
        full_prompt = f"{prompt} [y/N]: "
    
    # Uses get_user_input() to get text from the user (GeeksforGeeks: Python Functions)
    # Uses .strip() to remove spaces and .lower() to make it lowercase (W3Schools: Python String Methods)
    user_input = get_user_input(full_prompt).strip().lower()
    
    # If they didn't type anything, use the default
    # Uses if statement to check if the input is empty (W3Schools: Python If Statement)
    if user_input == "":
        return default_answer
    
    # Check what they typed
    # Uses if-elif-else to check different possible answers (W3Schools: Python If Statement)
    # Uses in operator to check if the input matches accepted values (GeeksforGeeks: Python Operators)
    if user_input in ("y", "yes"):
        return True
    elif user_input in ("n", "no"):
        return False
    else:
        # Uses print() to show an error message (W3Schools: Python Output)
        # Uses f-string with conditional expression to show the default (W3Schools: Python String Formatting)
        print(f"Please answer 'y' for yes or 'n' for no. Using default: {'Yes' if default_answer else 'No'}")
        return default_answer

def print_separator():
    """Print a nice line to separate sections."""
    # Uses print() to display text on the screen (W3Schools: Python Output)
    # Uses string multiplication to repeat "=" 50 times (GeeksforGeeks: Python String Operations)
    print("=" * 50)

def print_section_title(title):
    """Print a nice section title."""
    # Uses print_separator() to print a line above the title (GeeksforGeeks: Python Functions)
    # Uses print_separator() to print a line below the title (GeeksforGeeks: Python Functions)
    print_separator()
    # Uses print() to display the title (W3Schools: Python Output)
    # Uses f-string to insert the title into the output (W3Schools: Python String Formatting)
    print(f"  {title}")
    print_separator()
