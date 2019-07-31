# seniorcar-program
ubuntu14.04 indigo
## ultimate-seniorcar
改造セニアカーの基本的なプログラム
1.セニアカーのCAN通信をマウントしてPCからの制御値が入るようにする
roslaunch ultimate_seniorcar seniorcar_canusb.launch
2.内界センサ及び外界センサの起動、操舵モータとの接続
roslaunch ultimate_seniorcar seniorcar_without_canusb.launch
３．適当なプログラムでv、δの指令値を出せば走る
