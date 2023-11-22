import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from kmodes.kprototypes import KPrototypes
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
import seaborn as sns
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import pdist


##PREPOCESSING DATA##
def filter_data_new(bool):
    tbranch = bool #indicating whether TeamsBranch should be included or not
    #reading file
    df = pd.read_csv('survey_results_public.csv')
    #filtering data 
    if tbranch:
        condition = (df['Country'] == "Germany") & (df["TBranch"] == "Yes")
    else:
        condition = (df['Country'] == "Germany") 

    df = df.loc[condition] 

    #remove columns: (possibly more if considered obsolete)
        # CompTotal, Currency and Comp Freq are all used to calculae ConvertedCompYearly
        # 'VCHostingPersonal use', 'VCHostingProfessional use' werent answered by anybody
        # there also questions which I consider to be irrelevant

    drop_cols = ['CompTotal', "Currency", "CompFreq", 'VCHostingPersonal use', 'VCHostingProfessional use', 
        "SurveyLength","SurveyEase","ResponseId", "Blockchain", "NEWSOSites", "SOVisitFreq", "SOAccount", "SOPartFreq", "Trans", 
        "Sexuality", "Ethnicity", "Accessibility"]
    
    if not tbranch:
        drop_cols += ['WorkExp', "ICorPM","Knowledge_1","Knowledge_2","Knowledge_3","Knowledge_4","Knowledge_5","Knowledge_6","Knowledge_7",
                      "Frequency_1", "Frequency_2", "Frequency_3","TimeSearching","TimeAnswering","Onboarding","ProfessionalTech",
                      "TrueFalse_1","TrueFalse_2","TrueFalse_3"]
        
    df = df.drop(labels=drop_cols, axis=1)

    ## NUMERICAL DATA ##

    #replace ambivalent labels with concrete values(estimation)
    df["YearsCodePro"] = df["YearsCodePro"].replace("Less than 1 year", "0.5")
    df["YearsCode"].replace({"More than 50 years": "51", "Less than 1 year": "0"}, inplace=True)
    df["Age"].replace({"Under 18 years old": "17", "18-24 years old": "21", "25-34 years old": "29.5", "35-44 years old": "39.5",
        "45-54 years old": "49.5", "55-64 years old": "59.5", "65 years or older": "65", "Prefer not to say": "0"}, inplace=True)
    
    if tbranch:
        #normalize "WorkExperience" to value between 0 and 2
        # because for other categories like "Education Level", the maximum distance is 2
        # e.g. the first person chose "master" (1) and the other one didn´t (0). The other person chose "bachelor"(1) and the first one didn´t (0)
        # -> resulting maximum distance is 2. 
        #This step is only necessary for categories relevant for the clustering
        scalers = {}
        cols_to_transform = ["WorkExp"]
        for col in cols_to_transform:
            scaler = MinMaxScaler(feature_range=(0, 2))
            df[col] = scaler.fit_transform(df[[col]])
            scalers[col] = scaler
        
        knowledge_list = ["Knowledge_1", "Knowledge_2", "Knowledge_3", "Knowledge_4", "Knowledge_5", "Knowledge_6", "Knowledge_7"]
        for element in knowledge_list:
            df[element].replace({"Strongly disagree": "0", "Disagree": "0.25", "Neither agree nor disagree": "0.5", "Agree": "0.75",
            "Strongly agree": "1", np.nan: "0.5"}, inplace=True)

        for element in knowledge_list:
            df[element] = df[element].astype(float)

    else:
        scalers = 0

    ## ORDINAL DATA ##

    #replace levels of agreement with corresponding digits between 0 and 1
    df["SOComm"].replace({"No, not at all": "0", "No, not really": "0.25", "Neutral": "0.5", "Yes, somewhat": "0.75",
        "Yes, definitely": "1", "Not sure": "0.5"}, inplace=True)
    

    #convert to float and fill nan-values with median
    numerical_cols = ["YearsCode", "YearsCodePro", "ConvertedCompYearly", "Age", "SOComm"] #add work experience for teams branch
    for element in numerical_cols:
        df[element] = df[element].astype(float)
        df[element] = df[element].fillna(df[element].median())
    df["Age"] = df["Age"].replace(0, df["Age"].median())


    ## CATEGORICAL DATA ##

    #selecting categorical columns; NaN-entrys are treated as own value
    cat_cols = list(df.select_dtypes(exclude=['float64',"int64"]).columns)
    df[cat_cols] = df[cat_cols].astype(str)
    df[cat_cols] = df[cat_cols].fillna('unknown')

    #one-hot-encoding of categorical data
    for col in cat_cols:
        mlb = MultiLabelBinarizer(sparse_output=True)
        df = df.join(
                    pd.DataFrame.sparse.from_spmatrix(
                        mlb.fit_transform(df.pop(col).apply(lambda x: x.split(';'))),
                        index=df.index,
                        columns=[col+'_'+c for c in mlb.classes_]))
    
    #for "DevType", multiple answers were possible
    # the maximum distance that was reached is 24
    # therefore, each value (1 or 0) is divided by 12 in order the decrease the maximum distance to 2.
    transform = df.filter(regex='^DevType_', axis=1).columns.tolist()
    df[transform] = df[transform].multiply(1/12)

    #return new dataframe and scaler 
    return df, scalers

def load_filtered_data(filename):
    df = pd.read_csv(filename)
    #print(df['TBranch_Yes'].mean() * 100)
    return df

def elbow_method(df, n, bool):
    tbranch = bool
    #select relevant columns
    relevant_cols = []
    relevant_cols += df.filter(regex='^MainBranch_', axis=1).columns.tolist()
    relevant_cols += df.filter(regex='^EdLevel_', axis=1).columns.tolist()
    relevant_cols += df.filter(regex='^DevType_', axis=1).columns.tolist()
    
    if tbranch:
        relevant_cols.append("WorkExp")

    cost = []
    for i in range(2, n):
        model = AgglomerativeClustering(n_clusters=i, linkage='ward')
        model.fit(df[relevant_cols].to_numpy())
        
        score = silhouette_score(df[relevant_cols], model.labels_)
        # Append the silhouette score to the list
        cost.append(score)

    # Plot the elbow graph
    plt.plot(range(2, n), cost)
    plt.title('Elbow Graph')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Cost')
    plt.show()

def cluster(df, n, bool, file_exc, file_csv, scalers, bool_2):
    tbranch = bool_2
   
    relevant_cols = []
    relevant_cols += df.filter(regex='^MainBranch_', axis=1).columns.tolist()
    relevant_cols += df.filter(regex='^EdLevel_', axis=1).columns.tolist()
    relevant_cols += df.filter(regex='^DevType_', axis=1).columns.tolist()
    
    if tbranch:
        relevant_cols.append("WorkExp")


    agg_cluster = AgglomerativeClustering(n_clusters=n)
    clusters = agg_cluster.fit_predict(df[relevant_cols].to_numpy())

    df_clusters = pd.DataFrame({'Cluster': clusters}, index=df.index)
    print(df_clusters['Cluster'].value_counts().sort_index)
    # merge the original dataframe with the cluster assignments
    df = pd.concat([df, df_clusters], axis=1)

    new_df = pd.DataFrame(index= range(n), columns=df.columns)
    print("ok")
    
    transform = df.filter(regex='^DevType_', axis=1).columns.tolist()
    df[transform] = df[transform].multiply(12)

    # Loop through each column of the original dataframe and calculate the percentage of people who answered "yes" for that question within each group
    for col in df.columns:
        if col != 'Cluster':
            if col in ["YearsCodePro", "YearsCode", "ConvertedCompYearly", "Age"]:
                for i in range(n):
                    new_df.loc[i, col] = round([[df[df['Cluster'] == i][col].mean()]][0][0],1)
            
            elif col == "WorkExp":
                scaler = scalers[col]
                for i in range(n):
                    new_df.loc[i, col] = round(scaler.inverse_transform([[df[df['Cluster'] == i][col].mean()]])[0][0],1)

            else:
                for i in range(n):
                    new_df.loc[i, col] = round(df[df['Cluster'] == i][col].mean()*100,1)
    
    print("ok2")
    # Convert the values in the new dataframe to floats
    new_df = new_df.astype(float)
    new_df = new_df.drop(labels=["Cluster"], axis=1)

    # Print and save the new dataframe
    print(new_df)
    if bool:
        new_df.to_excel(file_exc, index=False)
        new_df.to_csv(file_csv, index=False)
    return new_df


def dendogram(df, bool):
    tbranch = bool
    relevant_cols = []
    relevant_cols += df.filter(regex='^MainBranch_', axis=1).columns.tolist()
    relevant_cols += df.filter(regex='^EdLevel_', axis=1).columns.tolist()
    relevant_cols += df.filter(regex='^DevType_', axis=1).columns.tolist()

    if tbranch:
        relevant_cols.append("WorkExp")

    plt.figure()  
    plt.title("Dendrogram")  
    dend = shc.dendrogram(shc.linkage(df[relevant_cols], method='ward'))
    plt.show()


##CODE##
df, scalers = filter_data_new(False)

#corr_matrix = df.corr()
#corr_matrix.to_excel('correlation_matrix.xlsx', index=True)

elbow_method(df, 20, False)

dendogram(df, False)

new_df = cluster(df, 4, True, "df_thursday_agg.xlsx", 'df_thursday_agg.csv',scalers, False)


