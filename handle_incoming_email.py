# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START log_sender_handler]
import logging
import csv
import base64
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2
import time
import datetime
#BigQuery
from google.cloud import bigquery



# Cloud Storage
import os
import cloudstorage as gcs
from google.appengine.api import app_identity

BUCKET= #[TODO] Bucket name


#BigQuery
data_set =#[TODO]BigQuery Dataset name
table = #[TODO] Bigquery Table name
client = bigquery.Client()
table_ref = client.dataset(data_set).table(table)
table_id = #[TODO]BigQuery Table ID


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        # Log email sender
        logging.info("Received a message from: " + mail_message.sender)


        #Timestamp
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('-%Y-%m-%d-%H:%M:%S')
        
        #Grab email attachement
        for file in mail_message.attachments:
                #generate filename
        	fname = BUCKET + st + file.filename
        	logging.info(fname)
                #create a file handler
        	gcs_file=gcs.open(fname, 
        	                  'w',
        	                  content_type='text/csv')                 
	
        	#Grab data from attachment
                file_data = file.payload.decode()
        	
       		#Log file contents
       		logging.info(file_data)
       		
                #write the lines we want on to the output file
       		lines=file_data.split("\n")
       		for line in lines:
       			items = line.split(',')
       			if line and items[2]:
       				clean_line = line.strip(",") + "\n"
       				logging.info(clean_line)
       				gcs_file.write(str(clean_line))

			
       
		gcs_file.close()
                
                #grab last row
                previous_rows = client.get_table(table_ref).num_rows
                dataset_ref = client.dataset(table_id)

                #Job Config
                job_config = bigquery.LoadJobConfig()
                job_config.source_format = "CSV"
                job_config.skip_leading_rows = 1 #file has a header row
                job_config.write_disposition = "WRITE_APPEND" #We want to append rows to the table

                # Batch load data from GCS
                load_job = client.load_table_from_uri(
                        'gs:/'+ fname,
                         table_ref,
                         job_config=job_config)  # API request    

                assert load_job.job_type == 'load'
                load_job.result()  # Waits for table load to complete.
                assert load_job.state == 'DONE'








# [START app]
app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
# [END app]
