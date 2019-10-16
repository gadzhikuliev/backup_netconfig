import collections
import os
import datetime
from netmiko import ConnectHandler

# Пусть к домашнему каталогу, IP-адрес TFTP-сервера, путь к конфигурационному файлу TFTP-сервера
HOME_LINK = '/home/tftp/'
TFTP_IP = '172.31.4.13'
TFTP_CONFIG = '/etc/default/tftpd-hpa'

# IP-адреса устройств, с которых собираем конфигурационные файлы
DEVICES_IP = ['172.31.0.20', '172.31.0.21','172.31.0.22', '172.31.0.23', '172.31.0.24', '172.31.0.25', '172.31.0.64', '172.31.0.67', '172.31.0.76', '172.31.0.77',
'172.31.0.42', '172.31.0.43', '172.31.0.44', '172.31.0.45', '172.31.0.46', '172.31.0.47', '172.31.0.48', '172.31.0.49', '172.31.0.50', '172.31.0.90']

CORE_IP = ['172.31.0.1', '172.31.0.9', '172.31.0.10', '172.31.0.11', '172.31.0.12', '172.31.0.13', '172.31.0.15', '172.31.0.18', '172.31.0.40']

# Каталог по умолчанию для TFTP
folder = str(datetime.date.today())
path = '"' + HOME_LINK + folder + '"'

# Редактирование конфигурационного файла TFTP-сервера с учётом изменения каталога по умолчанию. Каталог именуется по текущей дате
def edit():
    str1 = 'TFTP_USERNAME="tftp"'
    str2 = 'TFTP_ADDRESS="0.0.0.0:69"'
    str3 = 'TFTP_OPTIONS="--secure --create"'

    with open(TFTP_CONFIG) as cfg:
        for line in cfg:
            if line.startswith('TFTP_DIRECTORY'):
                break
    sett = line.split('=')[1].strip()
    line = line.replace(sett,path)

    with open(TFTP_CONFIG, 'w') as cfg:
        cfg.write(str1)
        cfg.write('\n' + str2)
        cfg.write('\n' + str3)
        cfg.write('\n' + line)


# Здесь создаётся папка, куда складываются конфиги, и перезапускается служба TFTP
def tftp_start():
    os.mkdir(HOME_LINK + folder)
    os.system('chown tftp:tftp ' + HOME_LINK + folder)
    os.system('chmod 766 ' + HOME_LINK + folder)
    os.system('systemctl restart tftpd-hpa')

# Копирование конфигурационных файлов с сетевых устройств, используем библиотеку netmiko
def copy_config():
    for IP in DEVICES_IP:
        DEVICES_PARAMS = { 
            'device_type' : 'hp_procurve',
            'ip'          : IP,
            'username'    : 'admin',
            'password'    : 'password' }
        connect = ConnectHandler(**DEVICES_PARAMS)
        connect.send_command('copy running-config tftp ' + TFTP_IP + ' conf-' + str(IP))

    for IP in CORE_IP:
        DEVICES_PARAMS = { 
            'device_type' : 'hp_procurve',
            'ip'          : IP,
            'username'    : 'admin',
            'password'    : 'password',
            'global_delay_factor' : 2 }
        connect = ConnectHandler(**DEVICES_PARAMS)
        connect.send_command('copy running-config tftp ' + TFTP_IP + ' conf-' + str(IP)) 

def main():
    edit()
    tftp_start()
    copy_config()

if __name__ == '__main__':
    main()