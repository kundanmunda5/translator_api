import os
import re
import json
import logging
import subprocess               #to execute bash commands
from dotenv import load_dotenv
from custom_errors import *

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApiHandler:
    def __init__(self, api_ec2_id:str = None):
        try:
            if api_ec2_id == None:
                message = f"ERROR! api_ec2_id is None , ApiHandler() requires the APIs EC2 instance id"
                raise ValueError(message)
            
            self.api_ec2_id = api_ec2_id
            self.get_ec2_details(self.api_ec2_id)


        except ValueError as e:
            message = f"ApiHandler() api_ec2_id is None. error : {e}"
            logger.error(message)
            raise
                
    def run_bash_command(self, command:str) -> str:
        try:

            # command = f"aws ec2 describe-instances --instance-ids {instance_id} --query 'Reservations[0].Instances[0].PublicIpAddress' --output json"
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
        
            # Check if there was any output to stdout
            if result.stdout:
                message = result.stdout
                status = "success"
            elif result.stderr:
                message = f"Error occured for command:{command} | error:{result.stderr}"
                status = "error"
            else:
                message =  f"No output received! from executing the command : {command}"
                status = "success"
        
        except subprocess.CalledProcessError as e:
            message = f"Unable to execute command : {command} | error : {e.stderr}"
            status = "error"

        return message, status


    
    def stop_ec2(self, ec2_id:str = None) -> str:
        if ec2_id is None:
            ec2_id = self.api_ec2_id
        stop_ec2_cmd = f"aws ec2 stop-instances --instance-ids {ec2_id}"
        results, status = self.run_bash_command(stop_ec2_cmd)
        if status == "success":
            json_results = json.loads(results)
            logger.error(json_results)
            current_state = json_results['StoppingInstances'][0]['CurrentState']['Name']
            previous_state = json_results['StoppingInstances'][0]['PreviousState']['Name']
            message = f"Attempted to STOP EC2 : Previous State:{previous_state} >> Current State:{current_state}"
        else:
            message = f"Attempt to STOP EC2 Failed!!! Check Command : {stop_ec2_cmd}"
        return message, status

    def start_ec2(self, ec2_id:str = None) -> str:
        if ec2_id is None:
            ec2_id = self.api_ec2_id
        start_ec2_cmd = f"aws ec2 start-instances --instance-ids {ec2_id}"
        results, status = self.run_bash_command(start_ec2_cmd)
        if status == "success":
            json_results = json.loads(results)
            current_state = json_results['StartingInstances'][0]['CurrentState']['Name']
            previous_state = json_results['StartingInstances'][0]['PreviousState']['Name']
            message = f"Attempted to START EC2 : Previous State:{previous_state} >> Current State:{current_state}"
        else:
            message = f"Attempt to START EC2 Failed!!! Check Command : {start_ec2_cmd}"
        return message, status


    def get_ec2_details(self, ec2_id:str = None) -> dict:
        if ec2_id is None:
            ec2_id = self.api_ec2_id
        
        bash_command = f"aws ec2 describe-instances --instance-ids {ec2_id} --output json"
        response, status = self.run_bash_command(bash_command)
        if status == "success":
            ec2_details = json.loads(response) #has many more details related to the ec2
            self.ec2_state = ec2_details['Reservations'][0]['Instances'][0]['State']['Name']
            if self.ec2_state == "running":
                self.api_public_ip = ec2_details['Reservations'][0]['Instances'][0]['PublicIpAddress']
            else:
                self.api_public_ip = None
            message = f"EC2 Details : PublcIP : {self.api_public_ip} | Ec2State : {self.ec2_state}"

            return message, status
        else:
            message = f"Error Occurred while fetching EC2 details"
            return message, status
    
    
    def health_check(self, ec2_id:str = None) -> tuple[str,...]:
        if ec2_id is None:
            ec2_id = self.api_ec2_id
        message = f"HealthCheck >> ec2_state : {self.ec2_state} | ec2_public_ip : {self.api_public_ip}"
        status = "status"
        return message, status
    
    def translate_text(self,  params:dict, ec2_id:str = None,) -> tuple[str,...]:
        if ec2_id == None:
            ec2_id = self.api_ec2_id

        
        return "translate_text called"

    

    def get_constructors(self, ec2_id:str = None) -> str:
        if ec2_id == None:
            ec2_id = self.api_ec2_id
        logger.info(f"EC2 ; {self.api_ec2_id} | {self.api_public_ip}")


class Translator(ApiHandler):
    def __init__(self, ec2_id:str = None):
        
        # if ec2_id is None:
        #     raise MissingParameterError(f"Translator() requires API's EC2 instance ID : Translator(ec2_id:str)")

        self.ec2_id = ec2_id
        if self.ec2_id is None:
            self.ec2_id = os.getenv('TRANSLATE_API_EC2_ID')
            if self.ec2_id is None:
                raise MissingParameterError("TRANSLATE_API_EC2_ID environment variable is not set")

        super().__init__(self.ec2_id) #access all the parent class variables
        self.api_public_ip = self.api_public_ip
    
    
    def translate(self, params:dict = None):
        if params is None:
            raise MissingParameterError(f"Translator.translate() expecting dict() params;")

        logger.info(f"PARAMS RECEIVED : {params}")

        message = "RECEIVED THE TRANSLATE TEXTS"
        status = "success"
        return message, status
    


if __name__ == "__main__":
    # apiHandler = ApiHandler()
    # apiHandler.get_constructors()
    ec2_id = os.getenv("TRANSLATE_API_EC2_ID")
    translator = Translator(ec2_id)
    translator.get_constructors()
    print(translator.api_public_ip)