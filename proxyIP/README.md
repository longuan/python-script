## 介绍

从代理网站获取代理数据, 验证可用性后存到本地

## 用法

```python
python3 proxyIP.py
```

同目录下会生成result.txt文件

## 各个文件说明

- proxyIP.py 主程序
- config 配置文件, 存放代理网站的网址和re模块写成的提取ip-port-protocol的pattern
- utils.py 辅助文件