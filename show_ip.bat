@echo off
echo ===========================================
echo     AI 新聞學習系統 - 網路訪問資訊
echo ===========================================
echo.
echo 本機 IP 地址：
ipconfig | findstr "IPv4"
echo.
echo 訪問方式：
echo 本機訪問：http://localhost:5000
echo 區域網路訪問：http://你的IP:5000
echo.
echo 例如，如果你的IP是192.168.1.100，
echo 其他設備可以訪問：http://192.168.1.100:5000
echo.
echo ===========================================
pause