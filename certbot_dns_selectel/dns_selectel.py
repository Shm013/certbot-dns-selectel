#   Copyright 2019 Nikolay Shamanovich shm013@yandex.ru
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""DNS Authenticator for Selectel DNS."""
import re
import logging

import selectel_dns_api
from selectel_dns_api.rest import ApiException

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

ACCOUNT_KEYS_URL = 'https://my.selectel.ru/profile/apikeys'


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Selectel DNS

    This Authenticator uses the Selectel DNS API to fulfill a dns-01 challenge.
    """

    description = ('Obtain certificates using a DNS TXT record (if you are using Selectel for '
                   'DNS).')
    ttl = 120

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add)
        add('credentials', help='Selectel DNS API credentials file.')

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Selectel DNS API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'Selectel DNS credentials file',
            {
                'api-key': 'API key for Selectel DNS API, obtained from {0}'.format(ACCOUNT_KEYS_URL)
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._get_selectel_client().add_txt_record(domain, validation_name, validation, self.ttl)

    def _cleanup(self, domain, validation_name, validation):
        self._get_selectel_client().del_txt_record(domain, validation_name, validation)

    def _get_selectel_client(self):
        return  _SelectelDNSClient(self.credentials.conf('api-key'))

class NoRecordError(Exception):
    pass

class NoDomainZoneError(Exception):
    pass

class _SelectelDNSClient(object):
    """
    Encapsulates all communication with the Selectel API.
    """

    def __init__(self, api_key):
        selectel_dns_api.configuration.api_key['X-Token'] = api_key
        self.domains = selectel_dns_api.DomainsApi()
        self.records = selectel_dns_api.RecordsApi()

    def _find_domain_id(self, domain):
        try:
            # Getting domains info
            api_response = self.domains.get_domains()
        except ApiException as e:
            print("Exception when calling DomainsApi->get_domains: %s\n" % e)

        # Search for most suitable domain_zone
        result = None
        match_len = 0
        for domain_zone in api_response:
            # Domain and zone the same
            if domain == domain_zone.name:
                result = domain_zone
                break
            # Search subdomain domain in domain_zone
            res = re.search("{}$".format(domain_zone.name), domain)
            if res:
                current_match_len = res.span()[1] - res.span()[0]
                # More specific zone found
                if current_match_len > match_len:
                    result = domain_zone
                    match_len = current_match_len

        # Domain zone not found
        if not result:
            raise NoDomainZoneError("No any suitable domain zone for {}".format(record_name, domain))

        return result.id

    def _find_record_id(self, domain_id, record_name):
        result = None

        try:
            # Find domain by id
            api_response = self.records.get_resource_records_by_domain_id(domain_id)
        except ApiException as e:
            print("Exception when calling RecordsApi->get_resource_records_by_domain_id: %s\n" % e)

        for record in api_response:
            if record.name == record_name:
                result = record.id

        if result == None:
            raise NoRecordError("No record {} found".format(record_name))

        return result

    def add_txt_record(self, domain, record_name, record_content, record_ttl):

        domain_id = self._find_domain_id(domain)

        body = selectel_dns_api.NewOrUpdatedRecord(
            name = record_name,
            type = 'TXT',
            ttl = record_ttl,
            content = record_content
        )

        try:
            # Create resource records for domain
            api_response = self.records.add_resource_record(body, domain_id)
        except ApiException as e:
            print("Exception when calling RecordsApi->add_resource_record: %s\n" % e)

    def del_txt_record(self, domain, record_name, record_content):
        domain_id = self._find_domain_id(domain)
        record_id = self._find_record_id(domain_id, record_name)

        try:
            # Deletes a resource record
            api_response = self.records.delete_resource_record(domain_id, record_id)
        except ApiException as e:
            print("Exception when calling RecordsApi->delete_resource_record: %s\n" % e)
