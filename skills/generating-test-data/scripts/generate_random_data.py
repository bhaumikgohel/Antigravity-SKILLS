import random
import string

def generate_valid_password(min_len=8, max_len=16):
    """Generates a password meeting typical complex rules."""
    length = random.randint(min_len, max_len)
    chars = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()")
    ]
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    chars += [random.choice(all_chars) for _ in range(length - 4)]
    random.shuffle(chars)
    return "".join(chars)

if __name__ == "__main__":
    print(f"Sample Valid Password: {generate_valid_password()}")
