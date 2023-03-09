import time
import re
import utils

class UpdateConsoleAndServer():
    def __init__(self):
        self.obj_yaml = utils.Yaml()
        self.yaml_info = self.obj_yaml.yaml_read()
        self.obj_ssh = utils.SSHconn(host=self.yaml_info['node_info']['ip']
                                     ,password=self.yaml_info['node_info']['password'])

    def set_linstor_csi(self):
        print("应用linstor CSI......")
        self.obj_yaml.csi_yaml(self.yaml_info["LINSTOR Controller IP"])
        utils.exec_cmd('kubectl apply -f linstor.yaml',self.obj_ssh)
        time.sleep(5)

    def change_linstorip(self):
        print("获取ksapi.yaml......")
        utils.exec_cmd("kubectl get deployment.apps/ks-apiserver -n kubesphere-system -o yaml > ksapi.yaml",self.obj_ssh)
        # utils.exec_cmd("sudo chmod -R 777 /root")
        time.sleep(5)
        print("更改ksapi.yaml......")
        self.obj_yaml.linstorip_yaml()
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
        utils.exec_cmd(change_configmap_cmd)
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

if __name__ == "__main__":
    pass