from prettytable import PrettyTable
import subprocess
import yaml
import paramiko
import logging
import logging.handlers
import datetime
import sys
import socket

class SSHconn(object):
    def __init__(self, host, port=22, username="root", password=None, timeout=8):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.timeout = timeout
        self.sshconnection = None
        self.ssh_conn()


    def ssh_conn(self):
        """
        SSH连接
        """
        try:
            conn = paramiko.SSHClient()
            conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            conn.connect(hostname=self._host,
                         username=self._username,
                         port=self._port,
                         password=self._password,
                         timeout=self.timeout,
                         look_for_keys=False,
                         allow_agent=False)
            self.sshconnection = conn
        except paramiko.AuthenticationException:
            print(f" Error SSH connection message of {self._host}")
        except Exception as e:
            print(f" Failed to connect {self._host}")

    def exec_cmd(self, command):
        """
        命令执行
        """
        if self.sshconnection:
            stdin, stdout, stderr = self.sshconnection.exec_command(command)
            result = stdout.read()
            result = result.decode() if isinstance(result, bytes) else result
            if result is not None:
                return {"st": True, "rt": result}

            err = stderr.read()
            if err is not None:
                return {"st": False, "rt": err}

def get_host_ip():
    """
    查询本机ip地址
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def exec_cmd(cmd, conn=None):
    local_obj = LocalProcess()
    if conn:
        result = conn.exec_cmd(cmd)
    else:
        result = local_obj.exec_cmd(cmd)
    result = result.decode() if isinstance(result, bytes) else result
    log_data = f'{get_host_ip()} - {cmd} - {result}'
    Log().logger.info(log_data)
    if result['st']:
        pass
        # f_result = result['rt'].rstrip('\n')
    if result['st'] is False:
        print(f"{cmd} : error")
        sys.exit()
    return result['rt']

class LocalProcess(object):
    def exec_cmd(self,command):
        """
        命令执行
        """
        sub_conn = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if sub_conn.returncode == 0:
            result = sub_conn.stdout
            return {"st": True, "rt": result}
        else:
            print(f"Can't to execute command: {command}")
            err = sub_conn.stderr
            print(f"Error message:{err}")
            return {"st": False, "rt": err}

class Log(object):
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            Log._instance = super().__new__(cls)
            Log._instance.logger = logging.getLogger()
            Log._instance.logger.setLevel(logging.INFO)
            Log.set_handler(Log._instance.logger)
        return Log._instance

    @staticmethod
    def set_handler(logger):
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = str(now_time) + '.log'
        fh = logging.FileHandler(file_name, mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)


class Table(object):
    def __init__(self,field_name):
        self.table = PrettyTable(field_name)

    def add_row(self, list_data):
        self.table.add_row(list_data)

    def print_table(self):
        print(self.table)

class Yaml:
    def __init__(self):
        self.yaml_info = self.yaml_read()

    def yaml_read(self):
        with open('./config.yaml') as f:
            config = yaml.safe_load(f)
        return config

    def csi_yaml(self,linstor_cip):
        list = []
        with open('./linstor.yaml') as f:
            config = yaml.load_all(f.read(),Loader=yaml.FullLoader)
        for i in config:
            list.append(i)
            # if i['kind'] == "DaemonSet":
            #     i['spec']['template']['spec']['containers'][1]['env'][2]['value'] = "http://10.203.1.68:3370"
            # elif i['kind'] == "StatefulSet":
            #     i['spec']['template']['spec']['containers'][4]['env'][2]['value'] = "http://10.203.1.68:3370"

        list[0]['spec']['template']['spec']['containers'][4]['env'][2]['value'] = f"http://{linstor_cip}:3370"
        list[8]['spec']['template']['spec']['containers'][1]['env'][2]['value'] = f"http://{linstor_cip}:3370"
        with open('./linstor.yaml', "w", encoding="utf-8") as f:
            yaml.dump_all(list, f)
        return config

    def linstorip_yaml(self):
        try:
            with open('./ksapi.yaml') as f:
                config = yaml.load(f.read(),Loader=yaml.FullLoader)
        except:
            print("获取ksapi.yaml失败！")
            sys.exit()

        flag1 = False
        for i in config['spec']['template']['spec']['containers'][0]['volumeMounts']:
            if i['name'] == 'linstorip':
                print("linstorip键值对存在1")
                flag1 = True
        if not flag1:
            config['spec']['template']['spec']['containers'][0]['volumeMounts'].append(
                {'mountPath': '/etc/linstorip', 'name': 'linstorip'})

        flag2 = False
        for i in config['spec']['template']['spec']['volumes']:
            if i['name'] == 'linstorip':
                print("linstorip键值对存在2")
                flag2 = True
        if not flag2:
            config['spec']['template']['spec']['volumes'].append(
                {'configMap': {'defaultMode': 420, 'name': 'linstorip'}, 'name': 'linstorip'})

        with open('./ksapi.yaml', "w", encoding="utf-8") as f:
            yaml.dump(config, f)
        return config
