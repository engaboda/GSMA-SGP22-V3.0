class ProfileContentManagement:
    """
        The response to this HTTP POST request should contain a single script targeting a specific application of a
        specific Secure Element that is accessible through the requesting Admin Agent.

        The Admin Agent finally has the responsibility to forward the script to the right application of the right Secure
        Element, for execution of the individual APDUs.

        A dialog between the Admin Agent and the Admin Server is then initiated, and represented by consecutive
        HTTP POST requests and responses. Each HTTP POST request serves two purposes:
            1.  Send back the APDU script responses (returned by the execution of the APDU script by the Secure Element) to the Admin Server.
                1.  The script response is set in the Body of the HTTP POST request, and identified as such by setting
                    the “Content-Type” header to the
                    value: “application/vnd.globalplatform.card-content-mgt-response;version=1.0”
                2. Ask again the question: “Is there any other script ready to be executed by one of my Secure Element(s)?”

        Progress within the overall administration session is performed through the usage of specific HTTP headers,
        and in particular by the navigation of a “Next URI”. The Next URI information is returned by the Admin Server
        in each HTTP POST response, in the “X-Admin-Next-URI” header:
            1.  The chaining of consecutive HTTP POST requests within a dialog is ensured by this Next URI. When
                set in a HTTP POST response, the Next URI represents the location where to post the execution
                result of the script, and to query for the next script.
            2.  The Next URI also enables to switch from one dialog to another within the same administration
                session, each of the dialogs implying the same Admin Agent, but potentially several Admin Servers.
                An HTTP POST response may then not contain a script, but may however provide a Next URI
                pointing to another feature of the same Admin Server, or to another Admin Server.
            3.  Note that by convention, if a script is present in a HTTP POST response, then the HTTP code of the
                HTTP POST response shall be “200 OK”. If no script is present in the HTTP POST response, then
                the HTTP POST response Body is empty and the HTTP code of the HTTP POST response shall be
                “204 No Content”.
            4.  The Next URI may also state the end of the administration session. When no Next URI is provided
                by the Admin Server, then the administration session ends. If a script is present in this last HTTP
                POST response, this last script shall be executed but the script execution result will not be returned
                to the Admin Server as the session has ended.

        Note that for any reason, Admin Servers might want to allocate individual identifiers to the various dialogs they
        are performing with Admin Agents. However, the way to identify such dialogs and the way to communicate this
        information back and forth between the Admin Server and the Admin Agent (through the usage of a specific
        HTTP header, or through a specific query parameter in the Next URI, etc.) are implementation dependent.


        Similarly, within a dialog, Admin Servers might want to allocate individual identifiers to the various scripts or
        steps (i.e. HTTP POSTs) that take part of the dialog. However, the way to identify such scripts/steps and the
        way to communicate this information back and forth between the Admin Server and the Admin Agent (through
        the usage of a specific HTTP header, or through a specific query parameter in the URL, etc.) are
        implementation dependent.

        An administration session may be interrupted due to many reasons such as network connectivity issues, the
        Admin Agent stop/crash, the shutdown of the device, etc. If so, the Admin Agent is responsible to restart the
        administration session (when technically feasible, i.e. when the device has restarted or when the network
        connectivity issues are over) by re-navigating the last navigated URI, and setting a dedicated flag to indicate
        to the Admin Server that the administration session is in resume mode (setting the “X-Admin-Resume” header
        to “true”). This is then the responsibility of the Admin Server to determine whether the dialog can be continued
        from the point it has been interrupted, or if the dialog should be restarted from the beginning.

        Multiple Secure Elements
            In order to address several Secure Elements using a single Admin Agent in the device, and to allow the Admin
            Agent to provide information about the SE(s) it manages and the SE it is currently talking to, headers must be
            added to the ones already defined in the administration protocol of [GP Amd B]:
                1.  The “X-Admin-SE-List” header is added in the HTTP POST request of the Admin Agent, to
                    enable the Admin Agent to notify the Admin Server about the SEs that are accessible through the
                    agent.
                2.  The “X-Admin-Targeted-SE” header is added in the HTTP POST requests and responses, to
                    enable the Admin Agent and the Admin Server to know the SE that is/was targeted for the script
                    execution.

            The “X-Admin-SE-List” header shall be sent by the Admin Agent to the Admin Server at the beginning of
            each dialog (and in particular in the first Admin Agent HTTP POST request of the administration session), as
            dialogs within an administration session might be processed by different Admin Servers.
            The “X-Admin-SE-List” header shall be set even if the Admin Agent manages a single Secure Element.
            If the “X-Admin-SE-List” header is present in the HTTP POST request, the header value shall be a list of
            SE identifiers. Each element of the list is separated by ‘;’ character.

            The “X-Admin-Targeted-SE” header is mandatory:
                1.  In all HTTP POST responses that contain a script to be executed by a Secure Element, in order the
                    Admin Agent to clearly know which SE the script should be forwarded to, and
                2.  In all HTTP POST requests that contain a script response, in order for the Admin Server to identify
                    which SE the response is coming from.

            The “X-Admin-Targeted-SE” header shall be set even if the Admin Agent manages a single Secure
            Element. It shall not be present if the HTTP POST response/request does not contain any script/script
            response.

            If the “X-Admin-Targeted-SE” header is present in the HTTP POST response, the header value shall be
            composed of the SE identifier type and the SE identifier value, using the following format: //se-id/<se-id-type>/<se-id-value>

            Pre-defined SE identifier types are:
                1.  Card Unique Data. This is a common identifier defined by [GPCS]. When the Card Unique Data is
                    used as SE Identifier, the coding of the “X-Admin-Targeted-SE” header is defined as follows: //se-id/CUD/<CUD-value>
                    Where the <CUD-value> shall be the hexadecimal string representation of the Card Unique Data of
                    the Secure Element. For example “//se-id/CUD/0123456789ABCDEF0123”.
                2.  ICCID. When the SE type is a UICC, the usual UICC identifier, ICCID defined by ITU-T E.118 [ITU E.118], can be used.
                    In this case, the coding of the “X-Admin-Targeted-SE” header is defined as follows: //se-id/ICCID/<ICCID-value>
                    Where the <ICCID-value> shall be the hexadecimal string representation of the ICCID of the UICC packed in BCD (not swapped).
                    For example “//se-id/ICCID/0123456789ABCDEF0123”.

        the delivery status: Header: X-Admin-Script-Status
            1.  “unavailable-se”: This value is used if the SE targeted by the “X-Admin-Targeted-SE” header
                of the previous HTTP POST response is not present in the device or cannot be reached by the
                Admin Agent. The HTTP POST request that contains this value of “X-Admin-Script-Status”
                header shall not include any script response.
            2.  “temporarily-unavailable-application”: This value is used if the application targeted by
                the “X-Admin-Targeted-Application” header of the previous HTTP POST response is
                temporarily not reachable, for example because the maximum number of logical channels is
                reached, or if the application is not multi-selectable and is already selected on another channel, or if
                the SE Access API raises a timeout when sending data to the application. Depending on the time
                when the error occurs, the HTTP POST request that contains this value of “X-Admin-Script
                Status” header may include a script response corresponding to the result of the commands already
                executed.
            3.  “script-format-error”: This value is used in case of script formatting error (e.g. script
                malformed or cannot be parsed by the Admin Agent or by the SE Access API). Depending on the
                time when the error occurs, the HTTP POST request that contains this value of “X-Admin-Script
                Status” header may include a script response corresponding to the result of the commands already
                executed.


        Targeted Application:

            For the direct remote administration of UICCs defined in [GP Amd B], the “X-Admin-Targeted
            Application” header is optional: it represents the AID of the Security Domain that is targeted, and it shall
            be used only in case this targeted Security Domain is not the one in charge of the PSK TLS security.

            For the remote administration of Secure Elements through an Admin Agent in a device, the “X-Admin
            Targeted-Application” header is mandatory and it represents the AID of the application (and not only a
            Security Domain) to which the script shall be forwarded, and that will execute the script.
            As defined in [GP Amd B], the format of the “X-Admin-Targeted-Application” header shall be: //aid/<RID>/<PIX>
            Where <RID> and <PIX> are the two components of the application AID.

            The Admin Agent shall use the SE Access API to open a connection with the SE identified by the “X-Admin
            Targeted-SE” header, and then a logical channel with the application identified by the (“X-Admin
            Targeted-Application” header. The script shall then not contain the SELECT by AID APDU.

        Protocol Version:
            Because of the adaptations of the administration protocol is updated mentioned above, the value of the field
            “X-Admin-Protocol” header is upgraded to “globalplatform-remote-admin/1.1.1”.
    """

    @classmethod
    def hex_range(cls, start, end):
        hex_range_value = []

        for hex_value in range(start, end):
            hex_range_value.append('{:02x}'.format(hex_value).upper())

        return hex_range_value

    KEY_USAGE_QUALIFIER_CODING = {
        14: 'C-MAC',
        24: 'R-MAC',
        34: 'C-MAC + R-MAC',
        18: 'C-ENC',
        28: 'R-ENC',
        38: 'C-ENC + R-ENC',
        48: 'C-DEK',
        88: 'R-DEK',
        'C8': 'C-DEK + R-DEK',
        82: 'PK_SD_AUT',
        42: 'SK_SD_AUT',
        81: 'Token',
        44: 'Receipt',
        84: 'DAP',
        83: ' PK_SD_AUT + Token',
        43: 'SK_SD_AUT + Receipt',
        86: 'PK_SD_AUT + DAP',
        87: 'PK_SD_AUT + Token + DAP'
    }

    KEY_TYPE_CODING = {
        **{
            key_type_hex: 'Reserved for private use'
            for key_type_hex in hex_range(0x00, 0x80)
        },
        80: 'DES – mode (ECB/CBC) implicitly known',
        81: 'Reserved (Triple DES)',
        82: 'Triple DES in CBC mode',
        83: 'DES in ECB mode',
        84: 'DES in CBC mode',
        **{
            rfu_symmetric: 'RFU (symmetric algorithms)'
            for rfu_symmetric in hex_range(0x85, 0x88)
        },
        88: 'AES (16, 24, or 32 long keys)',
        **{
            _rfu_symmetric: 'RFU (symmetric algorithms)'
            for _rfu_symmetric in hex_range(0x89, 90)
        },
        90: 'HMAC-SHA1 – length of HMAC is implicitly known',
        91: 'HMAC-SHA1-160 – length of HMAC is 160 bits',
        **{
            _rfu_symmetric: 'RFU (symmetric algorithms)'
            for _rfu_symmetric in hex_range(0x82, 0x10)
        },
        'A0': 'RSA Public Key - public exponent e component (clear text)',
        'A1': 'RSA Public Key - modulus N component (clear text) ',
        'A2': 'RSA Private Key - modulus N component',
        'A3': 'RSA Private Key - private exponent d component',
        'A4': 'RSA Private Key - Chinese Remainder P component',
        'A5': 'RSA Private Key - Chinese Remainder Q component ',
        'A6': 'RSA Private Key - Chinese Remainder PQ component ( q-1 mod p )',
        'A7': 'RSA Private Key - Chinese Remainder DP1 component ( d mod (p-1) )',
        'A8': 'RSA Private Key - Chinese Remainder DQ1 component ( d mod (q-1) )',
        **{
            _rfu_asymmetric: 'RFU (symmetric algorithms)'
            for _rfu_asymmetric in hex_range(0xA9, 0xFF)
        },
        'FF': 'Extended format'
    }

    KEY_VERSION_NUMBER_KEY_IDENTIFIER_MAPPED_TO_MECHANISM = {
        **{
            f"{key_version_number_hex}-{key_identifier_hex}": "SCP 80"
            for key_version_number_hex in hex_range(0x01, 0x10)
            for key_identifier_hex in hex_range(0x01, 0x04)
        },
        **{
            f"{key_version_number_hex}-{key_identifier_hex}": "SCP 11"
            for key_version_number_hex in hex_range(0x18, 0x20)
            for key_identifier_hex in hex_range(0x01, 0x80)
        },
        **{
            f"{key_version_number_hex}-{key_identifier_hex}": "SCP 02"
            for key_version_number_hex in hex_range(0x20, 0x30)
            for key_identifier_hex in hex_range(0x01, 0x04)
        },
        **{
            f"{key_version_number_hex}-{key_identifier_hex}": "SCP 03"
            for key_version_number_hex in hex_range(0x30, 0x40)
            for key_identifier_hex in hex_range(0x01, 0x04)
        },
        **{
            f"{key_version_number_hex}-{key_identifier_hex}": "SCP 81"
            for key_version_number_hex in hex_range(0x40, 0x50)
            for key_identifier_hex in hex_range(0x01, 0x80)
        },
        '07-01': 'Token Verification',
        '71-01': 'Receipt Generation Key',
        '73-01': 'DAP Verification Key',
        '75-01': 'Ciphered Load File Data Block Key'
    }

    def __init__(
            self, target_application, target_secure_element, apdu_script,
            current_url, steps, request
    ):
        self.target_application = target_application
        self.target_secure_element = target_secure_element
        self.apdu_script = apdu_script
        self.current_url = current_url
        self.steps = steps
        self.request = request
        self.current_step = 1

    def _next_url(self):
        host_url, current_step = self.current_url.split('step=')
        self.current_step = int(current_step)
        if self.current_step == self.steps:
            return {}
        return {"X-Admin-Next-URI": host_url + f"?step={self.current_step + 1}"}

    def _response_header(self):
        return {
            "Content-Type": "application/vnd.globalplatform.card-content-mgt;version=1.1.1",
            "X-Admin-Targeted-Application": self.target_application,
            "X-Admin-Targeted-SE": self.target_secure_element,
            **self._next_url()
        }

    def _response_body(self):
        return self.apdu_script

    def check_admin_script_status(self):
        admin_script_status = self.request.header.get('X-Admin-Script-Status')
        agent_id = self.request.header.get('X-Admin-From')
        print(f'Status of step: {self.current_step - 1} Has Been {admin_script_status} AgentId: {agent_id}')

    def response(self):
        return {
            "header": self._response_header(),
            "body": self._response_body()
        }
