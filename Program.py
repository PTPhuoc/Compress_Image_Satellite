import io
import os
import psycopg2
import rasterio

# Kết nối đến cơ sở dữ liệu PostgreSQL
conn = psycopg2.connect(
    dbname="Compress",
    user="postgres",
    password="12345",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Thư mục đầu vào
directory = "F:/my_project/python/input/LE07_L2SP_125052_20181226_20200827_02_T1"


# Kiểm tra và lưu tên thư mục vào cơ sở dữ liệu nếu chưa tồn tại
def Check(directory):
    Folder_Name = os.path.basename(directory)

    # Kiểm tra xem thư mục đã tồn tại trong bảng `folder_compress` hay chưa
    cur.execute("SELECT COUNT(*) FROM folder_compress WHERE namefl=%s", (Folder_Name,))
    result = cur.fetchone()
    if result and result[0] == 1:
        print("Tệp " + Folder_Name + " này đã được nén!")
    else:
        # Thêm thư mục mới vào bảng nếu chưa tồn tại
        cur.execute("SELECT COUNT(*) FROM folder_compress")
        Count = cur.fetchone()[0] + 1
        cur.execute("INSERT INTO folder_compress (idfl, namefl) VALUES (%s, %s)", (Count, Folder_Name))
        conn.commit()
        Read_File(directory, Count)


# Đọc các tệp từ thư mục và nén nếu là tệp .tif, lưu tệp khác vào DB
def Read_File(directory, id):
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            if filename.lower().endswith('.tif'):
                Compress(directory, filename, id)
            else:
                # Mở và đọc nội dung của các tệp không phải .tif (ví dụ: .txt, .json,...)
                with open(os.path.join(directory, filename), "rb") as FL:
                    OtherFile = FL.read()
                    Save_Database(OtherFile, filename, len(OtherFile) / 1024, id)


# Nén tệp .tif và lưu kết quả nén vào cơ sở dữ liệu
def Compress(directory, filename, id):
    with rasterio.open(os.path.join(directory, filename)) as src:
        profile = src.profile
        profile.update(
            driver='JP2OpenJPEG',  # Định dạng JPEG 2000
            compress='jpeg2000',  # Phương pháp nén
            quality=25,  # Mức chất lượng nén
            tilexsize=512,  # Kích thước ô gạch (x)
            tileysize=512  # Kích thước ô gạch (y)
        )
        # Tạo tệp nén trong bộ nhớ
        with io.BytesIO() as MemoryFile:
            with rasterio.open(MemoryFile, "w", **profile) as Compressed:
                Compressed.write(src.read())
            MemoryFile.seek(0)
            File_Compressed = MemoryFile.read()
            Save_Database(File_Compressed, (os.path.splitext(filename)[0] + ".jp2"), len(File_Compressed) / 1024, id)


# Lưu thông tin tệp và nội dung tệp vào cơ sở dữ liệu
def Save_Database(File, Name, Capacity, id):
    cur.execute("INSERT INTO file_compress (idfl, namef, dataf, kilobytes) VALUES (%s,%s,%s,%s)",
                (id, Name, psycopg2.Binary(File), Capacity))
    conn.commit()
    print("Đã nén và lưu trữ thành công tệp " + Name)


# Thực hiện kiểm tra và xử lý tệp
Check(directory)

# Đóng kết nối cơ sở dữ liệu
cur.close()
conn.close()
