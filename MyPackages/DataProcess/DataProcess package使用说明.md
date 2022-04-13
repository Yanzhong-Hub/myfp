# DataProcess Package使用说明
Author: Yanzhong Huang  
Latest update: 5 Nov 2021
___
## 更新日志

无
___
## Requirements
- python == 3.9.7
- pandas == 1.3.4
- numpy == 1.21.2 
- openpyxl == 3.0.9

___
## 使用说明
本package对数据进行计算处理  

要求：
- 数据输入为pandas DataFrame格式
- index为时间序列
- columns为各标的名称
- 数据频率为周频，计算其他频率需在公式中声明
- 数据完整无空值
- 数据已完成切割处理（选择时间）

功能：
1. 每期收益率表格
2. 各标的期望收益率
3. 各标的波动率
4. 协方差矩阵
5. 相关性矩阵
6. 滚动波动率
7. 累计收益率表格（净值归一处理）
8. 年化收益率
9. 夏普比率
___
## Functions
### 1. 每期收益率表格
***def*** return_table(data):  
***return*** return_table   

输入：data=基金净值数据表格    
输出：每期收益率表格  
输出格式：Pandas DataFrame

### 2. 各标的期望收益率
***def*** expected_return(data, annual=52)：  
***return*** expected_return  

输入：data=基金净值数据表格, annual=年化参数（默认为52，周频）    
输出：各标的期望收益率，不加百分号（20%收益率显示为0.2)  
输出格式：Pandas Series 

### 3. 各标的波动率
***def*** volatility(data, annual=52)：  
***return*** volatility 

输入：data=基金净值数据表格, annual=年化参数（默认为52，周频）    
输出：各标的波动率，不加百分号（20%波动率显示为0.2)  
输出格式：Pandas Series 

### 4. 协方差矩阵
***def*** cov_matrix(data)：  
***return*** cov_matrix 

输入：data=基金净值数据表格    
输出：协方差矩阵 
输出格式：Pandas DataFrame  

### 5. 相关性矩阵
***def*** corr_matrix(data)：  
***return*** corr_matrix 

输入：data=基金净值数据表格    
输出：相关性矩阵 
输出格式：Pandas DataFrame  

### 6. 滚动波动率
***def*** rolling_volatility(data, period=26, annual=52)：  
***return*** rolling_volatility 

输入：data=基金净值数据表格, period=滚动区间（默认六个月，26期）, annual=年化参数（52周频，52）    
输出：滚动波动率 
输出格式：Pandas DataFrame 

### 7. 累计收益率表格（净值归一处理）
***def*** accumulate_return(data)：  
***return*** accumulate_return 

输入：data=基金净值数据表格    
输出：累计收益率表格（净值归一处理） 
输出格式：Pandas DataFrame 

### 8. 年化收益率
***def*** rolling_volatility(data, annual=52)：  
***return*** rolling_volatility 

输入：data=基金净值数据表格, annual=年化参数（52周频，52）    
输出：各标的年化收益率  
输出格式：Pandas Series

### 9. 夏普比率
***def*** sharpe(data, annual=52)：  
***return*** sharpe 

输入：data=基金净值数据表格, annual=年化参数（52周频，52）    
输出：各标的年化收益率  
输出格式：Pandas Series
___
