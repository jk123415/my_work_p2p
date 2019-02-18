import re
from w3lib.html import remove_tags


limited_reason = '''限制原因</td><td align="left" style="height:22px;">法院冻结</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制时间</td><td align="left" style="height:22px;">自2018-03-26至2021-03-25</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制状态</td><td align="left" style="height:22px;">限制中</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制说明</td><td align="left" style="height:22px;">轮候：（2018）粤0304执1632、1677号之二冻结（轮候）罗永标持有的100%的股权，三年。（2018-7173）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">备注</td><td align="left" style="height:22px;">轮候：（2018）粤0304执1632、1677号之二冻结（轮候）罗永标持有的100%的股权，三年。（2018-7173）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制原因</td><td align="left" style="height:22px;">法院冻结</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制时间</td><td align="left" style="height:22px;">自2018-10-16至2021-10-15</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制状态</td><td align="left" style="height:22px;">限制中</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制说明</td><td align="left" style="height:22px;">轮候：（2017）粤0304执17719号之一冻结（轮候）罗永标持有的100%的股权，三年。（2018-23397）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">备注</td><td align="left" style="height:22px;">轮候：（2017）粤0304执17719号之一冻结（轮候）罗永标持有的100%的股权，三年。（2018-23397）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制原因</td><td align="left" style="height:22px;">法院冻结</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制时间</td><td align="left" style="height:22px;">自2017-12-07至2020-12-06</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制状态</td><td align="left" style="height:22px;">限制中</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制说明</td><td align="left" style="height:22px;">查封：（2017）粤0304执25375号冻结罗永标所持100%的股权，三年。（其中35.86%为轮候冻结）（2017-13715）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">备注</td><td align="left" style="height:22px;">查封：（2017）粤0304执25375号冻结罗永标所持100%的股权，三年。（其中35.86%为轮候冻结）（2017-13715）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制原因</td><td align="left" style="height:22px;">法院冻结</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制时间</td><td align="left" style="height:22px;">自2015-08-28至2020-08-14</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制状态</td><td align="left" style="height:22px;">限制中</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制说明</td><td align="left" style="height:22px;">（2015）深福法民一初字第5945号冻结罗永标持有的35.86%的股权，两年。（2015-4979）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">备注</td><td align="left" style="height:22px;">续冻：（2015）深福法民一初字第5945号冻结罗永标持有的35.86%的股权。（2015-4979）（２０１７－７３０２）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制原因</td><td align="left" style="height:22px;">法院冻结</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制时间</td><td align="left" style="height:22px;">自2018-03-15至2021-03-14</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制状态</td><td align="left" style="height:22px;">限制中</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">限制说明</td><td align="left" style="height:22px;">轮候：（2017）粤0304执17716号之一冻结（轮候）罗永标持有的100%的股权，三年。（2018-2536）</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">备注</td><td align="left" style="height:22px;">轮候：（2017）粤0304执17716号之一冻结（轮候）罗永标持有的100%的股权，三年。（2018-2536）</td>
            </tr>
        </table>'''

tar_str = ""
regex_exp_str = "限制原因([\s\S]*?)限制时间([\s\S]*?)限制状态([\s\S]*?)限制说明([\s\S]*?)备注</td>([\s\S]*?)</td>"
template_str = "限制原因：{arr[0]}|限制时间：{arr[1]}|限制状态:{arr[2]}|限制说明:{arr[3]}|备注:{arr[4]}|"

owing_tax = """纳税人名称</td><td align="left" style="height:22px;">深圳市宝宝贷互联网金融服务有限公司</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">纳税人识别号</td><td align="left" style="height:22px;">440300319619948</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">征收项目代码</td><td align="left" style="height:22px;">10101</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">欠税余额</td><td align="left" style="height:22px;">40411.79</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">当前新发生的欠税额</td><td align="left" style="height:22px;">40411.79</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">税款所属机关</td><td align="left" style="height:22px;">14403510800</td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">应征发生日期</td><td align="left" style="height:22px;"> </td>
            </tr><tr>
                <td align="right" style="background-color:#f9f9f9;width:180px;">缴款期限</td><td align="left" style="height:22px;"> </td>
            </tr>
        </table>"""
owing_tax_regex_exp_str = '纳税人名称([\s\S]*?)纳税人识别号([\s\S]*?)征收项目代码([\s\S]*?)欠税余额([\s\S]*?)当前新发生的欠税额([\s\S]*?)税款所属机关([\s\S]*?)应征发生日期([\s\S]*?)缴款期限([\s\S]*?)</tr>'
owing_tax_template_str = "纳税人名称:{arr[0]}|纳税人识别号:{arr[1]}|征收项目代码:{arr[2]}|欠税余额:{arr[3]}|当前新发生的欠税额:{arr[4]}|税款所属机关:{arr[5]}|应征发生日期:{arr[6]}|"


def regex_loop_match(tar_str, regex_exp_str, template_str):
    if tar_str:
        result = ""
        regex_exp = re.compile(regex_exp_str)
        lst = regex_exp.findall(tar_str)
        for tup in lst:
            temporary_a = template_str.format(arr=tup)
            temporary_b = remove_tags(temporary_a)
            temporary_c = re.subn("[\t\r\n\s]", "", temporary_b)
            result = result+ temporary_c[0]
        return result

'''
if limited_reason:
    limited_reason_result = ""
    express = re.compile('限制原因([\s\S]*?)限制时间([\s\S]*?)限制状态([\s\S]*?)限制说明([\s\S]*?)备注</td>([\s\S]*?)</td>')
    lim_list = express.findall(limited_reason)
    if lim_list:
        for arr in lim_list:
            modern = "限制原因：{arr[0]}|限制时间：{arr[1]}|限制状态:{arr[2]}|限制说明:{arr[3]}|备注:{arr[4]}|"
            lim_result = modern.format(arr=arr)
            limited_reason_result = limited_reason_result + remove_tags(lim_result)
        print(re.subn('[\t\r\n\s]',"",limited_reason_result)[0])
'''
sss = regex_loop_match(limited_reason,regex_exp_str,template_str)
aaa = regex_loop_match(owing_tax,owing_tax_regex_exp_str,owing_tax_template_str)
print(aaa)