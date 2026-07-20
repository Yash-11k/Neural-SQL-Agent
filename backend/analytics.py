import sqlite3

DB_PATH = "sample.db"

def get_telemetry_metrics():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total Queries count
        cursor.execute("SELECT COUNT(*) FROM query_logs")
        total_queries = cursor.fetchone()[0]
        
        # Successful Queries count
        cursor.execute("SELECT COUNT(*) FROM query_logs WHERE status = 'SUCCESS'")
        successful_queries = cursor.fetchone()[0]
        
        # Success Rate
        success_rate = round((successful_queries / total_queries * 100), 1) if total_queries > 0 else 0.0
        
        conn.close()
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": success_rate
        }
    except Exception as e:
        return {
            "total_queries": 0,
            "successful_queries": 0,
            "success_rate": 0.0,
            "error": str(e)
        }