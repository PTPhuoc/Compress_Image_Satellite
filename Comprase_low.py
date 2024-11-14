import rasterio
import os


def normalize_path(path):
    # Thay thế tất cả dấu '\' bằng '/'
    return path.replace("\\", "/")


def input_folders_and_check():
    # Nhập đường dẫn thư mục từ bàn phím
    folder_origin = input("Nhập đường dẫn thư mục gốc: ").strip()
    folder_check = input("Nhập đường dẫn thư mục kiểm tra: ").strip()

    # Chuẩn hóa đường dẫn (đổi \ thành /)
    folder_origin = normalize_path(folder_origin)
    folder_check = normalize_path(folder_check)

    # Kiểm tra sự tồn tại của các thư mục
    if not os.path.exists(folder_origin):
        print(f"Thư mục gốc '{folder_origin}' không tồn tại.")
        return None, None

    if not os.path.exists(folder_check):
        print(f"Thư mục kiểm tra '{folder_check}' không tồn tại.")
        return None, None

    # Kiểm tra có ít nhất một tệp .tif trong thư mục gốc
    tif_files_origin = [f for f in os.listdir(folder_origin) if f.lower().endswith('.tif')]
    if not tif_files_origin:
        print(f"Không tìm thấy tệp .tif trong thư mục gốc '{folder_origin}'.")
        return None, None

    # Kiểm tra có ít nhất một tệp .tif trong thư mục kiểm tra
    tif_files_check = [f for f in os.listdir(folder_check) if f.lower().endswith('.tif')]
    if not tif_files_check:
        print(f"Không tìm thấy tệp .tif trong thư mục kiểm tra '{folder_check}'.")
        return None, None

    # Nếu tất cả kiểm tra thành công
    print(f"Đã tìm thấy tệp .tif trong cả hai thư mục.")
    return folder_origin, folder_check


# Gọi hàm để nhận đầu vào và kiểm tra thư mục
folder_origin, folder_check = input_folders_and_check()


def check_same_filename(original_file_path, file_to_check_path):
    # Lấy tên tệp (không có đường dẫn) từ đường dẫn đầy đủ
    original_filename = os.path.basename(original_file_path)
    file_to_check_filename = os.path.basename(file_to_check_path)
    # So sánh tên tệp
    if original_filename == file_to_check_filename:
        # Mở hai tệp để kiểm tra kích thước ma trận
        with rasterio.open(original_file_path) as original, rasterio.open(file_to_check_path) as file_to_check:
            # Lấy thông tin kích thước và số dải phổ
            original_width, original_height, original_band_count = original.width, original.height, original.count
            check_width, check_height, check_band_count = file_to_check.width, file_to_check.height, file_to_check.count
            if (original_width == check_width and original_height == check_height and
                    original_band_count == check_band_count):
                return True
            else:
                print("Kích thước ma trận và số dải phổ của hai tệp không giống nhau.")
                return False
    else:
        print(f"Tên tệp '{original_filename}' không tồn tại bên thư mục kiểm tra")
        return False



def print_image_info():
    for filename in os.listdir(folder_origin):
        if filename.lower().endswith('.tif'):
            origin_file_path = os.path.join(folder_origin, filename)
            check_file_path = os.path.join(folder_check, filename)
            if os.path.isfile(origin_file_path) and check_same_filename(origin_file_path, check_file_path):
                # Mở hai tệp bằng rasterio
                with rasterio.open(origin_file_path) as origin, rasterio.open(check_file_path) as check:
                    # Lấy kích thước ảnh
                    width, height = origin.width, origin.height
                    total_pixels = width * height
                    print(f"Đang kiểm tra tệp '{filename}'...")
                    print(f"width: {width}, height: {height}")
                    identical = 0  # Biến để đếm số pixel giống nhau
                    # Đọc dữ liệu dải phổ đầu tiên (band 1)
                    origin_data = origin.read(1)  # Dữ liệu band 1
                    check_data = check.read(1)  # Dữ liệu band 1
                    # Duyệt qua từng pixel để so sánh
                    for y in range(height):
                        for x in range(width):
                            # So sánh giá trị pixel tại vị trí (x, y)
                            if origin_data[y, x] == check_data[y, x]:
                                identical += 1  # Tăng số lượng pixel giống nhau
                                # In tiến trình - Tính phần trăm pixel giống nhau
                                similarity_percentage = (identical / total_pixels) * 100
                                print(f"Phần trăm giống nhau: {similarity_percentage:.2f}%",
                                      end='\r')
                    print(f"Ảnh giống với ảnh gốc {(identical / total_pixels) * 100:.2f}%")
                    print()


# Chạy hàm kiểm tra ảnh trong thư mục
if folder_origin is not None and folder_check is not None:
    print('------------------------------------------ Bắt đầu kiểm tra ------------------------------------------')
    print_image_info()
else:
    print('Đường dẩn không hợp lệ')

