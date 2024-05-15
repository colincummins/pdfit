import binascii
import base64


class UnrecognizedFileTypeError(Exception):
    """
    Raised when handler does not recognize value in the 'file_type' field
    """

    def __init__(self):
        self.message = f"File type not recognized"
        super().__init__(self.message)


class MissingPayloadError(Exception):
    """
    Raised when JSON message has no payload
    """

    def __init__(self):
        self.message = f"Message has no payload"
        super().__init__(self.message)


class PayloadNotBase64Error(Exception):
    """
    Raised when message payload cannot be decoded from base64
    """

    def __init__(self):
        self.message = f"Message payload cannot be decoded from base64"
        super().__init__(self.message)


class CantEncodePayloadError(Exception):
    """
    Raised when message payload cannot be decoded from base64
    """

    def __init__(self):
        self.message = f"Cannot encode payload into base64"
        super().__init__(self.message)


def decode_payload(message: dict) -> dict:
    """
    Decodes the 'payload' attribute of 'message' from base64
    :type message: [dict]
    :param message: Dict with 'payload' attribute of base64 encoded data
    :return: 'message' dict but with 'payload' decoded
    """
    try:
        message['payload'] = base64.b64decode(message['payload'])
        return message
    except binascii.Error:
        raise PayloadNotBase64Error


def encode_payload(message: dict) -> dict:
    """
    Encodes the 'payload' attribute of 'message' into base64
    :rtype:
    :type message: [dict]
    :param message: Dict with 'payload' attribute
    :return: 'message' dict but with 'payload' encoded base64 [dict | None]
    """
    try:
        message['payload'] = base64.b64encode(message['payload']).decode("utf-8")
        return message
    except binascii.Error:
        raise CantEncodePayloadError


class MessageHandler:
    def __init__(self, string_to_func=None) -> None:
        if string_to_func is None:
            self.function_dictionary = dict()
        else:
            self.function_dictionary = string_to_func

    def add_function(self, file_type: str, f: object) -> None:
        self.function_dictionary[file_type] = f

    def validate_json(self, message_json: dict) -> None:
        """
        Checks JSON for presence of required fields, and confirms that files is
        a type that can be handled by the MessageHandler
        :param message_json: [dict]
        :return: None
        :except: Raises descriptive error if json is missing required fields or file type not recognized
        """
        if message_json['type'] not in self.function_dictionary:
            raise UnrecognizedFileTypeError

    def generate_reply(self, message: dict):
        """
        Takes a 'message' dict, validates it, then uses the function corresponding to 'type' from the handlers
        dictionary of functions to generate the payload for a reply dictionary object If the message is invalid or
        some error occurs with payload creation, an error dictionary will be returned instead :param message:
        JSON/dict with a 'type' and 'payload' field :return: JSON/dict with a 'status' and 'payload' field.
        """
        try:
            self.validate_json(message)
            message = decode_payload(message)
            reply_payload = self.function_dictionary[message['type']](**message)
            reply = {"status": "ok", "payload": reply_payload}
            reply = encode_payload(reply)
        except (UnrecognizedFileTypeError, MissingPayloadError, PayloadNotBase64Error, CantEncodePayloadError) as error:
            reply = {"status": "error", "payload": error.message}
        except KeyError as error:
            reply = {"status": "error", "payload": "JSON object missing required field" + str(error)}
        except Exception as error:
            reply = {"status": "error", "payload": "Server error: " + str(error)}
        finally:
            return reply
