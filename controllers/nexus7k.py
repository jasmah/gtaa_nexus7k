from jinja2 import Environment
from jinja2 import FileSystemLoader
from constants import *
import requests
import json
import base64
import os

DIR_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
JSON_TEMPLATES = Environment(loader=FileSystemLoader(DIR_PATH + '/json_templates'))
os.environ['NO_PROXY'] = '10.10.100.111,10.10.100.112,10.10.200.105,10.10.200.106,10.10.200.109,10.10.200.110,10.10.200.107,10.10.200.108'

class n7kcontroller:
    def __init__(self, server_url):
        self.server_url = server_url

    def configure_nexus(self, p_url, method, data=""):
        """ Sending REST call to N7K
        :param p_url:
        :param method:
        :param data:
        :return:
        """
        credentials = base64.encodebytes(bytes(NX_USER + ":" + NX_PASSWORD, "utf-8")).decode("utf-8")

        headers = {
            'Authorization': "Basic " + credentials[:len(credentials) - 1],  # Remove the escape character at the end
            "Content-Type": "application/json"
            # "Accept": "application/json"
        }
        if method == "POST":
            response = requests.post(self.server_url + p_url, data=data, headers=headers, verify=False)
            #print(self.server_url)
            #print(data)

        elif method == "GET":
            response = requests.get(self.server_url + p_url, headers=headers, verify=False)

        else:
            raise Exception("Method " + method + " not supported by this controller")
        if 199 > response.status_code > 300:
            errorMessage = json.loads(response.text)["errorDocument"]["message"]
            raise Exception("Error: status code" + str(response.status_code) + " - " + errorMessage)

            for status_code in response.json()["ins_api"]["outputs"]["output"]:
                if status_code['code'] == "400":
                    print(response.json())
                    raise Exception("Error: status code :" + status_code['code'] + " Msg: " + status_code['msg'] +
                               " CLI : " + status_code['input'] + " Server :" + self.server_url)

        return response


    def createvrfname(self, vrfname):
        """
        Create VRF context name
        :param vrfname:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_vrf_name.j2.json')
        payload = template.render(vrfname=vrfname)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")


    def createvrfdescription(self, vrfname, vrfdescription):
        """
        Create VRF context description
        :param vrfname:
        :param vrfdescription:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_vrf_description.j2.json')
        payload = template.render(vrfname=vrfname, vrfdescription=vrfdescription)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")

    def createvrfrd(self, vrfname, bgprd):
        """
        Create VRF BGP RD label
        :param vrfname:
        :param bgprd:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_vrf_bgprd.j2.json')
        payload = template.render(vrfname=vrfname, bgprd=bgprd)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")

    def createvrfrt(self, vrfname, bgprt):
        """
        Create VRF BGP RT both import and export
        :param vrfname:
        :param bgprt:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_vrf_bgprt.j2.json')
        payload = template.render(vrfname=vrfname, bgprt=bgprt)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")

    def createvlaninterface(self, vlanid, vlanname, stppriority):
        """
        Create Vlan interface, description and set priority
        :param vlanid:
        :param vlanname:
        :param stppriority:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_vlan_int.j2.json')
        payload = template.render(vlanid=vlanid, vlanname=vlanname, stppriority=stppriority)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")


    def createl3svi(self, vlanid, vlanname, vrfname, sviip, hsrpgroup, svivip, hsrppriority):
        """
        Create L3 SVI interface with vlan, vrf name and HSRP and priority
        :param vlanid:
        :param vlanname:
        :param vrfname:
        :param sviip:
        :param hsrpgroup:
        :param svivip:
        :param hsrppriority:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_vlan_svi_int.j2.json')
        payload = template.render(vlanid=vlanid, vlanname=vlanname, vrfname=vrfname, sviip=sviip, hsrpgroup=hsrpgroup,
                                  svivip=svivip, hsrppriority=hsrppriority)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")


    def createbgp(self, bgpnum, vrfname, bgpdefault):
        """
        Create BGP interface
        :param bgpnum:
        :param vrfname:
        :param bgpdefault:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_bgp.j2.json')
        if bgpdefault == "Yes":
            payload = template.render(bgpnum=bgpnum, vrfname=vrfname, default="default-information originate")
            self.configure_nexus(
                p_url='/ins',
                data=payload,
                method="POST")
        else:
            payload = template.render(bgpnum=bgpnum, vrfname=vrfname, default="")
            self.configure_nexus(
                p_url='/ins',
                data=payload,
                method="POST")


    def createstaticroute(self, static):
        """
        Create static routes
        :param static:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_static_route.j2.json')
        payload = template.render(static=static)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")

    def createroutemap(self, vrfname, prefixlist):
        """
        Create route map
        :param vrfname:
        :param prefixlist:
        :return:
        """
        template = JSON_TEMPLATES.get_template('add_route_map.j2.json')
        routemapname = "GREY_" + vrfname
        payload = template.render(routemapname=routemapname, prefixlist=prefixlist)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")

    def addroutetarget(self, vrfname):

        template = JSON_TEMPLATES.get_template('add_route_target.j2.json')
        routemapname = "GREY_" + vrfname
        payload = template.render(vrfname=vrfname, routemapname=routemapname)
        self.configure_nexus(
            p_url='/ins',
            data=payload,
            method="POST")
