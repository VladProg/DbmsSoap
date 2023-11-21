import spyne

from Models import Values
import Messages


class Type:

    @staticmethod
    def from_message(message):
        type_enum = message.type_enum
        if type_enum == Messages.TypeEnum.Char:
            return Char()
        elif type_enum == Messages.TypeEnum.Color:
            return Color()
        elif type_enum == Messages.TypeEnum.ColorInvl:
            return ColorInvl(
                r1=message.R1,
                r2=message.R2,
                g1=message.G1,
                g2=message.G2,
                b1=message.B1,
                b2=message.B2
            )
        elif type_enum == Messages.TypeEnum.Integer:
            return Integer()
        elif type_enum == Messages.TypeEnum.Real:
            return Real()
        elif type_enum == Messages.TypeEnum.String:
            return String()
        else:
            raise spyne.Fault(faultcode="Client", faultstring='Unsupported Type')


class Char(Type):
    def parse(self, s):
        return Values.Char(self, s)

    def __eq__(self, other):
        return isinstance(other, Char)

    def __str__(self):
        return "Char"

    def to_message(self):
        return Messages.Type(type_enum=Messages.TypeEnum.Char, to_str=str(self))


class Color(Type):
    def parse(self, s):
        return Values.Color(self, s)

    def __eq__(self, other):
        return isinstance(other, Color)

    def __str__(self):
        return "Color"

    def to_message(self):
        return Messages.Type(type_enum=Messages.TypeEnum.Color, to_str=str(self))


class Integer(Type):
    def parse(self, s):
        return Values.Integer(self, s)

    def __eq__(self, other):
        return isinstance(other, Integer)

    def __str__(self):
        return "Integer"

    def to_message(self):
        return Messages.Type(type_enum=Messages.TypeEnum.Integer, to_str=str(self))


class Real(Type):
    def parse(self, s):
        return Values.Real(self, s)

    def __eq__(self, other):
        return isinstance(other, Real)

    def __str__(self):
        return "Real"

    def to_message(self):
        return Messages.Type(type_enum=Messages.TypeEnum.Real, to_str=str(self))


class String(Type):
    def parse(self, s):
        return Values.String(self, s)

    def __eq__(self, other):
        return isinstance(other, String)

    def __str__(self):
        return "String"

    def to_message(self):
        return Messages.Type(type_enum=Messages.TypeEnum.String, to_str=str(self))


class ColorInvl:
    def __init__(self, r1, r2, g1, g2, b1, b2):
        self.r1 = r1
        self.r2 = r2
        self.g1 = g1
        self.g2 = g2
        self.b1 = b1
        self.b2 = b2
        self._validate()

    def _validate(self):
        if min(self.r1, self.r2, self.g1, self.g2, self.b1, self.b2) < 0 or max(self.r1, self.r2, self.g1, self.g2, self.b1, self.b2) > 255:
            raise spyne.Fault(faultcode="Client", faultstring="RGB bounds bust be in [0..255]")
        if self.r1 > self.r2:
            raise spyne.Fault(faultcode="Client", faultstring="Minimum bound of R must be less than or equal to maximum bound of R")
        if self.g1 > self.g2:
            raise spyne.Fault(faultcode="Client", faultstring="Minimum bound of G must be less than or equal to maximum bound of G")
        if self.b1 > self.b2:
            raise spyne.Fault(faultcode="Client", faultstring="Minimum bound of B must be less than or equal to maximum bound of B")

    def parse(self, s):
        return Values.ColorInvl(self, s)

    def __eq__(self, other):
        return (
                isinstance(other, ColorInvl) and
                self.r1 == other.r1 and self.r2 == other.r2 and
                self.g1 == other.g1 and self.g2 == other.g2 and
                self.b1 == other.b1 and self.b2 == other.b2
        )

    def __str__(self):
        return f"ColorInvl (R∈[{self.r1}..{self.r2}], G∈[{self.g1}..{self.g2}], B∈[{self.b1}..{self.b2}])"

    def to_message(self):
        return Messages.Type(
            type_enum=Messages.TypeEnum.ColorInvl,
            r1=self.r1, r2=self.r2, g1=self.g1, g2=self.g2, b1=self.b1, b2=self.b2,
            to_str=str(self)
        )
