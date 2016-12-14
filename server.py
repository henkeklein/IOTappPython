import os
import json
import keystoneclient.v3 as keystoneclient
import swiftclient.client as swiftclient
try:
  from SimpleHTTPServer import SimpleHTTPRequestHandler as Handler
  from SocketServer import TCPServer as Server
except ImportError:
  from http.server import SimpleHTTPRequestHandler as Handler
  from http.server import HTTPServer as Server

# Read port selected by the cloud for our application
PORT = int(os.getenv('VCAP_APP_PORT', 8000))
# Change current directory to avoid exposure of control files
os.chdir('static')

def swift():

    cloudant_service = json.loads(os.environ['VCAP_SERVICES'])['Object-Storage'][0]
    objectstorage_creds = cloudant_service['credentials']

    if objectstorage_creds:
        auth_url = objectstorage_creds['auth_url'] + '/v3'
        project_name = objectstorage_creds['project']
        password = objectstorage_creds['password']
        user_domain_name = objectstorage_creds['domainName']
        project_id = objectstorage_creds['projectId']
        user_id = objectstorage_creds['userId']
        region_name = objectstorage_creds['region']

    # Get a Swift client connection object
    conn = swiftclient.Connection(
            key=password,
            authurl=auth_url,
            auth_version='3',
            os_options={"project_id": project_id,
                        "user_id": user_id,
                        "region_name": region_name})

    container_name = 'new-container'

    # File name for testing
    file_name = 'example_file.txt'

    # Create a new container
    conn.put_container(container_name)
    print "\nContainer %s created successfully." % container_name

    # List your containers
    print ("\nContainer List:")
    for container in conn.get_account()[1]:
        print container['name']

    # Create a file for uploading
    with open(file_name, 'w') as example_file:
        conn.put_object(container_name,
        file_name,
        contents= "",
        content_type='text/plain')

    # List objects in a container, and prints out each object name, the file size, and last modified date
    print ("\nObject List:")
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            print 'object: {0}\t size: {1}\t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])

    # Download an object and save it to ./my_example.txt
    obj = conn.get_object(container_name, file_name)
    with open(file_name, 'w') as my_example:
           my_example.write(obj[1])
           print "\nObject %s downloaded successfully." % file_name

    # Delete an object
    conn.delete_object(container_name, file_name)
    print "\nObject %s deleted successfully." % file_name

    # To delete a container. Note: The container must be empty!
    conn.delete_container(container_name)
    print "\nContainer %s deleted successfully.\n" % container_name

httpd = Server(("", PORT), Handler)
try:
  print("Start serving at port %i" % PORT)
  swift()
  httpd.serve_forever()
except KeyboardInterrupt:
  pass
httpd.server_close()
