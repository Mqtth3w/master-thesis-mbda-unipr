"""
@author Mqtth3w https://github.com/Mqtth3w
@license GPL-3.0
"""

import sqlite3


def db_parse(db, out):
    # Connect to the database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    # Execute the query
    cursor.execute("""
        SELECT a.type, a.testID, b.testLabel, a.testStatus, a.testResult, a.error, a.report 
        FROM notifications AS a 
        JOIN testIdVocabulary AS b ON a.testID = b.testCode
        WHERE a.type IN (4, 7)
    """)
    
    # Define mapping for testResult values
    result_mapping = {
        0: "Default",
        1: "NotExecuted",
        2: "PASS",
        3: "FAIL"
    }
    
    with open(out, 'w', encoding='utf-8') as f:
        pass

    # Process each row
    for row in cursor.fetchall():
        type_val, testID, testLabel, testStatus, testResult, error, report = row
        
        # Map testResult to its string equivalent
        result_str = result_mapping.get(testResult, "Unknown")
        
        # Determine if there was an error (type 7 indicates an error)
        had_error = (type_val == 7)
        
        # Format the output
        output = (
            f"test{{{testLabel}}}, "
            f"test_result{{{result_str}}}, "
            f"test_report{{{report}}}, "
            f"test_error{{{error}}}, "
            f"test_had_error{{{had_error}}}\n"
        )
        with open(out, 'a', encoding='utf-8') as f:
            f.write(output)
        print(output)
    
    # Close the connection
    conn.close()


if __name__ == "__main__":
    db_parse("../1/report_20250613_16h08m27s", "output_1.txt")
    db_parse("../2/report_20250613_16h38m36s", "output_2.txt")
    db_parse("../3/report_20250613_16h45m34s", "output_3.txt")