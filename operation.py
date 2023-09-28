import time
import re
import utils

class UpdateConsoleAndServer():
    def __init__(self):
        self.obj_yaml = utils.Yaml()
        self.yaml_info = self.obj_yaml.yaml_read()
        self.obj_ssh = utils.SSHconn(host=self.yaml_info['node_info']['ip']
                                     ,password=self.yaml_info['node_info']['password'])

    # def set_linstor_csi(self):
    #     print("应用linstor CSI......")
    #     self.obj_yaml.csi_yaml(self.yaml_info["LINSTOR Controller IP"])
    #     utils.exec_cmd('kubectl apply -f linstor.yaml',self.obj_ssh)
    #     time.sleep(5)

    def change_linstorip(self):
        print("获取ksapi.yaml......")
        utils.exec_cmd("kubectl get deployment.apps/ks-apiserver -n kubesphere-system -o yaml > ksapi.yaml",self.obj_ssh)
        print("更改ksapi.yaml......")
        utils.exec_cmd("sed -i '96 a \        - mountPath: /etc/linstorip' ksapi.yaml",self.obj_ssh)
        utils.exec_cmd("sed -i '97 a \          name: linstorip' ksapi.yaml",self.obj_ssh)
        utils.exec_cmd("sed -i '119 a \      - configMap:' ksapi.yaml",self.obj_ssh)
        utils.exec_cmd("sed -i '120 a \          defaultMode: 420' ksapi.yaml",self.obj_ssh)
        utils.exec_cmd("sed -i '121 a \          name: linstorip' ksapi.yaml",self.obj_ssh)
        utils.exec_cmd("sed -i '122 a \        name: linstorip' ksapi.yaml",self.obj_ssh)
        print("应用ksapi.yaml......")
        utils.exec_cmd("kubectl apply -f ksapi.yaml",self.obj_ssh)
        time.sleep(5)
        print("清理文件，删除ksapi.yaml")
        utils.exec_cmd("rm ksapi.yaml",self.obj_ssh)
        time.sleep(5)

    def change_image(self):
        print("更改image镜像......")
        change_server_cmd = f'kubectl set image deployment ks-apiserver ks-apiserver={self.yaml_info["images"]["server"]} -n kubesphere-system'
        change_console_cmd = f'kubectl set image deployment ks-console ks-console={self.yaml_info["images"]["console"]} -n kubesphere-system'
        utils.exec_cmd(change_server_cmd,self.obj_ssh)
        time.sleep(5)
        utils.exec_cmd(change_console_cmd,self.obj_ssh)
        time.sleep(5)

    def change_configmap(self):
        print("创建configmap")
        change_configmap_cmd = f'kubectl create configmap linstorip -n kubesphere-system --from-literal=user=admin --from-literal=linstorip={self.yaml_info["node_info"]["ip"]}:3370'
        utils.exec_cmd(change_configmap_cmd,self.obj_ssh)
        time.sleep(5)

    def wait_for_pods(self):
        get_pods_info_cmd = f"kubectl get pod -n kubesphere-system"

        a = False
        while a is False:
            print("等待pod启动......")
            time.sleep(10)
            result1 = utils.exec_cmd(get_pods_info_cmd, self.obj_ssh)
            test1 = re.findall(r'(ks-)', result1)
            test2 = re.findall(r'(Running)', result1)
            if len(test1) == len(test2):
                print("相关pod启动成功")
                break

    def main(self):
        # self.set_linstor_csi()
        self.change_linstorip()
        self.change_image()
        self.change_configmap()
        self.wait_for_pods()

class UpdateArmImage:
    def __init__(self):
        self.obj_yaml = utils.Yaml()
        self.yaml_info = self.obj_yaml.yaml_read()
        self.obj_ssh = utils.SSHconn(host=self.yaml_info['node_info']['ip']
                                     ,password=self.yaml_info['node_info']['password'])
        self.list_init_image = ["mirrorgooglecontainers/defaultbackend-amd64:1.4"
                                ,"kubesphere/elasticsearch-oss:6.8.22"
                                ,"kubesphere/elasticsearch-curator:v5.7.6"
                                ,"kubesphere/log-sidecar-injector:1.1"]
        self.list_arm_image = ["mirrorgooglecontainers/defaultbackend-arm64:1.4"
                                ,"kubesphere/elasticsearch-oss:6.7.0-1-arm64"
                                ,"kubespheredev/elasticsearch-curator:v5.7.6-arm64"
                                ,"kubespheredev/log-sidecar-injector:1.1.1"]
        self.list_feixitek_image = ["feixitek/defaultbackend-arm64:1.4"
                                ,"feixitek/elasticsearch-oss:6.8.22"
                                ,"feixitek/elasticsearch-curator:v5.7.6"
                                ,"feixitek/log-sidecar-injector:1.1"]

    def check_loacl_arm_image(self):
        cmd = "docker images"
        info_image = utils.exec_cmd(cmd,self.obj_ssh)

        list_alive_arm_image = {}
        list_absent_arm_image = {}
        for i,j in zip(self.list_arm_image,range(len(self.list_arm_image))):
            flag = re.findall(r'(%s)'%i,info_image)
            if not flag == []:
                list_alive_arm_image[flag[0]] = j  #键值对：image名称：在list中的排列顺序号
            else:
                list_absent_arm_image[i] = j

        if not list_alive_arm_image == {}:  #返回1：本地有的arm image，返回2：本地不存在的arm image
            return list_alive_arm_image,list_absent_arm_image

    def arm_tag_replace(self,list_alive_arm_image):
        for i, j in zip(list_alive_arm_image, list_alive_arm_image.values()):
            cmd1 = f"docker tag {self.list_init_image[j]} {i}"
            cmd2 = f"docker rmi {self.list_init_image[j]}"
            utils.exec_cmd(cmd1,self.obj_ssh)
            utils.exec_cmd(cmd2,self.obj_ssh)

    def check_feixitek_image(self,list_absent_arm_image):
        cmd = "docker images"
        info_image = utils.exec_cmd(cmd,self.obj_ssh)

        list_alive_feixitek_image = {}
        list_absent_feixitek_image = {}
        for i,j in zip(list_absent_arm_image,range(len(list_absent_arm_image))):
            flag = re.findall(r'(%s)'%i,info_image)
            if not flag == []:
                list_alive_feixitek_image[flag[0]] = j  #键值对：image名称：在list中的排列顺序号
            else:
                list_absent_feixitek_image[i] = j

        return list_alive_feixitek_image,list_absent_feixitek_image

    def feixitek_tag_replace(self,list_alive_feixitek_image):
        for i, j in zip(list_alive_feixitek_image, list_alive_feixitek_image.values()):
            cmd1 = f"docker tag {self.list_init_image[j]} {i}"
            cmd2 = f"docker rmi {self.list_init_image[j]}"
            utils.exec_cmd(cmd1,self.obj_ssh)
            utils.exec_cmd(cmd2,self.obj_ssh)

    def pull_image(self,list_absent_arm_image):
        for i in list_absent_arm_image:
            cmd = f"docker pull {i}"
            utils.exec_cmd(cmd,self.obj_ssh)

    def main_un_pull(self):
        flag_arm_list = self.check_loacl_arm_image()
        self.arm_tag_replace(flag_arm_list[0])
        flag_feixitek_list = self.check_feixitek_image(flag_arm_list[1])
        self.feixitek_tag_replace(flag_feixitek_list[0])
        list_absent_image = flag_feixitek_list[1]

        for i,j in zip(list_absent_image,list_absent_image.values()):
            print(f"{self.list_init_image[j]}未被{self.list_arm_image[j]}或{i}替换")

    def main_pull(self):
        flag_arm_list = self.check_loacl_arm_image()
        self.arm_tag_replace(flag_arm_list[0])
        flag_feixitek_list = self.check_feixitek_image(flag_arm_list[1])
        self.feixitek_tag_replace(flag_feixitek_list[0])
        self.pull_image(flag_arm_list[1])

if __name__ == "__main__":
    pass