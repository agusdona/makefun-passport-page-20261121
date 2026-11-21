def get_val(c):
    if '0' <= c <= '9': return int(c)
    if 'A' <= c <= 'Z': return ord(c) - ord('A') + 10
    return 0

def checksum(s):
    weights = [7, 3, 1]
    res = 0
    for i, char in enumerate(s):
        res += get_val(char) * weights[i % 3]
    return res % 10

# Doc No: MD0847132
print(f"Checksum MD0847132: {checksum('MD0847132')}")
# DOB: 960312
print(f"Checksum 960312: {checksum('960312')}")
# Expiry: 340408
print(f"Checksum 340408: {checksum('340408')}")
# Personal number: 14 '<'s
# Correction: The checksum digit AFTER the 14 characters is of the 14 characters alone.
print(f"Checksum 14 '<'s: {checksum('<<<<<<<<<<<<<<')}")
