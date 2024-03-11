from serializers import RpmOrderRequestSerializer, RpmOrderResponseSerializer


class RpmCommandName:
    ENABLE: str = 'enable'
    DISABLE: str = 'disable'
    DELETE: str = 'delete'
    LIST_PROFILE_INFO: str = 'listProfileInfo'
    UPDATE_METADATA: str = 'updateMetadata'
    CONTACT_PCMP: str = 'contactPcmp'


class RpmOrderHelper:
    RESPONSE_SERIALIZER = RpmOrderResponseSerializer

    def __init__(self, request):
        self.tenant_name = request.tenant_name

        rpm_order_serializer = RpmOrderRequestSerializer(
            data=request.data, context={'tenant_name': self.tenant_name}
        )
        rpm_order_serializer.is_valid(raise_exception=True)
        self.serializer_data = rpm_order_serializer.data

    @property
    def response(self):
        _response = self.RESPONSE_SERIALIZER(
            {
                'header': {
                    "functionExecutionStatus": {"status": "Executed-Success"}
                },
                'matchingId': self.serializer_data.matchingId
            }
        ).data

        return _response
