import streamlit as st
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import json
import base64
from io import BytesIO

#pd.set_option("max_colwidth", 40)

st.set_page_config(layout='wide')

@st.cache
def download_link(dframe, download_filename, download_link_text):
    if isinstance(dframe,pd.DataFrame):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        dframe.to_excel(writer,sheet_name='Sheet1',index=False)
        workbook=writer.book
        worksheet = writer.sheets['Sheet1']
        format = workbook.add_format({'text_wrap': True})
        worksheet.set_column('A:D',50, format)
        writer.save()
        object_to_download = output.getvalue()
    b64 = base64.b64encode(object_to_download)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{download_filename}">{download_link_text}</a>'


def search_google(final_kw_search,top_num_entry=10):
    final_kw_search = kw_search+'+-'+kw_exclude
    url = f'https://google.com/search?q={final_kw_search}+&num={top_num_entry}'
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
    raw_response = urllib.request.urlopen(request).read()
    html = raw_response.decode("utf-8")
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.select("#search div.g")
    title = []
    url = []
    contents = []
    for div in divs:
        try:
            title.append(div.find('h3').text)
        except:
            title.append('NA')
        try:
            url.append(div.find('a')['href'])
        except:
            url.append('NA')
        try:
            contents.append(div.text.split('›')[-1])
        except:
            contents.append('NA')
    df = pd.DataFrame([title,url,contents]).T
    df.columns = ['title','url','description']
    return df.loc[:,['title','description','url']]

def make_clickable(val):
    # target _blank to open new window
    return '<a target="_blank" href="{}">{}</a>'.format(val, 'Website link')



st.title('Searching the Resources for AI Applications')

#col_login = st.beta_columns([1,2,2])
col_login = st.columns([1,2,2])
access_token = col_login[0].text_input('Please enter your password:')
if not access_token == "aiApplication2021":
    st.write('Sorry, password is incorrect. Please try again or contact the administrator.')
    st.stop()

# --- data defination ----

AI_level = ['Resources for Machine Learning', 'Resources for Deep Learning', 'Resources for Natural Language Processing']

with open("level_data.json", "r") as level_data_json:
    AI_level_data = json.load(level_data_json)

st.markdown('### Resources for AI Applications')

st.markdown('Welcome to use AI Application App! This application can be used to find related sources in Machine Learning, Deep Learning, and Natural Language Processing.')

#st.markdown('----')


#------ main page ----

'''
### First, please select the Target Resources
'''
AI_lvl = st.radio('',AI_level)

#st.markdown('----')

if AI_lvl == AI_level[0]:
    n_component_keyword = "Two ML keywords"
    n_process_keyword = "Two ML-related Phrases"
    st.markdown(AI_level_data.get(AI_lvl).get('Application'))
elif AI_lvl == AI_level[1]:
    n_component_keyword = "Two DL keywords"
    n_process_keyword = "Two DL-related Phrases"
    st.markdown(AI_level_data.get(AI_lvl).get('Application'))
else:
    n_component_keyword = "Two NLP keywords"
    n_process_keyword = "Two NLP-related Phrases"
    st.markdown(AI_level_data.get(AI_lvl).get('Application'))

#'''----'''
st.markdown(f"### Second, plese select {n_component_keyword} and {n_process_keyword} for the search")

#col1,col2 = st.beta_columns(2)
#col3,col4 = st.beta_columns(2)
col1,col2 = st.columns(2)
col3,col4 = st.columns(2)
# build the keyword for searching
kw_component = col1.multiselect('AI keywords',AI_level_data.get(AI_lvl).get('keyword'))
kw_process = col2.multiselect('Related phrases',AI_level_data.get(AI_lvl).get('phrase'))
kw_search = '|'.join(kw_component+kw_process).replace('|','+').replace(' ','+')

# build the keword for exclusion
if kw_component:
    kw_exclude_component = AI_level_data.get(AI_lvl).get('exclude_keyword')
    kw_exclude_process = AI_level_data.get(AI_lvl).get('exclude_phrase')
    kw_exclude = '|'.join(kw_exclude_component+kw_exclude_process).replace('|','+-').replace(' ','+-')

    st.markdown('* Based on your selection, the keywords to search are:')
    st.markdown('```'+' '.join(kw_component+kw_process)+'```')
    st.markdown('* The keywords to exclude in the search are:')
    st.markdown('```'+' '.join(kw_exclude_component+kw_exclude_process)+'```')

    # final keyword search string
    final_kw_search = kw_search+'+-'+kw_exclude
    url_search = f'https://google.com/search?q={final_kw_search}'

    st.markdown('* You can click the link below to perform a search directly on google:')
    st.write(url_search)

''' ----'''

#col3.text_area('Excluded component keywords','|'.join(kw_exclude_component).replace('|',', '),height=200)
#col4.text_area('Excluded process keywords','|'.join(kw_exclude_process).replace('|',', '),height=200)



''' ### Alternatively, if you want to download the search results, select the number of entries you want from the search and then click the Google Search button '''


#n_entry = col3.number_input('Enter the number of search results: ')
n_entry = st.slider('Please specify the number of entries from the search', min_value=10, max_value=500, value=100, step=50)

if st.button('Google Search'):
    df = search_google(final_kw_search,top_num_entry=n_entry)
    # make the url clickable
    df['click_url'] = df.url.apply(make_clickable)
   
    # ---- download the converted csv file ----
    tmp_download_link = download_link(df.loc[:,['title','description','url']], 'search_results.xlsx', 'Click this link to download the Excel file of the searching results!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

    # ---- write the search result table ---
    st.write(df.loc[:,['title','description','click_url']].to_html(escape=False, index=False), unsafe_allow_html=True)
 





