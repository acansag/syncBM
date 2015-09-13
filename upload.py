import 	httplib2
import 	os, mimetypes

from 	apiclient 		import discovery, errors
from 	apiclient.http 	import MediaFileUpload
import 	oauth2client
from 	oauth2client 	import client
from 	oauth2client 	import tools

try:
	from gdrive_constants import DEFAULT_UPLOAD_FILE, DEFAULT_SYNC_FOLDER_ID
except ImportError:
	DEFAULT_UPLOAD_FILE 	= None
	DEFAULT_SYNC_FOLDER_ID 	= ''
	

try:
	import argparse
	parser = argparse.ArgumentParser(parents=[tools.argparser])
	parser.add_argument('-f', '--gfile', help='filename to upload')
	parser.add_argument('--gfolder', help='folder id to upload in')
	flags = parser.parse_args()
except ImportError:
	flags = None

SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Simple Google Drive File Uploader'

def get_credentials(useNewCredential=False):
	"""Gets valid user credentials from storage.
	
	    If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
			Credentials, the obtained credential.
	"""
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir, 'drive-quickstart.json')

	store = oauth2client.file.Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid or useNewCredential:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatability with Python 2.6
			credentials = tools.run(flow, store)
		print 'o Storing credentials to ' + credential_path
	else:
		print 'o Using saved credentials...'
	return credentials

def insert_file(service, title, description, parent_id, mime_type, filename):
	"""Insert new file.

	Args:
	service: Drive API service instance.
	title: Title of the file to insert, including the extension.
	description: Description of the file to insert.
	parent_id: Parent folder's ID.
	mime_type: MIME type of the file to insert.
	filename: Filename of the file to insert.
	Returns:
	Inserted file metadata if successful, None otherwise.
	"""
	media_body = MediaFileUpload(filename, 
								mimetype=mime_type, resumable=True)
	body = {
	'title': title,
	'description': description,
	'mimeType': mime_type
	}
	
	if parent_id:
		body['parents'] = [{'id': parent_id}]

	try:
		file = service.files().insert(
			body=body,
			media_body=media_body).execute()

		# Uncomment the following line to print the File ID
		#print 'File ID: %s' % file['id']

		return file
	except errors.HttpError, error:
		print 'An error occured: %s' % error
	return None








def main():
	
	_gfile = flags.gfile if flags.gfile else DEFAULT_UPLOAD_FILE
	_folder = flags.gfolder if flags.gfolder else DEFAULT_SYNC_FOLDER_ID
	
	if not os.path.isfile(_gfile):
		print 
		raise Exception('!!! file named <' + _gfile + '> does not exist !!!')
	
	
	credentials = get_credentials(useNewCredential=True)
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('drive', 'v2', http=http)


	f = _gfile.split('.');
	_title = _gfile #'.'.join( f[:-1] )
	_ftype = '.' + f[-1]
	_mime  = mimetypes.types_map[_ftype]

	f = insert_file(service,
				title 		= _title,
				description = '',
				parent_id 	= _folder,
				mime_type	= _mime,
				filename	= _gfile)
	if f:
		print 'o file named <' + _gfile + '> uploaded successfully!'



if __name__ == '__main__':
	main()
