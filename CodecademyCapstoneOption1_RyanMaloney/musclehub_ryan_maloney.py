
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have to pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[9]:

# This import only needs to happen once, at the beginning of the notebook
from codecademySQL_rm import sql_query


# In[2]:

# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[3]:

# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[10]:

# Examine visits here
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[11]:

# Examine fitness_tests here
sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5
''')


# In[12]:

# Examine applications here
sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# In[13]:

# Examine purchases here
sql_query('''
SELECT *
FROM purchases
LIMIT 5
''')


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[247]:

# Only select the columns we want!
df = sql_query('''SELECT visits.first_name, visits.last_name, visits.gender, visits.email, 
fitness_tests.fitness_test_date, applications.application_date, purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
ON visits.first_name = fitness_tests.first_name
AND visits.last_name = fitness_tests.last_name
AND visits.email = fitness_tests.email
LEFT JOIN applications
ON visits.first_name = applications.first_name
AND visits.last_name = applications.last_name
AND visits.email = applications.email
LEFT JOIN purchases
ON visits.first_name = purchases.first_name
AND visits.last_name = purchases.last_name
AND visits.email = purchases.email
WHERE visits.visit_date >= '7-1-17';
''')
print (len(df))
# the dataframe contains 5004 rows :-D
list(df)


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[49]:

import pandas as pd
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[248]:

# Use a simple lambda function with an if statement and 'apply' to enter the new column
df['ab_test_group'] = df.fitness_test_date.apply(lambda x: 'B' if x == None else 'A')
print(df[0:10])
#print(df.fitness_test_date[0:10])


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[251]:

# list (df) >this lists the column labels.
ab_counts = df.groupby(['ab_test_group']).first_name.count()
print (ab_counts)
# Janet has assigned approximately the same amount of visitors to each group.


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[254]:

plt.figure()
plt.pie([2504, 2500], autopct='%0.2f%%')
plt.title('Percentage of gym-goers assigned to each group')
plt.legend(['A', 'B'])
plt.axis('equal')
plt.savefig('ab_test_pie_chart.png')
plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[256]:

df['is_application'] = df.application_date.apply(lambda x: 'No Application' if x == None else 'Application')
list(df)


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[369]:

app_counts = df.groupby(['ab_test_group', 'is_application']).first_name.count().reset_index()
# rename the column something more meaningful than 'first_name'
app_counts.rename(columns={'first_name': 'Application_status'}, inplace=True)
print(app_counts[0:10])
#type(app_counts)


# We're going to want to calculate the percentage of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[370]:

app_pivot = app_counts.pivot(columns = 'is_application', index = 'ab_test_group').reset_index()
print(app_counts[0:9])


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[371]:

app_pivot['Total'] = app_pivot[('Application_status', 'Application')] + app_pivot[('Application_status', 'No Application')]
print (app_pivot)


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[372]:

app_pivot['Percent with Application'] = app_pivot[('Application_status', 'Application')] / app_pivot[('Total')] * 100
print(app_pivot)


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[458]:

# We will perform a chi-squared test for independence
from scipy.stats import chi2_contingency

chi2, pval, dof, expected = chi2_contingency([app_pivot[('Application_status', 'Application')],                                                app_pivot[('Application_status', 'No Application')]])
  
print (chi2)
print(dof)
print (pval)
# The chi2 statistic IS significant at P < 0.001, so we can REJECT THE NULL hypothesis that there is no difference in the number of gym
# applications made between groups A and B.


# ## Step 5: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[294]:

df['is_member'] = df.purchase_date.apply(lambda x: 'Not Member' if x == None else 'Member')
list(df)


# Now, let's create a DataFrame called `just_apps` the contains **only people who picked up an application.**

# In[314]:

just_apps = df[df.is_application == 'Application']
print(just_apps[0:9])
len(just_apps)


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[348]:

# First, groupby membership status and AB test group assignment. Count by first name
member_counts = just_apps.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()

# Just rename the column to something more meaningful than 'first_name'
member_counts.rename(columns={"first_name": "Membership"}, inplace=True)
list(member_counts)

#Now perform the pivot
member_pivot = member_counts.pivot(columns = 'is_member', index = 'ab_test_group').reset_index()
#print(member_pivot[0:9])

#Generate a new column with the totals from Groups A and B:
member_pivot['Total'] = member_pivot[('Membership', 'Member')] + member_pivot[('Membership', 'Not Member')]

# Compute the percentages now that went on to purchase a membership
member_pivot['Percent Purchase'] = member_pivot[('Membership', 'Member')] / member_pivot[('Total')] * 100
print (member_pivot)


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[459]:

# We will perform another chi-squared test for independence
from scipy.stats import chi2_contingency

chi2, pval, dof, expected = chi2_contingency([member_pivot[('Membership', 'Member')],                                                member_pivot[('Membership', 'Not Member')]])
  
print (chi2)
print(dof)
print (pval)

# "people who took the fitness test were more likely to purchase a membership if they picked up an application"
# It's possible they felt pressured to do so by the fitness instructor; 
# or maybe discovering how unfit they were in the test motivated
# them to purchase the application?
# It's irrelevant anyway because the result is not significant, we retain the null hypothesis that there was no difference
# in the number of people who purchased a membership depending on whether they were in group A or B.


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[355]:

# First, groupby membership status and AB test group assignment. Count by first name
final_member_counts = df.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()

# Just rename the column to something more meaningful than 'first_name'
final_member_counts.rename(columns={"first_name": "Membership"}, inplace=True)

#Now perform the pivot
final_member_pivot = final_member_counts.pivot(columns = 'is_member', index = 'ab_test_group').reset_index()

#Generate a new column with the totals from Groups A and B:
final_member_pivot['Total'] = final_member_pivot[('Membership', 'Member')] + final_member_pivot[('Membership', 'Not Member')]

# Compute the percentages now that went on to purchase a membership
final_member_pivot['Percent Purchase'] = final_member_pivot[('Membership', 'Member')] / final_member_pivot[('Total')] * 100
print (final_member_pivot[0:9])


# Previously, when we only considered people who had **already picked up an application**, we saw that there was **no significant difference in membership** between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant difference in memberships between Group A and Group B.  Perform a significance test and check.

# In[461]:

# We will perform another chi-squared test for independence

chi2, pval, dof, expected = chi2_contingency([final_member_pivot[('Membership', 'Member')],                                                final_member_pivot[('Membership', 'Not Member')]])
  
print (chi2)
print(dof)
print (pval)

# the Chi**2 statistic is significant to p < 0.02 so we can reject the null hypothesis that there is no difference in overall 
# membership numbers between groups A and B.


# ## Step 6: Summarize the acquisition funnel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each stage of the process:
# - Percentage of visitors who apply
# - Percentage of applicants who purchase a membership
# - Percentage of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percentages (i.e., `5%`)
# - Have a title

# In[457]:

# 1. Generate bar plot for the percentage of visitors from each group who make an application
from matplotlib import pyplot as plt
from numpy import sqrt as sqrt

print(app_pivot)
#Compute binomial standard errors for the bar plot:
bin_se = sqrt( (app_pivot['Application_status', 'Application']/app_pivot['Total']) * (app_pivot['Application_status', 'No Application']/app_pivot['Total']) / app_pivot['Total'] ) * 100 #multiply by 100 to express as percentage

labels = ['A: Fitness Test', 'B: No Fitness Test']

fig = plt.figure()
ax = plt.subplot()
ax.bar([0, 1], app_pivot['Percent with Application'], yerr = bin_se)
ax.set_xticks([0, 1])

ax.set_xticklabels(labels)
plt.title('Applications made following the A/B test')
plt.ylabel('Applicants (% of group)')
plt.show()
fig.savefig('applications_made.png')


# In[460]:

# 2. Generate bar plot to depict percentage of those who made applications that purchased memberships
print(member_pivot)

#Compute binomial standard errors for the bar plot:
bin_se = sqrt( (member_pivot['Membership', 'Member']/member_pivot['Total']) * (member_pivot['Membership', 'Not Member']/member_pivot['Total']) / member_pivot['Total'] ) * 100 #multiply by 100 to express as percentage

labels = ['A: Fitness Test', 'B: No Fitness Test']
fig = plt.figure()
ax = plt.subplot()
plt.bar([0, 1], member_pivot['Percent Purchase'], yerr = bin_se)

ax.set_xticks([0, 1])
ax.set_xticklabels(labels)
plt.title('Memberships purchased by visitors after application')
plt.ylabel('Memberships (% of applicants)')
plt.show()
fig.savefig('apps_made_memberships')


# In[463]:

# 3. Bar plot to depict percentage of all visitors in the A/B test who went on to purchase memberships
print(final_member_pivot)

#Compute binomial standard errors for the bar plot:
bin_se = sqrt( (final_member_pivot['Membership', 'Member']/final_member_pivot['Total']) * (final_member_pivot['Membership', 'Not Member']/final_member_pivot['Total']) / final_member_pivot['Total'] ) * 100 # multiply by 100 to express as percentage

labels = ['A: Fitness Test', 'B: No Fitness Test']

fig = plt.figure()
ax = plt.subplot()
plt.bar([0, 1], final_member_pivot['Percent Purchase'], yerr = bin_se)

ax.set_xticks([0, 1])
ax.set_xticklabels(labels)
plt.title('Memberships purchased by all visitors in A/B test')
plt.ylabel('Memberships (% of group)')
plt.show()
fig.savefig('memberships_purchased.png')

