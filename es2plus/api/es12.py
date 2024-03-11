import requests

from exceptions import RpmOrderSMDSInAccessibleException, RpmOrderSMDSExecutionErrorException


class SmdsHelper:
    ES_12_PLATFORM_URL = ''
    DELETE_PATH = '/gsma/rsp2/es12/deleteEvent'
    REGISTER_PATH = '/gsma/rsp2/es12/registerEvent'

    def __init__(self, eid, rspServerAddress, eventId, forwardingIndicator):
        self.eid = eid
        self.rspServerAddress = rspServerAddress
        self.eventId = eventId
        self.forwardingIndicator = forwardingIndicator

    @staticmethod
    def _request_header():
        return {
            'Content-Type': 'application/json',
            'X-Admin-Protocol': 'v2.2.0'
        }

    @staticmethod
    def _header():
        return {
            "header": {
                "functionRequesterIdentifier": "",
                "functionCallIdentifier": ""
            }
        }

    def _register_body(self):
        return {
            "eid": self.eid,
            "rspServerAddress": self.rspServerAddress,
            "eventId": self.eventId,
            "forwardingIndicator": self.forwardingIndicator
        }

    def _delete_body(self):
        return {
            "eid": self.eid,
            "eventId": self.eventId,
        }

    def register(self):
        try:
            response = requests.post(
                self.ES_12_PLATFORM_URL + self.REGISTER_PATH,
                data={**self._header(), **self._register_body()},
                headers=self._request_header()
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise RpmOrderSMDSInAccessibleException()
        if response.data.get('header', {}).get('functionExecutionStatus', {}).get('status') == 'Failed':
            raise RpmOrderSMDSExecutionErrorException()
        return response

    def delete(self):
        response = requests.post(
            self.ES_12_PLATFORM_URL + self.DELETE_PATH,
            data={**self._header(), **self._delete_body()},
            headers=self._request_header()
        )
        return response
