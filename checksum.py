def calculate_checksum(data: str) -> int:
    return sum(ord(ch) for ch in data) % 256


def verify_checksum(data: str, checksum: int) -> bool:
    return calculate_checksum(data) == checksum