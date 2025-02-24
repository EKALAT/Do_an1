import mysql.connector
from datetime import datetime
from typing import List, Dict

class DatabaseHandler:
    def __init__(self):
        """Khởi tạo kết nối database"""
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Thay đổi mật khẩu nếu có
            'database': 'stock_bot'
        }

    def get_connection(self):
        """Tạo kết nối đến MySQL database"""
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as e:
            print(f"Lỗi kết nối database: {e}")
            raise e

    async def update_stock_data(self, stocks_data: List[Dict]):
        """Cập nhật dữ liệu chứng khoán mới"""
        if not stocks_data:
            print("Không có dữ liệu để cập nhật")
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            print(f"Bắt đầu cập nhật với {len(stocks_data)} mã chứng khoán")

            # Backup dữ liệu cũ vào bảng history
            cursor.execute("""
                INSERT INTO price_history (ma_ck, gia, klgd, tongklgd)
                SELECT ma_ck, gia, klgd, tongklgd FROM current_prices
                WHERE ma_ck IS NOT NULL
            """)
            
            # Xóa dữ liệu cũ
            cursor.execute("DELETE FROM current_prices")
            
            # Chuẩn bị câu lệnh INSERT
            insert_query = """
                INSERT INTO current_prices (ma_ck, gia, klgd, tongklgd)
                VALUES (%s, %s, %s, %s)
            """
            
            # Chuẩn bị dữ liệu để insert
            values = [(
                stock['ma_ck'],
                stock['gia'],
                stock['klgd'],
                stock['tongklgd']
            ) for stock in stocks_data]
            
            # Thực hiện insert nhiều dòng cùng lúc
            cursor.executemany(insert_query, values)
            
            # Commit thay đổi
            conn.commit()
            
            # Kiểm tra số lượng đã insert
            cursor.execute("SELECT COUNT(*) FROM current_prices")
            count = cursor.fetchone()[0]
            print(f"Đã cập nhật thành công {count} mã chứng khoán")
            
            return count > 0

        except Exception as e:
            print(f"Lỗi khi cập nhật database: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    async def get_current_prices(self) -> List[Dict]:
        """Lấy dữ liệu giá hiện tại từ database"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    ma_ck,
                    gia,
                    klgd,
                    tongklgd,
                    DATE_FORMAT(updated_at, '%H:%i:%s %d/%m/%Y') as updated_at
                FROM current_prices 
                WHERE ma_ck IS NOT NULL
                ORDER BY ma_ck
            """)
            
            results = cursor.fetchall()
            count = len(results)
            print(f"Đã lấy {count} mã chứng khoán từ database")
            
            if count == 0:
                print("Không tìm thấy dữ liệu trong database")
            
            return results

        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu từ database: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    async def get_stock_by_code(self, stock_code):
        """Lấy thông tin của một mã chứng khoán cụ thể"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Truy vấn SQL để lấy thông tin mã chứng khoán
            query = """
                SELECT 
                    ma_ck,
                    gia,
                    klgd,
                    tongklgd,
                    DATE_FORMAT(updated_at, '%%H:%%i:%%s %%d/%%m/%%Y') as updated_at
                FROM current_prices 
                WHERE ma_ck = '%s'
            """
            cursor.execute(query % stock_code)
            result = cursor.fetchone()
            
            if result:
                # Trả về giá trị nguyên bản từ database
                return {
                    "ma_ck": result["ma_ck"],
                    "gia": result["gia"],
                    "klgd": result["klgd"],
                    "tongklgd": result["tongklgd"],
                    "updated_at": result["updated_at"]
                }
            return None
                
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu mã {stock_code}: {e}")
            return None
        finally:
            cursor.close()
            conn.close() 