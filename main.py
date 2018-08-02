"""
GTAA N7K Excel Configuration Tool

"""

import xlrd
from xlrd.sheet import ctype_text
from constants import *
from controllers.nexus7k import n7kcontroller

"""Setting Excel File"""
fname = "script_template.xlsx"

"""Setting Device URLs"""
T1_111 = n7kcontroller(server_url=NX_URL)
T1_112 = n7kcontroller(server_url=NX_URL)
T3_105 = n7kcontroller(server_url=NX_URL)
T3_106 = n7kcontroller(server_url=NX_URL)
ADM_109 = n7kcontroller(server_url=NX_URL)
ADM_110 = n7kcontroller(server_url=NX_URL)
IFT_107 = n7kcontroller(server_url=NX_URL)
IFT_108 = n7kcontroller(server_url=NX_URL)

if __name__ == "__main__":

    xl_workbook = xlrd.open_workbook(fname)


    # Pull the first row by index
    #  (rows/columns are also zero-indexed)
    #
    xl_sheet = xl_workbook.sheet_by_index(0)
    row = xl_sheet.row(0)  # 1st row

    # Print 1st row values and types
    #

    xl_col_title = []
    print('(Column #) type:value')
    for idx, cell_obj in enumerate(row):
        cell_type_str = ctype_text.get(cell_obj.ctype, 'unknown type')
        print('(%s) %s %s' % (idx, cell_type_str, cell_obj.value))
        xl_col_title.append(cell_obj.value)

    print(xl_col_title)

    # Print all values, iterating through rows and columns

    num_cols = xl_sheet.ncols  # Number of columns
    bgp_num = []
    result = {}
    col_key = ""

    for col_idx in range(0, num_cols):
        for row_idx in range(0, xl_sheet.nrows):
            cell_obj = xl_sheet.cell(row_idx, col_idx)

            if row_idx == 0:
                # headers
                col_key = cell_obj.value
                result[col_key] = []
            else:
                # values
                result[col_key].append(cell_obj.value)



    print(str(result))


    for row_idx in range(1, xl_sheet.nrows):  # Iterate through rows
        print('-' * 40)
        print('Row: %s' % row_idx)  # Print row number
        server = {'T1': 0, 'T3': 0, 'ADM': 0, 'IFT': 0}
        for col_idx in range(0, num_cols):  # Iterate through columns

            cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
            if cell_obj.value == "": continue # Skip empty cells
            print('Column: [%s] cell_obj: [%s]' % (col_idx, cell_obj.value))

            if xl_col_title[col_idx] == "Execute":
                if cell_obj.value == "No": break
            elif xl_col_title[col_idx] == "VRF-Name":
                vrf_name = cell_obj.value
            elif xl_col_title[col_idx] == "VRF-Desc":
                vrf_description = cell_obj.value
            elif xl_col_title[col_idx] == "RD":
                bgp_RD = cell_obj.value
                bgp_num = bgp_RD.split(':')[0]
            elif xl_col_title[col_idx] == "RT-Both":
                bgp_RT = cell_obj.value
            elif xl_col_title[col_idx] == "Vlan-ID":
                vlan_ID = int(cell_obj.value)
            elif xl_col_title[col_idx] == "Vlan-Name":
                vlan_name = cell_obj.value
            elif xl_col_title[col_idx] == "L3-SVI-Desc":
                l3_svi_description = cell_obj.value
            elif xl_col_title[col_idx] == "HSRP-Group":
                hsrp_group = int(cell_obj.value)
    #T1 Dist
            elif xl_col_title[col_idx] == "T1-111-SVI-IP":
                n7k1_svi_ip = cell_obj.value
                server['T1'] = 1
            elif xl_col_title[col_idx] == "T1-112-SVI-IP":
                n7k2_svi_ip = cell_obj.value
            elif xl_col_title[col_idx] == "T1-SVI-VIP":
                n7k_svi_vip = cell_obj.value
            elif xl_col_title[col_idx] == "T1-STP-Root":
                T1_111.createvrfname(vrf_name)
                T1_111.createvrfdescription(vrf_name, vrf_description)
                T1_111.createvrfrd(vrf_name, bgp_RD)
                T1_111.createvrfrt(vrf_name, bgp_RT)
                T1_112.createvrfname(vrf_name)
                T1_112.createvrfdescription(vrf_name, vrf_description)
                T1_112.createvrfrd(vrf_name, bgp_RD)
                T1_112.createvrfrt(vrf_name, bgp_RT)
                n7k_stp_root = int(cell_obj.value)
                if n7k_stp_root == 111:
                    T1_111.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    T1_111.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    T1_112.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    T1_112.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
                else:
                    T1_112.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    T1_112.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    T1_111.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    T1_111.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
            elif xl_col_title[col_idx] == "T1-BGP-Default":
                T1_111.createbgp(bgp_num, vrf_name, cell_obj.value)
                T1_112.createbgp(bgp_num, vrf_name, cell_obj.value)
            elif xl_col_title[col_idx] == "T1-Static-Routes":
                for static in cell_obj.value.splitlines():
                    T1_111.createstaticroute(static)
                    T1_112.createstaticroute(static)
    #T3 Dist
            elif xl_col_title[col_idx] == "T3-105-SVI-IP":
                n7k1_svi_ip = cell_obj.value
                server['T3'] = 1
            elif xl_col_title[col_idx] == "T3-106-SVI-IP":
                n7k2_svi_ip = cell_obj.value
            elif xl_col_title[col_idx] == "T3-SVI-VIP":
                n7k_svi_vip = cell_obj.value
            elif xl_col_title[col_idx] == "T3-STP-Root":
                T3_105.createvrfname(vrf_name)
                T3_105.createvrfdescription(vrf_name, vrf_description)
                T3_105.createvrfrd(vrf_name, bgp_RD)
                T3_105.createvrfrt(vrf_name, bgp_RT)
                T3_106.createvrfname(vrf_name)
                T3_106.createvrfdescription(vrf_name, vrf_description)
                T3_106.createvrfrd(vrf_name, bgp_RD)
                T3_106.createvrfrt(vrf_name, bgp_RT)
                n7k_stp_root = int(cell_obj.value)
                if n7k_stp_root == 105:
                    T3_105.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    T3_105.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    T3_106.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    T3_106.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
                else:
                    T3_106.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    T3_106.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    T3_105.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    T3_105.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
            elif xl_col_title[col_idx] == "T3-BGP-Default":
                T3_105.createbgp(bgp_num, vrf_name, cell_obj.value)
                T3_106.createbgp(bgp_num, vrf_name, cell_obj.value)
            elif xl_col_title[col_idx] == "T3-Static-Routes":
                for static in cell_obj.value.splitlines():
                    T3_105.createstaticroute(static)
                    T3_106.createstaticroute(static)
    #ADM Dist
            elif xl_col_title[col_idx] == "ADM-109-SVI-IP":
                n7k1_svi_ip = cell_obj.value
                server['ADM'] = 1
            elif xl_col_title[col_idx] == "ADM-110-SVI-IP":
                n7k2_svi_ip = cell_obj.value
            elif xl_col_title[col_idx] == "ADM-SVI-VIP":
                n7k_svi_vip = cell_obj.value
            elif xl_col_title[col_idx] == "ADM-STP-Root":
                ADM_109.createvrfname(vrf_name)
                ADM_109.createvrfdescription(vrf_name, vrf_description)
                ADM_109.createvrfrd(vrf_name, bgp_RD)
                ADM_109.createvrfrt(vrf_name, bgp_RT)
                ADM_110.createvrfname(vrf_name)
                ADM_110.createvrfdescription(vrf_name, vrf_description)
                ADM_110.createvrfrd(vrf_name, bgp_RD)
                ADM_110.createvrfrt(vrf_name, bgp_RT)
                n7k_stp_root = int(cell_obj.value)
                if n7k_stp_root == 109:
                    ADM_109.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    ADM_109.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    ADM_110.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    ADM_110.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
                else:
                    ADM_110.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    ADM_110.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    ADM_109.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    ADM_109.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
            elif xl_col_title[col_idx] == "ADM-BGP-Default":
                ADM_109.createbgp(bgp_num, vrf_name, cell_obj.value)
                ADM_110.createbgp(bgp_num, vrf_name, cell_obj.value)
            elif xl_col_title[col_idx] == "ADM-Static-Routes":
                for static in cell_obj.value.splitlines():
                    ADM_109.createstaticroute(static)
                    ADM_110.createstaticroute(static)
    #IFT Dist
            elif xl_col_title[col_idx] == "IFT-107-SVI-IP":
                n7k1_svi_ip = cell_obj.value
                server['IFT'] = 1
            elif xl_col_title[col_idx] == "IFT-108-SVI-IP":
                n7k2_svi_ip = cell_obj.value
            elif xl_col_title[col_idx] == "IFT-SVI-VIP":
                n7k_svi_vip = cell_obj.value
            elif xl_col_title[col_idx] == "IFT-STP-Root":
                IFT_107.createvrfname(vrf_name)
                IFT_107.createvrfdescription(vrf_name, vrf_description)
                IFT_107.createvrfrd(vrf_name, bgp_RD)
                IFT_107.createvrfrt(vrf_name, bgp_RT)
                IFT_108.createvrfname(vrf_name)
                IFT_108.createvrfdescription(vrf_name, vrf_description)
                IFT_108.createvrfrd(vrf_name, bgp_RD)
                IFT_108.createvrfrt(vrf_name, bgp_RT)
                n7k_stp_root = int(cell_obj.value)
                if n7k_stp_root == 107:
                    IFT_107.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    IFT_107.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    IFT_108.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    IFT_108.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
                else:
                    IFT_108.createvlaninterface(vlan_ID, vlan_name, stppriority="8192")
                    IFT_108.createl3svi(vlan_ID, vlan_name, vrf_name, n7k2_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="100")
                    IFT_107.createvlaninterface(vlan_ID, vlan_name, stppriority="16384")
                    IFT_107.createl3svi(vlan_ID, vlan_name, vrf_name, n7k1_svi_ip, hsrp_group, n7k_svi_vip, hsrppriority="90")
            elif xl_col_title[col_idx] == "IFT-BGP-Default":
                IFT_107.createbgp(bgp_num, vrf_name, cell_obj.value)
                IFT_108.createbgp(bgp_num, vrf_name, cell_obj.value)
            elif xl_col_title[col_idx] == "IFT-Static-Routes":
                for static in cell_obj.value.splitlines():
                    IFT_107.createstaticroute(static)
                    IFT_108.createstaticroute(static)

    #Grey
            elif xl_col_title[col_idx] == "GREY":
                if cell_obj.value == "Yes":
                    prefix_list = vrf_name + "_GREY_PFL"
                    for value in server:
                        if value == "T1" and server[value] == 1:
                            T1_111.createroutemap(vrf_name, prefix_list)
                            T1_112.createroutemap(vrf_name, prefix_list)
                            T1_111.addroutetarget(vrf_name)
                            T1_111.createipprefix(vrf_name, prefix_list)
                            T1_112.addroutetarget(vrf_name)
                            T1_112.createipprefix(vrf_name, prefix_list)
                        elif value == "T3" and server[value] == 1:
                            T3_105.createroutemap(vrf_name, prefix_list)
                            T3_106.createroutemap(vrf_name, prefix_list)
                            T3_105.addroutetarget(vrf_name)
                            T3_105.createipprefix(vrf_name, prefix_list)
                            T3_106.addroutetarget(vrf_name)
                            T3_106.createipprefix(vrf_name, prefix_list)
                        elif value == "ADM" and server[value] == 1:
                            ADM_109.createroutemap(vrf_name, prefix_list)
                            ADM_110.createroutemap(vrf_name, prefix_list)
                            ADM_109.addroutetarget(vrf_name)
                            ADM_109.createipprefix(vrf_name, prefix_list)
                            ADM_110.addroutetarget(vrf_name)
                            ADM_110.createipprefix(vrf_name, prefix_list)
                        elif value == "IFT" and server[value] == 1:
                            IFT_107.createroutemap(vrf_name, prefix_list)
                            IFT_108.createroutemap(vrf_name, prefix_list)
                            IFT_107.addroutetarget(vrf_name)
                            IFT_107.createipprefix(vrf_name, prefix_list)
                            IFT_108.addroutetarget(vrf_name)
                            IFT_108.createipprefix(vrf_name, prefix_list)

