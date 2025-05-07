def load_accounts(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if ":" in line]

def load_proxies(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_result(path, lines):
    with open(path, "w") as f:
        f.write("\n".join(lines))
