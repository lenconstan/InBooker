import requests
import json

def login(email, password):
    """Log in with user credentials. Retrieves a 'token' needed for other requests"""

    url = 'https://br8.freightlive.eu/api/v2/authenticate/sign-in'
    response = requests.post(url, json={"email": email, "password": password})
    token = response.json()["token"]

    return token

def get_activity(barcode, token):
    """Get the activity data by submitting the barcode.
    Returns a dict with all the key-value pairs for that activity"""

    def trim_input(string):
        "Trims the barcode input for barcode input"
        if len(string) > 4:
            if string[-2] == '-':
                newstring = string[:-2]
                string = newstring
                if 'XLS' or 'BR8' in string and len(string) > 9:
                    string = string[:3] + '00' + string[3:]
            elif string[-3] == '-':
                newstring = string[:-3]
                string = newstring
                if 'XLS' or 'BR8' in string and len(string) > 9:
                    string = string[:3] + '00' + string[3:]
            else:
                pass

        return string

    url = "https://br8.freightlive.eu/api/v2/activity"

    payload = data = "{\n    \"options\": {\n        \"include_activity_status\": \"true\",\n        \"include_status_name\": \"true\",\n        \"include_activity_type_name\": \"true\",\n        \"include_activity_meta_data\": \"false\",\n        \"include_meta_data\": \"false\",\n        \"include_address_applied\": \"true\",\n        \"include_address\": \"true\",\n        \"include_address_object\": \"false\",\n        \"include_allowed_driver_ids\": \"false\",\n        \"include_allowed_drivers\": \"false\",\n        \"include_allowed_drivers_links\": \"true\",\n        \"include_time_slots\": \"true\",\n        \"include_time_slot_tags\": \"true\",\n        \"include_route_info\": \"true\",\n        \"include_route\": \"true\",\n        \"include_package_lines\": \"true\",\n        \"include_package_line_links\": \"true\",\n        \"include_package_lines_info\": \"true\",\n        \"include_driver_info\": \"false\",\n        \"include_driver\": \"false\",\n        \"include_driver_links\": \"false\",\n        \"include_car\": \"false\",\n        \"include_vehicle\": \"false\",\n        \"include_trailer\": \"false\",\n        \"include_communication\": \"true\",\n        \"include_communication_object\": \"true\",\n        \"include_compartment_ids\": \"true\",\n        \"include_compartments\": \"true\",\n        \"include_links\": \"false\",\n        \"include_activity_links\": \"false\",\n        \"include_files\": \"false\",\n        \"include_activity_files_meta_data\": \"false\",\n        \"include_assignment_nr\": \"true\",\n        \"include_assignment\": \"true\",\n        \"include_activity_tags\": \"true\",\n        \"include_tag_type_name\": \"true\",\n        \"include_record_info\": \"true\",\n        \"include_record_object\": \"true\",\n        \"include_notes\": \"true\",\n        \"include_activity_notes\": \"true\",\n        \"include_activity_note_tags\": \"true\",\n        \"include_depot_address\": \"false\",\n        \"include_depot_address_object\": \"false\",\n        \"include_capacity_object\": \"false\",\n        \"include_capacities\": \"false\",\n        \"include_filled_capacities\": \"false\",\n        \"include_applied_capacities\": \"false\",\n        \"include_zones\": \"true\",\n        \"include_brand\": \"true\",\n        \"include_brand_name\": \"true\",\n        \"include_brand_colours\": \"true\",\n        \"include_brand_files\": \"true\",\n        \"apply_address_bundling\": \"true\",\n        \"include_bundled_activity_ids\": \"true\",\n        \"include_activity_files\": \"false\",\n        \"include_activity_record_info\": \"true\",\n        \"include_activity_record_object\": \"true\",\n        \"include_party_name\": \"true\",\n        \"include_shipment_activity_nr\": \"true\"\n    },\n    \"filters\": {\n        \n        \"search_text\": \"ACT0292875\"\n        \n    },\n    \"limit\": \"5\"\n    \n}"

    """
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
    print(respons_dict)

    return respons_dict, response.status_code

def update_activity(activity_id, update_dict, token):
    """Update an activity by using the updated key-value pairs
    of the response of the request for activity data"""

    url = "https://br8.freightlive.eu/api/v2/activity/{}".format(activity_id)
    headers = {'token': token}
    response = requests.request("PUT", url, headers=headers, json=update_dict)

    return response.status_code
