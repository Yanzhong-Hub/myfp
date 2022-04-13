"""
产品管理会工具主程序
latest update: 15 Nov 2021
"""
from PIL import Image
import streamlit as st

from MyPackages.Streamlit_Multipage.Multipage import MultiPage

from Apps import home
from Apps.product_performance import product_performance
from Apps.portfolio_stimulation import portfolio_stimulation
# from Apps.weekly_report import weekly_report_main

if __name__ == '__main__':
    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        # 标志
        sign_image = Image.open('Apps/SAMCO sign.png')
        st.image(sign_image)

    with col_3:
        st.markdown("""
                Author: Yanzhong Huang  
                Version: 2.0   
                Update: 8 April 2022  
                数据来源：金方数据库  
                http://kingfund.myfund.com/
                """)

    # 标题
    # st.write('---')
    new_title = '<p style="font-family:Kai-ti; color:Grey; font-size: 70px;">弘酬投资--工具合集</p>'
    st.markdown(new_title, unsafe_allow_html=True)

    app = MultiPage()

    # Add all your application here
    app.add_app("主页", home.app)
    app.add_app('1. 弘酬产品表现', product_performance.app)
    app.add_app('2. 组合测算工具', portfolio_stimulation.app)
    # The main app
    app.run()
