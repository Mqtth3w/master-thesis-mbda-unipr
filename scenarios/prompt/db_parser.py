"""
@author Mqtth3w https://github.com/Mqtth3w
@license GPL-3.0
"""

import sqlite3
import re

def db_parse(db, out, pbit):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.type, a.testID, b.testLabel, a.testStatus, a.testResult, a.error, a.errorLabel, a.report, a.reportLabel 
        FROM notifications AS a 
        JOIN testIdVocabulary AS b ON a.testID = b.testCode
        WHERE a.type IN (4, 7)
    """)
    
    result_mapping = {
        0: "Default",
        1: "NotExecuted",
        2: "PASS",
        3: "FAIL"
    }
    status_mapping = {
        0: "Default",
        1: "Init",
        2: "Running",
        3: "Terminated",
        4: "Stopped",
        5: "Deleted",
        6: "Error"
    }
    
    with open(out, 'w', encoding='utf-8') as f:
        pass

    for row in cursor.fetchall():
        type_val, testID, testLabel, testStatus, testResult, error, errorLabel, report, reportLabel = row
        result_str = result_mapping.get(testResult, "Unknown")
        had_error = (type_val == 7)
        if re.findall(r"PBIT", testID) and (re.findall(r"GWS1", testID) or re.findall(r"SERVER", testID) or 
                                            re.findall(r"SBC1", testID) or re.findall(r"NAS", testID) or 
                                            re.findall(r"WS1", testID) or re.findall(r"SWITCH1", testID) or
                                            re.findall(r"SWITCH2", testID) or re.findall(r"SWITCH3", testID)):
            
            output = (
                '{"test":'f'{testLabel},'
                f'"result":{result_str},'
                f'"report":{report if pbit else reportLabel},'
                f'"error":{errorLabel},'
                f'"had_error":{had_error}''},'
                )
            '''
            output = (
                f"test{{{testLabel}}}, "
                f"result{{{result_str}}}, "
                f"report{{{report if pbit else reportLabel}}}, "
                f"error{{{errorLabel}}}, "
                f"had_error{{{had_error}} }\n"
            )'''
            with open(out, 'a', encoding='utf-8') as f:
                f.write(output)
            print(output)
    conn.close()

if __name__ == "__main__":
    dbs = ["/report_20250613_16h08m27s", "/report_20250613_16h38m36s", 
           "/report_20250613_16h45m34s"]
    for i in range(1, 4):
        db_parse(f"../{i}{dbs[i-1]}", f"short_pbit_json_output_{i}.txt", True)
    