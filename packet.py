import json

class Packet:
    def __init__(self, seq_num, data, checksum):
        self.seq_num = seq_num
        self.data = data
        self.checksum = checksum

    def to_json(self):
        return json.dumps({
            "seq_num": self.seq_num,
            "data": self.data,
            "checksum": self.checksum
        })

    @staticmethod
    def from_json(json_data):
        obj = json.loads(json_data)
        return Packet(obj["seq_num"], obj["data"], obj["checksum"])