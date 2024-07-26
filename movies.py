import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(page_title='Movies Analysis Dashboard', layout='wide')

data = pd.read_excel("Movies_Preprocessed_Data_2.xlsx")
movies_df = data[data['TYPE']=='movie'].reset_index(drop=True)
series_df = data[data['TYPE']=='series'].reset_index(drop=True)

data['all_genres'] = data[['GENRE1', 'GENRE2', 'GENRE3']].apply(lambda x: ',' .join(x.dropna()), axis=1)

# Explode the combined genre column
df_exploded = data.assign(genre=data['all_genres'].str.split(',')).explode('genre')

# Group by genre and calculate the mean rating
genre_mean_rating = df_exploded.groupby('genre')['Gross'].mean()
better_genre_mean_rating = genre_mean_rating[genre_mean_rating.index.str.strip() != '']

# Find the genre with the highest mean rating
highest_mean_genre = genre_mean_rating.idxmax()
highest_mean_rating = genre_mean_rating.max()



def lin_grad(title, data):
    highest_grossing_movie = data
    gradient_css = f"""
            <style>
            .gradient-text {{
                background: linear-gradient(90deg, #FF512F, #DD2476);
                -webkit-background-clip: text;
                color: transparent;
            }}
            .metric-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                border: 2px solid #1E90FF;
                padding: 20px;
                margin: 10px 0;
                border-radius: 10px;
            }}
            .st-ak :hover{{
                cursor : pointer;
            }}
            .metric-title {{
                font-size: 1em;
                font-weight: bold;
                margin-bottom: 0.5em;
            }}
            .metric-value {{
                font-size: 2em;
            }}
        </style>
        <div class="metric-container">
            <div class="metric-title">{title}</div>
            <div class="metric-value gradient-text" style="color:#1E90FF;">{highest_grossing_movie}</div>
        </div>
    """
    return gradient_css

def title_mark(title):
    gradient_css = f"""
            <style>
            .gradient-text {{
                background: linear-gradient(90deg, #FF512F, #DD2476);
                -webkit-background-clip: text;
                color: transparent;
            }}
            .metric-container2 {{
                display: flex;
                flex-direction: column;
                align-items: center;
                
            }}
            .st-ak :hover{{
                cursor : pointer;
            }}
            .metric-title2 {{
                font-size: 2em;
                font-weight: bold;
            }}
            .metric-value {{
                font-size: 2em;
            }}
        </style>
        <div class="metric-container2">
            <div class="metric-title2">{title}</div>
        </div>
    """
    return gradient_css

# Group by the 'year' column and count the number of movies for each year
year_counts = movies_df[movies_df['StartYear'] != ""]['StartYear'].value_counts()

# Find the year with the maximum number of movies
most_common_year = year_counts.idxmax()
most_common_year_count = year_counts.max()

print(f"The year with the most number of movies is {most_common_year} with {most_common_year_count} movies.")

a1 , a2, a3, a4 = st.columns(4)
a1.markdown(lin_grad("Highest Gross",'$'+"{:,}".format(int(data.Gross.max()))), unsafe_allow_html=True)
a2.markdown(lin_grad('Highest Grossing Movie', data.loc[data['Gross'].idxmax()]['MOVIES']), unsafe_allow_html=True)
a3.markdown(lin_grad("Most Year With Movies", int(most_common_year)),unsafe_allow_html=True)
a4.markdown(lin_grad("Most Movies per Year", most_common_year_count), unsafe_allow_html=True)

st.write('')
st.write('')
st.write('')
st.write('')

def get_color(rating):
    if rating < 5:
        return 'Low'
    elif 5 <= rating <= 8:
        return 'Mid'
    else:
        return 'High'
    
s1,s2 = st.columns([1,1])
crieteria1 = s2.selectbox('Release Year Criteria', ['Gross', 'MOVIES'])
if crieteria1 == 'Gross': selection = 'sum'
else: selection = "count"

# w1, w2 = st.columns([1,1])1

a1,a2 = st.columns([1,1])  

a1.markdown(title_mark('Scatter of Gross & Votes'),unsafe_allow_html=True)

movies_df['RATINGS'] = movies_df['RATING'].apply(get_color)
fig = px.scatter(y='Gross', x='VOTES',hover_data=[
            'MOVIES','RATING'
        ],size='Gross', data_frame= movies_df[movies_df['Gross']>10000], width=1000, height=700,color='RATINGS', color_discrete_map={
                     'Low':'#4682B4' ,
                     'Mid': '#1E90FF',
                     'High': '#0000CD'}, category_orders={'RATINGS': ['Low','Mid','High']})

# fig.update_xaxes(showline=True,
#         linewidth=1.5,
#         linecolor='#f03d4f',
#         mirror=True)

# fig.update_yaxes(showline=True,
#          linewidth=1.5,
#          linecolor='#f03d4f',
#          mirror=True)


movies_df.drop(columns=['RATINGS'],inplace= True)
a1.plotly_chart(fig, use_container_width=True)

a2.markdown(title_mark('Total (Gross/Count) of Movies per Year'),unsafe_allow_html=True)

gross_grouped= movies_df.groupby('StartYear').agg({crieteria1: selection}).reset_index()
fig2 = px.line(y=crieteria1, x='StartYear',data_frame= gross_grouped, width=1000, height=700)
a2.plotly_chart(fig2, use_container_width=True)


movies_split_director = movies_df.copy()

movies_split_director['Director/s'] = movies_split_director['Director/s'].str.split(',') 
movies_split_director = movies_split_director.explode('Director/s')

def top_dir(num):
    return movies_split_director.groupby('Director/s')['Gross'].sum().nlargest(num).to_frame().reset_index()

def top_movies_dir(num):
    return movies_split_director[movies_split_director['Director/s']!= ''].groupby('Director/s')['MOVIES'].count().nlargest(num).to_frame().reset_index()

b1 , b2 = st.columns([2,1])
c1, c2, c3 = st.columns([1,1,1])
d1, d2 = st.columns([2,1])
num = c1.selectbox('Criteria Number', [None] + list(range(11)))
crieteria2 = c2.selectbox("Filter Directors By:", [None,'Gross', 'MOVIES'])
if crieteria2 == None and num == None : 
    dir_df = top_dir(5)
    crieteria2 = 'Gross'
elif crieteria2 == None and num != None: 
    crieteria2 = 'Gross'
    dir_df = top_dir(num)

elif crieteria2 == 'Gross' and num != None: dir_df = top_dir(num)
elif crieteria2 == 'Gross' and num == None: dir_df = top_dir(5)

elif crieteria2 == 'MOVIES' and num != None: dir_df = top_movies_dir(num)
elif crieteria2 == 'MOVIES' and num == None: dir_df = top_movies_dir(5)

b1.markdown(title_mark('Top Directors (Movies/Gross)'),unsafe_allow_html=True)

fig3 = px.bar(data_frame=dir_df, x='Director/s', y=crieteria2)
d1.plotly_chart(fig3, use_container_width=True)

def movies_gross_comparison(num):
    movies_df_temp = movies_df.sort_values(by='Gross', ascending=False).reset_index(drop=True)
    top_movies = movies_df_temp.head(num)
    others_gross = movies_df_temp.iloc[num:]['Gross'].sum()
    others_row = pd.DataFrame({'Movie': ['Others'], 'Gross': [others_gross]})
    final_df = pd.concat([top_movies, others_row], ignore_index=True)
    final_df.loc[final_df.MOVIES.isna(),'MOVIES'] = "Others"
    return final_df

b2.markdown(title_mark('Top Grossing Movies'),unsafe_allow_html=True)

num2 = c3.selectbox('Select Top N:', [None] + list(range(6)))
if num2 == None:num2 = 3

fig4 = px.pie(movies_gross_comparison(num2), values='Gross', names='MOVIES', hole=0.7)
d2.plotly_chart(fig4, use_container_width=True)