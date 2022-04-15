"""
模拟组合分析

"""

# 模拟组合起始、结束时间
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import platform

from MyPackages.DataProcess.DataProcess import DataProcess



# 中文字体
import matplotlib.font_manager as fm

if platform.system() == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # for mac
else:
    fm.findSystemFonts(fontpaths=None, fontext="ttf")
    fm.findfont("simhei")  # for windows
    plt.rcParams['font.sans-serif'] = ['SimHei']  # for windows
# 实例化module
dp = DataProcess()


# read data
def read_data():
    # read fund list
    fund_list = pd.read_csv('data/基金/私募基金/fund_list/在投标的.csv')
    fund_list = fund_list[['投资标的', '所属策略']]

    # separate fund list by strategy
    fund_list = tuple(fund_list.groupby(['所属策略']))
    strategy_list = [fund_list[_][0] for _ in range(5)]
    strategy_fund_list = [tuple(fund_list[_][1]['投资标的']) for _ in range(5)]

    # read fund data and modify columns name
    fund_data = pd.read_csv('data/基金/私募基金/fund_prices.csv', index_col=0)
    fund_data.index = pd.to_datetime(fund_data.index).date
    fund_data.columns = [_[:-4] for _ in fund_data.columns]

    # read index data
    index_data = pd.read_csv('data/指数/index_data_weekly.csv', index_col=0)
    index_data = index_data[['沪深300', '中证全债']]
    index_data.index = pd.to_datetime(index_data.index).date

    return strategy_list, strategy_fund_list, fund_data, index_data


def sidebar_setting(date_options, year_start_setting):
    # 组合测算周期
    st.sidebar.subheader('设置组合参数')
    portfolio_start_date = st.sidebar.selectbox(label='组合模拟起始日期', options=date_options)
    portfolio_end_date = st.sidebar.selectbox(label='组合模拟结束日期', options=date_options,
                                              index=(len(date_options) - 1))
    # 业绩基准设置
    index_ratio = st.sidebar.selectbox(label='业绩基准沪深300比例（%)',
                                       options=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                                       index=8)
    index_ratio = index_ratio / 100
    target_vol = st.sidebar.slider(label='目标波动率（%）', min_value=0, max_value=20, value=8, step=1)

    # 数据展示周期
    st.sidebar.write('___')
    st.sidebar.subheader('测算结果展示周期选择')
    year_start = st.sidebar.selectbox(label='年初时间选择', options=date_options,
                                      index=list(date_options).index(year_start_setting))
    three_month = st.sidebar.selectbox(label='三个月时间选择', options=date_options,
                                       index=(len(date_options) - 14))
    month_start = st.sidebar.selectbox(label='月初时间选择', options=date_options,
                                       index=(len(date_options) - 5))

    # result tuple
    result = (portfolio_start_date, portfolio_end_date, year_start, three_month, month_start, index_ratio, target_vol)
    return result


# 计算业绩基准returns
def comparison_base(index_data, index_ratio):
    data_index_returns = dp.return_table(index_data)
    comparison_base_returns = data_index_returns['沪深300'] * index_ratio + data_index_returns['中证全债'] * (
            1 - index_ratio)

    comparison_base_returns.name = '业绩基准'

    return comparison_base_returns


def fund_selections(strategy_list, strategy_fund_list):
    # 各策略选择标的, 选择框
    portfolio_strategy_fund_list = ['', '', '', '', '']  # 组合内各策略标的选择
    [col1, col2, col3] = st.columns(3)

    with col1:
        portfolio_strategy_fund_list[0] = st.multiselect(label=f'{strategy_list[0]}',
                                                         options=strategy_fund_list[0])
        portfolio_strategy_fund_list[1] = st.multiselect(label=f'{strategy_list[1]}',
                                                         options=strategy_fund_list[1])

    with col2:
        portfolio_strategy_fund_list[2] = st.multiselect(label=f'{strategy_list[2]}',
                                                         options=strategy_fund_list[2])
        portfolio_strategy_fund_list[3] = st.multiselect(label=f'{strategy_list[3]}',
                                                         options=strategy_fund_list[3])

    with col3:
        portfolio_strategy_fund_list[4] = st.multiselect(label=f'{strategy_list[4]}',
                                                         options=strategy_fund_list[4])

    # 运算按钮
    portfolio_all_fund_name = portfolio_strategy_fund_list[0] + portfolio_strategy_fund_list[1] + \
                              portfolio_strategy_fund_list[2] + portfolio_strategy_fund_list[3] + \
                              portfolio_strategy_fund_list[4]

    return portfolio_strategy_fund_list, portfolio_all_fund_name


def weight_input(portfolio_all_fund_name):
    st.subheader('设置各标的权重(%)')
    weight = []

    col_1, col_2 = st.columns(2)

    with col_1:
        for fund in portfolio_all_fund_name:
            weight.append(st.number_input(label=f'{fund}', max_value=100., min_value=0., step=0.01))

    with col_2:
        # 显示总仓位
        st.write(f'总仓位：{sum(weight)}%')
        if sum(weight) > 100:
            st.warning('总仓位超过100%!!!!')
        else:
            weight = [_ / 100 for _ in weight]

            # 显示各标的权重
            fig_data = pd.Series(weight, index=portfolio_all_fund_name, dtype='float64')
            fig_data['流动性'] = 1 - sum(weight)

            fig, ax = plt.subplots()
            ax.pie(fig_data, labels=fig_data.index)

            st.pyplot(fig=fig, clear_figure=None)

    return weight


def cal_portfolio(fund_data, portfolio_all_fund_name, portfolio_start_date, portfolio_end_date,
                  weight, comparison_base, target_vol):
    # 提取数据
    portfolio_all_data = fund_data.loc[portfolio_start_date:portfolio_end_date, portfolio_all_fund_name].copy()

    # 计算各标的收益矩阵
    portfolio_all_return = portfolio_all_data / portfolio_all_data.shift(1) - 1
    portfolio_all_return.fillna(value=0, inplace=True)

    # 组合收益矩阵
    portfolio_return = pd.Series(np.dot(portfolio_all_return, weight),
                                 index=portfolio_all_return.index, name='模拟组合')
    # 合并对比基准
    portfolio_return = pd.concat([portfolio_return, comparison_base], axis=1, join='inner')

    # 计算组合滚动波动率
    portfolio_vol = portfolio_return.rolling(26).std() * np.sqrt(52) * 100
    portfolio_vol.dropna(how='any', inplace=True)
    portfolio_vol['目标波动率'] = target_vol

    # 计算组合净值曲线
    portfolio_prices = (portfolio_return + 1).cumprod()

    # 基础数据
    expected_return = portfolio_return['模拟组合'].mean()
    expected_return_annual = ((expected_return + 1) ** 52 - 1) * 100
    expected_vol = portfolio_return['模拟组合'].std() * np.sqrt(52) * 100
    expected_return = expected_return * 100

    # 4. 组合测算结果
    st.write('---')
    st.subheader('组合测算结果')

    st.markdown(f"""
        该组合周期望收益率为：{round(expected_return, 2)}%，  
        年化期望收益为：{round(expected_return_annual, 2)}%，  
        年化波动率为：{round(expected_vol, 2)}%。  
        ### 组合拟合净值曲线及滚动波动率情况如下：
        """)

    def plotting():
        def plotting_accumulate_returns():
            st.markdown('### 组合净值曲线')
            st.line_chart(portfolio_prices, use_container_width=True)

        def plotting_rolling_vol():
            st.markdown('### 组合滚动波动率曲线')
            st.line_chart(portfolio_vol, use_container_width=True)

        plotting_accumulate_returns()
        plotting_rolling_vol()

    plotting()


def fund_performance(fund_data, strategy_list, portfolio_strategy_fund_list,
                     year_start, three_month, month_start, portfolio_end_date):
    st.write('___')
    st.subheader('模拟组合内各策略标的收益及波动情况')
    example_data_total = pd.DataFrame([])
    for i in range(len(strategy_list)):
        # 判断是否为空
        if portfolio_strategy_fund_list[i]:
            st.subheader(f'{strategy_list[i]}')
            example_data = fund_data.loc[:, portfolio_strategy_fund_list[i]]
            # 收益率曲线
            st.write('收益率曲线')
            example_return = dp.accumulate_return(example_data)
            example_return.index = pd.to_datetime(example_return.index)
            example_return.dropna(inplace=True)
            st.line_chart(example_return)
            # 波动率曲线
            st.write('区间内滚动波动率(%)')
            rolling_vol = dp.rolling_volatility(example_data) * 100
            rolling_vol.index = pd.to_datetime(rolling_vol.index)
            st.line_chart(rolling_vol)

            example_data_total = pd.concat([example_data_total, example_data], axis=1)

    # 标的数据表格
    st.write('___')
    st.subheader('模拟组合内各策略标的数据情况')

    st.write('净值情况')
    example_data_total = example_data_total.loc[[year_start, three_month, month_start, portfolio_end_date], :]
    st.write(example_data_total)

    st.write('业绩情况（%）')
    this_year_return = 100 * example_data_total.iloc[3, :] / example_data_total.iloc[0, :] - 100
    three_month_return = 100 * example_data_total.iloc[3, :] / example_data_total.iloc[1, :] - 100
    this_month_return = 100 * example_data_total.iloc[3, :] / example_data_total.iloc[2, :] - 100

    result = pd.concat([example_data_total.iloc[3, :].copy(),
                        this_year_return,
                        three_month_return,
                        this_month_return],
                       axis=1)
    result.columns = ['本期累计净值', '今年以来收益(%)', '三个月收益(%)', '本月收益(%)']

    st.table(result)


def app():
    st.header('组合测算及标的数据')

    # read data and setting
    strategy_list, strategy_fund_list, fund_data, index_data = read_data()
    year_start_date = datetime.date(2021, 12, 31)

    # sidebar setting
    side_bar_result = sidebar_setting(date_options=fund_data.index, year_start_setting=year_start_date)
    """
    side_bar_result: 
    0: portfolio_start_date, 
    1: portfolio_end_date, 
    2: year_start, 
    3: three_month, 
    4: month_start, 
    5: index_ratio, 
    6: target_vol)
    """

    # 业绩基准 setting
    comparison_base_return = comparison_base(index_data=index_data, index_ratio=side_bar_result[5])

    # 主页面
    # 1. 选择标的
    portfolio_strategy_fund_list, portfolio_all_fund_name = fund_selections(strategy_list, strategy_fund_list)

    # 2. 标的weight
    weight = weight_input(portfolio_all_fund_name)

    # 3. 测算
    col_1, col_2 = st.columns(2)
    with col_1:
        st.subheader('是否测算')
        button_1 = st.button('测算')
    with col_2:
        st.subheader('选择标的业绩表现')
        button_2 = st.button('显示')

    if button_1:
        cal_portfolio(fund_data, portfolio_all_fund_name, side_bar_result[0], side_bar_result[1],
                      weight, comparison_base_return, side_bar_result[6])

    if button_2:
        fund_performance(fund_data, strategy_list, portfolio_strategy_fund_list,
                         side_bar_result[2], side_bar_result[3], side_bar_result[4], side_bar_result[1])
