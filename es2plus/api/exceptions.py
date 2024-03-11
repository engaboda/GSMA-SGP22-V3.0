from rest_framework.exceptions import ValidationError


class RpmOrderMandatoryElementMissingEidException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.1.1",
                    'reasonCode': "2.2",
                    'message': "Indicates that the EID is missing in the context of this order.",
                }
            }
        }
    }


class RpmOrderUnknownEidException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.1.1",
                    'reasonCode': "3.9",
                    'message': "Indicates that the eUICC, identified by this EID is unknown to the SM-DP+.",
                }
            }
        }
    }


class RpmOrderMatchingIdInvalidException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.2.6",
                    'reasonCode': "2.1",
                    'message': "Matching ID provided by the Operator is not valid.",
                }
            }
        }
    }


class RpmOrderMatchingIdAlreadyIsUseException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.2.6",
                    'reasonCode': "3.3",
                    'message': "Matching ID provided by the Operator is already in use at the SM-DP+.",
                }
            }
        }
    }


class RpmOrderInvalidProfileOwnerOIDException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.2.12",
                    'reasonCode': "3.10",
                    'message': "The Operator provided incorrect Profile Owner OID.",
                }
            }
        }
    }


class RpmOrderConditionalElementMissingICCIDException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.2.1",
                    'reasonCode': "2.3",
                    'message': "Indicates that the ICCID is missing in the context of the RPM Command.",
                }
            }
        }
    }


class RpmOrderICCIDIsUnknownException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.2.1",
                    'reasonCode': "3.9",
                    'message': "Indicates that the Profile, identified by this ICCID is unknown to the SM-DP+. ",
                }
            }
        }
    }


class RpmOrderConditionalElementMissingUpdateMetadataRequestException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.2.9",
                    'reasonCode': "2.3",
                    'message': "Indicates that no Metadata object is provided in the.",
                }
            }
        }
    }


class RpmOrderSMDSInAccessibleException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.9",
                    'reasonCode': "5.1",
                    'message': "Indicates that the smdsAddress is invalid or not reachable.",
                }
            }
        }
    }


class RpmOrderSMDSExecutionErrorException(ValidationError):
    status_code = 200
    default_detail = {
        'header': {
            'functionExecutionStatus': {
                'status': 'Failed',
                'statusCodeData': {
                    'subjectCode': "8.9",
                    'reasonCode': "4.2",
                    'message': "The cascade SM-DS registration has failed. SMDS has raised an error.",
                }
            }
        }
    }
