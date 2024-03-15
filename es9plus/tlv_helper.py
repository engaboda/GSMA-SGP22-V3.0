from binascii import hexlify


class TlvHelper:

    @staticmethod
    def get_length_value(data):
        """
            the definite form for simple tlv.
            The tag field T consists of a single byte encoding only a number from 1 to 254.
            The length field consists of 1 or 3 consecutive bytes.
            SIMPLE-TLV has restrictions regarding the tag number (between 1 and 254, inclusive) and length (up to 65535)
        """
        if int(len(data) % 2) != 0:
            return
        elif len(data) // 2 < 127:
            # In the short form, the length octets shall consist of a single octet in which bit 8 is zero and bits 7
            # to 1 encode the number of octets in the contents octets (which may be zero), as an unsigned binary
            # integer with bit 7 as the most significant bit.
            return hexlify((len(data) // 2).to_bytes(1, 'big')).decode() + data
        elif len(data) // 2 < 255:
            return "81" + hexlify((len(data) // 2).to_bytes(1, 'big')).decode().upper() + data
        else:
            return "82" + hexlify((len(data) // 2).to_bytes(2, 'big')).decode().upper() + data
