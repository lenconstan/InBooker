import requests
import json
import datetime
import math

def trim_input(string):
    string = string.strip()
    "Trims the barcode input for barcode input"
    if len(string) > 4:
        if string[-2] == '-':
            newstring = string[:-2]
            string = newstring
            if 'XLS' or 'BR8' in string:
                if len(string) == 11:
                    string = string[:3] + '00' + string[3:]
                elif len(string) == 10:
                    string = string[:3] + '000' + string[3:]
                else:
                    pass
            else:
                pass
        elif string[-3] == '-':
            newstring = string[:-3]
            string = newstring
            if 'XLS' or 'BR8' in string:
                if len(string) == 11:
                    string = string[:3] + '00' + string[3:]
                elif len(string) == 10:
                    string = string[:3] + '000' + string[3:]
                else:
                    pass
            else:
                pass
        else:
            pass

    return string


def login(email, password):
    """Log in with user credentials. Retrieves a 'token' needed for other requests"""

    url = 'https://br8.freightlive.eu/api/v2/authenticate/sign-in'
    response = requests.post(url, json={"email": email, "password": password})
    token = response.json()["token"]

    return token

def get_activity_paginated(token, date_time_from, date_time_to):
    """Get all activities on basis of route id's."""
    def append_items(append_to, append_from):
        try:
            append_to.append(append_from)
        except KeyError:
            print('error')

    items = []
    offset = 0

    url = "https://br8.freightlive.eu/api/v2/activity"
    payload = data ="{\n    \"options\": {\n        \"include_activity_status\": \"true\",\n        \"include_status_name\": \"true\",\n        \"include_activity_type_name\": \"true\",\n        \"include_activity_meta_data\": \"false\",\n        \"include_meta_data\": \"false\",\n        \"include_address_applied\": \"false\",\n        \"include_address\": \"false\",\n        \"include_address_object\": \"false\",\n        \"include_allowed_driver_ids\": \"false\",\n        \"include_allowed_drivers\": \"false\",\n        \"include_allowed_drivers_links\": \"false\",\n        \"include_time_slots\": \"false\",\n        \"include_time_slot_tags\": \"false\",\n        \"include_route_info\": \"true\",\n        \"include_route\": \"true\",\n        \"include_package_lines\": \"false\",\n        \"include_package_line_links\": \"false\",\n        \"include_package_lines_info\": \"false\",\n        \"include_driver_info\": \"false\",\n        \"include_driver\": \"false\",\n        \"include_driver_links\": \"false\",\n        \"include_car\": \"false\",\n        \"include_vehicle\": \"false\",\n        \"include_communication\": \"false\",\n        \"include_communication_object\": \"false\",\n        \"include_compartment_ids\": \"false\",\n        \"include_compartments\": \"false\",\n        \"include_links\": \"false\",\n        \"include_activity_links\": \"false\",\n        \"include_files\": \"false\",\n        \"include_activity_files_meta_data\": \"false\",\n        \"include_assignment_nr\": \"true\",\n        \"include_assignment\": \"true\",\n        \"include_activity_tags\": \"true\",\n        \"include_tag_type_name\": \"true\",\n        \"include_record_info\": \"false\",\n        \"include_record_object\": \"false\",\n        \"include_notes\": \"false\",\n        \"include_activity_notes\": \"false\",\n        \"include_activity_note_tags\": \"false\",\n        \"include_depot_address\": \"false\",\n        \"include_depot_address_object\": \"false\",\n        \"include_capacity_object\": \"false\",\n        \"include_capacities\": \"false\",\n        \"include_filled_capacities\": \"false\",\n        \"include_applied_capacities\": \"false\",\n        \"include_zones\": \"true\",\n        \"include_brand\": \"false\",\n        \"include_brand_name\": \"false\",\n        \"include_brand_colours\": \"false\",\n        \"include_brand_files\": \"false\",\n        \"apply_address_bundling\": \"false\",\n        \"include_bundled_activity_ids\": \"false\",\n        \"include_activity_files\": \"false\",\n        \"include_activity_record_info\": \"false\",\n        \"include_activity_record_object\": \"false\",\n        \"include_party_name\": \"true\",\n        \"include_shipment_activity_nr\": \"false\"\n    },\n    \"filters\": {\n        \n        \n    },\n    \"limit\": \"100\",\n    \"offset\": \"0\"\n}"

    payload_dict = json.loads(data)
    payload_dict['filters']['date_time_from'] = date_time_from
    payload_dict['filters']['date_time_to'] = date_time_to

    headers = {
      'token': token
    }

    response = requests.request("PUT", url, headers=headers, json=payload_dict)
    respons_dict = json.loads(response.text)

    #Handle pagination
    for i in range(math.ceil(int(respons_dict["count_filtered"])/100)):
        payload_dict['offset'] = i*100
        response = requests.request("PUT", url, headers=headers, json=payload_dict)
        items += json.loads(response.text)["items"]

    return items, response.status_code


def get_activity(barcode, token):
    """Get the activity data by submitting the barcode.
    Returns a dict with all the key-value pairs for that activity"""

    url = "https://br8.freightlive.eu/api/v2/activity"


    payload = data = "{\n    \"options\": {\n        \"include_activity_status\": \"true\",\n        \"include_status_name\": \"true\",\n        \"include_activity_type_name\": \"true\",\n        \"include_activity_meta_data\": \"false\",\n        \"include_meta_data\": \"false\",\n        \"include_address_applied\": \"true\",\n        \"include_address\": \"true\",\n        \"include_address_object\": \"false\",\n        \"include_allowed_driver_ids\": \"false\",\n        \"include_allowed_drivers\": \"false\",\n        \"include_allowed_drivers_links\": \"false\",\n        \"include_time_slots\": \"false\",\n        \"include_time_slot_tags\": \"false\",\n        \"include_route_info\": \"false\",\n        \"include_route\": \"false\",\n        \"include_package_lines\": \"true\",\n        \"include_package_line_links\": \"false\",\n        \"include_package_lines_info\": \"false\",\n        \"include_driver_info\": \"false\",\n        \"include_driver\": \"false\",\n        \"include_driver_links\": \"false\",\n        \"include_car\": \"false\",\n        \"include_vehicle\": \"false\",\n        \"include_communication\": \"true\",\n        \"include_communication_object\": \"false\",\n        \"include_compartment_ids\": \"false\",\n        \"include_compartments\": \"false\",\n        \"include_links\": \"false\",\n        \"include_activity_links\": \"false\",\n        \"include_files\": \"false\",\n        \"include_activity_files_meta_data\": \"true\",\n        \"include_assignment_nr\": \"true\",\n        \"include_assignment\": \"true\",\n        \"include_activity_tags\": \"true\",\n        \"include_tag_type_name\": \"true\",\n        \"include_record_info\": \"false\",\n        \"include_record_object\": \"false\",\n        \"include_notes\": \"true\",\n        \"include_activity_notes\": \"true\",\n        \"include_activity_note_tags\": \"false\",\n        \"include_depot_address\": \"false\",\n        \"include_depot_address_object\": \"false\",\n        \"include_capacity_object\": \"false\",\n        \"include_capacities\": \"false\",\n        \"include_filled_capacities\": \"false\",\n        \"include_applied_capacities\": \"false\",\n        \"include_zones\": \"true\",\n        \"include_brand\": \"false\",\n        \"include_brand_name\": \"false\",\n        \"include_brand_colours\": \"false\",\n        \"include_brand_files\": \"false\",\n        \"apply_address_bundling\": \"false\",\n        \"include_bundled_activity_ids\": \"false\",\n        \"include_activity_files\": \"false\",\n        \"include_activity_record_info\": \"false\",\n        \"include_activity_record_object\": \"false\",\n        \"include_party_name\": \"false\",\n        \"include_shipment_activity_nr\": \"true\"\n    },\n    \"filters\": {\n        \"search_text\": \"P2020-4488\"\n    },\n    \"limit\": \"1\"\n}"

    """
    payload = data = "{\n    \"options\": {\n        \"include_activity_status\": \"true\",\n        \"include_status_name\": \"true\",\n        \"include_activity_type_name\": \"true\",\n        \"include_activity_meta_data\": \"false\",\n        \"include_meta_data\": \"false\",\n        \"include_address_applied\": \"true\",\n        \"include_address\": \"true\",\n        \"include_address_object\": \"false\",\n        \"include_allowed_driver_ids\": \"false\",\n        \"include_allowed_drivers\": \"false\",\n        \"include_allowed_drivers_links\": \"true\",\n        \"include_time_slots\": \"true\",\n        \"include_time_slot_tags\": \"true\",\n        \"include_route_info\": \"true\",\n        \"include_route\": \"true\",\n        \"include_package_lines\": \"true\",\n        \"include_package_line_links\": \"true\",\n        \"include_package_lines_info\": \"true\",\n        \"include_driver_info\": \"false\",\n        \"include_driver\": \"false\",\n        \"include_driver_links\": \"false\",\n        \"include_car\": \"false\",\n        \"include_vehicle\": \"false\",\n        \"include_trailer\": \"false\",\n        \"include_communication\": \"true\",\n        \"include_communication_object\": \"true\",\n        \"include_compartment_ids\": \"true\",\n        \"include_compartments\": \"true\",\n        \"include_links\": \"false\",\n        \"include_activity_links\": \"false\",\n        \"include_files\": \"false\",\n        \"include_activity_files_meta_data\": \"false\",\n        \"include_assignment_nr\": \"true\",\n        \"include_assignment\": \"true\",\n        \"include_activity_tags\": \"true\",\n        \"include_tag_type_name\": \"true\",\n        \"include_record_info\": \"true\",\n        \"include_record_object\": \"true\",\n        \"include_notes\": \"true\",\n        \"include_activity_notes\": \"true\",\n        \"include_activity_note_tags\": \"true\",\n        \"include_depot_address\": \"false\",\n        \"include_depot_address_object\": \"false\",\n        \"include_capacity_object\": \"false\",\n        \"include_capacities\": \"false\",\n        \"include_filled_capacities\": \"false\",\n        \"include_applied_capacities\": \"false\",\n        \"include_zones\": \"true\",\n        \"include_brand\": \"true\",\n        \"include_brand_name\": \"true\",\n        \"include_brand_colours\": \"true\",\n        \"include_brand_files\": \"true\",\n        \"apply_address_bundling\": \"true\",\n        \"include_bundled_activity_ids\": \"true\",\n        \"include_activity_files\": \"false\",\n        \"include_activity_record_info\": \"true\",\n        \"include_activity_record_object\": \"true\",\n        \"include_party_name\": \"true\",\n        \"include_shipment_activity_nr\": \"true\"\n    },\n    \"filters\": {\n        \n        \"search_text\": \"ACT0292875\"\n        \n    },\n    \"limit\": \"5\"\n    \n}"


    payload_data = data = "{\n    \"options\": {\n        \"include_activity_status\": \"true\",\n        \"include_status_name\": \"true\",\n        \"include_activity_type_name\": \"true\",\n        \"include_activity_meta_data\": \"true\",\n        \"include_meta_data\": \"true\",\n        \"include_address_applied\": \"true\",\n        \"include_address\": \"true\",\n        \"include_address_object\": \"true\",\n        \"include_allowed_driver_ids\": \"true\",\n        \"include_allowed_drivers\": \"true\",\n        \"include_allowed_drivers_links\": \"true\",\n        \"include_time_slots\": \"true\",\n        \"include_time_slot_tags\": \"true\",\n        \"include_route_info\": \"true\",\n        \"include_route\": \"true\",\n        \"include_package_lines\": \"true\",\n        \"include_package_line_links\": \"true\",\n        \"include_package_lines_info\": \"true\",\n        \"include_driver_info\": \"true\",\n        \"include_driver\": \"true\",\n        \"include_driver_links\": \"true\",\n        \"include_car\": \"true\",\n        \"include_vehicle\": \"true\",\n        \"include_trailer\": \"false\",\n        \"include_communication\": \"true\",\n        \"include_communication_object\": \"true\",\n        \"include_compartment_ids\": \"true\",\n        \"include_compartments\": \"true\",\n        \"include_links\": \"true\",\n        \"include_activity_links\": \"true\",\n        \"include_files\": \"true\",\n        \"include_activity_files_meta_data\": \"true\",\n        \"include_assignment_nr\": \"true\",\n        \"include_assignment\": \"true\",\n        \"include_activity_tags\": \"true\",\n        \"include_tag_type_name\": \"true\",\n        \"include_record_info\": \"true\",\n        \"include_record_object\": \"true\",\n        \"include_notes\": \"true\",\n        \"include_activity_notes\": \"true\",\n        \"include_activity_note_tags\": \"true\",\n        \"include_depot_address\": \"true\",\n        \"include_depot_address_object\": \"true\",\n        \"include_capacity_object\": \"true\",\n        \"include_capacities\": \"true\",\n        \"include_filled_capacities\": \"true\",\n        \"include_applied_capacities\": \"true\",\n        \"include_zones\": \"true\",\n        \"include_brand\": \"true\",\n        \"include_brand_name\": \"true\",\n        \"include_brand_colours\": \"true\",\n        \"include_brand_files\": \"true\",\n        \"apply_address_bundling\": \"true\",\n        \"include_bundled_activity_ids\": \"true\",\n        \"include_activity_files\": \"true\",\n        \"include_activity_record_info\": \"true\",\n        \"include_activity_record_object\": \"true\",\n        \"include_party_name\": \"true\",\n        \"include_shipment_activity_nr\": \"true\"\n    },\n    \"filters\": {\n        \n        \"search_text\": \"ACT0292875\"\n        \n    },\n    \"limit\": \"5\"\n    \n}"
    """
    payload_dict = json.loads(data)
    payload_dict['filters']['search_text'] = trim_input(barcode)
    #print(payload_dict)
    headers = {
      'token': token
    }

    response = requests.request("PUT", url, headers=headers, json=payload_dict)
    respons_dict = json.loads(response.text)
    # print(respons_dict)

    return respons_dict, response.status_code

def get_nextday_activity(barcode, token):
    """Pulls a request for a activity that is scheduled on the next day (monday on saturday).
     This function is used in the docker route and narrows down needed database query to just
     the activities that are scheduled for the next working day"""

    def serialize_datetime(o):
        """Serializes datetime input"""
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

    route_day = 0 #0 is dummy variable
    #Check which day of the week it is 0 is monday 6 is sunday
    today = datetime.datetime.today().weekday()
    #Add 1 to the current date to get as input to get the activities scheduled for the next day
    #serialize it as input for request
    if today <= 4 or today == 6:
         route_day_start = serialize_datetime(datetime.datetime.combine(datetime.datetime.today(), datetime.time(00, 00, 00, 000)) + datetime.timedelta(days=1))
         route_day_end = serialize_datetime(datetime.datetime.combine(datetime.datetime.today(), datetime.time(23, 59, 59, 999)) + datetime.timedelta(days=1))
    else:
         route_day_start = serialize_datetime(datetime.datetime.combine(datetime.datetime.today(), datetime.time(00, 00, 00, 000)) + datetime.timedelta(days=2))
         route_day_end = serialize_datetime(datetime.datetime.combine(datetime.datetime.today(), datetime.time(23, 59, 59, 999)) + datetime.timedelta(days=2))

    url = "https://br8.freightlive.eu/api/v2/activity"

    payload = data = "{\n    \"options\": {\n        \"include_activity_status\": \"true\",\n        \"include_status_name\": \"true\",\n        \"include_activity_type_name\": \"true\",\n        \"include_activity_meta_data\": \"true\",\n        \"include_meta_data\": \"true\",\n        \"include_address_applied\": \"true\",\n        \"include_address\": \"true\",\n        \"include_address_object\": \"true\",\n        \"include_allowed_driver_ids\": \"true\",\n        \"include_allowed_drivers\": \"true\",\n        \"include_allowed_drivers_links\": \"true\",\n        \"include_time_slots\": \"true\",\n        \"include_time_slot_tags\": \"true\",\n        \"include_route_info\": \"true\",\n        \"include_route\": \"true\",\n        \"include_package_lines\": \"true\",\n        \"include_package_line_links\": \"true\",\n        \"include_package_lines_info\": \"true\",\n        \"include_driver_info\": \"true\",\n        \"include_driver\": \"true\",\n        \"include_driver_links\": \"true\",\n        \"include_car\": \"true\",\n        \"include_vehicle\": \"true\",\n        \"include_communication\": \"true\",\n        \"include_communication_object\": \"true\",\n        \"include_compartment_ids\": \"true\",\n        \"include_compartments\": \"true\",\n        \"include_links\": \"true\",\n        \"include_activity_links\": \"true\",\n        \"include_files\": \"true\",\n        \"include_activity_files_meta_data\": \"true\",\n        \"include_assignment_nr\": \"true\",\n        \"include_assignment\": \"true\",\n        \"include_activity_tags\": \"true\",\n        \"include_tag_type_name\": \"true\",\n        \"include_record_info\": \"true\",\n        \"include_record_object\": \"true\",\n        \"include_notes\": \"true\",\n        \"include_activity_notes\": \"true\",\n        \"include_activity_note_tags\": \"true\",\n        \"include_depot_address\": \"true\",\n        \"include_depot_address_object\": \"true\",\n        \"include_capacity_object\": \"true\",\n        \"include_capacities\": \"true\",\n        \"include_filled_capacities\": \"true\",\n        \"include_applied_capacities\": \"true\",\n        \"include_zones\": \"true\",\n        \"include_brand\": \"true\",\n        \"include_brand_name\": \"true\",\n        \"include_brand_colours\": \"true\",\n        \"include_brand_files\": \"true\",\n        \"apply_address_bundling\": \"true\",\n        \"include_bundled_activity_ids\": \"true\",\n        \"include_activity_files\": \"true\",\n        \"include_activity_record_info\": \"true\",\n        \"include_activity_record_object\": \"true\",\n        \"include_party_name\": \"true\",\n        \"include_shipment_activity_nr\": \"true\"\n    },\n    \"filters\": {\n        \"search_text\": \"P2020-4488\",\n        \n        \"date_time_from\": \"2020-12-08T00:00:00\",\n        \"date_time_to\": \"2020-12-09T23:59:59\"\n    },\n    \"limit\": \"100\"\n}"

    payload_dict = json.loads(data)
    payload_dict['filters']['search_text'] = trim_input(barcode)
    payload_dict['filters']['date_time_from'] = route_day_start
    payload_dict['filters']['date_time_to'] = route_day_end

    #print(payload_dict)
    headers = {
      'token': token
    }

    response = requests.request("PUT", url, headers=headers, json=payload_dict)
    respons_dict = json.loads(response.text)
    # print(respons_dict)

    return respons_dict, response.status_code

def update_activity(activity_id, update_dict, token):
    """Update an activity by using the updated key-value pairs
    of the response of the request for activity data"""

    url = "https://br8.freightlive.eu/api/v2/activity/{}".format(activity_id)
    headers = {'token': token}
    response = requests.request("PUT", url, headers=headers, json=update_dict)

    return response.status_code

def check_token(token):
    """Check whether the token is still valid"""
    url = "https://br8.freightlive.eu/api/v2/authenticate/check-token"
    headers = {
      'token': token
    }
    response = requests.request("GET", url, headers=headers).status_code
    return response

def get_route_data(start, stop, offset, token):
    url = "https://br8.freightlive.eu/api/v2/route"

    payload= data ="{\n    \"options\": {\n        \"include_address\": \"true\",\n        \"include_address_object\": \"true\",\n        \"include_route_status\": \"true\",\n        \"include_route_tags\": \"true\",\n        \"include_tag_names\": \"true\",\n        \"include_driver\": \"true\",\n        \"include_driver_links\": \"true\",\n        \"include_car\": \"true\",\n        \"include_car_links\": \"true\",\n        \"include_vehicle\": \"true\",\n        \"include_vehicle_links\": \"true\",\n        \"include_trailer\": \"true\",\n        \"include_trailer_links\": \"true\",\n        \"include_driver_info\": \"true\",\n        \"include_equipment_info_car\": \"true\",\n        \"include_equipment\": \"true\",\n        \"include_gps_locations\": \"true\",\n        \"include_pause\": \"true\",\n        \"include_activity_ids\": \"true\",\n        \"include_latest_position\": \"true\",\n        \"include_zones\": \"true\",\n        \"include_zone_names\": \"true\",\n        \"include_notes\": \"true\"\n    },\n    \"filters\": {\n        \n        \"date_time_from\": \"2020-10-18T00:00:00.000Z\",\n        \"date_time_to\": \"2020-10-18T23:59:59.999Z\"\n        \n    },\n    \"limit\": \"1000\",\n    \"as_list\": \"true\"\n}"

    payload_dict = json.loads(data)
    payload_dict['filters']['date_time_from'] = start
    payload_dict['filters']['date_time_to'] = stop
    payload_dict['offset'] = offset

    headers = {
      'token': token
      }

    response = requests.request("PUT", url, headers=headers, json=payload_dict)
    respons_dict = json.loads(response.text)

    return respons_dict, response.status_code



def servicelevel(package_lines, tag_identifier, servicelevels):
    """Inputs:
        list = list of the package lines in the form of dictionaries from the request response
        tag_identifier = the key name for the tags in the request response
        servicelevels = possible sercive levels
        Output = the servicelevel.
    """
    if len(package_lines) > 0:
        tag_list = [i[tag_identifier] for i in package_lines]
        for i in servicelevels:
            if i in tag_list:
                return i
    else:
        return 'Geen servicelevel aangegeven'

def get_fulfillment_customer(token, id):
    url = "https://br8.picqer.com/api/v1/fulfilment/customers/{}".format(id)

    payload={}
    headers = {
      'Authorization': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response_dict = json.loads(response.text)

    if response.status_code == 200:
        return response_dict, response.status_code
    else:
        pass
