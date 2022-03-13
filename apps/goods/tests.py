# from django.test import TestCase

# Create your tests here.
from django.core.cache import cache

from fdfs_client.client import Fdfs_client

if __name__ == "__main__":
    client = Fdfs_client('./utils/client.conf')
    ret = client.upload_by_filename('test.txt')
    print(ret)

    """ 
    ret = {
    	'Group name': b'group1',
    	'Remote file_id': b'group1/M00/00/00/test.jpg',
    	'Status': 'Upload successed.',
    	'Local file name': 'test.jpg',
    	'Uploaded size': '338KB',
    	'Storage IP': b'xx.xx.xx.xx'
    }
    """
