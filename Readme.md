# 中山大学自动每日健康打卡

本程序中验证码识别部分基于[Aggregation Cross-Entropy for Sequence Recognition](https://arxiv.org/abs/1904.08364)
实现。识别模型首先用类似的验证码生成算法生成大量类似的验证码进行训练，随后在少量真实验证码上进行fine-tuning。

## firefox安装
我们需要安装中文版的firefox浏览器，已经相关的driver.
首先卸载原来的firefox:
```bash
sudo apt-get remove firefox
```
之后下载[中文版的firefox](https://www.firefox.com.cn/download/) ，根据系统选择版本。

解压下载的安装包，并设置软连接：
```bash
tar -jxvf Firefox-latest-x86_64.tar.bz2
cd firefox/
sudo ln -s 'firefox绝对路径' /usr/bin/firefox
```

下载[驱动程序](https://github.com/mozilla/geckodriver/releases) ,放在目录 /usr/bin 下。

## 使用
首先下载预训练模型[model-raw-29.pth](https://github.com/7eu7d7/sysu_report/releases/tag/v1)，将其放在 capdet/weights/ 目录下。

随后在与rep.py同级的目录下创建文件 usr.yaml写入netid和密码即可。
```yaml
-
  uid: netid1
  pwd: 密码
-
  uid: netid2
  pwd: 密码
```

创建一个定时任务每天运行
```bash
python rep.py
```