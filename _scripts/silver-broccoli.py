#-*- coding: utf-8 -*-

"""
This script has the objetive to migrate basic disks to LVM in a virtual machine, maybe it could be used for physical machines.

If you want to collaborate visit our project, it's published at https://github.com/dmarchetti/silver-broccoli

Created by: dmarchetti - dmarchetti@gmail.com
"""

import subprocess, os, re, time, shlex, sys, logging

# VARIABLES
file_name = 'fsdump001.tmp' #this file will contain all selected basic disks
timestr = time.strftime('%d/%m/%Y %H:%M:%S') #generate timestamp
logging.basicConfig(filename='output-silver-broccoli.log',filemode='w',level=logging.DEBUG)

#EXECUTE OPERATIONAL SYSTEM COMMANDS
def subprocess_cmd(command):
	process  = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	procout, procerr = process.communicate()
	errcode = process.returncode
	if errcode == 0:
		logging.info('%s:%s', timestr,procout.rstrip())
		return errcode, procout
	else:
		logging.error('%s:%s', timestr,procerr.rstrip())
		raise IOError(errcode, procerr)

#CHECK IF USER WANT TO PROCEED
def confirm_exec(prompt, retries, complaint):
	while True:
		ok = raw_input(prompt).lower()
		if ok in ('y','yes'):
			logging.info('You\'ve selected [%s] to continue', ok)
			return True
		if ok in ('n','no'):
			sys.exit()
		retries = retries - 1
		if retries < 0:
			raise IOError('refusenik user')
		print complaint

#GET INFO FROM USER
def ask_info(prompt, retries, complaint, answer):
	while True:
		user_input = raw_input(prompt).lower()
		if re.search(answer, user_input):
			logging.info('user input was [%s]', user_input)
			return user_input
		retries = retries - 1
		if retries < 0:
			raise IOError('refusenik user')
		print complaint

# MAKE A FILTER TO EXCLUDE SYSTEM PARTITIONS (SYS/PROC/TMPFS) AND LVM PARTITIONS INCLUDING ALL RAW PARTITIONS FOR MIGRATION
def check_fs(filename):
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
	tmp_file = open(filename, 'wb')
	for i in lst_mpoints:
		line = "%s\n" %i
		tmp_file.write(line);
	tmp_file.close()
	return file_name

#GET SIZING FOR SELECTED PARTITIONS
def get_sizing(filename):
	lst_size = dict()
	for i in filename:
		args = shlex.split('df -h %s'%i)
		out = subprocess_cmd(args)
		for line in out:
			if out[0] == 0:
				line = out[1].split()
				lst_size[line[12]] = line[8]
	return lst_size.items()

#RUN BASH COMMANDS TO CREATE FILESYSTEM
def create_fs(fsystem,vgname,mountpoint,lvname):
	lst_commands = ['lvcreate -L %s -n lv_%s %s --yes' %(size, lvname, vgname),'mkfs.ext3 /dev/%s/lv_%s' %(vgname, lvname),'mount /dev/%s/lv_%s %s' %(vgname, lvname, mountpoint)]
	for i in lst_commands:
		logging.info('%s:RUNNING %s',timestr,i)
		args = shlex.split(i)
		subprocess_cmd(args)
		time.sleep(1)
		find_and_copy(fsystem, mountpoint, lvname)

#EXECUTE FIND AND CPIO USING PIPE
def find_and_copy(fsystem, mountpoint, lvname):
	logging.info('FINDING THINGS TO COPY.')
	fileName = '.sb-dump-%s.tmp' %(lvname)
	with open(fileName, "w+") as f:
		args = shlex.split('find %s -xdev' %(fsystem))
		pFind  = subprocess.Popen(args, stdout=f, stderr=subprocess.PIPE)
		procout, procerr = pFind.communicate()
		logging.info('%s:%s:%s', timestr,args,procout)
		errcode = pFind.returncode
		f.seek(0)
		if errcode == 0:
			logging.info('COPYING THINGS TO TEMPORARY FOLDER...')
			args = shlex.split('cpio -pvmd %s' %(mountpoint))
			pCPIO = subprocess.Popen(args, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			procout, procerr = pCPIO.communicate()
			logging.info('%s:%s:%s',timestr,args,procout)
			errcode = pCPIO.returncode
			if errcode == 0:
				logging.info('%s:SUCCESS',timestr)
			else:
				logging.warning('%s:CHECK LOGS',timestr)
				raise IOError(errcode, procerr)
		else:
			logging.error('%s:%s:%s', timestr,args,procerr.rstrip())
			raise IOError(errcode, procerr)
	f.close()

# EXECUTE OS COMMAND WIHT SHELL=TRUE ENABLED, THIS IS USING A INSECURE OPTION FOR SHELL COMMAND, DON'T USE THIS AS WEB APP
def subprocess_cmd_SH(command):
	process  = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	procout, procerr = process.communicate()
	errcode = process.returncode
	logging.info('%s:%s',timestr,procerr)
	if errcode == 0:
		logging.info('%s:SUCCESS',timestr)
		return errcode, procout
	else:
		logging.warning('%s:CHECK LOGS',timestr)
		raise IOError(errcode, procerr)
	
def create_initrd():
	logging.info('EXECUTING BASH SCRIPT.')
	p1  = subprocess.Popen('/create-initrd.sh', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	procout, procerr = p1.communicate()
	logging.info('%s:%s:%s', timestr,args,procout)
	errcode = p1.returncode
	if errcode == 0:
		logging.info('SUCCESS')
	else:
		logging.error('%s:%s:%s', timestr,args,procerr.rstrip())
		#return errcode, procerr
		raise IOError(errcode, procerr)
#---------------------------------------------BEGIN EXECUTION------------------------------------------------------

print """
Before you continue it's important to do the steps bellow, don't continue if you not ready!\n

1. Make a backup of your data and make sure that the restore is working! If it's a VM, you can simple clone it!
2. Present new disk to OS
3. Create new partition with fdisk and run partprobe
4. Check in grub.conf what initrd is currently working

\n
***********************
!!! ATENTION PLEASE !!!
***********************
\n\n
THIS SCRIPT WILL MIGRATE RAW PARTITIONS TO LVM PARTIONS THIS OPERATIONS CAN CAUSE DATA LOSS! MAKE SURE IF YOUR BACKUP IS OK!\n
"""

logging.info('Started')

confirm_exec(prompt='do you want to proceed? ', retries=3, complaint='yes or no, please!')

#GET GENERAL INFORMATION
fdev = ask_info(prompt='what device will receive the data? ', retries=3, complaint='enter a valid device (ex: /dev/sdo1!', answer='^/dev.+')
vgname = ask_info(prompt='what name do you want to user for volume group? ', retries=3, complaint='enter a valid name (ex: vg[whateveryouwant]', answer='^vg.+')
initrd = ask_info(prompt='what is the currently initrd? ', retries=3, complaint='enter a valid initrd name (ex: /boot/initrd-kernelversio.img)', answer='^/boot/initrd.+')

"""
_fhandle = open(check_fs(file_name))

lst_commands = ['vgscan','pvcreate %s'%fdev,'vgcreate %s %s'%(vgname,fdev),'mkdir -v -p /mnt/tmpFs']
for i in lst_commands:
	args = shlex.split(i)
	subprocess_cmd(args)

#for fsystem, size in get_sizing(_fhandle):
#	if re.search('^/$', fsystem):
#		create_fs(fsystem,vgname,mountpoint='/mnt/tmpFs',lvname='root')

_fhandle.seek(0)

for fsystem, size in get_sizing(_fhandle):
	if re.search('^/$', fsystem): continue
	lvname = re.findall('[a-z0-9]+$', fsystem)[0]
	#mountpoint = '/mnt/tmpFs/root/%s' %(lvname)
	mountpoint = '/mnt/tmpFs'
	create_fs(fsystem, vgname, mountpoint, lvname)

_fhandle.close()
"""

logging.info('%s:SETTING CURRENT KERNEL VERSION',timestr)
kernelversion = subprocess_cmd(shlex.split('uname -r'))
kernelversion = kernelversion[1].rstrip()

lst_commands = ['mkdir -vp /tmp/kill/00','ln -vs %s /boot/initrd-%s.img'%(initrd,kernelversion)]
for i in lst_commands:
	logging.info('%s:%s',timestr,i)
	args = shlex.split(i)
	subprocess_cmd(args)

command = 'cd /tmp/kill/00 && gunzip < %s | cpio -vid'%(initrd)
logging.info('%s:%s',timestr,command)
subprocess_cmd_SH(command)

args =  shlex.split('ls /tmp/kill/01/bin/lvm')
process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
procout, procerr = process.communicate()
logging.info('%s:%s:%s',timestr,args,procout)
errcode = process.returncode

if errcode == 0:
	logging.info('%s:SUCCESS:LVM BIN WAS FOUND.',timestr)
	print 'vi /mnt/root/fstab'
	print 'vi /boot/grub.conf'
else:
	logging.info('%s:ERROR:LVM BIN WAS NOT FOUND, RUNNING COMMANDS TO CREATE.',timestr)
	#create_initrd()	
	
	command = 'chroot /mnt/tmpFs && mount -t proc /proc /proc && mount -t sysfs /sys /sys && mount -B /dev /dev && vgmknodes -v && mkinitrd -v /boot/initrd-%s-lvm.img %s ; exit'%(kernelversion,kernelversion)
	subprocess_cmd_SH(command)
	#print 'chroot /mnt'
	#print 'mount -t proc /proc /proc'
	#print 'mount -t sysfs /sys /sys'
	#print 'mount -bind /dev'
	#print 'vgmknodes -v'
	#print 'mkinitrd -v /boot/initrd-$(uname -r)-lvm.img uname -r'
	#exit
	print 'vi /mnt/root/fstab'
	print 'vi /boot/grub.conf'



print """*** PARA FINALIZAR A ATIVIDADE EFETUE AS AÇÕES ABAIXO ***
1. Reinicie a máquina e valida se a atividade foi concluída com sucesso
2. Reinstalar VMtools
3. Remover serviços e módulos desnecessários
4. Remover disco sem uso após validação do usuário
"""
logging.info('Finished')
