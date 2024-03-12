import spacy
import pandas as pd
import streamlit as st
from streamlit_tree_select import tree_select
import json
import numpy as np
import os
import texte

THEME_FILE = './data/tree.csv'
TREE_FILE = './data/tree_structure.json'

class Tree():
    def __init__(self):
        self.tree_data = pd.DataFrame()
        self.text_data = pd.DataFrame()
        self.compared_raw = None
        self.compared_filtered = None
        self.nlp = spacy.load("de_core_news_lg") 
        self._tree = self.get_tree()
        self.display_mode = 'keine'
        self._mother_level = 0
        self._child_level = 0

    def get_level(self, level_id: int):
        df = self.tree_data[self.tree_data['ebene_id'] == level_id]
        return df
    
    @property 
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, value):
        self._tree = value
        with open(TREE_FILE, 'w') as file:
            json.dump(self.tree, file, indent=4)

    @property
    def child_level(self):
        return self._child_level

    @child_level.setter
    def child_level(self, value):
        self._child_level = value
        self.children_df = self.get_level(self.child_level)
        self.child_dict = dict(zip(self.children_df['bezeichnung'], self.children_df['id']))
    
    @property
    def mother_level(self):
        return self._mother_level

    @mother_level.setter
    def mother_level(self, value):
        self._mother_level = value
        self.mothers_df = self.get_level(self.mother_level)
        self.mother_dict = dict(zip(self.mothers_df['bezeichnung'], self.mothers_df['id']))

    def get_tree(self):
        if os.path.exists(TREE_FILE):
            with open(TREE_FILE, 'r') as file:
                tree = json.load(file)
        else:
            tree = {}
        return tree
    
    def create_json_tree(self, df, vorgaenger_id=0):
        """
        Recursively constructs a nested JSON tree from the given data frame.

        Args:
            df (pd.DataFrame): Data frame containing the hierarchical data.
            parent_id (int): ID of the parent node (default is 0 for the root).

        Returns:
            dict: Nested JSON tree representing the hierarchy.
        """
        children = df[df['vorgaenger_id'] == vorgaenger_id]
        json_tree = []
        for _, row in children.iterrows():
            node = {
                "value": row['id'],
                "label": row['bezeichnung'],
                "children": self.create_json_tree(df, vorgaenger_id=row['id'])
            }
            json_tree.append(node)
        return json_tree

    def build_tree_structure(self, df, mother_id):
        """
        Recursively builds a tree structure from a DataFrame of nodes.

        Parameters:
        - df: DataFrame with columns ['id', 'label', 'mother_id']
        - mother_id: The mother_id to filter child nodes. Default is None for top-level nodes.

        Returns:
        A list of dictionaries representing the node structure.
        """
        filtered_df = df[df['vorgaenger_id'] == mother_id]
        tree = []  # Initialize tree structure for the current level
        for _, row in filtered_df.iterrows():
            # print(row)
            node = {
                'value': row['id'],
                'label': row['bezeichnung'],
                'children': self.build_tree_structure(filtered_df, row['id'])  # Pass row['id'] to find children
            }
            # print(node)
            tree.append(node)
        return tree

    def display(self):
        if self.tree == {} or self.display_mode == 'keine':
            ...
        elif self.display_mode.lower() == 'baum':
            response = tree_select(self.tree)
            st.markdown("Selektierte :")
            st.write(response)
        elif self.display_mode == 'tabelle':
            level = st.selectbox('Ebene', [1, 2, 3])
            df = self.tree_data[self.tree_data['ebene_id'] == level]
            options_dict = dict(zip(list(self.tree_data['id']), list(self.tree_data['bezeichnung'])))
            df['vorgaenger_id'] = df['vorgaenger_id'].map(options_dict)
            config = {
                "vorgaenger_id": st.column_config.SelectboxColumn(
                    "Vorgänger",
                    help="Mutter Thema",
                    width="medium",
                    options=list(set(options_dict.values())),
                    required=True,
                )
            }
            df = st.data_editor(
                df,
                column_config=config,
                hide_index=True
            )
            st.write(df)

    def get_children(self, df, mother_id: int):
        children = df[df['vorgaenger_id'] == mother_id]
        return children

    def get_full_node_expression(self, row):
        return row['bezeichnung'] if row['beschreibung'] is np.nan else f"{row['bezeichnung']} {row['beschreibung']}"
    
    def auto_assign(self):
        comp = []
        placeholder = st.empty()
        for _, child_row in self.children_df.iterrows():
            placeholder.text(f"Comparing {child_row['bezeichnung']}")
            kw_child = self.nlp(self.get_full_node_expression(child_row))

            if self.mother_level == 2 and self.child_level == 3:
                self.mothers_df = self.get_children(self.tree_data, child_row['vorvorgaenger_id'])
                self.mother_dict = dict(zip(self.mothers_df['bezeichnung'], self.mothers_df['id']))
            for _, mother_row in self.mothers_df.iterrows():
                kw_mother = self.nlp(self.get_full_node_expression(mother_row))
                print(kw_mother)
                try:
                    child_node = {
                        'kw_child': child_row['bezeichnung'],
                        'id_child': self.child_dict[child_row['bezeichnung']],
                        'kw_mother': mother_row['bezeichnung'],
                        'id_mother': self.mother_dict[mother_row['bezeichnung']],
                        'similarity': kw_child.similarity(kw_mother)
                    }
                    comp.append(child_node)
                except Exception as e:
                    print(f'error für kombi "{kw_mother}"-"{kw_child}": {e}')
        placeholder = None
        self.compared_raw = pd.DataFrame(comp)
        df = self.compared_raw.loc[self.compared_raw.groupby("kw_child")["similarity"].idxmax()]
        self.compared_filtered = df.sort_values(by=['kw_child', 'similarity'], ascending=[True, False]).reset_index()
        self.compared_filtered.to_csv(f'similarity{self.mother_level}-{self.child_level}.csv', sep=';', index=False)
        st.success('Data has been classified')

        map_dict = dict(zip(
            list(self.compared_filtered['id_child']),
            list(self.compared_filtered['id_mother'])
            )
        )
        if self.child_level - self.mother_level > 1:
            self.tree_data.loc[self.tree_data['ebene_id'] == self.child_level, 'vorvorgaenger_id'] = self.tree_data['id'].map(map_dict)
        else:
            self.tree_data.loc[self.tree_data['ebene_id'] == self.child_level, 'vorgaenger_id'] = self.tree_data['id'].map(map_dict)
        self.tree_data['vorgaenger_id'] = self.tree_data['vorgaenger_id'].fillna(0).astype(int)
        self.tree_data['vorvorgaenger_id'] = self.tree_data['vorvorgaenger_id'].fillna(0).astype(int)
        
        self.tree_data.to_csv(THEME_FILE, sep=';', index=False)

    def info(self):
        st.markdown('## Info')
        st.write(texte.info)

    def load_data(self):
        def check_required_columns(req_list: list, col_list: list):
            return all([col in col_list for col in req_list])

        st.markdown('## Daten Upload')
        hierarchy = st.file_uploader('Hierachie der Stichworte', type=['csv'])
        if hierarchy:
            self.tree_data = pd.read_csv(hierarchy, sep=';')
            required_columns = ['id', 'bezeichnung', 'beschreibung', 'ebene_id', 'vorgaenger_id', 'vorvorgaenger_id']
            self.tree_data.columns = self.tree_data.columns.str.lower()
            if 'id' in self.tree_data.columns:
                self.tree_data['id'] = self.tree_data['id'].astype(int)
            if 'ebene_id' in self.tree_data.columns:
                self.tree_data['ebene_id'] = self.tree_data['ebene_id'].astype(int)
            with st.expander('Vorschau der Stichworte'):
                st.write(self.tree_data)
            if not check_required_columns(required_columns, self.tree_data.columns):
                st.error(f'Die Datei muss die folgenden Spalten enthalten: {required_columns}. Bitte passe die Spaltennamen an')
                st.stop()
        
        texts = st.file_uploader('zu klassifizierende Texte', type=['csv'])
        required_columns = ['id', 'bezeichnung', 'beschreibung', 'ebene_id', 'vorgaenger_id', 'vorvorgaenger_id']
        if texts:
            self.text_data = pd.read_csv(texts, sep=';')
            with st.expander('Vorschau der Texte'):
                st.write(self.text_data)
            if not check_required_columns(required_columns, self.tree_data.columns):
                st.error(f'Die Datei muss die folgenden Spalten enthalten: {required_columns}')
                st.stop()
    
    def keyword2text(self):
        st.markdown('## Stichworte zuweisen')
        st.markdown('Hier können die Stichworte auf der untersten Ebene Texten zugeordnet werden. Die App bietet eine automatische Zuordnung an. Diese kann aber auch manuell angepasst werden.')
        st.write('Hierarchie der Stichworte:')
        st.write(self.tree_data)
        st.write('Texte:')
        st.write(self.text_data)
        if st.button('Zuordnung starten'):
            comp = []
            placeholder = st.empty()
            texts = self.text_data.iterrows()
            keywords_level1 = self.tree_data[self.tree_data['ebene_id'] == 1].iterrows()
            
            for _, text_row in texts:
                placeholder.text(f"Comparing {text_row['text']}")
                kw_text = self.nlp(text_row['text'])
                similarity, level1_id = -1, 0
                # find most similar keyword in level 1, for the search in level 3, only descendants of the most similar keyword in 
                # level1 are considered
                for _, level1_row in keywords_level1:
                    kw_level1 = self.nlp(self.get_full_node_expression(level1_row))
                    try:
                        x = kw_text.similarity(kw_level1)
                        if x > similarity:
                            similarity = x
                            level1_id = level1_row['id']
                    except Exception as e:
                        print(f'error für kombi "{kw_level1}"-"{kw_text}": {e}')
                # find descendants of the most similar keyword in level 1
                keywords2 = self.tree_data[self.tree_data['vorgaenger_id'] == level1_id]
                keywords3 = self.tree_data[(self.tree_data['ebene_id'] == 3) & (self.tree_data['vorgaenger_id'].isin(keywords2))]
                keywords = keywords2 if len(keywords3) == 0 else keywords3
                similarity, level1_id = -1, 0
                # now find most similar keyword in level3
                row = None
                for _, keyword_row in keywords.iterrows():
                    kw_level1 = self.nlp(self.get_full_node_expression(keyword_row))
                    try:
                        x = kw_text.similarity(kw_level1)
                        print(x)
                        if x > similarity:
                            similarity = x
                            row = keyword_row
                    except Exception as e:
                        print(f'error für kombi "{kw_level1}"-"{kw_text}": {e}')
                if not row is None:
                    child_node = {
                        'id_child': text_row['id'],
                        'child': text_row['text'],
                        'id_mother': row['id'],
                        'mother': row['bezeichnung'],
                        'similarity': similarity
                    }
                    comp.append(child_node)
                    self.compared_filtered = pd.DataFrame(comp)
                    self.compared_filtered.to_csv(f'text2keyword{self.mother_level}-{self.child_level}.csv', sep=';', index=False)
                else:
                    st.error(f'{text_row["text"]}: no keyword found')
    
    def interactive_compare(self):
        st.markdown('## Interaktiver Vergleich')
        st.write('Es können zwei beliebige Wörter oder Sätze miteinander verglichen werden. Die Ähnlichkeit wird als Wert zwischen 0 und 1 ausgegeben. 1 bedeutet, dass die beiden Wörter oder Sätze identisch sind. 0 bedeutet, dass sie nichts gemeinsam haben.')

        text1 = st.text_area('Wort oder Satz', value='', height=100)
        text2 = st.text_area('vergleiche mit Wort oder Satz', value='', height=100)
        if text1 and text2:
            text1 = self.nlp(text1)
            text2 = self.nlp(text2)
            similarity = text1.similarity(text2)
            st.write(f'Ähnlichkeit: {similarity}')
                        
    def build_tree(self):
        st.markdown('## Hierarchie bilden')
        st.markdown(texte.info_tree_creation)
        cols = st.columns(2)
        with cols[0]:
            self.child_level = st.selectbox('Kind-Ebene', [2, 3])
            with st.expander('Kind-Ebene'):
                st.write(self.children_df)
        with cols[1]:
            self.mother_level = st.selectbox('Mutter-Ebene', [1, 2])
            with st.expander('Mutter-Themen'):
                st.write(self.mothers_df)
        
        if st.button('Themen zuweisen'):
            self.auto_assign()
        if self.compared_raw is not None:
            with st.expander('Alle Vergleiche mit Ähnlichkeitsindex'):
                options = ['Alle'] + list(self.compared_raw['kw_child'].unique())
                child = st.selectbox('Filtere nach', options)
                disp_df = self.compared_raw if child == 'Alle' else self.compared_raw[self.compared_raw['kw_child'] == child]
                st.dataframe(disp_df)
            with st.expander('Beste Zuordnung'):
                st.dataframe(self.compared_filtered)
        self.tree = self.create_json_tree(self.tree_data)
        self.display_mode = st.sidebar.selectbox('Anzeige', ['Keine', 'Baum', 'Tabelle']).lower()
        self.display()