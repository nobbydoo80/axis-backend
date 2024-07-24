"""mocked_responses.py: Django Mocked Responses for testing"""


import logging
import os

from requests import HTTPError

__author__ = "Steven K"
__date__ = "11/14/2019 10:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)

SOURCES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sources"))


class MockReponse:
    """Fake Response"""

    def __init__(self, response_content, status_code=200):
        self.content = response_content
        self.status_code = status_code

    def raise_for_status(self):
        """Raises stored :class:`HTTPError`, if one occurred."""
        if 400 <= self.status_code < 600:
            raise HTTPError("err", response=self)


def validation_mock(*args, **kwargs):
    return []


def doe_mocked_soap_responses(*args, **kwargs):
    """This will replace out the mocked responses"""

    data = kwargs.get("data")

    if data is None:
        # Testing out retrieve_file
        source = os.path.join(SOURCES, "hes_label_5dcdc93513_225_efd.pdf")
        if "page" in args[0]:
            source = os.path.join(SOURCES, "hes_label_5dcdc93513_225_efd.png")
        with open(source, "rb") as doc:
            data = doc.read()
        return MockReponse(data)

    data = data.decode("utf-8") if data else ""
    if "get_session_token" in data:
        response = """
             <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
                  <SOAP-ENV:Body>
                    <ns1:get_session_tokenResponse>
                      <ns1:get_session_token_result>
                        <ns1:session_token>3pajidhl5m9n1kh9v8r8n4282d</ns1:session_token>
                      </ns1:get_session_token_result>
                    </ns1:get_session_tokenResponse>
                  </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
         """
        if "BAD_API" in data:
            response = """
                 <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
                  <SOAP-ENV:Body>
                    <SOAP-ENV:Fault>
                      <faultcode>Sender</faultcode>
                      <faultstring>Invalid password</faultstring>
                    </SOAP-ENV:Fault>
                  </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
             """
        return MockReponse(response)

    if "destroy_session_token" in data:
        response = """
             <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
                  <SOAP-ENV:Body>
                    <ns1:destroy_session_tokenResponse>
                      <ns1:destroy_session_token_result>
                        <ns1:result>OK</ns1:result>
                      </ns1:destroy_session_token_result>
                    </ns1:destroy_session_tokenResponse>
                  </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
         """
        if "BAD_API" in data:
            response = """
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
                   <SOAP-ENV:Body>
                      <SOAP-ENV:Fault>
                         <faultcode>Receiver</faultcode>
                         <faultstring>Invalid session token or session has timed out</faultstring>
                      </SOAP-ENV:Fault>
                   </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
             """
        return MockReponse(response)

    if "submit_hpxml_inputs" in data:
        response = """
            <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
              <SOAP-ENV:Body>
                <ns1:submit_hpxml_inputsResponse>
                  <ns1:submit_hpxml_inputs_result>
                    <ns1:building_id>225871</ns1:building_id>
                    <ns1:result>OK</ns1:result>
                  </ns1:submit_hpxml_inputs_result>
                </ns1:submit_hpxml_inputsResponse>
              </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
         """
        if "building_id" in data:
            pass  # It's the same.

        if "BAD_API" in data:
            response = """
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
                  <SOAP-ENV:Body>
                    <ns1:submit_hpxml_inputsResponse>
                      <ns1:submit_hpxml_inputs_result>
                        <ns1:building_id>0</ns1:building_id>
                        <ns1:result>FAIL</ns1:result>
                        <ns1:message>Traceback (most recent call last):&#13;
File "/usr/local/lib/python3.6/dist-packages/hescorehpxml/__init__.py", line 2366, in main&#13;
  nrel_assumptions=args.nrelassumptions&#13;
  File "/usr/local/lib/python3.6/dist-packages/hescorehpxml/__init__.py", line 625, in
    hpxml_to_hescore_json&#13;
      hescore_bldg = self.hpxml_to_hescore_dict(*args, **kwargs)&#13;
      File "/usr/local/lib/python3.6/dist-packages/hescorehpxml/__init__.py", line 697, in
        hpxml_to_hescore_dict&#13;
          bldg['about'] = self._get_building_about(b, p)&#13;
          File "/usr/local/lib/python3.6/dist-packages/hescorehpxml/__init__.py", line 896, in
            _get_building_about&#13;
              xpath(site_el, 'h:OrientationOfFrontOfHome/text()'))&#13;
              File "/usr/local/lib/python3.6/dist-packages/hescorehpxml/__init__.py", line 621, in
                get_nearest_azimuth&#13;
              raise TranslationError('Either an orientation or azimuth is required.')&#13;
              hescorehpxml.TranslationError: Either an orientation or azimuth is required.&#13;
              &#13;
              During handling of the above exception, another exception occurred:&#13;
              &#13;
              Traceback (most recent call last):&#13;
              File "/usr/local/bin/hpxml2hescore", line 10, in &lt;module&gt;&#13;
                  sys.exit(main())&#13;
                    File "/usr/local/lib/python3.6/dist-packages/hescorehpxml/__init__.py",
                      line 2370, in main&#13;
                        exmsg = ex.message&#13;
                        AttributeError: 'TranslationError' object has no attribute 'message'&#13;
                        </ns1:message>
                      </ns1:submit_hpxml_inputs_result>
                    </ns1:submit_hpxml_inputsResponse>
                  </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
             """
        return MockReponse(response)

    if "building_label" in data:
        response = """
            <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
              <SOAP-ENV:Body>
                <ns1:generate_labelResponse>
                  <ns1:building_label_result>
                    <ns1:result>OK</ns1:result>
                    <ns1:message>Label for building #225875 successfully generated</ns1:message>
                    <ns1:file>
                      <ns1:type>pdf</ns1:type>
                      <ns1:url>https://hescore-pnnl-label-be.s3.amazonaws.com/hes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf</ns1:url>
                    </ns1:file>
                    <ns1:file>
                      <ns1:type>png</ns1:type>
                      <ns1:url>https://sandbeta.hesapi.labworks.org/st_rest/label_page?label_url=https%3A%2F%2Fhescore-pnnl-label-be.s3.amazonaws.com%2Fhes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf&amp;page=1</ns1:url>
                    </ns1:file>
                    <ns1:file>
                      <ns1:type>png</ns1:type>
                      <ns1:url>https://sandbeta.hesapi.labworks.org/st_rest/label_page?label_url=https%3A%2F%2Fhescore-pnnl-label-be.s3.amazonaws.com%2Fhes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf&amp;page=2</ns1:url>
                    </ns1:file>
                    <ns1:file>
                      <ns1:type>png</ns1:type>
                      <ns1:url>https://sandbeta.hesapi.labworks.org/st_rest/label_page?label_url=https%3A%2F%2Fhescore-pnnl-label-be.s3.amazonaws.com%2Fhes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf&amp;page=3</ns1:url>
                    </ns1:file>
                    <ns1:file>
                      <ns1:type>png</ns1:type>
                      <ns1:url>https://sandbeta.hesapi.labworks.org/st_rest/label_page?label_url=https%3A%2F%2Fhescore-pnnl-label-be.s3.amazonaws.com%2Fhes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf&amp;page=4</ns1:url>
                    </ns1:file>
                    <ns1:file>
                      <ns1:type>png</ns1:type>
                      <ns1:url>https://sandbeta.hesapi.labworks.org/st_rest/label_page?label_url=https%3A%2F%2Fhescore-pnnl-label-be.s3.amazonaws.com%2Fhes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf&amp;page=5</ns1:url>
                    </ns1:file>
                    <ns1:file>
                      <ns1:type>png</ns1:type>
                      <ns1:url>https://sandbeta.hesapi.labworks.org/st_rest/label_page?label_url=https%3A%2F%2Fhescore-pnnl-label-be.s3.amazonaws.com%2Fhes_label_5dcdc939cef998.89098513_225875_ef3cb1ec9b1cf583979d2cd277dec3ed.pdf&amp;page=6</ns1:url>
                    </ns1:file>
                  </ns1:building_label_result>
                </ns1:generate_labelResponse>
              </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
         """
        if "BAD_API" in data:
            response = """
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
                   <SOAP-ENV:Body>
                      <SOAP-ENV:Fault>
                         <faultcode>Receiver</faultcode>
                         <faultstring>Building 10245 does not exist.</faultstring>
                      </SOAP-ENV:Fault>
                   </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
             """
        return MockReponse(response)
    if "retrieve_label_resultsRequest" in data:
        response = """
            <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
              <SOAP-ENV:Body>
                <ns1:retrieve_label_resultsResponse>
                  <ns1:label_result>
                    <ns1:address>123 Main Street</ns1:address>
                    <ns1:city>Golden</ns1:city>
                    <ns1:state>CO</ns1:state>
                    <ns1:zip_code>80401</ns1:zip_code>
                    <ns1:conditioned_floor_area>2400</ns1:conditioned_floor_area>
                    <ns1:year_built>1961</ns1:year_built>
                    <ns1:cooling_present>1</ns1:cooling_present>
                    <ns1:base_score>8</ns1:base_score>
                    <ns1:package_score>8</ns1:package_score>
                    <ns1:cost_savings>35</ns1:cost_savings>
                    <ns1:assessment_type>Official - Initial</ns1:assessment_type>
                    <ns1:assessment_date>2014-12-02</ns1:assessment_date>
                    <ns1:label_number>225883</ns1:label_number>
                    <ns1:qualified_assessor_id>TST-Pivotal</ns1:qualified_assessor_id>
                    <ns1:hescore_version>2019.2.0</ns1:hescore_version>
                    <ns1:utility_electric>8302</ns1:utility_electric>
                    <ns1:utility_natural_gas>541</ns1:utility_natural_gas>
                    <ns1:utility_fuel_oil>0</ns1:utility_fuel_oil>
                    <ns1:utility_lpg>0</ns1:utility_lpg>
                    <ns1:utility_cord_wood>0</ns1:utility_cord_wood>
                    <ns1:utility_pellet_wood>0</ns1:utility_pellet_wood>
                    <ns1:utility_generated>0</ns1:utility_generated>
                    <ns1:source_energy_total_base>135</ns1:source_energy_total_base>
                    <ns1:source_energy_asset_base>63</ns1:source_energy_asset_base>
                    <ns1:estimated_annual_energy_cost>1200</ns1:estimated_annual_energy_cost>
                    <ns1:average_state_cost>0.67</ns1:average_state_cost>
                    <ns1:average_state_eui>51.8</ns1:average_state_eui>
                  </ns1:label_result>
                </ns1:retrieve_label_resultsResponse>
              </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
        """
        if "BAD_API" in data:
            response = """
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
                   <SOAP-ENV:Body>
                      <SOAP-ENV:Fault>
                         <faultcode>0</faultcode>
                         <faultstring>The request failed due to access control restrictions:
                            User does not have the administrator role.
                            -- User has the appropriate role, but the following buildings were not
                            created by assessors associated with partner 'Test': 1000.
                            -- User does not have the mentor role.
                            -- User does not own the following building(s): 1000
                            -- User is not a quality assurance provider.
                            -- User has the appropriate role, but the following buildings were not
                            created by assessors associated with partner 'Test': 1000.</faultstring>
                      </SOAP-ENV:Fault>
                   </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
             """
        return MockReponse(response)

    if "retrieve_extended_resultsRequest" in data:
        response = """
            <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
              <SOAP-ENV:Body>
                <ns1:retrieve_extended_resultsResponse>
                  <ns1:extended_result>
                    <ns1:label_number>225875</ns1:label_number>
                    <ns1:building_id>225875</ns1:building_id>
                    <ns1:weather_station_location>Broomfield Jeffco</ns1:weather_station_location>
                    <ns1:create_label_date>2019-11-15</ns1:create_label_date>
                    <ns1:cooling_present>1</ns1:cooling_present>
                    <ns1:source_energy_total_base>135</ns1:source_energy_total_base>
                    <ns1:source_energy_total_package>130</ns1:source_energy_total_package>
                    <ns1:source_energy_asset_base>63</ns1:source_energy_asset_base>
                    <ns1:source_energy_asset_package>57</ns1:source_energy_asset_package>
                    <ns1:base_cost>1239</ns1:base_cost>
                    <ns1:package_cost>1204</ns1:package_cost>
                    <ns1:source_eui_base>56</ns1:source_eui_base>
                    <ns1:source_eui_package>54</ns1:source_eui_package>
                    <ns1:base_score>8</ns1:base_score>
                    <ns1:package_score>8</ns1:package_score>
                    <ns1:site_energy_base>82</ns1:site_energy_base>
                    <ns1:site_energy_package>77</ns1:site_energy_package>
                    <ns1:site_eui_base>34</ns1:site_eui_base>
                    <ns1:site_eui_package>32</ns1:site_eui_package>
                    <ns1:carbon_base>17686</ns1:carbon_base>
                    <ns1:carbon_package>17090</ns1:carbon_package>
                    <ns1:utility_electric_base>8302</ns1:utility_electric_base>
                    <ns1:utility_natural_gas_base>541</ns1:utility_natural_gas_base>
                    <ns1:utility_fuel_oil_base>0</ns1:utility_fuel_oil_base>
                    <ns1:utility_lpg_base>0</ns1:utility_lpg_base>
                    <ns1:utility_cord_wood_base>0</ns1:utility_cord_wood_base>
                    <ns1:utility_pellet_wood_base>0</ns1:utility_pellet_wood_base>
                    <ns1:utility_generated_base>0</ns1:utility_generated_base>
                    <ns1:utility_electric_package>8302</ns1:utility_electric_package>
                    <ns1:utility_natural_gas_package>490</ns1:utility_natural_gas_package>
                    <ns1:utility_fuel_oil_package>0</ns1:utility_fuel_oil_package>
                    <ns1:utility_lpg_package>0</ns1:utility_lpg_package>
                    <ns1:utility_cord_wood_package>0</ns1:utility_cord_wood_package>
                    <ns1:utility_pellet_wood_package>0</ns1:utility_pellet_wood_package>
                    <ns1:utility_generated_package>0</ns1:utility_generated_package>
                  </ns1:extended_result>
                </ns1:retrieve_extended_resultsResponse>
              </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
        """
        if "BAD_API" in data:
            response = """
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
                   <SOAP-ENV:Body>
                      <SOAP-ENV:Fault>
                         <faultcode>0</faultcode>
                         <faultstring>The request failed due to access control restrictions:
                            User does not have the administrator role.
                            -- User has the appropriate role, but the following buildings were not
                            created by assessors associated with partner 'Test': 1000.
                            -- User does not have the mentor role.
                            -- User does not own the following building(s): 1000
                            -- User is not a quality assurance provider.
                            -- User has the appropriate role, but the following buildings were not
                            created by assessors associated with partner 'Test': 1000.</faultstring>
                      </SOAP-ENV:Fault>
                   </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
             """
        return MockReponse(response)

    if "delete_buildings_by_id" in data:
        response = """
        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
          <SOAP-ENV:Body>
            <ns1:delete_buildings_by_idResponse>
              <ns1:delete_buildings_by_id_result>
                <ns1:status>true</ns1:status>
              </ns1:delete_buildings_by_id_result>
            </ns1:delete_buildings_by_idResponse>
          </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """
        if "BAD_API" in data:
            response = """
            <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
               <SOAP-ENV:Body>
                  <SOAP-ENV:Fault>
                     <faultcode>Receiver</faultcode>
                     <faultstring>Building 225888 has status 'deleted'. delete_buildings_by_id is
                     only permitted with building status 'initializing', 'base_calculated',
                     'locked', 'completed'</faultstring>
                  </SOAP-ENV:Fault>
               </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>"""
        return MockReponse(response)

    if "validate_inputs" in data:
        response = """"""

        if "BAD_API" in data:
            response = """<SOAP-ENV:Envelope
                xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:ns1="http://hesapi.labworks.org/st_api/serve">
            <SOAP-ENV:Body>
                <ns1:validate_inputsResponse>
                  <ns1:validation_message>
                    <ns1:field>roof_area_1</ns1:field>
                    <ns1:type>error</ns1:type>
                    <ns1:message>This home’s minimum footprint is approximately 2070sqft, but you have only specified 600sqft of total roof area. Please adjust any incorrect values. *The footprint is calculated as (&lt;total area&gt; - &lt;conditioned basement area&gt;) / &lt;number of floors&gt;</ns1:message>
                  </ns1:validation_message>
                  <ns1:validation_message>
                    <ns1:field>floor_area_1</ns1:field>
                    <ns1:type>error</ns1:type>
                    <ns1:message>This home’s minimum footprint is approximately 2070sqft, but you have only specified 600sqft of total floor area. Please adjust any incorrect values. *The footprint is calculated as (&lt;total area&gt; - &lt;conditioned basement area&gt;) / &lt;number of floors&gt;</ns1:message>
                  </ns1:validation_message>
                </ns1:validate_inputsResponse>
              </SOAP-ENV:Body>
            </SOAP-ENV:Envelope>"""
        return MockReponse(response)
    print("Unhandled", data)
