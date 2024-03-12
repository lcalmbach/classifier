import streamlit as st
from tree import Tree
from streamlit_option_menu import option_menu

__version__ = "0.0.1"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2024-03-10"
GIT_REPO = "https://github.com/lcalmbach/climate-strategy-bs"
MY_EMOJI = "🌳"
MY_NAME = "Classifer"


def init():
    st.set_page_config(
        page_title=MY_NAME,
        page_icon=MY_EMOJI,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "https://www.extremelycoolapp.com/bug",
            'About': "# This is a header. This is an *extremely* cool app!"
        }
    )


def main():
    init()
    if 'tree' not in st.session_state:
        st.session_state.tree = Tree()
    my_tree = st.session_state.tree

    menu_options = ['Info', 'Daten laden', 'Hierarchie bilden', 'Stichworte zuweisen', 'Resultat editieren', 'Interaktiver Vergleich']
    with st.sidebar:
        with open( "./my.css" ) as css:
            st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
        st.markdown("<H1 style='color: blue;'>Classifier<H1>", unsafe_allow_html=True)
        menu_action = option_menu(None, menu_options, 
            icons=['info-square', 'filetype-csv', 'diagram-3', 'signpost-split', 'check2', 'keyboard'],
            menu_icon="cast", default_index=0
        )
    if menu_options.index(menu_action) == 0:
        my_tree.info()
    elif menu_options.index(menu_action) == 1:
        my_tree.load_data()
    elif menu_options.index(menu_action) == 2:
        my_tree.build_tree()
    elif menu_options.index(menu_action) == 3:
        my_tree.keyword2text()
    elif menu_options.index(menu_action) == 5:
        my_tree.interactive_compare()

if __name__ == '__main__':
    main()