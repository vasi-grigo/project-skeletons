# coding=utf-8
schema = {
    "type": "object",
    "additionalProperties": False,
    "required": ["grpc"],
    "properties": {
        "grpc": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "port": {"type": "integer", "minimum": 1, "maxiumum": 65535},
                "workers": {"type": "number"}
            }
        }
    },
}