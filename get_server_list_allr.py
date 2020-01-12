#!/usr/bin/env python

from novaclient import client
from keystoneauth1 import loading
from keystoneauth1.identity import v3 as auth_v3
from keystoneauth1 import session
from keystoneauth1.exceptions import EndpointNotFound, HTTPClientError
import write_excel
import re
from time import sleep
import gen_strings as gs

r_names = gs.gen_random_strings(10, 6)
r_fullnames = gs.gen_random_strings(10, 6, True)
regions = []

class Connect:
	region_name = []
	nova = []
	loader = loading.get_plugin_loader('password')
	auth = loader.load_from_options(auth_url='xx',
	                                 username='admin',
	                                 password='xx',
	                                 project_name='admin',
	                                 user_domain_name='Default',
		                             project_domain_name='Default',
	                                 tenant_name='admin')


	def __init__(self, region_name):
		if not(region_name=='xx'):
			sess = session.Session(auth=self.auth)
			self.nova = client.Client(2, session=sess, region_name=region_name)

class Region:
	native = [] #Servers created in cloud
	onboarded = []  #Servers onboarded
	r_name = ''
	def __init__(self, r_name):
		self.r_name = r_name
		self.native = []
		self.onboarded = []

	def cat_servers(self, all_servers_list, pattern):
		for s in all_servers_list:
			if re.search(pattern, str(s.metadata)):
				if not re.search('Onboarded', str(s.name)):
					self.native.append(s.name)
			else:
				self.onboarded.append(s.name)
		self.native.sort()
		self.onboarded.sort()

we = write_excel.WriteExcel()
sum_row = 1
we.insert_title(we.sheet1, 'Export for month ' + str(we.month_day))
we.insert_tab_header(we.sheet1, sum_row)

for rn, frn in zip(r_names, r_fullnames):
	try:
		conn = Connect(rn)
		reg = Region(rn)
		regions.append(reg)
		print('Server list for Region: ' + rn)
		servers = conn.nova.servers.list(search_opts={'all_tenants':1})

		reg.cat_servers(servers, 'native')
		print('native servers: ')
		for index, server in enumerate(reg.native, 1):
			print(index, server, end=" , ")
		print('nonative servers: ')
		for index, server in enumerate(reg.onboarded, 1):
			print(index, server, end=" , ")
			#print(s.name, s.metadata)

		row = we.insert_servers(we.sheet1, sum_row+1, reg.native, reg.onboarded, rn + ' - ' + frn)
		sum_row =+ row
		sleep(2)

	except (ConnectionError, EndpointNotFound) as conn_e:
		print('ConnectionError in region: ' + reg.r_name + '\n')
		print(conn_e)
		pass
	except (HTTPClientError) as http_e:
		print('HTTPClientError in region: ' + reg.r_name + '\n')
		print(http_e)
		pass

we.save_book('Server extract ' + we.month_day + '.xls')