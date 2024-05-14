import requests
from xml.etree import ElementTree as ET
import xml.dom.minidom

import os

default_institution_code = "INS002"


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


def get_sips(
    institution_code=default_institution_code,
    stage="Deposit,Loading,Validation,Assessor,Arranger,Approver,Bytestream,Enrichment,ToPermanent,Finished,SystemErrors",
    status="ALL",
    # status="REJECTED, DECLINED, INPROCESS, FINISHED, DELETED, ERROR, IN_HUMAN_STAGE",
    offset=0,
    limit=100,
    expand="iePids,numberOfIEs",
):

    payload = {
        "limit": limit,
        "stage": stage,
        "status": status,
        "offset": offset,
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


limit = 100
sips = get_sips(limit=limit)

tree = ET.fromstring(sips)

parsed_tree = parse_sip_xml(tree)
print(parsed_tree)
record_count = int(tree.attrib.get("total_record_count"))
print(record_count)
