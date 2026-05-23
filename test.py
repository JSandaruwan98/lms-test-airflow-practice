import pandas as pd

from config.db_config import (
    source_conn,
    warehouse_conn
)

from config.logger import logger
from utils.retry_handler import execute_with_retry


def load_dim_students_scd2():

    def scd2_process():

        # ==========================================
        # EXTRACT SOURCE DATA
        # ==========================================

        query = """
        SELECT
            id,
            name,
            city
        FROM students
        """

        df = pd.read_sql(query, source_conn)

        cursor = warehouse_conn.cursor()

        # ==========================================
        # PROCESS EACH ROW
        # ==========================================

        for _, row in df.iterrows():

            student_id = row['id']
            student_name = row['name']
            city = row['city']

            # ==========================================
            # CHECK CURRENT ACTIVE RECORD
            # ==========================================

            check_sql = """
            SELECT
                student_key,
                city
            FROM dim_student
            WHERE student_id = %s
            AND current_flag = 'Y'
            """

            cursor.execute(check_sql, (student_id,))

            existing = cursor.fetchone()

            # ==========================================
            # NEW STUDENT
            # ==========================================

            if existing is None:

                insert_sql = """
                INSERT INTO dim_student
                (
                    student_id,
                    student_name,
                    city,
                    start_date,
                    end_date,
                    current_flag
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    NOW(),
                    NULL,
                    'Y'
                )
                """

                values = (
                    student_id,
                    student_name,
                    city
                )

                cursor.execute(insert_sql, values)

                logger.info(
                    f"Inserted new student {student_id}"
                )

            else:

                student_key = existing[0]
                old_city = existing[1]

                # ==========================================
                # CHECK FOR CHANGES
                # ==========================================

                if old_city != city:

                    # ==========================================
                    # EXPIRE OLD RECORD
                    # ==========================================

                    update_sql = """
                    UPDATE dim_student
                    SET
                        end_date = NOW(),
                        current_flag = 'N'
                    WHERE student_key = %s
                    """

                    cursor.execute(update_sql, (student_key,))

                    # ==========================================
                    # INSERT NEW VERSION
                    # ==========================================

                    insert_sql = """
                    INSERT INTO dim_student
                    (
                        student_id,
                        student_name,
                        city,
                        start_date,
                        end_date,
                        current_flag
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        NOW(),
                        NULL,
                        'Y'
                    )
                    """

                    values = (
                        student_id,
                        student_name,
                        city
                    )

                    cursor.execute(insert_sql, values)

                    logger.info(
                        f"SCD2 change detected for student {student_id}"
                    )

        # ==========================================
        # COMMIT CHANGES
        # ==========================================

        warehouse_conn.commit()

        print("✅ SCD Type 2 load completed")

    # ==========================================
    # EXECUTE WITH RETRY
    # ==========================================

    try:

        execute_with_retry(scd2_process)

    except Exception as e:

        warehouse_conn.rollback()

        logger.error(
            f"SCD2 load failed: {str(e)}"
        )

        print("❌ SCD Type 2 load failed")
        print(e)