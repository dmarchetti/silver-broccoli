#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
This script has tje objetive to migrate LVM in virtual machine, maybe it could be used for physical machines.

If you have want to collaborate this project is published on GitHub
https://github.com/dmarchetti/silver-broccoli

Danilo Marchetti Chaves
dmarchetti@gmail.com
"""

import subprocess, os, re, time, shlex, sys

def subprocess_cmd(command):
	p = subprocess.Popen(command,stdout=subprocess.PIPE)
	p.communicate()
	print proc_stdout
	#print proc_stderr

args = shlex.split('ls -l')
subprocess_cmd(args)

"""
def confirm_exec(prompt='do you want to proceed? ', retries=3, complaint='yes or no, please!'):
	while True:
		ok = raw_input(prompt)
		if ok in ('y','yes'):
			return True
		if ok in ('n','no'):
			sys.exit()
		retries = retries - 1
		if retries < 0:
			raise IOError('refusenik user')
		print complaint

# MAKE A FILTER TO EXCLUDE SYSTEM PARTITIONS (SYS/PROC/TMPFS) AND LVM PARTITIONS INCLUDING ALL RAW PARTITIONS FOR MIGRATION
def check_fs():

	file_name = 'fsdump001.tmp'
	lst_mpoints = list()

	p = os.popen('mount')
	while 1:
		line = p.readline()
		if not line: break
		line = line.rstrip()
		if re.search('/boot',line): continue
		if not re.search('^/',line): continue
		if re.findall('^/dev/mapper.+', line):continue
		mpoints = line.split()
		lst_mpoints.append(mpoints[2])

	tmp_file = open(file_name, 'wb')

	for i in lst_mpoints:
		ltmp2 = '%s: O ponto de montagem %s foi adicionado ao arquivo temporario para migracao.'%(timestr,i)
		lst_logs.append(ltmp2)
		line = "%s\n" %i
		tmp_file.write(line);

	tmp_file.close()

	return file_name
	return lst_logs

#GENERATE LOGS
def create_logs():
	for line in lst_logs:
		time.sleep(1)
		print line

#GET SIZING FOR SELECTED PARTITIONS
def get_sizing(filename):
	lst_size = dict()
	for i in filename:
		args = shlex.split('df %s'%i)
		subprocess_cmd(args)
		#out, err = subprocess.Popen( args, stdout=subprocess.PIPE ).communicate()
		#out = out.split()
		print proc_stdout
		#lst_size[out[12]] = out[8]

	return lst_size.items()

#---------------------------------------------INICIO EXECUCAO------------------------------------------------------

print
Before you begin its important to do the steps bellow, don't continue if you not ready!\n

1. Make a backup of your data and make sure that the restore is working! If it is a VM, you can simple clone!
2. Present new disk to OS
3. Create new partition with fdisk and run partprobe

\n
***********************
!!! ATENTION PLEASE !!!
***********************
\n\n
THIS SCRIPT WILL MIGRATE RAW PARTITIONS TO LVM PARTIONS THIS OPERATIONS CAN CAUSE DATA LOSS! MAKE SURE IF YOUR BACKUP IS OK!\n


confirm_exec()

#GET TIMESTAMP
timestr = time.strftime('%Y%m%d-%H%M%S')

#DECLARE VARIABLES
lst_logs = list()

#GET GENERAL INFORMATION
fdev = "None"
vgname = "None"
while len(fdev) < 9 or len(vgname) < 3 or len(mpname) < 4:
	print "\n***INFORME OS DADOS ABAIXO OU DIGITE exit PARA SAIR***\n"
	fdev = raw_input("Insira o disco disponível para migração: ")
	vgname = raw_input("Insira um nome para o volume group: ")
	mpname = raw_input("Insira o ponto de montagem para a particao ROOT: ")
	if len(fdev) < 1: fdev = '/dev/sdd1'
	if len(vgname) < 1: vgname = 'vg00'
	if len(mpname) < 1: mpname = '/mnt/root'
	time.sleep(2)
	if fdev == "exit":
		break

time.sleep(2)

_fhandle = open(check_fs())
_sizing = get_sizing(_fhandle)

print "\n*** PREPARANDO DISCO E CRIANDO VOLUMES GROUP ***\n"

time.sleep(1)

out, err = subprocess.Popen(['vgscan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
lst_logs.append(out)
lst_logs.append(err)

args_pvc = shlex.split('pvcreate %s'%fdev)
out, err = subprocess.Popen(args_pvc, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
lst_logs.append(out)
lst_logs.append(err)

args_vgc = shlex.split('vgcreate %s %s'%(vgname,fdev))
out, err = subprocess.Popen(args_vgc, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
lst_logs.append(out)
lst_logs.append(err)

print "*** CRIANDO LOGICAL VOLUMES ***\n"

time.sleep(1)

mount_buffer = list()
for k, v in _sizing:
	if re.search('^/$',k):
		print 'lvcreate -L %s lv_root %s '%(v,vgname)
		print 'mkfs.ext3 /dev/%s/lv_root' %(vgname)
		print 'mkdir -p %s' %(mpname)
		print 'mount /dev/%s/lv_root %s' %(vgname,mpname)
		print 'find / -xdev | cpio -pvmd %s' %(mpname)
		continue

	lvname = re.findall('[a-z0-9]+$',k)[0]
	print 'lvcreate -L %s lv_%s %s' %(v,lvname,vgname)
	print 'mkfs.ext3 /dev/%s/lv_%s' %(vgname,lvname)
"""

#print 'mount /dev/%s/lv_%s %s%s' %(vgname,lvname,mpname,k)
