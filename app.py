import streamlit as st
# For visualization
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import urllib.parse
import requests
import altair as alt
from streamlit_lottie import st_lottie
import pandas as pd

st.set_page_config(page_title="BRS", page_icon=":tada:", layout="wide")


#Designing  ## function to access animation
def load_lottieURL(url):
    r = requests.get(url)
    if r.status_code !=200:
        return None
    return r.json()

#Animations
Animation1 = load_lottieURL("https://assets10.lottiefiles.com/private_files/lf30_ipvphpwo.json")
Animation2 = load_lottieURL("https://assets2.lottiefiles.com/private_files/lf30_5qccdrpm.json")
Animation3 = load_lottieURL("https://assets6.lottiefiles.com/private_files/lf30_x8aowqs9.json")

#WEB FUNCITONALLITY
with open("updated_recommendation_pickle.pkl", "rb") as file:
    pickle_data = pickle.load(file)

    
    
#HYBRID MODEL
def hybrid_recommend(book_name):
    # Content-based filtering
    book_features_subset = pickle_data[9][pickle_data[9]['bookTitle'] == book_name]
    if book_features_subset.empty:
        return []  # Return empty lis if book not found in book features
    book_subset_indices = book_features_subset.index.tolist()
    book_subset_similarity_scores = pickle_data[8][:, book_subset_indices].flatten()
    content_based_scores = list(enumerate(book_subset_similarity_scores))

    # Collaborative filtering
    collaborative_scores = list(enumerate(pickle_data[8][pickle_data[7].index == book_name].flatten()))

    # Combine scores from both approaches
    combined_scores = [(idx, content_based_scores[idx][1] + collaborative_scores[idx][1]) for idx in range(len(content_based_scores))]

    # Sort the combined scores
    combined_scores = sorted(combined_scores, key=lambda x: x[1], reverse=True)[:6]

    # Retrieve recommended books
    recommended_books = []
    for i in combined_scores:
        temp_df = pickle_data[0][pickle_data[0]['bookTitle'] == pickle_data[7].index[i[0]]]
        recommended_books.append((temp_df['bookTitle'].values[0], temp_df['bookAuthor'].values[0], temp_df['imageUrlM'].values[0]))
    
    return recommended_books

def recommend_for_user(userID, location, age):
        l2 = []
        if (userID in pickle_data[6]['userId'].unique()) & (userID in pickle_data[0]['userId'].unique()):
            # User exists in the dataset, recommend based on their ratings
            user_books = pickle_data[6].loc[pickle_data[6]['userId'] == userID]['bookTitle'].values[:3]
            for book in user_books:
                recommendations = hybrid_recommend(book)
                l2.extend(recommendations[:3])  # Take the top 2 recommendations for each book
            return l2

        elif ((userID not in pickle_data[6]['userId'].unique()) & (userID in pickle_data[0]['userId'].unique())):
            most_rated_book = pickle_data[6].groupby('bookTitle').count().sort_values('bookRating', ascending=False).index[0:10]
            l1 = list(most_rated_book)
            for i in l1:
                l2.append((i, pickle_data[6].loc[pickle_data[6]['bookTitle'] == i]['bookAuthor'].values[0], pickle_data[6].loc[pickle_data[6]['bookTitle'] == i]['imageUrlM'].values[0]))
            return l2

        elif ((userID not in pickle_data[6]['userId'].unique()) & (userID not in pickle_data[0]['userId'].unique()) & (location!='none') & (age=='0')):
            location_wise = pickle_data[0].groupby(['bookTitle', 'country']).size().reset_index(name='rating_count').sort_values('rating_count', ascending=False)
            books_for_country = location_wise[location_wise['country'] == " "+location].head(10)
            l3 = list(books_for_country['bookTitle'])
            for i in l3:
                l2.append((i, pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['bookAuthor'].values[0], pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['imageUrlM'].values[0]))
            return l2

        elif ((userID not in pickle_data[6]['userId'].unique()) & (userID not in pickle_data[0]['userId'].unique()) & (location== 'none') & (age!='0')):
            age_wise = pickle_data[0].groupby(['bookTitle', 'Age_group']).size().reset_index(name='rating_count').sort_values('rating_count', ascending=False)
            books_by_age = age_wise[age_wise['Age_group'] == age].head(10)
            l4 = list(books_by_age['bookTitle'])
            for i in l4:
                l2.append((i, pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['bookAuthor'].values[0], pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['imageUrlM'].values[0])) 
            return l2

        elif ((userID not in pickle_data[6]['userId'].unique()) & (userID not in pickle_data[0]['userId'].unique()) & (location== 'none') & (age=='0')):
            most_rated_book = pickle_data[6].groupby('bookTitle').count().sort_values('bookRating', ascending=False).index[0:10]
            l5 = list(most_rated_book)
            for i in l5:
                l2.append((i, pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['bookAuthor'].values[0], pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['imageUrlM'].values[0]))
            return l2

        elif ((userID not in pickle_data[6]['userId'].unique()) & (userID not in pickle_data[0]['userId'].unique()) & (location!= 'none') & (age!='0')):
            books_by_country_n_age = pickle_data[0].groupby(['bookTitle', 'Age_group', 'country']).size().reset_index(name='rating_count').sort_values('rating_count', ascending=False)
            books_by_country_n_age = books_by_country_n_age[(books_by_country_n_age['country'] == " "+location) & (books_by_country_n_age['Age_group'] == age)].head(10)
            l6 = list(books_by_country_n_age['bookTitle'])
            for i in l6:
                l2.append((i, pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['bookAuthor'].values[0], pickle_data[0].loc[pickle_data[0]['bookTitle'] == i]['imageUrlM'].values[0]))
            return l2


        else:
            st.write('Some ERROR Occured')

#Books to be displayed in app
def display_all_books(books):
    st.title("Recommendations for You!")
    for book in books:
        with st.container():
            left_column, right_column = st.columns(2)
        with left_column:
            search_url = "[Click here to visit]" + "(https://www.goodreads.com/search?q=" + urllib.parse.quote_plus(book[0]) +")"
            st.subheader(book[0]) 
            st.markdown(search_url)
            st.write("Author:", book[1]) 
        with right_column:
            st.image(book[2])  
        st.write("---")  # Add a horizontal line

#WEBAPP STARTED HERE
# Create the navbar
st.sidebar.title("MENU")
nav_selection = st.sidebar.radio("Go to", ("Recommender System","Book Search", "Report", "Reference"))

# Display different content based on the navbar selection
if nav_selection == "Recommender System":
    with st.container():
        left_column, right_column = st.columns(2)
    with left_column:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.title("This is Book Recommender System") 
    with right_column:
        st_lottie(Animation1,key="coding",height=310)
    Age_group_list = ['Prefer not to Say','Children', 'Youth', 'Adults', 'Senior Citizens']
    Location_list = ['Prefer not to Say','Australia', 'Canada', 'France', 'Germany', 'Italy', 'Netherlands', 'New Zealand', 'Portugal', 'Spain', 'United Kingdom', 'USA',]
    #FORM STARTS HERE
    form = st.form(key='my_form')
    UserID = form.text_input(label='Enter UserID')
    Age_selected_option = form.selectbox("Select an Age Group", Age_group_list)
    Location_selected_option = form.selectbox("Select a Location", Location_list)
    submit_button = form.form_submit_button(label='Submit')

    if submit_button and len(UserID) != 0:
        if int(UserID) in pickle_data[0]['userId'].unique():
            if int(UserID) in pickle_data[6]['userId'].unique():
                book_data = recommend_for_user(int(UserID),'none','0')
                display_all_books(book_data)
            else:
                book_data = recommend_for_user(int(UserID),'none','0')
                display_all_books(book_data)
        else:
            st.subheader(f'Welcome New User. Your User ID is : {UserID}')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            if((Age_selected_option!='Prefer not to Say') & (Location_selected_option!='Prefer not to Say')):
                book_data = recommend_for_user(int(UserID), Location_selected_option.lower(), Age_selected_option)
                display_all_books(book_data)
            elif((Age_selected_option=='Prefer not to Say') & (Location_selected_option!='Prefer not to Say')):
                book_data = recommend_for_user(int(UserID), Location_selected_option.lower(), '0')
                display_all_books(book_data)
            elif((Age_selected_option!='Prefer not to Say') & (Location_selected_option=='Prefer not to Say')):
                book_data = recommend_for_user(int(UserID), 'none', Age_selected_option)
                display_all_books(book_data)
            elif((Age_selected_option=='Prefer not to Say') & (Location_selected_option=='Prefer not to Say')):
                book_data = recommend_for_user(int(UserID), 'none', '0')
                display_all_books(book_data)
        
    
 
               
    
    
elif nav_selection == "Book Search":
    with st.container():
        left_column, right_column = st.columns(2)
    with left_column:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.title("Book Search")    
    with right_column:
        st_lottie(Animation3,key="coding",height=230)
    st.write("---")
    st.write("")
    st.write("")
    searchable_books = pickle_data[6]["bookTitle"]
    #searchable_books = searchable_books.sort_values() #used for series
    searchable_books = set(searchable_books)
    searchable_books = list(searchable_books)
    searchable_books.sort()
    st.subheader("Enter the name of your book")
    #hiding starts here
    show = False
    search_placeholder = st.empty()
    if show:
        search_term = search_placeholder.text_input("Enter a keyword", key="search", on_change=True)
    else:
        search_term = ""
    #hiding ends here
    
    
    # Generate suggestions based on search term
    filtered_suggestions = [s for s in searchable_books if search_term.lower() in s.lower()] 
    selected_suggestion = st.selectbox("", options=filtered_suggestions)
    try:
        suggested_books2 = hybrid_recommend(selected_suggestion)
        display_all_books(suggested_books2)
    except:
        st.write("Please select other book while we expand our search")
    

    
    
    
elif nav_selection == "Report":
    st.title("These are the top 5 graphs")
    
    # most rated book
    book_rating = pickle_data[0].groupby(['bookTitle'])['bookRating'].count().sort_values(ascending=False).reset_index()

    # Create the bar chart using Altair
    st.subheader("Most-Rated Books")
    chart = alt.Chart(book_rating[:10]).mark_bar().encode(
        x=alt.X('bookRating', axis=alt.Axis(title='Rating Count')),
        y=alt.Y('bookTitle', sort='-x', axis=alt.Axis(title='Book Title')),
        tooltip=[alt.Tooltip('bookTitle', title='Book Title'), alt.Tooltip('bookRating', title='Number of people rated')],
        color=alt.Color('bookTitle', scale=alt.Scale(scheme='category20'))
    ).properties(
        width=1400,
        height=400
    ).interactive()

    # Display the chart in Streamlit
    st.altair_chart(chart)
    
    
    # most rated book
    auth_rating=pickle_data[0].groupby(['bookAuthor'])['bookRating'].count().sort_values(ascending=False).reset_index()
       # Filter the data for books with ratings greater than 3000
    filtered_data = auth_rating[auth_rating['bookRating'] > 3000]

    # Create a column for color based on bookAuthor
    filtered_data['color'] = pd.Categorical(filtered_data['bookAuthor']).codes

    # Create the Altair bar chart with color encoding
    chart = alt.Chart(filtered_data).mark_bar().encode(
        x='bookAuthor',
        y='bookRating',
        color=alt.Color('color', scale=alt.Scale(scheme='category20'))
    ).properties(
        width=700,
        height=800
    ).configure_axis(
        labelAngle=25
    )

    # Display the chart using st.altair_chart()
    st.subheader("Most-Rated Author")
    st.altair_chart(chart, use_container_width=True)


    # Group the rating count by age group
    rating_count_by_age = pickle_data[0].groupby('Age_group')['bookRating'].count().reset_index()
    # Create the Altair bar chart
    chart = alt.Chart(rating_count_by_age).mark_bar().encode(
        x='Age_group',
        y='bookRating',
        color=alt.Color('Age_group', scale=alt.Scale(scheme='category20'))
    ).properties(
        width=700,
        height=800
    ).configure_axis(
        labelAngle=45
    )
    # Display the chart using st.altair_chart()
    st.subheader("Number of Ratings by Age Group")
    st.altair_chart(chart, use_container_width=True)
    
    
    
    # Your data and plot code
    year = pickle_data[0]['yearOfPublication'].value_counts().reset_index()
    year.columns = ['value', 'count']
    year['year'] = year['value'].astype(str) + ' year'
    year = year.sort_values('count', ascending=False)

    # Create a color scale
    color_scale = alt.Scale(scheme='category10')

    # Create the Altair bar chart with color encoding
    chart = alt.Chart(year.head(10)).mark_bar().encode(
        x='count',
        y=alt.Y('year', sort='-x'),
        color=alt.Color('year', scale=color_scale),
        tooltip=['year', 'count']
    ).properties(
        title='Top 10 years of publishing'
    )

    # Display the chart using st.altair_chart()
    st.title('Top 10 years of publishing')
    st.altair_chart(chart, use_container_width=True)
    
    
    
    # Set up the Streamlit app
    st.title('Count of Users Country-wise')

    # Compute the count of each country and select the top 10
    top_countries = pickle_data[0]['country'].value_counts().head(10).reset_index()
    top_countries.columns = ['country', 'count']

    # Define a categorical color scheme for the bars
    color_scale = alt.Scale(scheme='category20')

    # Create the Altair chart with different colors for each bar
    chart = alt.Chart(top_countries).mark_bar().encode(
        y=alt.Y('country:N', sort='-x'),
        x='count:Q',
        color=alt.Color('country:N', scale=color_scale)
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
    
    
    # Assuming you have loaded the data into a DataFrame called 'pickle_data'
    rating_count = pickle_data[0].groupby('bookTitle')['bookRating'].count().reset_index()

    # Set up the Streamlit app
    st.title('Number of Ratings by Age Group')

    # Calculate the count of ratings by age group
    rating_by_age = pickle_data[0].groupby('Age_group')['bookRating'].count().reset_index()

    # Define a categorical color scheme for the bars
    color_scale = alt.Scale(scheme='category20')

    # Create the Altair chart with different colors for each bar
    chart = alt.Chart(rating_by_age).mark_bar().encode(
        x='Age_group',
        y='bookRating',
        color=alt.Color('Age_group:N', scale=color_scale),
        tooltip=['Age_group', 'bookRating']
    ).properties(
        width=alt.Step(40),
        height=800
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
    
    
    

    # Assuming you have loaded the data into a DataFrame called 'pickle_data'
    # Assuming you have loaded the data into a DataFrame called 'pickle_data'
    new_age_group_counts = pickle_data[10]['Age_group'].value_counts().reset_index()
    new_age_group_counts.columns = ['Age_group', 'Count']

    # Calculate the sum of counts
    total_count = new_age_group_counts['Count'].sum()

    # Calculate the percentage and format it with one decimal place
    new_age_group_counts['Percentage'] = (new_age_group_counts['Count'] / total_count * 100).round(1).astype(str) + '%'

    # Create the Altair chart as a bar plot
    chart = alt.Chart(new_age_group_counts).mark_bar().encode(
        x='Age_group:N',
        y='Count:Q',
        color='Age_group:N',
        tooltip=['Age_group', 'Count', 'Percentage']
    ).properties(
        width=1000,
        height=500,
        title='Age Group Distribution'
    )

    # Add text labels to show percentage values on top of the bars
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        fontSize=12,
        fontWeight='bold',
        color='black',
        dy=-5,  # Adjust the vertical position of the labels
    ).encode(
        text='Percentage'
    )

    # Combine the chart and text labels
    chart_with_labels = (chart + text)

    # Display the chart with labels
    chart_with_labels


elif nav_selection == "Reference":
    with st.container():
        left_column, right_column = st.columns(2)
    with left_column:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.title("References")
    with right_column:
        st_lottie(Animation2,key="coding",height=200)
    
    st.write("---")
    st.subheader("- Official documentation for Streamlit")
    st.markdown("[Click here to access documentation](https://docs.streamlit.io/)")
    st.subheader("- Pickle Library guide on Geeks For Geeks")
    st.markdown("[Click here to know more](https://www.geeksforgeeks.org/understanding-python-pickling-example/)")
    st.subheader("- Official documentation for Urllib Library")
    st.markdown("[Click here to access documentation](https://docs.python.org/3/library/urllib.parse)")
    st.subheader("- Video tutorial from ExcelR")
    st.markdown("[Click here to view video](https://elearning.excelr.com/dashboard)")
    st.subheader("- Short guide for Streamlit on YouTube")
    st.markdown("[Click here to view video](https://www.youtube.com/watch?v=VqgUkExPvLY)")
    
    # Add content for the About page
    
    
    
    