"""
产品基本情况页

1.1 净值表现
- 上期日期
- 本期日期
- 单位净值
- 区间涨跌幅
- 今年以来涨跌幅
- 净值曲线（与业绩基准对比）

1.2 风险评价
- 6个月滚动波动率
"""

import streamlit as st
import pandas as pd
import datetime
from MyPackages.DataProcess.DataProcess import DataProcess

# 实例化module
dp = DataProcess()


def read_data():
    product_data = pd.read_csv('data/基金/私募基金/product_prices.csv', index_col=0)
    index_data = pd.read_csv('data/指数/index_data_weekly.csv', index_col=0)
    index_data = index_data[['沪深300', '中证全债']]
    product_data.index = pd.to_datetime(product_data.index).date
    index_data.index = pd.to_datetime(index_data.index).date
    return product_data, index_data


# 计算业绩基准returns
def comparison_base(index_data, index_ratio):
    data_index_returns = dp.return_table(index_data)
    comparison_base_returns = data_index_returns['沪深300'] * index_ratio + data_index_returns['中证全债'] * (
            1 - index_ratio)
    comparison_base_prices = (comparison_base_returns + 1).cumprod()
    comparison_base_prices.name = '业绩基准'

    return comparison_base_prices


# side bar setting
def side_bar_setting(product_list, date_options, year_start_setting):
    # 选择产品
    st.sidebar.header('参数设置')
    st.write('___')
    selected_product = st.sidebar.selectbox(label='选择产品', options=[_[:-4] for _ in product_list])
    selected_product = selected_product + '复权净值'
    index_ratio = st.sidebar.selectbox(label='业绩基准沪深300比例（%)',
                                       options=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                                       index=8)
    index_ratio = index_ratio / 100
    target_vol = st.sidebar.slider(label='目标波动率（%）', min_value=0, max_value=20, value=8, step=1)

    # 选择日期
    st.sidebar.write('___')
    st.sidebar.subheader('日期选择')

    # 选择产品的日期范围
    date_options = date_options[selected_product].copy()
    date_options.dropna(inplace=True)
    date_options = date_options.index

    year_start = st.sidebar.selectbox(label='年初时间选择', options=date_options,
                                      index=list(date_options).index(year_start_setting))
    three_month = st.sidebar.selectbox(label='三个月时间选择', options=date_options,
                                       index=(len(date_options) - 14))
    month_start = st.sidebar.selectbox(label='月初时间选择', options=date_options,
                                       index=(len(date_options) - 5))
    current_date = st.sidebar.selectbox(label='当前日期', options=date_options,
                                        index=(len(date_options) - 1))

    return selected_product, index_ratio, target_vol, year_start, three_month, month_start, current_date


# 净值表现
def performance_result(product_prices, comparison_base_prices, current_date, month_start, three_month, year_start):
    # 产品净值表现计算
    product_prices.dropna(axis=0, how='any', inplace=True)

    def cal_returns(prices_df):
        # 各期净值
        current_price = prices_df[current_date]
        month_start_price = prices_df[month_start]
        three_month_price = prices_df[three_month]
        year_start_price = prices_df[year_start]
        # 计算各期收益率
        this_month_return = (current_price / month_start_price - 1) * 100
        three_month_return = (current_price / three_month_price - 1) * 100
        this_year_return = (current_price / year_start_price - 1) * 100

        return (current_price, month_start_price, three_month_price, year_start_price, \
                this_month_return, three_month_return, this_year_return)

    def show_performance():
        # 产品净值表现
        product_performance = cal_returns(product_prices)
        comparison_base_performance = cal_returns(comparison_base_prices)

        # 显示文字描述
        st.markdown(f"""
        ### {product_prices.name[:-4]}产品表现
        {product_prices.name[:-4]}产品成立于{product_prices.index[0]}，截止{current_date}，该产品复权累计净值{product_prices[current_date]}。累计净值从{month_start}至{current_date}涨跌幅为{round(product_performance[4], 2)}%，三个月涨跌幅为{round(product_performance[5], 2)}%，今年以来涨跌幅为{round(product_performance[6], 2)}%。净值历史表现如下：
        """)

        # 显示各期收益率
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
                        #### 净值表现
                        当前净值：{round(product_performance[0], 2)}  
                        上期净值：{round(product_performance[1], 2)}  
                        三个月前净值：{round(product_performance[2], 2)}   
                        年初净值：{round(product_performance[3], 2)}  
                        本月涨跌幅：{round(product_performance[4], 2)}%  
                        三个月涨跌幅：{round(product_performance[5], 2)}%  
                        今年以来涨跌幅：{round(product_performance[6], 2)}%
                        """)
        with col2:
            st.markdown(f"""
                        #### 业绩基准表现
                        当前净值：{round(comparison_base_performance[0], 2)}  
                        上期净值：{round(comparison_base_performance[1], 2)}  
                        三个月前净值：{round(comparison_base_performance[2], 2)}   
                        年初净值：{round(comparison_base_performance[3], 2)}  
                        本月涨跌幅：{round(comparison_base_performance[4], 2)}%  
                        三个月涨跌幅：{round(comparison_base_performance[5], 2)}%  
                        今年以来涨跌幅：{round(comparison_base_performance[6], 2)}%
                        """)

    show_performance()


# plotting
def plotting(product_prices, comparison_base_prices, target_vol):
    product_prices.dropna(axis=0, how='any', inplace=True)
    plot_prices_df = pd.concat([product_prices, comparison_base_prices], axis=1, join='inner')
    plot_prices_df = dp.accumulate_return(plot_prices_df)

    def plot_prices():
        st.write('___')
        st.markdown('### 产品净值曲线')
        st.line_chart(plot_prices_df, use_container_width=True)

    def plot_volatility():
        st.write('___')
        st.markdown('### 产品6个月滚动波动率曲线（%）')

        df_vol = dp.rolling_volatility(plot_prices_df) * 100
        df_vol['目标波动率'] = target_vol
        st.line_chart(df_vol, use_container_width=True)

    plot_prices()
    plot_volatility()


def app():
    st.header('产品基本情况页')

    # read and setting
    product_data, index_data = read_data()
    year_start_date = datetime.date(2021, 12, 31)

    # sidebar setting
    selected_product, index_ratio, target_vol, year_start, three_month, month_start, current_date = \
        side_bar_setting(product_list=list(product_data.columns), date_options=product_data,
                         year_start_setting=year_start_date)

    # 业绩基准 setting
    comparison_base_prices = comparison_base(index_data=index_data, index_ratio=index_ratio)
    product_prices = product_data[selected_product]

    # 主页面
    # 1. 业绩表现
    performance_result(product_prices, comparison_base_prices, current_date, month_start, three_month, year_start)

    # 2. 净值曲线、滚动波动率曲线
    plotting(product_prices, comparison_base_prices, target_vol)
