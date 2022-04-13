"""
Data update module
"""

from MyPackages.KingFund.KingFund import KingFund
from MyPackages.Tushare.TusharePro import TushareData

import pandas as pd


def update_kingfund():
    fund_list = pd.read_csv('data/基金/私募基金/fund_list/在投标的.csv')
    product_list = pd.read_csv('data/基金/私募基金/fund_list/产品列表.csv')

    kf = KingFund()

    def get_from_kingfund(name_list, fund_code_list):
        prices = list(map(kf.get_equity_price,
                          name_list,
                          fund_code_list))

        prices = [_.iloc[:, 2] for _ in prices]  # 提取复权净值
        prices = pd.concat(prices, axis=1, join='outer')
        prices.sort_index(ascending=True, inplace=True)
        return prices

    def data_clean(df):
        for date in df.index:
            if df.loc[date, :].isna().sum() >= 30:
                df.drop(index=date, inplace=True)

        df.fillna(method='ffill', inplace=True)

    # 更新在投标的净值
    fund_prices = get_from_kingfund(name_list=fund_list['投资标的'],
                                    fund_code_list=fund_list['fund_code'])
    data_clean(fund_prices)

    # 更新产品净值
    product_prices = get_from_kingfund(name_list=product_list['产品名称'],
                                       fund_code_list=product_list['fund_code'])
    data_clean(product_prices)

    # 保存
    fund_prices.to_csv('data/基金/私募基金/fund_prices.csv')
    product_prices.to_csv('data/基金/私募基金/product_prices.csv')

    # 显示更新日期
    print(f'在投标的最新净值日期：{fund_prices.index[-1]}')
    print(f'产品最新净值日期：{product_prices.index[-1]}')


def update_index():
    ts = TushareData()

    # 测算用各指数
    index_list = pd.DataFrame(
        ['000300.SH', '000905.SH', '000852.SH', '399006.SZ', '399005.SZ', '399903.SZ', '000016.SH'],
        index=['沪深300', '中证500', '中证1000', '创业板', '中小100', '中证100', '上证50'],
        columns=['指数代码'])

    index_data_daily = list(map(ts.daily_index, index_list['指数代码']))
    index_data_daily = [_['close'] for _ in index_data_daily]
    index_data_daily = pd.concat(index_data_daily, axis=1, join='outer')
    index_data_daily.columns = index_list.index
    index_data_daily.sort_index(ascending=True, inplace=True)

    index_data_weekly = list(map(ts.weekly_index, index_list['指数代码']))
    index_data_weekly = [_['close'] for _ in index_data_weekly]
    index_data_weekly = pd.concat(index_data_weekly, axis=1, join='outer')
    index_data_weekly.columns = index_list.index
    index_data_weekly.sort_index(ascending=True, inplace=True)

    # 添加中证全债数据
    zzqz = pd.read_excel('data/指数/中证全债.xlsx', index_col=0)
    zzqz.index = pd.to_datetime(zzqz.index).date

    index_data_daily = pd.concat([index_data_daily, zzqz], axis=1, join='inner')
    index_data_weekly = pd.concat([index_data_weekly, zzqz], axis=1, join='inner')
    # 保存数据
    index_data_daily.to_csv('data/指数/index_data_daily.csv')
    index_data_weekly.to_csv('data/指数/index_data_weekly.csv')


def run():
    update_kingfund()
    update_index()


if __name__ == '__main__':
    run()
