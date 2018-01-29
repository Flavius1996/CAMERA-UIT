# CAMERA UIT
Script thực hiện capture các frames từ camera của UIT

Ngôn ngữ: Python 2.7 (Đã test ok trên python 3.6)

Thư mục Google Drive chính sẽ chứa các frame capture được:
```Shell
https://drive.google.com/drive/u/1/folders/1ZuJIs8o1SSbgGQvKZSPJ01QgK-bOC3WQ
```


### Thư viện cần thiết

Có thể sử dụng pip để cài đặt các lib cần thiết sau cho python:
```Shell
opencv-python (Capture video): https://pypi.python.org/pypi/opencv-python
schedule (Hẹn lịch chạy): https://pypi.python.org/pypi/schedule
pydrive (Upload Google Drive): https://pythonhosted.org/PyDrive
```

### Hướng dẫn sử dụng script

1. Clone github này
```Shell
git clone https://github.com/Flavius1996/CAMERA-UIT.git
```

2. Truy cập VPN tới một máy server UIT Cloud.

3. Chạy CameraUIT.py trên máy server đó:
```Shell
python CameraUIT.py [Các thông số ARGS truyền vào]
```

### Các tùy chọn thông số ARGS
**-camera_link**: đường dẫn đến stream của camera cần capture

**-camera_name**: tên sẽ được đặt cho camera này, nên đặt tên khác nhau cho mỗi camera.

**-sampling_rate**: số frames sẽ được captured trong 1 giây

**-start_time**: thời gian bắt đầu capture trong ngày. Ví dụ input là '07:00' sẽ bắt đầu capture từ 7:00 mỗi ngày.

**-end_time**: thời gian kết thúc capture trong ngày. Ví dụ input là '08:00' sẽ kết thúc capture và 8:00 mỗi ngày.

*Để chạy 24/24 thì start_time và end_time sẽ là: 00:00 và 23:59, tuy nhiên cần lưu ý dung lượng ổ cứng khả dụng.*

*Lưu ý: thời gian được xét là thời gian của máy tính chạy script, không phải thời gian của camera*

**-store_mode**: Chế độ lưu trữ frame. Các giá trị store_mode có thể chọn:

    0 - Các frames chỉ được lưu ở máy tính local tại thư mục: <camera_name>/<DATE>
    
    1 - Các frames được lưu ở local và được upload lên thư mục Google Drive ở trên. Các frames được upload sau khi kết thúc session của một ngày.
    
    2 - Các frames được lưu ở local và được upload lên thư mục Google Drive ở trên. Các frames được upload ngay sau khi được capture.
    
    3 - Tương tự mode 2, tuy nhiên frames chỉ lưu trong 1 ngày, local folder sẽ bị xóa tại khi session của ngày tiếp theo bắt đầu chạy. (Dành cho máy local có dung lượng ổ cứng ít)

*Ưu tiên sử dụng mode 2 hoặc 3, để upload dữ liệu ngay lập tức và nhanh hơn do phân thành nhiều uploading threads. Mode 1 được sử dụng khi muốn chỉ thực hiện uploading vào end_time và không chiếm dụng nhiều băng thông network khi chạy*


**-image_quality**: Chất lượng ảnh JPG được nén (default=100%), số này càng thấp ảnh càng tốn ít dung lượng tuy nhiên chất lượng ảnh sẽ kém.

### <<<VÍ DỤ>>>
Ta có link camera của UIT như sau: "rtsp://id:pass@192.168.75.27:554"
  
Cần capture frames từ camera này trong khoảng thời gian từ 7:30 đến 15:00 mỗi ngày, lấy 3 frames mỗi giây, chất lượng ảnh 80%,  lưu cả ở ổ cứng của máy mình và upload tại thư mục Google Drive chính.

Câu lệnh sẽ là:
  
```Shell
nice python CameraUIT.py -camera_link rtsp://<id>:<pass>**@192.168.75.27:554 -camera_name Front_MMLAB -sampling_rate 3 -start_time 7:30 -end_time 15:00 -store_mode 2 -image_quality 80
```

*Sử dụng lệnh nice của linux để không chiếm CPU usage của các Process khác. Trước đó có thể sử dụng lệnh screen của linux để có thể tắt VPN mà không làm tắt session ở server.*

Với lần đầu tiên chạy script này thì sẽ có một của sổ trình duyệt Browser (Firefox) hiện ra yêu cầu đăng nhập Google cho client account để có thể upload file lên Google Drive. Ưu tiên sử dụng account với Unlimited Storage (account gmail UIT) để upload. Sau khi đăng nhập, script sẽ tự lưu token lại tại file **uitcamera_creds.txt** để dùng cho lần chạy sau.

Muốn đổi account upload lên Google drive thì thoát session của Browser (xóa History,cache,...), xóa file **uitcamera_creds.txt** và chạy lại script.

### Quy cách đặt tên file
Cách đặt tên các file ảnh frames đã captured

    <Tên camera>_<Ngày/tháng/năm>_<giờ>_<phút>_<giây>___<Số thứ tự frames captured trong ngày>.jpg

Ví dụ:

    Front_MMLAB_29012018_07-05-12___243.jpg


