import string

A = string.ascii_uppercase

ROTORS = {
    "I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    "IV": ("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
    "V": ("VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
}

REFLECTORS = {
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}


class Rotor:
    def __init__(self, name, ring=1, pos="A"):
        wiring, notch = ROTORS[name]
        self.fwd = [A.index(c) for c in wiring]
        self.bwd = [self.fwd.index(i) for i in range(26)]
        self.notch = A.index(notch)
        self.ring = ring - 1
        self.pos = A.index(pos)

    def at_notch(self):
        return self.pos == self.notch

    def step(self):
        self.pos = (self.pos + 1) % 26

    def forward(self, c):
        return (self.fwd[(c + self.pos - self.ring) % 26] - self.pos + self.ring) % 26

    def backward(self, c):
        return (self.bwd[(c + self.pos - self.ring) % 26] - self.pos + self.ring) % 26


class Enigma:
    def __init__(self, rotors=("I", "II", "III"), reflector="B",
                 rings=(1, 1, 1), positions="AAA", plugboard=""):
        self.left, self.mid, self.right = (
            Rotor(n, r, p) for n, r, p in zip(rotors, rings, positions)
        )
        self.reflector = [A.index(c) for c in REFLECTORS[reflector]]
        self.plug = {c: c for c in A}
        for pair in plugboard.upper().split():
            a, b = pair
            self.plug[a], self.plug[b] = b, a

    def step(self):
        if self.mid.at_notch():
            self.mid.step()
            self.left.step()
        elif self.right.at_notch():
            self.mid.step()
        self.right.step()

    def encrypt_char(self, ch):
        self.step()
        c = A.index(self.plug[ch])
        c = self.right.forward(c)
        c = self.mid.forward(c)
        c = self.left.forward(c)
        c = self.reflector[c]
        c = self.left.backward(c)
        c = self.mid.backward(c)
        c = self.right.backward(c)
        return self.plug[A[c]]

    def encrypt(self, text):
        return "".join(
            self.encrypt_char(ch) if ch in A else ch for ch in text.upper()
        )


if __name__ == "__main__":
    settings = dict(
        rotors=("I", "II", "III"),
        reflector="B",
        rings=(1, 1, 1),
        positions="AAA",
        plugboard="AB CD EF",
    )
    message = "HELLO WORLD"
    cipher = Enigma(**settings).encrypt(message)
    plain = Enigma(**settings).encrypt(cipher)
    print(cipher)
    print(plain)
