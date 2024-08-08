import pandas as pd
import requests
from xml.etree import ElementTree as ET
import xml.dom.minidom

import os

default_institution_code = "TRN"


def get_rosetta_data(
    endpoint: str, institution_code=default_institution_code, payload={}
):

    user = os.environ.get("ROSETTA_USER")
    password = os.environ.get("ROSETTA_PASSWORD")

    rest_url = f"https://rostestapp1.slv.vic.gov.au:8443/rest/v0/{endpoint}"

    response = requests.get(
        rest_url,
        auth=(f"{user}-institutionCode-{institution_code}", password),
        params=payload,
    )

    if response.status_code != 200:
        print(
            f"Couldn't retrieve data from Rosetta. Here's the status code returned {response.status_code}"
        )
        return False

    return response.content


def post_rosetta_data(
    endpoint: str, institution_code=default_institution_code, data={}
):

    user = os.environ.get("ROSETTA_USER")
    password = os.environ.get("ROSETTA_PASSWORD")

    rest_url = f"https://rostestapp1.slv.vic.gov.au:8443/rest/v0/{endpoint}"

    response = requests.post(
        rest_url,
        auth=(f"{user}-institutionCode-{institution_code}", password),
        params=data,
    )

    if response.status_code != 200:
        print(
            f"Couldn't retrieve data from Rosetta. Here's the status code returned {response.status_code}"
        )
        return False

    return response.content


def get_sips(
    institution_code=default_institution_code,
    stage="Deposit,Loading,Validation,Assessor,Arranger,Approver,Bytestream,Enrichment,ToPermanent,Finished,SystemErrors",
    status="REJECTED, DECLINED, INPROCESS, FINISHED, DELETED, ERROR, IN_HUMAN_STAGE",
    expand="iePids,numberOfIEs",
):

    payload = {
        "stage": stage,
        "status": status,
        "expand": expand,
    }

    sips_data = get_rosetta_data(
        "sips", institution_code=institution_code, payload=payload
    )

    if not sips_data:
        return False

    # print(xml.dom.minidom.parseString(sips_data).toprettyxml())

    return sips_data


def get_sip(
    sip_id: str, institution_code=default_institution_code, expand="iePids,numberOfIEs"
):

    payload = {"expand": expand}

    sip_data = get_rosetta_data(
        f"sips/{sip_id}", institution_code=institution_code, payload=payload
    )

    if not sip_data:

        return False

    return sip_data


def parse_sip_xml(tree: ET.Element) -> list:

    parsed_sips = {
        "sip_ids": [sip_id.text for sip_id in tree.iter("id")],
        "stages": [stage.text for stage in tree.iter("stage")],
        "statuses": [status.text for status in tree.iter("status")],
        "ie_counts": [ie_count.text for ie_count in tree.iter("numberOfIEs")],
        "ie_pids": [ie_pid.text for ie_pid in tree.iter("iePids")],
        "external_id": [ie_pid.text for ie_pid in tree.iter("externalId")],
        "external_system": [ie_pid.text for ie_pid in tree.iter("externalSystem")],
    }

    return parsed_sips


# sips = get_sips()

# tree = ET.fromstring(sips)

# parsed_tree = parse_sip_xml(tree)
# print(parsed_tree)
# record_count = int(tree.attrib.get("total_record_count"))
# print(record_count)


def export_ie(ie_pid: str):

    data = {"op": "export", "export_path": f"{ie_pid}_export"}

    ie_pid_endpoint = f"ies/{ie_pid}"

    data = post_rosetta_data(ie_pid_endpoint, data=data)

    return data


# example_ie_pid = "IE228302"
# export_ie(example_ie_pid)


def parse_xml(tree: ET.Element, xml_field_names: list) -> pd.DataFrame:

    parsed_xml = {
        field: [
            node.find(field).text if node.find(field) != None else "N/A"
            for node in tree
        ]
        for field in xml_field_names
    }

    df = pd.DataFrame(parsed_xml, columns=xml_field_names)

    return df


def get_users(limit=100):

    payload = {"limit": limit, "expand": "roles"}

    users = get_rosetta_data("users", payload=payload)
    print(users)

    tree = ET.fromstring(users)

    parsed_users = parse_xml(
        tree,
        [
            "id",
            "user_name",
            "record_type",
            "active",
            "job_title",
            "account_type",
            "shared",
        ],
    )

    return parsed_users


def get_user_roles(user_id: str):

    roles = get_rosetta_data(f"users/{user_id}/roles")

    tree = ET.fromstring(roles)

    role_description = [node.find("description").text for node in tree]

    return role_description


# users = get_users()
# users["roles"] = users["id"].apply(lambda x: get_user_roles(x))
# print(users)
# users.to_csv("rosetta-users.csv")
