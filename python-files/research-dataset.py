import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# Create student IDs and demographics
n_students = 358
student_ids = ['S' + str(i+1).zfill(3) for i in range(n_students)]
semesters = np.concatenate([np.repeat(2, 180), np.repeat(4, 178)])
gender = np.random.choice(['Male', 'Female'], size=n_students, p=[0.35, 0.65])  # Assuming 35% male, 65% female

# Create dimensions for Feedback Literacy
# Dimensions based on Carless & Boud (2018): 
# appreciating feedback, making judgments, managing affect, taking action
fl_appreciation = np.random.normal(3.7, 0.8, n_students).clip(1, 5)
fl_judgment = np.random.normal(3.5, 0.9, n_students).clip(1, 5)
fl_affect = np.random.normal(3.4, 0.9, n_students).clip(1, 5)
fl_action = np.random.normal(3.6, 0.85, n_students).clip(1, 5)

# Create dimensions for Psychological Well-being
# Dimensions based on Ryff's model: 
# autonomy, environmental mastery, personal growth, positive relations, purpose, self-acceptance
pwb_autonomy = np.random.normal(3.6, 0.8, n_students).clip(1, 5)
pwb_mastery = np.random.normal(3.5, 0.75, n_students).clip(1, 5)
pwb_growth = np.random.normal(3.8, 0.7, n_students).clip(1, 5)
pwb_relations = np.random.normal(3.7, 0.85, n_students).clip(1, 5)
pwb_purpose = np.random.normal(3.6, 0.8, n_students).clip(1, 5)
pwb_acceptance = np.random.normal(3.5, 0.9, n_students).clip(1, 5)

# Create dimensions for Willingness to Communicate
# Based on MacIntyre et al.'s model:
# communication readiness, communication confidence, communication anxiety (reverse)
wtc_readiness = np.random.normal(3.4, 0.9, n_students).clip(1, 5)
wtc_confidence = np.random.normal(3.3, 1.0, n_students).clip(1, 5)
wtc_anxiety = (6 - np.random.normal(3.0, 1.1, n_students).clip(1, 5))  # Reverse scored

# Create dimensions for Speaking Performance
# Based on Housen & Kuiken's (2009) CAF framework:
# fluency, accuracy, complexity, appropriateness
sp_fluency = np.random.normal(3.4, 0.9, n_students).clip(1, 5)
sp_accuracy = np.random.normal(3.5, 0.85, n_students).clip(1, 5)
sp_complexity = np.random.normal(3.3, 0.8, n_students).clip(1, 5)
sp_appropriateness = np.random.normal(3.6, 0.75, n_students).clip(1, 5)

# Adjust 4th semester students to have slightly higher scores
# (reflecting their greater experience and proficiency)
fourth_semester_idx = np.where(semesters == 4)[0]
skill_improvement = 0.3  # Average improvement for 4th semester students

for idx in fourth_semester_idx:
    # Feedback Literacy improvements
    fl_appreciation[idx] += np.random.normal(skill_improvement, 0.2)
    fl_judgment[idx] += np.random.normal(skill_improvement, 0.2)
    fl_affect[idx] += np.random.normal(skill_improvement, 0.2)
    fl_action[idx] += np.random.normal(skill_improvement, 0.2)
    
    # Psychological Well-being improvements
    pwb_autonomy[idx] += np.random.normal(skill_improvement, 0.15)
    pwb_mastery[idx] += np.random.normal(skill_improvement, 0.15)
    pwb_growth[idx] += np.random.normal(skill_improvement, 0.15)
    pwb_relations[idx] += np.random.normal(skill_improvement, 0.15)
    pwb_purpose[idx] += np.random.normal(skill_improvement, 0.15)
    pwb_acceptance[idx] += np.random.normal(skill_improvement, 0.15)
    
    # Willingness to Communicate improvements
    wtc_readiness[idx] += np.random.normal(skill_improvement, 0.25)
    wtc_confidence[idx] += np.random.normal(skill_improvement, 0.25)
    wtc_anxiety[idx] += np.random.normal(skill_improvement, 0.25)
    
    # Speaking Performance improvements
    sp_fluency[idx] += np.random.normal(skill_improvement, 0.25)
    sp_accuracy[idx] += np.random.normal(skill_improvement, 0.25)
    sp_complexity[idx] += np.random.normal(skill_improvement, 0.25)
    sp_appropriateness[idx] += np.random.normal(skill_improvement, 0.25)

# Clip all values to ensure they remain within 1-5 scale
fl_appreciation = fl_appreciation.clip(1, 5)
fl_judgment = fl_judgment.clip(1, 5)
fl_affect = fl_affect.clip(1, 5)
fl_action = fl_action.clip(1, 5)

pwb_autonomy = pwb_autonomy.clip(1, 5)
pwb_mastery = pwb_mastery.clip(1, 5)
pwb_growth = pwb_growth.clip(1, 5)
pwb_relations = pwb_relations.clip(1, 5)
pwb_purpose = pwb_purpose.clip(1, 5)
pwb_acceptance = pwb_acceptance.clip(1, 5)

wtc_readiness = wtc_readiness.clip(1, 5)
wtc_confidence = wtc_confidence.clip(1, 5)
wtc_anxiety = wtc_anxiety.clip(1, 5)

sp_fluency = sp_fluency.clip(1, 5)
sp_accuracy = sp_accuracy.clip(1, 5)
sp_complexity = sp_complexity.clip(1, 5)
sp_appropriateness = sp_appropriateness.clip(1, 5)

# Calculate composite scores
feedback_literacy = (fl_appreciation + fl_judgment + fl_affect + fl_action) / 4
psychological_wellbeing = (pwb_autonomy + pwb_mastery + pwb_growth + 
                          pwb_relations + pwb_purpose + pwb_acceptance) / 6
willingness_to_communicate = (wtc_readiness + wtc_confidence + wtc_anxiety) / 3
speaking_performance = (sp_fluency + sp_accuracy + sp_complexity + sp_appropriateness) / 4

# Create relationships between variables to match our theoretical model
# (introducing some correlation while keeping natural variability)

# Adjust Speaking Performance based on our model's relationships
for i in range(n_students):
    # Direct effect of Feedback Literacy on Speaking Performance (H3)
    sp_direct_fl = 0.3 * (feedback_literacy[i] - np.mean(feedback_literacy))
    
    # Direct effect of Psychological Well-being on Speaking Performance (H4)
    sp_direct_pwb = 0.25 * (psychological_wellbeing[i] - np.mean(psychological_wellbeing))
    
    # Indirect effect through WTC (H6 & H7)
    wtc_effect = 0.35 * (willingness_to_communicate[i] - np.mean(willingness_to_communicate))
    
    # Apply combined effects with some random noise
    speaking_performance[i] += sp_direct_fl + sp_direct_pwb + wtc_effect + np.random.normal(0, 0.3)

# Clip again to ensure values remain within scale
speaking_performance = speaking_performance.clip(1, 5)

# Create dataframe with all variables
data = pd.DataFrame({
    'StudentID': student_ids,
    'Semester': semesters,
    'Gender': gender,
    
    # Feedback Literacy dimensions
    'FL_Appreciation': fl_appreciation.round(2),
    'FL_Judgment': fl_judgment.round(2),
    'FL_Affect': fl_affect.round(2),
    'FL_Action': fl_action.round(2),
    'Feedback_Literacy': feedback_literacy.round(2),
    
    # Psychological Well-being dimensions
    'PWB_Autonomy': pwb_autonomy.round(2),
    'PWB_Mastery': pwb_mastery.round(2),
    'PWB_Growth': pwb_growth.round(2),
    'PWB_Relations': pwb_relations.round(2),
    'PWB_Purpose': pwb_purpose.round(2),
    'PWB_Acceptance': pwb_acceptance.round(2),
    'Psychological_Wellbeing': psychological_wellbeing.round(2),
    
    # Willingness to Communicate dimensions
    'WTC_Readiness': wtc_readiness.round(2),
    'WTC_Confidence': wtc_confidence.round(2),
    'WTC_Anxiety': wtc_anxiety.round(2),
    'Willingness_to_Communicate': willingness_to_communicate.round(2),
    
    # Speaking Performance dimensions
    'SP_Fluency': sp_fluency.round(2),
    'SP_Accuracy': sp_accuracy.round(2),
    'SP_Complexity': sp_complexity.round(2),
    'SP_Appropriateness': sp_appropriateness.round(2),
    'Speaking_Performance': speaking_performance.round(2)
})

# Display basic info about the dataset
print(f"Dataset shape: {data.shape}")
print("\nSample of the data:")
print(data.head())

# Basic statistics for main variables
print("\nBasic statistics for main variables:")
main_vars = ['Feedback_Literacy', 'Psychological_Wellbeing', 
             'Willingness_to_Communicate', 'Speaking_Performance']
print(data[main_vars].describe().round(2))

# Correlation matrix for main variables
print("\nCorrelation matrix for main variables:")
corr_matrix = data[main_vars].corr().round(3)
print(corr_matrix)

# Compare means by semester
print("\nMean scores by semester:")
semester_means = data.groupby('Semester')[main_vars].mean().round(2)
print(semester_means)

# Calculate differences between semesters
print("\nDifference between 4th and 2nd semester (percentage):")
diff = ((semester_means.loc[4] - semester_means.loc[2]) / semester_means.loc[2] * 100).round(1)
print(diff)

# Sample data for analysis
sample_data = data.sample(min(20, len(data)))
print("\nSample rows for detailed analysis:")
print(sample_data[['StudentID', 'Semester', 'Gender'] + main_vars].head(10))

# Export to CSV
data.to_csv('efl_research_data.csv', index=False)
print("\nDataset exported to 'efl_research_data.csv'")

# Create some basic visualizations
plt.figure(figsize=(10, 8))

# Correlation heatmap
plt.subplot(2, 2, 1)
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=.5)
plt.title('Correlation Between Main Variables')

# Variable distributions
plt.subplot(2, 2, 2)
for var in main_vars:
    sns.kdeplot(data[var], label=var)
plt.title('Distribution of Main Variables')
plt.legend()

# Comparison by semester
plt.subplot(2, 2, 3)
semester_means.plot(kind='bar')
plt.title('Mean Scores by Semester')
plt.ylabel('Score (1-5 scale)')
plt.ylim(1, 5)

# Scatter plot with regression line
plt.subplot(2, 2, 4)
sns.regplot(x='Willingness_to_Communicate', y='Speaking_Performance', data=data)
plt.title('WTC vs Speaking Performance')

plt.tight_layout()
plt.savefig('efl_data_visualization.png')
print("Basic visualizations saved to 'efl_data_visualization.png'")

# Display first 20 rows of data in a more readable format
pretty_data = data.iloc[:20].round(2)
print("\nFirst 20 rows of dataset (for review):")
pretty_data
