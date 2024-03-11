from rest_framework import viewsets
from rest_framework.response import Response

from api.utils import RpmOrderHelper


class RpmOrderViewSet(viewsets.ViewSet):
    """
        This function is used to instruct the SM-DP+ of a new RPM Package.

        On reception of this function call, the SM-DP+ SHALL:
        1.  Verify that the eid is present. Otherwise, the SM-DP+ SHALL return a status code
            "EID - Mandatory Element Missing".
        2.  Identify the eUICC by using the eid. If it cannot be identified, the SM-DP+ SHALL
            return a status code "EID - Unknown".
        3.  Generate a MatchingID (section 4.1.1) if it is not provided by the Operator.
        4.  If the Operator has provided the MatchingID:
            1.  If its format is invalid, then the SM-DP+ SHOULD return a status code
                "Matching ID - Invalid".
            2.  If it conflicts with one already stored, then the SM-DP+ SHALL return a status
                code "Matching ID - Already in Use".
        5.  Store the MatchingID and the EID.
        6.  Prepare an RPM Package as follows.
            1.  If the rpmScript includes RPM Command(s) 'List Profile Info' (with Profile Owner OID)
                coded as defined in section 2.10.1, for each of these commands,
                the SM-DP+ SHALL verify that the function caller correctly presented its Profile
                Owner OID in the RPM Command. If not, the SM-DP+ SHALL return a status
                code "Profile Owner - Invalid Association".

            2.  If the rpmScript includes RPM Command 'Enable Profile', 'Disable Profile',
                'Delete Profile', 'List Profile Info' (with ICCID), 'Contact PCMP' or 'Update
                Metadata' coded as defined in section 2.10.1, the SM-DP+ SHALL for each of
                these commands:
                    1.  Identify the Profile associated with the ICCID. If the ICCID is not
                        provided, the SM-DP+ SHALL return a status code "Profile ICCID -
                        Conditional Element Missing". If the Profile cannot be identified, the SM
                        DP+ SHALL return a status code "Profile ICCID - Unknown".
                    2.  Verify that the function caller is the Profile Owner of the Profile. If it is
                        not, the SM-DP+ SHALL return a status code "Profile ICCID - Unknown".
                    3.  Verify that the Profile is installed in the target eUICC. If it is not, the SM
                        DP+ SHALL return a status code "EID - Invalid Association".
                    4.  For RPM Command 'Update Metadata', validate the provided updateMetadataRequest field.
                        If no Metadata object is present, the SMDP+ SHALL return a status code
                        "Profile Metadata - Conditional Element Missing". If it is invalid, the SM-DP+ SHALL return a status
                        code "Profile Metadata - Invalid".
        7.  Associate the RPM Package with the EID and MatchingID.
        8.  If a Root SM-DS address is provided and optionally also an Alternative SM-DS address with non-empty value(s)
                1.  Verify that the MatchingID is not a zero length value. If the MatchingID is a zero
                    length value, the SM-DP+ SHALL return a status code "Matching ID - Invalid".
                2.  Store the SM-DS address(es) with the RPM Package to be used later for Event
                    Registration and Event Deletion.
                    1.  If the Root SM-DS address begins with a full stop character (e.g., '.unspecified'),
                        the SM-DP+ MAY determine the applicable Root SM-DS for this Profile in an
                        implementation-dependent manner.
                    2.  If the Alternative SM-DS address begins with a full stop character (e.g.,
                        '.unspecified'), the SM-DP+ MAY determine the applicable
                        Alternative SM-DS for this Profile in an implementation-dependent
                        manner.
                3.  Perform Event Registration, where the MatchingID SHALL be used as the EventID.
                    If the SM-DS is not reachable, the SM-DP+ SHALL return a status code "SM-DS - Inaccessible".
                    If the Event Registration fails, the SM-DP+ SHALL return a status code "SM-DS - Execution Error".
                    1.  If an Alternative SM-DS was specified, this SHALL be a cascaded registration.
                        Otherwise, it SHALL be a non cascaded registration.
    """
    rpm_order_helper = RpmOrderHelper

    def create(self, request):
        Response(self.rpm_order_helper(request).response)