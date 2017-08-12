
## 使用流程

- 将样本hwp文件(已提供)和poc文件放到本目录下, 并重命名为 "a.hwp"和"poc.str"
- 首先运行exe文件, 看到提示 "extract DocInfo done!", 同时本目录下出现 "DocInfo" 文件, 说明docinfo提取成功
- 看到提示 "wait for "docinfo.compress"", 这时运行exploit2.py脚本, 生成新的docinfo文件--"docinfo.compress"
- 回到exe文件运行的控制台, 回车 , 在本目录下会生成最终的poc.hwp

## 运行流程

- exe文件首先从样本hwp文件提取DocInfo
- python脚本解压DocInfo, 并修改count字段(每个样本hwp文件不同,硬编码在脚本中)触发漏洞, 同时将poc内容加入到DocInfo文件. 之后压缩, 得到新的DocInfo文件--docinfo.compress
- exe文件更新hwp文件的docinfo以及其相关部分, 最后得到poc.hwp

## 输入输出

需要提供:
- poc.str文件, 存放poc

生成的新文件:
- DocInfo, 从样本hwp提取的DocInfo
- DocInfo.bin, 将DocInfo解压之后得到的原生数据
- DocInfo.bin.new, 修改count并且加入poc之后的未经压缩DocInfo数据
- docinfo.compress, 将DocInfo.bin.new压缩得到,作为新的docinfo填充进poc.hwp
- poc.hwp, 生成的poc文件


## 相关说明

已经提供hwp文件, 并且硬编码到py脚本的count字段的值与之对应.

如果想要用别的hwp文件, 首先保证满足触发漏洞的条件, 其次找到count在DocInfo的偏移修改py脚本.
