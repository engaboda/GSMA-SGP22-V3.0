import codecs
import hashlib

from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from ecdsa import SigningKey, BRAINPOOLP256r1, VerifyingKey, ECDH

from es9plus.tlv_helper import TlvHelper


class SCP11:
    """
        SCP 11 Specification
        --
        1. The data field is padded according to the encryption algorithm and mode used, as defined in table 4c.
            If this algorithm is AES-CBC-128 or SM4-CBC, padding SHALL be done as follows:
                1. Append a byte with value '80' to the right of the data block;
                2. Append 0 to 15 bytes with value '00' so that the length of the padded data block is a multiple of 16 bytes.
        2. The result of step 1 is encrypted according to the encryption algorithm and mode used, as defined in table 4c.
            If this algorithm is AES-CBC-128 or SM4-CBC, the following applies:
                1.  The data blocks SHALL be numbered starting from 1
                2.  The binary value of this number SHALL be left padded with zeroes to form a full block.
                3.  This block SHALL be encrypted with S-ENC to produce the ICV for command encryption.
        3. The input data used for C-MAC computation comprises the MAC Chaining value, the tag, the final length and
            the result of step 2.
            1.  The initial MAC Chaining value is set as defined in 2.6.4.2 or 2.6.4.6.
            2.  Subsequent MAC chaining values are the full result of step 4 of the previous data block
                (which may also be a data block with C-MAC only).
        4.  The full MAC value is computed using the MACing algorithm as defined in table 4c.
        5.  The output data is computed by concatenating the following data: the tag, the final length,
            the result of step 2 and the C-MAC value.

            If the algorithm is AES-CBC-128 or SM4-CBC, the C-MAC value is the 8 most significant bytes of the result of step 4.

        tag: is based on segment [87, 88, 86]
    """
    tlv_helper = TlvHelper()

    DEFAULT_ICV = "00000000000000000000000000000000"
    MAX_PAYLOAD_LENGTH = 1007
    KEY_TYPE = '88'
    KEY_LENGTH = '10'
    HOST_ID = '74657374736D6470706C7573312E6773'

    def __init__(self, imcv, s_enc, s_cmac):
        self.icv = self.DEFAULT_ICV
        self.imcv = imcv
        self.s_enc = s_enc
        self.s_cmac = s_cmac
        self.counter = 1

        self.ot_pk_smdp_ecka = None

    @classmethod
    def create_key_pair_for_diffie_hellman(cls):
        private_key = SigningKey.generate(curve=BRAINPOOLP256r1)
        ot_sk_euicc_ecka = SigningKey.from_pem(private_key.to_pem())

        # Get the public key.
        public_key = private_key.get_verifying_key()
        return ot_sk_euicc_ecka, public_key.to_string(encoding="uncompressed")[1:]

    @classmethod
    def get_shared_secret(cls, local_private_key, received_public_key_bytes):
        ot_sk_euicc = SigningKey.from_string(local_private_key.to_string(), curve=BRAINPOOLP256r1)
        received_public_key = VerifyingKey.from_string(received_public_key_bytes, curve=BRAINPOOLP256r1)
        ecdh = ECDH(curve=BRAINPOOLP256r1, private_key=ot_sk_euicc, public_key=received_public_key)
        shared_secret = ecdh.generate_sharedsecret()
        return hex(shared_secret)[2:]

    @classmethod
    def shared_info(cls, eid):
        return (
            cls.KEY_TYPE + cls.KEY_LENGTH + cls.tlv_helper.get_length_value(cls.HOST_ID) +
            cls.tlv_helper.get_length_value(eid.decode())
        )

    @classmethod
    def generate_session_key(cls, ephemeral_shared_secret, static_shared_secret, shared_info):
        """
            X9.63 Key Derivation Function.
            Key Derivation Function for Session Keys.

        """
        counter = "1".zfill(8)
        msg = ephemeral_shared_secret + counter + shared_info
        key_data1 = hashlib.sha256(bytearray.fromhex(msg)).hexdigest()

        counter = "2".zfill(8)
        msg = ephemeral_shared_secret + counter + shared_info
        key_data2 = hashlib.sha256(bytearray.fromhex(msg)).hexdigest()

        counter = "3".zfill(8)
        msg = static_shared_secret + counter + shared_info
        key_data3 = hashlib.sha256(bytearray.fromhex(msg)).hexdigest()

        counter = "4".zfill(8)
        msg = static_shared_secret + counter + shared_info
        key_data4 = hashlib.sha256(bytearray.fromhex(msg)).hexdigest()

        final_key_data = key_data1 + key_data2 + key_data3 + key_data4
        return final_key_data[0:32], final_key_data[32:64], final_key_data[64:96]

    @classmethod
    def get_scp03_instance(cls, received_public_key_bytes, eid, remote_static_public_key, local_static_private_key):
        ot_sk_smdp_ecka, ot_pk_smdp_ecka = cls.create_key_pair_for_diffie_hellman()
        shared_secret_ephemeral = cls.get_shared_secret(ot_sk_smdp_ecka, received_public_key_bytes)
        shared_secret_static = cls.get_shared_secret(local_static_private_key, remote_static_public_key)
        shared_info = cls.shared_info(eid)
        # Initial MAC chaining value
        # Secure Channel session key for command and response encryption
        # Secure Channel C-MAC session key
        imcv, s_enc, s_cmac = cls.generate_session_key(shared_secret_ephemeral, shared_secret_static, shared_info)

        scp03_instance = cls(imcv, s_enc, s_cmac)
        scp03_instance.ot_pk_smdp_ecka = ot_pk_smdp_ecka

        return scp03_instance

    def get_counter_as_hex(self):
        counter = format(self.counter, 'X')
        parity = 0 if len(counter) % 2 == 0 else 1
        counter = counter.rjust(parity, '0')
        return counter.rjust(32, '0')

    def pad(self, payload):
        """
            padding prior to performing an AES operation across a block of data is achieved in the following manner:
            1. Append an '80' to the right of the data block;
            2. If the resultant data block length is a multiple of 16, no further padding is required;
            3. Append binary zeroes to the right of the data block until the data block length is a multiple of 16.
        """
        if len(payload)/2 > self.MAX_PAYLOAD_LENGTH:
            print(f"Euicc Can handle up to this Size: {self.MAX_PAYLOAD_LENGTH}")
            return
        elif len(payload)/2 == self.MAX_PAYLOAD_LENGTH:
            msg_upp = payload + "80"
        else:
            msg_upp = payload + "80"
            msg_upp = msg_upp + "0" * (32 - (len(msg_upp) % 32))

        return msg_upp

    def generate_icv(self):
        msg = self.get_counter_as_hex()
        encrypted_icv = self._encrypt(self.icv, msg)

        return encrypted_icv

    def _encrypt(self, icv, message):
        cipher = AES.new(codecs.decode(self.s_enc, 'hex'), AES.MODE_CBC, codecs.decode(icv, 'hex'))
        encrypted_data = cipher.encrypt(codecs.decode(message, 'hex'))
        return encrypted_data

    def encrypt(self, message):
        icv = self.generate_icv().hex()
        padded_msg = self.pad(message)
        encrypted_data = self._encrypt(icv, padded_msg)
        return encrypted_data

    def cmac(self, message, tag):
        """
            cmac is Cipher message authentication code
            The input data used for C-MAC computation comprises the MAC Chaining value, the tag,
            the final length and the result of step 2.
                .   The initial MAC Chaining value is set as defined in 2.6.4.2 or 2.6.4.6.
                .   Subsequent MAC chaining values are the full result of step 4 of the previous data block
                    (which may also be a data block with C-MAC only).
        """
        self.counter += 1
        final_length = len(self.imcv) + len(message)
        msg = self.imcv + tag + final_length + message
        mac = self.generate_aes_cmac(msg, self.s_cmac)
        self.imcv = mac
        # If the algorithm is AES-CBC-128 or SM4-CBC, the C-MAC value is the 8 most significant bytes
        return message + mac[0:16]

    @staticmethod
    def generate_aes_cmac(message_data, cmac_key):
        cmac = CMAC.new(bytearray.fromhex(cmac_key), ciphermod=AES)
        cmac.update(bytearray.fromhex(message_data))
        mac = cmac.hexdigest()
        return mac
