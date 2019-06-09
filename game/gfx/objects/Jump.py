class Jump:
    POINTER_DOMAIN = 0b111

    def __init__(self, data):
        self.data = data

        # domain: 0b1110
        # unused: 0b0001
        self.screen_index = data[0] & 0x0F
        self.exit_vertical = (data[1] & 0xF0) >> 4
        self.exit_action = data[1] & 0x0F
        self.exit_horizontal = data[2]

    def to_bytes(self):
        return self.data

    def __repr__(self):
        return (
            f"Jump: Screen #{self.screen_index}, "
            + f"Exit ({self.exit_horizontal}, {self.exit_vertical}), "
            + f"Action #{self.exit_action}"
        )

    def __str__(self):
        return f"Jump on screen #{self.screen_index}"

    @staticmethod
    def is_jump(data):
        return data[0] >> 5 == Jump.POINTER_DOMAIN
