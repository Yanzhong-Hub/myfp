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


def header():
    st.header('产品基本情况页')

    # basic setting
    year_start_date = datetime.date(2021, 12, 31)

    # read_data
    products_data = pd.read_csv('data/基金/私募基金/product_prices.csv', index_col=0)
    index_data = pd.read_csv('data/指数/index_data_weekly.csv', index_col=0)
    index_data = index_data[['沪深300', '中证全债']]
    products_data.index = pd.to_datetime(products_data.index).date
    index_data.index = pd.to_datetime(index_data.index).date

    products_data.columns = [_[:-4] for _ in products_data.columns]

    header_setting_result = {'year_start_date': year_start_date, 'products_data': products_data,
                             'index_data': index_data}
    return header_setting_result


# sidebar setting
def sidebar(header_setting):
    products_list = header_setting['products_data'].columns

    # 选择产品
    st.sidebar.header('参数设置')
    st.write('___')
    selected_product = st.sidebar.selectbox(label='选择产品', options=products_list)
    selected_product_data = header_setting['products_data'][selected_product].copy()
    selected_product_data.dropna(axis=0, how='any', inplace=True)

    # 设置业绩基准
    index_ratio = st.sidebar.selectbox(label='业绩基准沪深300比例（%)',
                                       options=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                                       index=8)
    index_ratio = index_ratio / 100

    data_index_returns = dp.return_table(header_setting['index_data'])
    comparison_base_returns = data_index_returns['沪深300'] * index_ratio + data_index_returns['中证全债'] * (
            1 - index_ratio)
    comparison_base_prices = (comparison_base_returns + 1).cumprod()
    comparison_base_prices.name = '业绩基准'

    # 设置目标波动率
    target_vol = st.sidebar.slider(label='目标波动率（%）', min_value=0, max_value=20, value=8, step=1)

    # 选择日期
    st.sidebar.write('___')
    st.sidebar.subheader('日期选择')

    # 选择产品的日期范围
    date_options = selected_product_data.index

    year_start = st.sidebar.selectbox(label='年初时间选择', options=date_options,
                                      index=list(date_options).index(header_setting['year_start_date']))
    three_month = st.sidebar.selectbox(label='三个月时间选择', options=date_options,
                                       index=(len(date_options) - 14))
    month_start = st.sidebar.selectbox(label='月初时间选择', options=date_options,
                                       index=(len(date_options) - 5))
    current_date = st.sidebar.selectbox(label='当前日期', options=date_options,
                                        index=(len(date_options) - 1))

    # result
    sidebar_setting_result = {'selected_product_data': selected_product_data,
                              'index_ratio': index_ratio,
                              'target_vol': target_vol,
                              'year_start': year_start,
                              'three_month': three_month,
                              'month_start': month_start,
                              'current_date': current_date,
                              'comparison_base_prices': comparison_base_prices}

    return sidebar_setting_result


def body(sidebar_setting):
    product_data = sidebar_setting['selected_product_data']
    cp_data = sidebar_setting['comparison_base_prices']

    # 各期净值
    current_price = product_data[sidebar_setting['current_date']]
    month_start_price = product_data[sidebar_setting['month_start']]
    three_month_price = product_data[sidebar_setting['three_month']]
    year_start_price = product_data[sidebar_setting['year_start']]

    # 各期收益率
    this_month_return = (current_price / month_start_price - 1) * 100
    three_month_return = (current_price / three_month_price - 1) * 100
    this_year_return = (current_price / year_start_price - 1) * 100

    # 业绩基准净值及收益率
    current_price_cp = cp_data[sidebar_setting['current_date']]
    month_start_price_cp = cp_data[sidebar_setting['month_start']]
    three_month_price_cp = cp_data[sidebar_setting['three_month']]
    year_start_price_cp = cp_data[sidebar_setting['year_start']]

    this_month_return_cp = (current_price_cp / month_start_price_cp - 1) * 100
    three_month_return_cp = (current_price_cp / three_month_price_cp - 1) * 100
    this_year_return_cp = (current_price_cp / year_start_price_cp - 1) * 100

    # 产品净值表现
    # 显示文字描述
    st.markdown(f"""
            ### {product_data.name}产品表现
            {product_data.name}产品成立于{product_data.index[0]}，截止{sidebar_setting['current_date']}，
            该产品复权累计净值{current_price}。累计净值从{sidebar_setting['month_start']}至{sidebar_setting['current_date']}
            涨跌幅为{round(this_month_return, 2)}%，
            三个月涨跌幅为{round(three_month_return, 2)}%，
            今年以来涨跌幅为{round(this_year_return, 2)}%。净值历史表现如下：
            """)

    # 显示各期收益率
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
                            #### 净值表现
                            当前净值：{current_price}  
                            上期净值：{month_start_price}  
                            三个月前净值：{three_month_price}   
                            年初净值：{year_start_price}  
                            本月涨跌幅：{round(this_month_return, 2)}%  
                            三个月涨跌幅：{round(three_month_return, 2)}%  
                            今年以来涨跌幅：{round(this_year_return, 2)}%
                            """)
    with col2:
        st.markdown(f"""
                            #### 业绩基准表现  
                            本月涨跌幅：{round(this_month_return_cp, 2)}%  
                            三个月涨跌幅：{round(three_month_return_cp, 2)}%  
                            今年以来涨跌幅：{round(this_year_return_cp, 2)}%  
                            """)

    # plotting
    def plotting():
        plot_prices_df = pd.concat([product_data, cp_data], axis=1, join='inner')
        plot_prices_df = dp.accumulate_return(plot_prices_df)

        def plot_prices():
            st.write('___')
            st.markdown('### 产品净值曲线')
            st.line_chart(plot_prices_df, use_container_width=True)

        def plot_volatility():
            st.write('___')
            st.markdown('### 产品6个月滚动波动率曲线（%）')

            df_vol = dp.rolling_volatility(plot_prices_df) * 100
            df_vol['目标波动率'] = sidebar_setting['target_vol']
            st.line_chart(df_vol, use_container_width=True)

        plot_prices()
        plot_volatility()

    plotting()


def app():
    header_setting_result = header()
    sidebar_setting_result = sidebar(header_setting=header_setting_result)
    body(sidebar_setting=sidebar_setting_result)
