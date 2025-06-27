"""
@author Mqtth3w https://github.com/Mqtth3w
@license GPL-3.0
"""

import sqlite3

def db_parse(db, out):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.type, a.testID, b.testLabel, a.testStatus, a.testResult, a.error, a.reportLabel 
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
        type_val, testID, testLabel, testStatus, testResult, error, report = row
        result_str = result_mapping.get(testResult, "Unknown")
        had_error = (type_val == 7)
        output = (
            f"test{{{testLabel}}}, "
            f"result{{{result_str}}}, "
            f"report{{{report}}}, "
            f"error{{{error}}}, "
            f"had_error{{{had_error}}}\n"
        )
        with open(out, 'a', encoding='utf-8') as f:
            f.write(output)
        print(output)
    conn.close()

if __name__ == "__main__":
    dbs = ["/report_20250613_16h08m27s", "/report_20250613_16h38m36s", 
           "/report_20250613_16h45m34s"]
    for i in range(1, 4):
        db_parse(f"../{i}{dbs[i-1]}", f"short_output_{i}.txt")
    