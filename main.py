import uuid 
import logging
from pprint import pprint
import json
from dotenv import load_dotenv

load_dotenv(override = True)

from backend.src.graph.workflow import app 

logging.basicCongig(
    level = logging.INFO,
    format = 

)
logger = logging.getlogger("brand-guardian-runner")


def run_cli_simulation():
    '''
    Simulates the video compliance audit request.

    This function orchestrates the entire audit process:
    - Creates a unique session ID
    - Prepares the video URL and metadata
    - Runs it through the AI workflow
    - Displays the compliance results

    '''

    # Generate session id 
    session_id = str(uuid.uuid4())
    logger.info((f"starting audit session {session_id}"))

    # Define initial state

    initials_input = {
        'video_url': "https://youtu.be/dT7S75eYhcQ",
        'video_id': f'vid_{session_id[:8]}',
        'compliance_result': [],
        'erros': []
    }
    print("n---Initialized workflow...")
    print(f"Input payload : {json.dummps(initials_input, Indent = 2)}")

    try :
        final_state = app.invoke(initials_inputs)
        print("\n-------Workflow execution is complete.....")

        print("\n Compliance audit report ==")
        print(f"Video ID: {final_state.get('video_id')}")
        print(f"Final status: {final_state.get('final_status')}")
        print("\n [VIOLATIONS DETECTED]")
        results = final_state.get('compliance_results, []')
        if results:
            for issue in results:
                print(f"- [{issue.get('severity')}] [issue.get('category')] [issue.get('discription')]")

        else:
            print(" NO VIOLATIONS DETECTED....")
            print("\n [FINAL SUMMARY]")
            print(final_state.get('final_state'))
    
    except Exception as e:
        logger.error(f"Workflow execution failed :str{e}")
        raise e

if __name__ ==  "main":
    run_cli_simulation
